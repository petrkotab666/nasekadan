#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import html
import json
import re
import shutil
import ssl
import subprocess
import time
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlparse

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "research" / "kadanska-hriste-20260805"
WORK = Path("/tmp/nasekadan-hriste-20260805")
OUT.mkdir(parents=True, exist_ok=True)
WORK.mkdir(parents=True, exist_ok=True)

UA = "NaseKadan-playgrounds-research/1.0"
CITY_ICO = "00261912"

CITY_PAGES = [
    ("uredni-deska-hriste-2026", "https://www.mesto-kadan.cz/redakce/index.php?as4uOriginalDomain=www.mesto-kadan.cz&as4u_protocol=https&clanek=274670&detail_claim=293074&lanG=cs&slozka=219380"),
    ("uredni-deska", "https://www.mesto-kadan.cz/cs/system/uredni-deska-nova.html"),
    ("setkavani-kadan", "https://www.setkavanikadan.cz/"),
    ("mp-kadan", "https://www.mpkadan.eu/"),
    ("mp-zpravy", "https://www.mpkadan.eu/zpravy-z-ulice.html"),
    ("mp-kamery", "https://www.mpkadan.eu/kamerovy-system.html"),
    ("lanacek", "https://kadan.eu/aktivity/hriste-lanacek/"),
    ("chytre-hriste", "https://kadan.eu/aktivity/chytre_hriste/"),
    ("dopravni-hriste", "https://kadan.eu/aktivity/dopravni_hriste/"),
    ("skatepark-parkour", "https://kadan.eu/aktivity/skatepark-a-parkourove-hriste/"),
    ("workout", "https://kadan.eu/aktivity/workoutove-hriste/"),
]

# Měsíce s nejvyšší pravděpodobností objednávek, revizí a oprav. Záměrně jsou
# zařazeny i starší začátky roku, kdy město obvykle objednává roční kontroly.
DUMPS = [
    *[f"https://data.smlouvy.gov.cz/dump_2026_{m:02d}.xml" for m in range(1, 9)],
    *[f"https://data.smlouvy.gov.cz/dump_2025_{m:02d}.xml" for m in (1, 2, 3, 4, 5, 6, 9, 10, 11, 12)],
    *[f"https://data.smlouvy.gov.cz/dump_2024_{m:02d}.xml" for m in (1, 2, 3, 4, 5, 6, 9, 10, 11, 12)],
]

KEYWORDS = (
    "hřiště", "hriste", "sportoviště", "sportoviste", "herní", "herni", "houpačk", "houpac",
    "kolotoč", "kolotoc", "brank", "pískoviště", "piskoviste", "kačírek", "kacirek",
    "pryžov", "pryzov", "dopadov", "fitness", "workout", "skate", "parkour", "lanáček",
    "lanacek", "golovinova", "rafanda", "strážiště", "straziste", "podlesí", "podlesi",
    "roosevelt", "revize dětských", "revize detskych", "hlavní roční kontrol", "hlavni rocni kontrol",
    "provozní kontrol", "provozni kontrol", "herold", "hřiště hrou", "hriste hrou",
    "envy sport", "radana kučer", "radana kucer",
)
SUPPLIERS = (
    "hřiště hrou", "hriste hrou", "herold - dětský svět", "herold - detsky svet",
    "envy sport servis", "radana kučer", "radana kucer",
)


def local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def ssl_context(url: str):
    host = urlparse(url).hostname or ""
    if host.endswith("mesto-kadan.cz") or host.endswith("smlouvy.gov.cz"):
        return ssl._create_unverified_context()
    return ssl.create_default_context()


def fetch_bytes(url: str, attempts: int = 5, timeout: int = 300) -> bytes:
    last: Exception | None = None
    for attempt in range(1, attempts + 1):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
            with urllib.request.urlopen(req, timeout=timeout, context=ssl_context(url)) as r:
                data = r.read()
            if not data:
                raise RuntimeError("prázdná odpověď")
            return data
        except Exception as exc:
            last = exc
            time.sleep(min(12, attempt * 2))
    raise RuntimeError(f"stažení selhalo po {attempts} pokusech: {url}: {last}")


def download(url: str, path: Path) -> None:
    data = fetch_bytes(url)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


class LinkTextParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[tuple[str, str]] = []
        self._href: str | None = None
        self._anchor: list[str] = []
        self.text: list[str] = []
        self.title: list[str] = []
        self._in_title = False

    def handle_starttag(self, tag: str, attrs):
        attrs_d = dict(attrs)
        if tag.lower() == "a":
            self._href = attrs_d.get("href")
            self._anchor = []
        if tag.lower() == "title":
            self._in_title = True

    def handle_endtag(self, tag: str):
        if tag.lower() == "a" and self._href:
            self.links.append((" ".join(self._anchor).strip(), self._href))
            self._href = None
            self._anchor = []
        if tag.lower() == "title":
            self._in_title = False

    def handle_data(self, data: str):
        value = re.sub(r"\s+", " ", html.unescape(data)).strip()
        if not value:
            return
        self.text.append(value)
        if self._href is not None:
            self._anchor.append(value)
        if self._in_title:
            self.title.append(value)


def clean_text(parts: list[str]) -> str:
    text = "\n".join(parts)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def safe_name(value: str, fallback: str) -> str:
    value = re.sub(r"[^0-9A-Za-zÀ-ž._-]+", "-", value).strip("-.")
    return value[:150] or fallback


def run(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, text=True, capture_output=True, check=False)


def extract_pdf(pdf: Path, stem: str, max_pages: int = 25) -> dict[str, object]:
    raw_path = WORK / f"{stem}-raw.txt"
    run(["pdftotext", "-layout", str(pdf), str(raw_path)])
    raw = raw_path.read_text(encoding="utf-8", errors="replace") if raw_path.exists() else ""
    info = run(["pdfinfo", str(pdf)]).stdout
    m = re.search(r"^Pages:\s+(\d+)", info, re.M)
    pages = int(m.group(1)) if m else 0
    useful = len(re.sub(r"\s+", "", raw))
    used_ocr = useful < max(350, min(pages or 1, max_pages) * 80)
    combined = raw
    if used_ocr:
        prefix = WORK / f"{stem}-page"
        run(["pdftoppm", "-jpeg", "-r", "220", "-f", "1", "-l", str(min(pages or max_pages, max_pages)), str(pdf), str(prefix)])
        chunks: list[str] = []
        for idx, image in enumerate(sorted(WORK.glob(f"{stem}-page-*.jpg")), 1):
            outbase = WORK / f"{stem}-ocr-{idx:03d}"
            run(["tesseract", str(image), str(outbase), "-l", "ces+eng", "--psm", "6"])
            txt = outbase.with_suffix(".txt")
            chunks.append(f"\n\n===== STRANA {idx} / OCR =====\n" + (txt.read_text(encoding="utf-8", errors="replace") if txt.exists() else ""))
        combined = raw + "".join(chunks)
    out_txt = OUT / "attachments" / f"{stem}.txt"
    out_txt.parent.mkdir(parents=True, exist_ok=True)
    out_txt.write_text(combined, encoding="utf-8", newline="\n")
    return {"pages": pages, "used_ocr": used_ocr, "text_file": str(out_txt.relative_to(OUT))}


def extract_document(path: Path, stem: str) -> dict[str, object]:
    suffix = path.suffix.lower()
    if suffix == ".pdf" or path.read_bytes()[:5] == b"%PDF-":
        return extract_pdf(path, stem)
    if suffix in {".doc", ".docx", ".rtf", ".odt"}:
        converted = WORK / f"{stem}.txt"
        run(["libreoffice", "--headless", "--convert-to", "txt:Text", "--outdir", str(WORK), str(path)])
        candidates = list(WORK.glob(path.stem + "*.txt"))
        text = candidates[0].read_text(encoding="utf-8", errors="replace") if candidates else ""
        out_txt = OUT / "attachments" / f"{stem}.txt"
        out_txt.parent.mkdir(parents=True, exist_ok=True)
        out_txt.write_text(text, encoding="utf-8")
        return {"pages": None, "used_ocr": False, "text_file": str(out_txt.relative_to(OUT))}
    return {"pages": None, "used_ocr": False, "text_file": None}


# 1. Oficiální weby, úřední deska a zařízení.
web_results: list[dict[str, object]] = []
attachment_candidates: list[dict[str, str]] = []
for slug, url in CITY_PAGES:
    row: dict[str, object] = {"slug": slug, "url": url}
    try:
        data = fetch_bytes(url, attempts=6, timeout=120)
        parser = LinkTextParser()
        parser.feed(data.decode("utf-8", errors="replace"))
        links = [{"label": label, "url": urljoin(url, href)} for label, href in parser.links]
        row.update({"status": "ok", "title": " ".join(parser.title), "text": clean_text(parser.text), "links": links})
        for link in links:
            target = str(link["url"])
            label = str(link["label"])
            if re.search(r"\.(pdf|docx?|rtf|odt)(\?|$)", target, re.I) or "/filemanager/files/" in target:
                if any(k in (label + " " + target).casefold() for k in KEYWORDS) or slug == "uredni-deska-hriste-2026":
                    attachment_candidates.append({"source": slug, "label": label, "url": target})
    except Exception as exc:
        row.update({"status": "error", "error": str(exc)})
    web_results.append(row)

(OUT / "official-pages.json").write_text(json.dumps(web_results, ensure_ascii=False, indent=2), encoding="utf-8")

# Uložit čitelné výtahy z jednotlivých webů.
for row in web_results:
    if row.get("status") == "ok":
        (OUT / f"official-{row['slug']}.txt").write_text(str(row.get("text", "")), encoding="utf-8")

# 2. Přílohy z úřední desky a dalších oficiálních stránek.
official_attachments: list[dict[str, object]] = []
seen_urls: set[str] = set()
for idx, item in enumerate(attachment_candidates, 1):
    url = item["url"]
    if url in seen_urls:
        continue
    seen_urls.add(url)
    parsed = urlparse(url)
    suffix = Path(parsed.path).suffix.lower() or ".pdf"
    stem = safe_name(f"official-{idx:02d}-{item['source']}-{item['label']}", f"official-{idx:02d}")
    local_file = WORK / f"{stem}{suffix}"
    result: dict[str, object] = {**item}
    try:
        download(url, local_file)
        result["sha256"] = hashlib.sha256(local_file.read_bytes()).hexdigest()
        result.update(extract_document(local_file, stem))
    except Exception as exc:
        result["error"] = str(exc)
    official_attachments.append(result)
(OUT / "official-attachments.json").write_text(json.dumps(official_attachments, ensure_ascii=False, indent=2), encoding="utf-8")

# 3. Neprohledatelné a obrazové přílohy Registru smluv.
def values_from(elem: ET.Element) -> dict[str, list[str]]:
    result: dict[str, list[str]] = {}
    for node in elem.iter():
        val = (node.text or "").strip()
        if val:
            result.setdefault(local(node.tag), []).append(val)
        for val in node.attrib.values():
            if val:
                result.setdefault("@attr", []).append(val)
    return result


def first(values: dict[str, list[str]], *names: str) -> str:
    lowers = {n.casefold() for n in names}
    for key, vals in values.items():
        if key.casefold() in lowers and vals:
            return vals[0]
    return ""

contracts: list[dict[str, object]] = []
dump_errors: list[dict[str, str]] = []
for dump_url in DUMPS:
    dump_path = WORK / Path(urlparse(dump_url).path).name
    try:
        download(dump_url, dump_path)
    except Exception as exc:
        dump_errors.append({"url": dump_url, "error": str(exc)})
        continue
    try:
        for _event, elem in ET.iterparse(dump_path, events=("end",)):
            if local(elem.tag).casefold() != "zaznam":
                continue
            xml_text = ET.tostring(elem, encoding="unicode")
            folded = xml_text.casefold()
            city = CITY_ICO in folded or "město kadaň" in folded or "mesto kadan" in folded
            relevant = any(k in folded for k in KEYWORDS) or any(s in folded for s in SUPPLIERS)
            if not (city and relevant):
                elem.clear()
                continue
            values = values_from(elem)
            all_urls = sorted({v for vals in values.values() for v in vals if v.startswith("http")})
            attachments = [u for u in all_urls if re.search(r"\.(pdf|docx?|rtf|odt)(\?|$)", u, re.I) or "/soubor/" in u or "/priloha/" in u]
            row = {
                "dump": dump_path.name,
                "title": first(values, "predmet", "predmetSmlouvy", "predmet_smlouvy", "nazev"),
                "contract_number": first(values, "cisloSmlouvy", "cislo_smlouvy", "cisloJednaci"),
                "published": first(values, "casZverejneni", "datumZverejneni", "zverejneni"),
                "signed": first(values, "datumUzavreni", "datum_uzavreni"),
                "contract_id": first(values, "idSmlouvy", "idsmlouvy"),
                "version_id": first(values, "idVerze", "idverze"),
                "price_no_vat": first(values, "hodnotaBezDph", "hodnota_bez_dph"),
                "price_vat": first(values, "hodnotaVcetneDph", "hodnota_s_dph", "hodnota_vcetne_dph"),
                "attachments": attachments,
                "all_urls": all_urls,
                "values": values,
            }
            contracts.append(row)
            elem.clear()
    except Exception as exc:
        dump_errors.append({"url": dump_url, "error": f"parse: {exc}"})
    dump_path.unlink(missing_ok=True)

# Deduplikace podle verze a URL příloh.
unique: dict[str, dict[str, object]] = {}
for row in contracts:
    key = str(row.get("version_id") or "") + "|" + str(row.get("title") or "") + "|" + str(row.get("published") or "")
    unique[key] = row
contracts = sorted(unique.values(), key=lambda r: (str(r.get("published", "")), str(r.get("title", ""))))

processed_attachments: list[dict[str, object]] = []
attachment_limit = 140
count = 0
for cidx, row in enumerate(contracts, 1):
    for aidx, url in enumerate(row.get("attachments", []), 1):
        if count >= attachment_limit:
            break
        count += 1
        parsed = urlparse(str(url))
        suffix = Path(parsed.path).suffix.lower() or ".pdf"
        stem = safe_name(f"contract-{cidx:03d}-{row.get('contract_number') or row.get('title')}-{aidx}", f"contract-{cidx:03d}-{aidx}")
        local_file = WORK / f"{stem}{suffix}"
        info: dict[str, object] = {
            "contract_index": cidx,
            "title": row.get("title"),
            "contract_number": row.get("contract_number"),
            "contract_id": row.get("contract_id"),
            "version_id": row.get("version_id"),
            "url": url,
        }
        try:
            download(str(url), local_file)
            if local_file.stat().st_size > 35 * 1024 * 1024:
                info["error"] = "příloha je větší než 35 MB; OCR přeskočeno"
            else:
                info["sha256"] = hashlib.sha256(local_file.read_bytes()).hexdigest()
                info.update(extract_document(local_file, stem, ) if local_file.exists() else {})
        except Exception as exc:
            info["error"] = str(exc)
        processed_attachments.append(info)

(OUT / "contracts.json").write_text(json.dumps(contracts, ensure_ascii=False, indent=2), encoding="utf-8")
(OUT / "contract-attachments.json").write_text(json.dumps(processed_attachments, ensure_ascii=False, indent=2), encoding="utf-8")
(OUT / "dump-errors.json").write_text(json.dumps(dump_errors, ensure_ascii=False, indent=2), encoding="utf-8")

# 4. Souhrn a rychlý index lokalit, výrobků, závad a kontrol.
lines = [
    "# Kadaňská hřiště – hluboká dokumentová rešerše",
    "",
    "Automaticky stažené a zpracované oficiální weby, úřední deska a přílohy Registru smluv. Obrazová PDF byla OCR zpracována; OCR je pracovní pomůcka a rozhodující je originální dokument.",
    "",
    f"- Oficiální webové stránky: **{len(web_results)}**",
    f"- Přílohy z oficiálních webů: **{len(official_attachments)}**",
    f"- Relevantní záznamy Registru smluv: **{len(contracts)}**",
    f"- Stažené/OCR přílohy smluv: **{len(processed_attachments)}**",
    f"- Chyby dumpů: **{len(dump_errors)}**",
    "",
    "## Relevantní smlouvy a objednávky",
    "",
]
for idx, row in enumerate(contracts, 1):
    lines.extend([
        f"### {idx}. {row.get('title') or '(bez názvu)'}",
        f"- číslo: {row.get('contract_number') or 'neuvedeno'}",
        f"- uzavřeno / zveřejněno: {row.get('signed') or 'neuvedeno'} / {row.get('published') or 'neuvedeno'}",
        f"- ID smlouvy / verze: {row.get('contract_id') or '?'} / {row.get('version_id') or '?'}",
        f"- cena bez / s DPH: {row.get('price_no_vat') or 'neuvedeno'} / {row.get('price_vat') or 'neuvedeno'}",
        f"- příloh: {len(row.get('attachments', []))}",
        "",
    ])

(OUT / "PREHLED.md").write_text("\n".join(lines), encoding="utf-8", newline="\n")

# Sjednocený vyhledávací korpus pro rychlé ruční grepování.
corpus_parts: list[str] = []
for txt in sorted(OUT.rglob("*.txt")):
    try:
        corpus_parts.append(f"\n\n===== {txt.relative_to(OUT)} =====\n" + txt.read_text(encoding="utf-8", errors="replace"))
    except Exception:
        pass
(OUT / "FULLTEXT-OCR.txt").write_text("".join(corpus_parts), encoding="utf-8", newline="\n")

shutil.rmtree(WORK, ignore_errors=True)
print(json.dumps({"official_pages": len(web_results), "official_attachments": len(official_attachments), "contracts": len(contracts), "contract_attachments": len(processed_attachments), "dump_errors": len(dump_errors)}, ensure_ascii=False))
