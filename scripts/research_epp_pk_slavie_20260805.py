#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin
import json
import re
import subprocess
import tempfile
import time
import zipfile

import requests
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "research" / "epp-pk-slavie-20260805"
REPORT = OUT_DIR / "report.md"
RAW = OUT_DIR / "raw-findings.json"
TARGET = "https://pomahejpohybem.cz/"
KEYWORDS = (
    "pk slávie", "pk slavie", "slávie kadaň", "slavie kadan", "kadaň", "kadan",
    "plaveck", "plavání", "plavani", "swim",
)
APK_URLS = [
    "https://d.apkpure.net/b/APK/cz.cez.android.app.sporttracker.sporttracker?nc=&sv=23&versionCode=290193",
    "https://d.apkpure.net/b/APK/cz.cez.android.app.sporttracker.sporttracker?sv=23&versionCode=290193",
]


def has_keyword(value: str) -> bool:
    folded = value.casefold()
    return any(term in folded for term in KEYWORDS)


def text_windows(text: str, radius: int = 5) -> list[str]:
    lines = [re.sub(r"\s+", " ", line).strip() for line in text.splitlines()]
    lines = [line for line in lines if line]
    hits: list[str] = []
    used: set[tuple[int, int]] = set()
    for index, line in enumerate(lines):
        if has_keyword(line):
            start = max(0, index - radius)
            end = min(len(lines), index + radius + 1)
            key = (start, end)
            if key not in used:
                used.add(key)
                hits.append("\n".join(lines[start:end]))
    return hits


def flatten_json(value, path: str = "$", output: list[dict] | None = None) -> list[dict]:
    if output is None:
        output = []
    if isinstance(value, dict):
        for key, child in value.items():
            flatten_json(child, f"{path}.{key}", output)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            flatten_json(child, f"{path}[{index}]", output)
    elif isinstance(value, (str, int, float, bool)) or value is None:
        rendered = str(value)
        if has_keyword(rendered):
            output.append({"path": path, "value": rendered})
    return output


def probe_web() -> dict:
    result: dict = {
        "url": TARGET,
        "body_text": "",
        "keyword_windows": [],
        "network": [],
        "resources": [],
        "scripts": [],
        "script_matches": [],
        "detail_texts": [],
        "errors": [],
    }
    responses: list[dict] = []
    resource_urls: list[str] = []

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        context = browser.new_context(
            locale="cs-CZ",
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0 Safari/537.36"
            ),
            viewport={"width": 1440, "height": 1200},
        )
        page = context.new_page()

        def on_response(response) -> None:
            try:
                req_type = response.request.resource_type
                ctype = response.headers.get("content-type", "")
                entry = {
                    "url": response.url,
                    "status": response.status,
                    "resource_type": req_type,
                    "content_type": ctype,
                }
                if req_type in {"xhr", "fetch"} or "json" in ctype.casefold():
                    try:
                        body = response.text()
                        if len(body) <= 2_000_000:
                            entry["body"] = body
                            try:
                                parsed = json.loads(body)
                                matches = flatten_json(parsed)
                                if matches:
                                    entry["keyword_matches"] = matches
                            except Exception:
                                if has_keyword(body):
                                    entry["keyword_windows"] = text_windows(body, radius=2)
                    except Exception as exc:
                        entry["body_error"] = str(exc)
                responses.append(entry)
            except Exception as exc:
                result["errors"].append(f"response handler: {exc}")

        page.on("response", on_response)
        try:
            page.goto(TARGET, wait_until="domcontentloaded", timeout=90_000)
            page.wait_for_timeout(8_000)
        except Exception as exc:
            result["errors"].append(f"goto: {exc}")

        for consent in ("Souhlasím", "Přijmout", "Povolit vše", "Rozumím"):
            try:
                locator = page.get_by_text(consent, exact=True)
                if locator.count() and locator.first.is_visible():
                    locator.first.click(timeout=3_000)
                    page.wait_for_timeout(1_000)
            except Exception:
                pass

        last_text = ""
        for _ in range(20):
            try:
                body_now = page.locator("body").inner_text(timeout=10_000)
            except Exception:
                body_now = ""
            if body_now == last_text and last_text:
                break
            last_text = body_now
            clicked = False
            for pattern in (r"^DALŠÍ$", r"^DALŠÍ PROJEKTY$", r"^ZOBRAZIT DALŠÍ$"):
                try:
                    locator = page.get_by_text(re.compile(pattern, re.I))
                    for index in range(locator.count()):
                        item = locator.nth(index)
                        if item.is_visible():
                            item.scroll_into_view_if_needed()
                            item.click(timeout=5_000)
                            page.wait_for_timeout(1_500)
                            clicked = True
                            break
                    if clicked:
                        break
                except Exception:
                    continue
            if not clicked:
                break

        try:
            result["body_text"] = page.locator("body").inner_text(timeout=10_000)
            result["keyword_windows"] = text_windows(result["body_text"])
        except Exception as exc:
            result["errors"].append(f"body text: {exc}")

        for term in ("PK Slávie", "PK Slavie", "Slávie", "Slavie", "Kadaň", "Kadan"):
            try:
                locator = page.get_by_text(re.compile(re.escape(term), re.I))
                if locator.count():
                    item = locator.first
                    item.scroll_into_view_if_needed()
                    before = page.locator("body").inner_text()
                    item.click(timeout=4_000)
                    page.wait_for_timeout(2_000)
                    after = page.locator("body").inner_text()
                    if after != before:
                        result["detail_texts"].append({
                            "clicked_term": term,
                            "keyword_windows": text_windows(after, radius=8),
                            "body_text": after if len(after) < 120_000 else after[:120_000],
                        })
                    page.go_back(wait_until="domcontentloaded", timeout=30_000) if page.url != TARGET else None
                    page.wait_for_timeout(1_000)
            except Exception:
                pass

        try:
            resource_urls = page.evaluate(
                "performance.getEntriesByType('resource').map(e => e.name)"
            )
        except Exception as exc:
            result["errors"].append(f"performance resources: {exc}")
        try:
            script_urls = page.locator("script[src]").evaluate_all(
                "els => els.map(e => e.src)"
            )
        except Exception:
            script_urls = []
        result["scripts"] = sorted(set(script_urls))
        result["resources"] = sorted(set(resource_urls))
        browser.close()

    result["network"] = responses

    session = requests.Session()
    session.headers.update({"User-Agent": "NaseKadan-research/1.0"})
    endpoint_pattern = re.compile(
        r"(?:https?://[^\"'\\\s<>]+|/(?:api|rest|graphql|project|projects)[A-Za-z0-9_?&=./:%-]*)",
        re.I,
    )
    for script_url in result["scripts"]:
        try:
            response = session.get(script_url, timeout=35)
            text = response.text
            snippets: list[str] = []
            for match in endpoint_pattern.finditer(text):
                value = match.group(0)
                start = max(0, match.start() - 180)
                end = min(len(text), match.end() + 240)
                snippet = re.sub(r"\s+", " ", text[start:end])
                if value not in snippets:
                    snippets.append(snippet)
            for keyword in ("projects", "project", "pomahejpohybem", "nadacecez"):
                for match in re.finditer(keyword, text, re.I):
                    start = max(0, match.start() - 180)
                    end = min(len(text), match.end() + 260)
                    snippet = re.sub(r"\s+", " ", text[start:end])
                    if snippet not in snippets:
                        snippets.append(snippet)
                    if len(snippets) >= 120:
                        break
                if len(snippets) >= 120:
                    break
            if snippets:
                result["script_matches"].append({
                    "url": script_url,
                    "status": response.status_code,
                    "snippets": snippets[:120],
                })
        except Exception as exc:
            result["errors"].append(f"script {script_url}: {exc}")
    return result


def probe_apk() -> dict:
    result: dict = {"downloaded": False, "url": None, "size": 0, "matches": [], "errors": []}
    with tempfile.TemporaryDirectory(prefix="epp-apk-") as tmp:
        tmp_path = Path(tmp)
        apk = tmp_path / "epp.apk"
        for url in APK_URLS:
            try:
                proc = subprocess.run(
                    [
                        "curl", "-L", "--fail", "--retry", "3", "--connect-timeout", "30",
                        "--max-time", "240", "-A", "Mozilla/5.0", "-o", str(apk), url,
                    ],
                    text=True,
                    capture_output=True,
                    timeout=300,
                )
                if proc.returncode == 0 and apk.exists() and apk.stat().st_size > 5_000_000:
                    result["downloaded"] = True
                    result["url"] = url
                    result["size"] = apk.stat().st_size
                    break
                result["errors"].append(f"download {url}: {proc.stderr[-600:]}")
            except Exception as exc:
                result["errors"].append(f"download {url}: {exc}")
        if not result["downloaded"]:
            return result

        unpack = tmp_path / "unpacked"
        unpack.mkdir()
        try:
            with zipfile.ZipFile(apk) as archive:
                archive.extractall(unpack)
        except Exception as exc:
            result["errors"].append(f"unzip: {exc}")
            return result

        candidates = list(unpack.glob("classes*.dex"))
        candidates.extend([
            path for path in unpack.rglob("*")
            if path.is_file() and path.stat().st_size < 20_000_000
            and path.suffix.lower() in {".xml", ".json", ".txt", ".js", ".properties", ".arsc"}
        ])
        url_pattern = re.compile(r"https?://[^\s\"'<>\\]+", re.I)
        seen: set[str] = set()
        for path in candidates:
            try:
                proc = subprocess.run(
                    ["strings", "-a", "-n", "5", str(path)],
                    text=True,
                    capture_output=True,
                    timeout=45,
                    errors="replace",
                )
                text = proc.stdout
            except Exception as exc:
                result["errors"].append(f"strings {path.name}: {exc}")
                continue
            lines = text.splitlines()
            for index, line in enumerate(lines):
                folded = line.casefold()
                relevant = (
                    has_keyword(line)
                    or "pomahejpohybem" in folded
                    or "nadacecez" in folded
                    or "project" in folded
                    or "/api/" in folded
                    or "graphql" in folded
                    or bool(url_pattern.search(line))
                )
                if not relevant:
                    continue
                start = max(0, index - 2)
                end = min(len(lines), index + 3)
                snippet = " | ".join(x.strip() for x in lines[start:end] if x.strip())
                key = f"{path.relative_to(unpack)}::{snippet}"
                if key in seen:
                    continue
                seen.add(key)
                result["matches"].append({
                    "file": str(path.relative_to(unpack)),
                    "snippet": snippet[:1800],
                })
                if len(result["matches"]) >= 500:
                    return result
    return result


def extract_candidate_urls(data: dict) -> list[str]:
    found: set[str] = set()
    pattern = re.compile(r"https?://[^\s\"'<>|\\]+", re.I)
    rendered = json.dumps(data, ensure_ascii=False)
    for match in pattern.findall(rendered):
        clean = match.rstrip(".,);]}")
        if any(token in clean.casefold() for token in ("pomahejpohybem", "nadacecez", "api", "project")):
            found.add(clean)
    return sorted(found)


def probe_candidates(urls: list[str]) -> list[dict]:
    session = requests.Session()
    session.headers.update({"User-Agent": "NaseKadan-research/1.0", "Accept": "application/json,text/plain,*/*"})
    output: list[dict] = []
    for url in urls[:120]:
        try:
            response = session.get(url, timeout=30)
            ctype = response.headers.get("content-type", "")
            text = response.text[:2_000_000]
            entry = {"url": url, "status": response.status_code, "content_type": ctype}
            if "json" in ctype.casefold() or text.lstrip().startswith(("{", "[")):
                try:
                    parsed = json.loads(text)
                    entry["json_keyword_matches"] = flatten_json(parsed)
                    entry["json_preview"] = parsed if len(text) < 250_000 else text[:250_000]
                except Exception:
                    entry["text_windows"] = text_windows(text, radius=3) if has_keyword(text) else []
            elif has_keyword(text):
                entry["text_windows"] = text_windows(text, radius=3)
            output.append(entry)
        except Exception as exc:
            output.append({"url": url, "error": str(exc)})
    return output


def make_report(data: dict) -> str:
    now = datetime.now(timezone.utc).isoformat()
    web = data["web"]
    apk = data["apk"]
    candidates = data["candidate_responses"]
    all_matches: list[str] = []
    all_matches.extend(web.get("keyword_windows", []))
    for entry in web.get("network", []):
        for match in entry.get("keyword_matches", []):
            all_matches.append(f"{entry['url']} — {match['path']}: {match['value']}")
        all_matches.extend(entry.get("keyword_windows", []))
    for entry in candidates:
        for match in entry.get("json_keyword_matches", []):
            all_matches.append(f"{entry['url']} — {match['path']}: {match['value']}")
        all_matches.extend(entry.get("text_windows", []))
    exact_found = bool(all_matches)

    lines = [
        "# Technická rešerše EPP – PK Slávie Kadaň",
        "",
        f"Vygenerováno: `{now}`",
        "",
        "## Výsledek",
        "",
    ]
    if exact_found:
        lines.append("Dynamický web, síťové odpovědi nebo aplikační data obsahují stopy vztahující se ke Kadani či plaveckému projektu. Je nutné je redakčně vyhodnotit níže.")
    else:
        lines.append("Ani po vykreslení dynamického webu, načítání dalších projektů, zachycení síťových odpovědí a prohledání veřejného instalačního balíčku nebyl nalezen přesný veřejný údaj o částce, účelu, cílovém počtu bodů nebo termínu projektu PK Slávie Kadaň.")

    lines += [
        "",
        "## Nálezy z vykresleného webu a API",
        "",
    ]
    if all_matches:
        for match in all_matches[:120]:
            lines.append(f"- {match}")
    else:
        lines.append("- Bez přímé shody na PK Slávii, Kadaň nebo plavecký projekt v zachycených datech.")

    lines += [
        "",
        "## Síťové zdroje",
        "",
    ]
    for entry in web.get("network", [])[:200]:
        lines.append(f"- `{entry.get('status')}` `{entry.get('resource_type')}` {entry.get('url')}")

    lines += [
        "",
        "## Kandidátní endpointy nalezené ve webu a aplikaci",
        "",
    ]
    urls = data.get("candidate_urls", [])
    if urls:
        lines.extend(f"- {url}" for url in urls)
    else:
        lines.append("- Nebyl nalezen použitelný veřejný endpoint.")

    lines += [
        "",
        "## Instalační balíček aplikace",
        "",
        f"- Stažen: `{apk.get('downloaded')}`",
        f"- Velikost: `{apk.get('size', 0)}` bajtů",
        f"- Zdroj: `{apk.get('url')}`",
        f"- Počet relevantních řetězců: `{len(apk.get('matches', []))}`",
    ]
    for match in apk.get("matches", [])[:120]:
        lines.append(f"- `{match['file']}`: {match['snippet']}")

    errors = web.get("errors", []) + apk.get("errors", [])
    errors.extend(entry["error"] for entry in candidates if "error" in entry)
    lines += ["", "## Technické chyby a omezení", ""]
    if errors:
        lines.extend(f"- {error}" for error in errors[:80])
    else:
        lines.append("- Bez významné technické chyby.")

    lines += [
        "",
        "## Redakční závěr",
        "",
        "Přesné parametry projektu lze považovat za potvrzené pouze tehdy, jsou-li přímo uvedeny v aktuální projektové kartě EPP, v odpovědi PK Slávie Kadaň nebo Nadace ČEZ, případně v jejich veřejném dokumentu. Jiné částky z městských dotací nebo starších podpor se s tímto projektem nesmějí směšovat.",
        "",
    ]
    return "\n".join(lines)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    web = probe_web()
    apk = probe_apk()
    candidate_urls = extract_candidate_urls({"web": web, "apk": apk})
    candidate_responses = probe_candidates(candidate_urls)
    data = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "web": web,
        "apk": apk,
        "candidate_urls": candidate_urls,
        "candidate_responses": candidate_responses,
    }
    RAW.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    REPORT.write_text(make_report(data), encoding="utf-8")
    print(f"Zapsáno: {REPORT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
