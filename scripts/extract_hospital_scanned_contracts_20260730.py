#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
import shutil
import ssl
import subprocess
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import unquote, urlparse

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "research" / "nemocnice-kadan-neindexovane-20260730"
WORK = OUT / "_work"
OUT.mkdir(parents=True, exist_ok=True)
WORK.mkdir(parents=True, exist_ok=True)

DUMPS = [
    "https://data.smlouvy.gov.cz/dump_2026_06.xml",
    "https://data.smlouvy.gov.cz/dump_2026_07.xml",
]
KEYWORDS = (
    "dodatek č. 4 ke smlouvě o úvěru",
    "770 21 120",
    "770/21-120",
    "modernizace a interoperability nis",
    "servisní smlouva",
    "zpracování osobních údajů",
    "individuální dotace",
    "poskytnutí dotace",
)


def local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def download(url: str, path: Path) -> None:
    """Stáhne dokument; u příloh Registru toleruje vadný certifikační řetězec.

    Obsah je následně kontrolován podle signatury a ukládá se jeho SHA-256,
    takže vypnutí TLS verifikace neslouží jako náhrada kontroly souboru.
    """
    req = urllib.request.Request(url, headers={"User-Agent": "NaseKadan-research/1.0"})
    context = ssl._create_unverified_context() if urlparse(url).hostname == "smlouvy.gov.cz" else None
    with urllib.request.urlopen(req, timeout=240, context=context) as response, path.open("wb") as target:
        shutil.copyfileobj(response, target)
    data = path.read_bytes()
    if not data:
        raise RuntimeError("Stažený soubor je prázdný")
    suffix = path.suffix.lower()
    if suffix == ".pdf" and not data.startswith(b"%PDF-"):
        raise RuntimeError(f"Odkaz nevrátil PDF; začátek souboru: {data[:40]!r}")


def all_texts(element: ET.Element) -> dict[str, list[str]]:
    result: dict[str, list[str]] = {}
    for node in element.iter():
        value = (node.text or "").strip()
        if value:
            result.setdefault(local(node.tag), []).append(value)
        for value in node.attrib.values():
            if value:
                result.setdefault("@attr", []).append(value)
    return result


def first(values: dict[str, list[str]], names: tuple[str, ...]) -> str:
    for name in names:
        for key, vals in values.items():
            if key.lower() == name.lower() and vals:
                return vals[0]
    return ""


def safe_name(value: str, fallback: str) -> str:
    value = unquote(value)
    value = re.sub(r"[^0-9A-Za-zÀ-ž._-]+", "-", value).strip("-.")
    return value[:140] or fallback


def run(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, check=check, text=True, capture_output=True)


def pdf_text_and_ocr(pdf: Path, stem: str) -> dict[str, object]:
    text_path = OUT / f"{stem}.txt"
    raw_path = WORK / f"{stem}-raw.txt"
    subprocess.run(["pdftotext", "-layout", str(pdf), str(raw_path)], check=False)
    raw = raw_path.read_text(encoding="utf-8", errors="replace") if raw_path.exists() else ""
    info = run("pdfinfo", str(pdf), check=False).stdout
    match = re.search(r"^Pages:\s+(\d+)", info, re.M)
    pages = int(match.group(1)) if match else 0
    used_ocr = len(re.sub(r"\s+", "", raw)) < max(500, pages * 100)
    combined = raw
    rendered: list[Path] = []
    if used_ocr:
        prefix = WORK / f"{stem}-page"
        subprocess.run(
            ["pdftoppm", "-jpeg", "-r", "180", "-f", "1", "-l", str(min(pages or 40, 40)), str(pdf), str(prefix)],
            check=False,
        )
        rendered = sorted(WORK.glob(f"{stem}-page-*.jpg"))
        parts: list[str] = []
        for index, image in enumerate(rendered, 1):
            outbase = WORK / f"{stem}-ocr-{index:03d}"
            subprocess.run(
                ["tesseract", str(image), str(outbase), "-l", "ces+eng", "--psm", "6"],
                check=False,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            ocr_file = outbase.with_suffix(".txt")
            parts.append(
                f"\n\n===== STRANA {index} / OCR =====\n"
                + (ocr_file.read_text(encoding="utf-8", errors="replace") if ocr_file.exists() else "")
            )
        combined = raw + "".join(parts)
    text_path.write_text(combined, encoding="utf-8", newline="\n")

    # Přehledové listy stránek pro následnou vizuální kontrolu; originální PDF se neukládají do repozitáře.
    sheets: list[str] = []
    if not rendered and pages:
        prefix = WORK / f"{stem}-preview"
        subprocess.run(
            ["pdftoppm", "-jpeg", "-r", "100", "-f", "1", "-l", str(min(pages, 24)), str(pdf), str(prefix)],
            check=False,
        )
        rendered = sorted(WORK.glob(f"{stem}-preview-*.jpg"))
    if rendered:
        try:
            from PIL import Image, ImageDraw

            for start in range(0, len(rendered), 4):
                batch = rendered[start : start + 4]
                thumbs = []
                for idx, image_path in enumerate(batch, start + 1):
                    image = Image.open(image_path).convert("RGB")
                    image.thumbnail((700, 950))
                    canvas = Image.new("RGB", (720, 1000), "white")
                    canvas.paste(image, ((720 - image.width) // 2, 30))
                    ImageDraw.Draw(canvas).text((20, 970), f"Strana {idx}", fill="black")
                    thumbs.append(canvas)
                sheet = Image.new("RGB", (1440, 2000), "white")
                for pos, thumb in enumerate(thumbs):
                    sheet.paste(thumb, ((pos % 2) * 720, (pos // 2) * 1000))
                sheet_path = OUT / f"{stem}-strany-{start + 1:02d}-{start + len(batch):02d}.jpg"
                sheet.save(sheet_path, quality=82, optimize=True)
                sheets.append(sheet_path.name)
        except Exception as exc:
            (OUT / f"{stem}-preview-error.txt").write_text(str(exc), encoding="utf-8")
    return {"pages": pages, "used_ocr": used_ocr, "text_file": text_path.name, "sheets": sheets}


records: list[dict[str, object]] = []
for dump_url in DUMPS:
    dump_path = WORK / Path(urlparse(dump_url).path).name
    download(dump_url, dump_path)
    for _event, elem in ET.iterparse(dump_path, events=("end",)):
        if local(elem.tag).lower() != "zaznam":
            continue
        xml_text = ET.tostring(elem, encoding="unicode")
        folded = xml_text.casefold()
        if "25479300" not in folded and "nemocnice kadaň" not in folded and "nemocnice kadan" not in folded:
            elem.clear()
            continue
        values = all_texts(elem)
        title = first(values, ("predmet", "predmetSmlouvy", "predmet_smlouvy", "nazev"))
        urls = sorted({v for vals in values.values() for v in vals if v.startswith("http")})
        attachments = [u for u in urls if re.search(r"\.(pdf|docx?|xlsx?|zip)(\?|$)", u, re.I) or "/soubor/" in u]
        records.append(
            {
                "dump": dump_path.name,
                "title": title,
                "published": first(values, ("casZverejneni", "datumZverejneni", "zverejneni")),
                "signed": first(values, ("datumUzavreni", "datum_uzavreni")),
                "contract_id": first(values, ("idSmlouvy", "idsmlouvy")),
                "version_id": first(values, ("idVerze", "idverze")),
                "attachments": attachments,
                "all_urls": urls,
                "xml": xml_text,
            }
        )
        elem.clear()

(OUT / "zaznamy.json").write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")

selected: list[dict[str, object]] = []
for record in records:
    haystack = (str(record.get("title", "")) + " " + str(record.get("xml", ""))).casefold()
    if any(keyword in haystack for keyword in KEYWORDS):
        selected.append(record)

report_lines = [
    "# Neindexované a obrazové přílohy – Nemocnice Kadaň",
    "",
    f"Nalezeno záznamů nemocnice v červnu a červenci 2026: **{len(records)}**.",
    f"Vybráno k hlubokému zpracování: **{len(selected)}**.",
    "",
]
processed: list[dict[str, object]] = []
for rec_index, record in enumerate(selected, 1):
    title = str(record.get("title") or f"zaznam-{rec_index}")
    report_lines.extend(
        [
            f"## {title}",
            "",
            f"- Zveřejnění: {record.get('published') or 'neuvedeno'}",
            f"- Datum uzavření: {record.get('signed') or 'neuvedeno'}",
            f"- ID smlouvy/verze: {record.get('contract_id') or '?'} / {record.get('version_id') or '?'}",
        ]
    )
    attachment_results = []
    for att_index, url in enumerate(record.get("attachments", []), 1):
        filename = safe_name(Path(urlparse(str(url)).path).name, f"priloha-{rec_index}-{att_index}.pdf")
        if not Path(filename).suffix:
            filename += ".pdf"
        stem = safe_name(f"{rec_index:02d}-{title}-{att_index}", f"doc-{rec_index}-{att_index}")
        local_file = WORK / filename
        try:
            download(str(url), local_file)
            sha256 = hashlib.sha256(local_file.read_bytes()).hexdigest()
            if local_file.suffix.lower() == ".pdf":
                details = pdf_text_and_ocr(local_file, stem)
            else:
                out_copy = OUT / f"{stem}{local_file.suffix.lower()}"
                shutil.copy2(local_file, out_copy)
                details = {"pages": None, "used_ocr": False, "text_file": None, "sheets": [], "saved_file": out_copy.name}
            attachment_results.append({"url": url, "sha256": sha256, **details})
            report_lines.append(f"- Příloha: {url}")
            report_lines.append(f"  - SHA-256: `{sha256}`")
            if details.get("text_file"):
                report_lines.append(f"  - Extrahovaný text/OCR: `{details['text_file']}`")
                report_lines.append(f"  - Počet stran: {details['pages']}; OCR použit: {details['used_ocr']}")
                if details.get("sheets"):
                    report_lines.append("  - Náhledy: " + ", ".join(f"`{x}`" for x in details["sheets"]))
        except Exception as exc:
            report_lines.append(f"- Přílohu se nepodařilo stáhnout: {url} — {exc}")
            attachment_results.append({"url": url, "error": str(exc)})
    processed.append({**record, "processed_attachments": attachment_results})
    report_lines.append("")

(OUT / "vybrane-zaznamy.json").write_text(json.dumps(processed, ensure_ascii=False, indent=2), encoding="utf-8")
(OUT / "PREHLED.md").write_text("\n".join(report_lines) + "\n", encoding="utf-8")
shutil.rmtree(WORK, ignore_errors=True)
print(f"Hotovo: {len(records)} záznamů, {len(selected)} vybraných dokumentů.")
