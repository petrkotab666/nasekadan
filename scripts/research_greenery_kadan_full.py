#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import html
import json
import math
import os
import re
import shutil
import subprocess
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import quote, urljoin

import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / ".github" / "research" / "greenery-kadan-2026"
RAW = OUT / "raw"
PDFS = OUT / "pdfs"
TEXTS = OUT / "texts"
IMAGES = OUT / "images"
for p in (OUT, RAW, PDFS, TEXTS, IMAGES):
    p.mkdir(parents=True, exist_ok=True)

SESSION = requests.Session()
SESSION.headers.update({
    "User-Agent": "Mozilla/5.0 (compatible; NaseKadanResearch/1.0; +https://nasekadan.cz)",
    "Accept-Language": "cs-CZ,cs;q=0.9,en;q=0.6",
})

KEYWORDS = [
    "seč", "sečení", "sekání", "posečení", "trav", "tráv", "výška", "cm",
    "pokos", "mulč", "mulčování", "sídliště", "park", "zeleň", "zeleně",
    "sucho", "sucha", "hork", "praš", "odvoz", "bioodpad", "výhrab", "četnost",
    "termín", "harmonogram", "reklamac", "sankc", "kontrol", "osiny", "cyklostez",
]

PARTIES = {
    "zalabak": {
        "name": "J. Zalabák - údržba zeleně, s.r.o.",
        "urls": [
            "https://smlouvy.gov.cz/vyhledavani?party_box=u23sdpg&searchResultList-limit=500",
            "https://smlouvy.gov.cz/vyhledavani?party_idnum=04946081&searchResultList-limit=500",
        ],
    },
    "cepelak": {
        "name": "Marek Čepelák",
        "urls": [
            "https://smlouvy.gov.cz/vyhledavani?party_box=fftitrb&searchResultList-limit=500",
            "https://smlouvy.gov.cz/vyhledavani?party_idnum=63165902&searchResultList-limit=500",
        ],
    },
    "kuku": {
        "name": "Jaroslav Kučera KU-KU s.r.o.",
        "urls": [
            "https://smlouvy.gov.cz/vyhledavani?party_box=v37djpw&searchResultList-limit=500",
        ],
    },
    "tskadan": {
        "name": "Technické služby Kadaň, s.r.o.",
        "urls": [
            "https://smlouvy.gov.cz/vyhledavani?party_idnum=25441094&searchResultList-limit=500",
        ],
    },
}

KNOWN_CONTRACTS = {
    "36438289",  # Marek Čepelák 33/Jan/2026
    "36641905",  # KU-KU 83/Jan/2026
    "36641861",  # KU-KU 82/Jan/2026
    "36408293",  # KU-KU 6/Jan/2026
    "32202072",  # Zalabák sběr odpadu 2025
    "34054885",  # vinice 2025
}

LOCALITY_QUERIES = [
    "Sídliště A, Kadaň", "Sídliště B, Kadaň", "Sídliště C, Kadaň", "Sídliště D, Kadaň",
    "Strážiště I, Kadaň", "Strážiště II, Kadaň", "Strážiště III, Kadaň",
    "Obránců míru, Kadaň", "Smetanovy sady, Kadaň", "Rooseveltovy sady, Kadaň",
    "Na Podlesí, Kadaň", "Chomutovská, Kadaň", "Husova, Kadaň", "Golovinova, Kadaň",
    "Věžní, Kadaň", "Jitřní, Kadaň", "Václava Havla, Kadaň", "Polní, Kadaň",
    "Mírové náměstí, Kadaň", "Svatý kopeček, Kadaň", "Suchý důl, Kadaň",
    "Želina, Kadaň", "Prunéřov, Kadaň", "Tušimice, Kadaň", "Lomazice, Kadaň",
]


def safe_name(value: str, limit: int = 110) -> str:
    value = html.unescape(value)
    value = re.sub(r"[^0-9A-Za-zÀ-ž._-]+", "-", value).strip("-.")
    return value[:limit] or "file"


def get(url: str, *, timeout: int = 45, binary: bool = False) -> bytes | str:
    r = SESSION.get(url, timeout=timeout, allow_redirects=True)
    r.raise_for_status()
    return r.content if binary else r.text


def save_url(url: str, path: Path) -> bool:
    try:
        data = get(url, binary=True)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        return True
    except Exception as exc:
        (OUT / "errors.log").open("a", encoding="utf-8").write(f"DOWNLOAD {url}: {type(exc).__name__}: {exc}\n")
        return False


def run(cmd: list[str], timeout: int = 240) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, text=True, capture_output=True, timeout=timeout, check=False)


def extract_pdf_text(pdf: Path, stem: str) -> tuple[str, str]:
    txt_path = TEXTS / f"{stem}.txt"
    method = "pdftotext"
    p = run(["pdftotext", "-layout", str(pdf), str(txt_path)], timeout=180)
    text = txt_path.read_text(encoding="utf-8", errors="replace") if txt_path.exists() else ""
    useful = len(re.sub(r"\s+", "", text)) >= 180
    if useful:
        return text, method

    method = "ocr-tesseract"
    work = OUT / "ocr-work" / stem
    shutil.rmtree(work, ignore_errors=True)
    work.mkdir(parents=True, exist_ok=True)
    p = run(["pdftoppm", "-r", "220", "-png", str(pdf), str(work / "page")], timeout=300)
    chunks: list[str] = []
    pages = sorted(work.glob("page-*.png"))[:30]
    for i, image in enumerate(pages, 1):
        outbase = work / f"ocr-{i:03d}"
        proc = run(["tesseract", str(image), str(outbase), "-l", "ces+eng", "--psm", "6"], timeout=180)
        outtxt = outbase.with_suffix(".txt")
        if outtxt.exists():
            chunks.append(outtxt.read_text(encoding="utf-8", errors="replace"))
    text = "\n\n".join(chunks)
    txt_path.write_text(text, encoding="utf-8")
    shutil.rmtree(work, ignore_errors=True)
    return text, method


def snippets(text: str, width: int = 260, max_count: int = 20) -> list[str]:
    compact = re.sub(r"\s+", " ", text).strip()
    low = compact.lower()
    found: list[str] = []
    positions: list[int] = []
    for kw in KEYWORDS:
        start = 0
        kwl = kw.lower()
        while len(found) < max_count:
            pos = low.find(kwl, start)
            if pos < 0:
                break
            if all(abs(pos - prior) > width // 2 for prior in positions):
                left = max(0, pos - width // 2)
                right = min(len(compact), pos + width)
                found.append(compact[left:right])
                positions.append(pos)
            start = pos + max(1, len(kwl))
    return found


def parse_contract_page(url: str, party_key: str = "") -> dict:
    page = get(url)
    soup = BeautifulSoup(page, "html.parser")
    plain = "\n".join(x.strip() for x in soup.get_text("\n").splitlines() if x.strip())
    def grab(label: str) -> str:
        m = re.search(re.escape(label) + r"\s*:?\s*([^\n]+)", plain, re.I)
        return m.group(1).strip() if m else ""
    title = soup.find("h2")
    title_text = title.get_text(" ", strip=True) if title else ""
    contract_id = re.search(r"/smlouva/(\d+)", url)
    attachments = []
    for a in soup.select('a[href*="/smlouva/soubor/"]'):
        href = urljoin(url, a.get("href", ""))
        if href.lower().endswith(".pdf") or ".pdf" in href.lower():
            attachments.append({"name": a.get_text(" ", strip=True), "url": href})
    return {
        "url": url,
        "contract_version_id": contract_id.group(1) if contract_id else "",
        "party_key": party_key,
        "title": title_text,
        "subject": grab("Předmět smlouvy"),
        "date_signed": grab("Datum uzavření"),
        "published": grab("Zveřejnění"),
        "reference": grab("Číslo smlouvy / č.j."),
        "signer": grab("Podepisující osoba"),
        "value_no_vat": grab("Hodnota bez DPH"),
        "value_vat": grab("Hodnota vč. DPH"),
        "department": grab("Útvar / Odbor"),
        "plain": plain,
        "attachments": attachments,
    }


def discover_contracts() -> list[tuple[str, str]]:
    found: dict[str, str] = {}
    for key, cfg in PARTIES.items():
        for search_url in cfg["urls"]:
            try:
                page = get(search_url)
            except Exception as exc:
                (OUT / "errors.log").open("a", encoding="utf-8").write(f"SEARCH {search_url}: {exc}\n")
                continue
            soup = BeautifulSoup(page, "html.parser")
            for a in soup.select('a[href^="/smlouva/"]'):
                href = urljoin(search_url, a.get("href", ""))
                m = re.match(r"https://smlouvy\.gov\.cz/smlouva/(\d+)", href)
                if m:
                    found[m.group(1)] = key
    for cid in KNOWN_CONTRACTS:
        found.setdefault(cid, "known")
    return [(f"https://smlouvy.gov.cz/smlouva/{cid}", key) for cid, key in sorted(found.items(), key=lambda x: int(x[0]), reverse=True)]


def relevant_contract(meta: dict) -> bool:
    hay = " ".join([meta.get("title", ""), meta.get("plain", "")]).lower()
    if "město kadaň" not in hay:
        return False
    # Focus on the current assignment and on historical framework/background documents.
    years = re.findall(r"20\d{2}", meta.get("date_signed", "") + " " + meta.get("published", ""))
    year = int(years[0]) if years else 0
    return year >= 2018


def collect_contracts() -> list[dict]:
    output: list[dict] = []
    for idx, (url, party_key) in enumerate(discover_contracts(), 1):
        try:
            meta = parse_contract_page(url, party_key)
        except Exception as exc:
            (OUT / "errors.log").open("a", encoding="utf-8").write(f"CONTRACT {url}: {exc}\n")
            continue
        if not relevant_contract(meta):
            continue
        meta.pop("plain", None)
        extracted = []
        for j, att in enumerate(meta["attachments"], 1):
            fname = f"{meta['contract_version_id']}-{j:02d}-{safe_name(att['name'])}.pdf"
            pdf = PDFS / fname
            if not save_url(att["url"], pdf):
                continue
            stem = pdf.stem
            text, method = extract_pdf_text(pdf, stem)
            extracted.append({
                "name": att["name"], "url": att["url"], "file": str(pdf.relative_to(ROOT)),
                "text_file": str((TEXTS / f"{stem}.txt").relative_to(ROOT)),
                "method": method, "characters": len(text), "snippets": snippets(text),
            })
        meta["extracted"] = extracted
        output.append(meta)
        print(f"[{idx}] {meta['title']} – {len(extracted)} příloh")
        time.sleep(0.1)
    (OUT / "contracts.json").write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    return output


def collect_gis() -> dict:
    base = "https://gis.mesto-kadan.cz/portal/arcgis/rest/services/verejny_portal/Verejny_portal/MapServer"
    urls = {
        "service": f"{base}?f=pjson",
        "layer": f"{base}/2?f=pjson",
        "legend": f"{base}/legend?f=pjson",
        "geojson": f"{base}/2/query?where=1%3D1&outFields=*&returnGeometry=true&outSR=4326&f=geojson",
        "json": f"{base}/2/query?where=1%3D1&outFields=*&returnGeometry=true&outSR=5514&f=json",
        "export": f"{base}/export?bbox=-820232.48,-1000532.32,-818297.74,-997378.81&bboxSR=5514&imageSR=5514&size=2600,2600&layers=show:2&format=png32&transparent=true&f=image",
    }
    result = {"urls": urls, "errors": []}
    for name in ("service", "layer", "legend", "geojson", "json"):
        try:
            text = get(urls[name])
            (RAW / f"gis-{name}.json").write_text(text, encoding="utf-8")
            result[name] = json.loads(text)
        except Exception as exc:
            result["errors"].append(f"{name}: {type(exc).__name__}: {exc}")
    save_url(urls["export"], IMAGES / "gis-spravci-zelene-transparent.png")

    gj = result.get("geojson") or {}
    feature_summary = []
    area_by_properties = defaultdict(float)
    try:
        from shapely.geometry import shape
        from pyproj import Geod
        geod = Geod(ellps="WGS84")
        for f in gj.get("features", []):
            props = f.get("properties") or {}
            geom = shape(f.get("geometry"))
            area, _ = geod.geometry_area_perimeter(geom)
            area = abs(area)
            key = json.dumps(props, ensure_ascii=False, sort_keys=True)
            area_by_properties[key] += area
            feature_summary.append({"properties": props, "area_m2": round(area, 2), "centroid": [geom.centroid.x, geom.centroid.y]})
        result["feature_count"] = len(feature_summary)
        result["features"] = feature_summary
        result["area_by_properties"] = [
            {"properties": json.loads(k), "area_m2": round(v, 2), "hectares": round(v / 10000, 3)}
            for k, v in sorted(area_by_properties.items(), key=lambda x: x[1], reverse=True)
        ]
        render_geojson(gj, result.get("layer") or {})
        result["localities"] = assign_localities(gj)
    except Exception as exc:
        result["errors"].append(f"analysis: {type(exc).__name__}: {exc}")
    (OUT / "gis-summary.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    return result


def render_geojson(gj: dict, layer: dict) -> None:
    import matplotlib.pyplot as plt
    from shapely.geometry import shape
    features = gj.get("features", [])
    if not features:
        return
    renderer = ((layer.get("drawingInfo") or {}).get("renderer") or {})
    field = renderer.get("field1") or renderer.get("field")
    labels = {}
    colors = {}
    for info in renderer.get("uniqueValueInfos", []):
        val = str(info.get("value"))
        labels[val] = info.get("label") or val
        rgba = (((info.get("symbol") or {}).get("color")) or [100,100,100,150])
        colors[val] = tuple(c / 255 for c in rgba)
    fig, ax = plt.subplots(figsize=(12, 12))
    for f in features:
        geom = shape(f.get("geometry"))
        props = f.get("properties") or {}
        val = str(props.get(field, "")) if field else json.dumps(props, ensure_ascii=False, sort_keys=True)
        color = colors.get(val)
        if color is None:
            digest = hashlib.sha1(val.encode()).digest()
            color = (digest[0]/255, digest[1]/255, digest[2]/255, .58)
        geoms = list(geom.geoms) if geom.geom_type == "MultiPolygon" else [geom]
        for poly in geoms:
            x, y = poly.exterior.xy
            ax.fill(x, y, facecolor=color, edgecolor="black", linewidth=.25)
    ax.set_aspect("equal")
    ax.set_title("Kadaň – správci veřejné zeleně (městský GIS)")
    ax.set_xlabel("zeměpisná délka")
    ax.set_ylabel("zeměpisná šířka")
    handles = []
    if field:
        from matplotlib.patches import Patch
        vals = sorted({str((f.get("properties") or {}).get(field, "")) for f in features})
        for val in vals:
            handles.append(Patch(facecolor=colors.get(val, (.5,.5,.5,.6)), label=labels.get(val, val)))
        if handles:
            ax.legend(handles=handles, loc="best", fontsize=8)
    fig.tight_layout()
    fig.savefig(IMAGES / "gis-spravci-zelene-render.png", dpi=180)
    plt.close(fig)


def assign_localities(gj: dict) -> list[dict]:
    from shapely.geometry import Point, shape
    features = [(shape(f.get("geometry")), f.get("properties") or {}) for f in gj.get("features", [])]
    results = []
    for query in LOCALITY_QUERIES:
        try:
            r = SESSION.get("https://nominatim.openstreetmap.org/search", params={"q": query + ", Česko", "format": "jsonv2", "limit": 1}, timeout=30)
            r.raise_for_status()
            data = r.json()
            if not data:
                results.append({"query": query, "found": False})
                continue
            lon, lat = float(data[0]["lon"]), float(data[0]["lat"])
            point = Point(lon, lat)
            matches = [props for geom, props in features if geom.contains(point) or geom.touches(point)]
            results.append({"query": query, "found": True, "lat": lat, "lon": lon, "display_name": data[0].get("display_name"), "matches": matches})
        except Exception as exc:
            results.append({"query": query, "error": f"{type(exc).__name__}: {exc}"})
        time.sleep(1.05)
    return results


def collect_static_sources() -> None:
    targets = {
        "ts-greenery-page.html": "https://www.tskadan.cz/sekce/25/udrzba-zelene-a-cyklostezek",
        "ts-greenery-map.jpg": "https://www.tskadan.cz/dokumenty/bigmapazelen.jpg",
        "ts-pricelist-2026.pdf": "https://www.tskadan.cz/dokumenty/cenik-sluzeb-vcetne-kalkulaci-2026.pdf",
        "egordion-profile.html": "https://www.egordion.cz/nabidkaGORDION/profilMestoKadan",
    }
    for name, url in targets.items():
        path = RAW / name if not name.endswith(".jpg") else IMAGES / name
        if save_url(url, path) and path.suffix.lower() == ".pdf":
            text, method = extract_pdf_text(path, path.stem)
            (OUT / "static-source-methods.json").write_text(json.dumps({name: method}, ensure_ascii=False, indent=2), encoding="utf-8")
    map_path = IMAGES / "ts-greenery-map.jpg"
    if map_path.exists():
        proc = run(["tesseract", str(map_path), str(TEXTS / "ts-greenery-map"), "-l", "ces+eng", "--psm", "11"], timeout=180)


def report(contracts: list[dict], gis: dict) -> None:
    lines = [
        "# Údržba veřejné zeleně v Kadani – úplný strojový průchod",
        "",
        "Výstup vznikl stažením aktuální mapy a GIS vrstvy města, průchodem Registru smluv a OCR skenovaných příloh. Automatické OCR je pracovní podklad; u zásadních čísel a formulací je nutné vždy porovnat také obraz původního dokumentu.",
        "",
        "## GIS a mapa správců",
        "",
        f"- Počet polygonů ve vrstvě: **{gis.get('feature_count', 'nezjištěno')}**.",
    ]
    for row in gis.get("area_by_properties", []):
        lines.append(f"- `{json.dumps(row['properties'], ensure_ascii=False)}`: **{row['hectares']} ha**")
    lines += ["", "### Přiřazení známých lokalit", ""]
    for loc in gis.get("localities", []):
        lines.append(f"- **{loc.get('query')}**: `{json.dumps(loc.get('matches', []), ensure_ascii=False)}`" if loc.get("found") else f"- **{loc.get('query')}**: nenalezeno / {loc.get('error','')}")

    lines += ["", "## Smlouvy a objednávky", ""]
    by_party = defaultdict(list)
    for c in contracts:
        by_party[c.get("party_key", "unknown")].append(c)
    for key, rows in by_party.items():
        lines.append(f"### {PARTIES.get(key, {}).get('name', key)}")
        lines.append("")
        for c in sorted(rows, key=lambda x: x.get("date_signed", ""), reverse=True):
            lines.append(f"#### {c.get('title') or c.get('subject')}")
            lines.append(f"- Datum: {c.get('date_signed')} · Č. j.: {c.get('reference')} · bez DPH: {c.get('value_no_vat')} · s DPH: {c.get('value_vat')}")
            lines.append(f"- Registr: {c.get('url')}")
            for a in c.get("extracted", []):
                lines.append(f"- Příloha: `{a.get('name')}` · extrakce: **{a.get('method')}** · {a.get('characters')} znaků")
                for sn in a.get("snippets", [])[:12]:
                    lines.append(f"  - …{sn}…")
            lines.append("")

    lines += ["## Soubory", "", "- `contracts.json` – strukturovaný seznam smluv a OCR výstupů", "- `gis-summary.json` – vlastnosti a výměry polygonů", "- `images/` – oficiální mapa a vykreslená GIS vrstva", "- `texts/` – úplné textové/OCR přepisy příloh", ""]
    (OUT / "REPORT.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    (OUT / "errors.log").write_text("", encoding="utf-8")
    collect_static_sources()
    gis = collect_gis()
    contracts = collect_contracts()
    report(contracts, gis)
    state = {
        "status": "completed",
        "contracts": len(contracts),
        "attachments": sum(len(c.get("extracted", [])) for c in contracts),
        "gis_features": gis.get("feature_count", 0),
        "errors": (OUT / "errors.log").read_text(encoding="utf-8", errors="replace").splitlines(),
    }
    (OUT / "status.json").write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(state, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
