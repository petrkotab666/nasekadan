#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
from email.utils import format_datetime
from html import escape
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
SLUG = "komunalni-volby-kadan-kandidaty-lhuta-2026"
ARTICLE = ROOT / "clanky" / f"{SLUG}.html"
ARTICLE_REL = f"/clanky/{SLUG}.html"
ARTICLE_URL = f"https://nasekadan.cz{ARTICLE_REL}"
PUBLISHED = "2026-08-04T18:46:00+02:00"
MODIFIED = "2026-08-05T15:23:00+02:00"
DESC = (
    "Podávání kandidátek do komunálních voleb skončilo. ODS a Dáme Kadani novou šanci "
    "zveřejnily sestavy, ANO oznámilo podání a další kandidátku tvoří nezávislí s podporou Pirátů."
)
LEAD = (
    "V úterý 4. srpna v 16 hodin skončila lhůta pro podání kandidátních listin do podzimních "
    "komunálních voleb. Úplný úřední seznam pro Kadaň ještě zveřejněný není. Z veřejných oznámení "
    "se rýsuje střet ODS vedené starostou Janem Losenickým, uskupení Dáme Kadani novou šanci a "
    "silného opozičního ANO. Další kandidátku připravuje sdružení nezávislých kandidátů s podporou "
    "Pirátské strany; nekandiduje samotná Pirátská strana."
)


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def replace_meta(text: str, attr: str, key: str, value: str) -> str:
    patterns = (
        rf'<meta\s+{attr}="{re.escape(key)}"\s+content="[^"]*"\s*/?>',
        rf'<meta\s+content="[^"]*"\s+{attr}="{re.escape(key)}"\s*/?>',
    )
    replacement = f'<meta {attr}="{key}" content="{escape(value, quote=True)}">'
    for pattern in patterns:
        if re.search(pattern, text, flags=re.I):
            return re.sub(pattern, replacement, text, count=1, flags=re.I)
    raise RuntimeError(f"Chybí meta {attr}={key}.")


def update_article() -> None:
    text = ARTICLE.read_text(encoding="utf-8")
    text = replace_meta(text, "name", "description", DESC)
    text = replace_meta(text, "property", "og:description", DESC)
    text = replace_meta(text, "name", "twitter:description", DESC)
    text = replace_meta(text, "property", "article:modified_time", MODIFIED)

    def patch_jsonld(match: re.Match[str]) -> str:
        start, raw, end = match.group(1), match.group(2), match.group(3)
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            return match.group(0)
        if isinstance(data, dict) and data.get("@type") == "NewsArticle":
            data["description"] = DESC
            data["datePublished"] = PUBLISHED
            data["dateModified"] = MODIFIED
            about = data.setdefault("about", [])
            if isinstance(about, list):
                names = {item.get("name") for item in about if isinstance(item, dict)}
                if "Sdružení nezávislých kandidátů s podporou Pirátů" not in names:
                    about.append({"@type": "Organization", "name": "Sdružení nezávislých kandidátů s podporou Pirátů"})
        return start + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + end

    text = re.sub(
        r'(<script[^>]*type="application/ld\+json"[^>]*>)(.*?)(</script>)',
        patch_jsonld,
        text,
        flags=re.S,
    )

    text = re.sub(
        r'<p class="tag">.*?</p>',
        '<p class="tag">KOMUNÁLNÍ VOLBY 2026 · KADAŇ · AKTUALIZOVÁNO 5. SRPNA 2026 · 15:23</p>',
        text,
        count=1,
        flags=re.S,
    )
    text = re.sub(
        r'<p class="leadtext">.*?</p>',
        f'<p class="leadtext"><strong>{escape(LEAD)}</strong></p>',
        text,
        count=1,
        flags=re.S,
    )

    if ".correction-box{" not in text:
        text = text.replace(
            ".update-box strong{font:800 23px Georgia,serif;display:block;color:#72500d;margin-bottom:6px}",
            ".update-box strong{font:800 23px Georgia,serif;display:block;color:#72500d;margin-bottom:6px}.correction-box{background:#fff0f0;border-color:#d7a0a5}.correction-box strong{color:#8b1f28}",
            1,
        )

    correction = (
        '<div class="update-box correction-box" data-editorial-correction="20260805-1523">'
        '<strong>Oprava článku z 5. srpna 2026</strong>'
        '<p>Původní verze článku chybně uváděla, že v Kadani kandiduje Česká pirátská strana, '
        'a jako letošní kandidátku uvedla Miloslavu Karfilátovou. Podle písemného upozornění '
        'kandidátky Elišky Hladové bude kandidovat sdružení nezávislých kandidátů s podporou '
        'Pirátské strany. Jméno Miloslavy Karfilátové jsme nesprávně převzali ze čtyři roky '
        'staré stránky ke komunálním volbám 2022. Za chybu se omlouváme.</p></div>'
    )
    text = re.sub(
        r'\s*<div class="update-box correction-box" data-editorial-correction="20260805-1523">.*?</div>',
        '',
        text,
        flags=re.S,
    )
    hero = re.search(r'<img class="hero-image"[^>]*>', text, flags=re.S)
    if not hero:
        raise RuntimeError("Chybí hlavní obrázek článku.")
    text = text[: hero.end()] + "\n" + correction + text[hero.end():]

    old_row = (
        '<tr><td><strong>Piráti</strong></td><td>Jana Hladová a další veřejně představení kandidáti</td>'
        '<td>Úplná podaná listina zatím není úředně potvrzená</td></tr>'
    )
    new_row = (
        '<tr><td><strong>Nezávislí s podporou Pirátů</strong></td><td>Eliška Hladová; úplné složení '
        'zatím není zveřejněné</td><td>Nekandiduje Pirátská strana jako samostatná volební strana</td></tr>'
    )
    if old_row not in text and new_row not in text:
        raise RuntimeError("Nelze najít původní řádek Pirátů v tabulce.")
    text = text.replace(old_row, new_row, 1)

    section_pattern = re.compile(
        r'<h2>Piráti ukazují jména, úřední potvrzení teprve přijde</h2>.*?'
        r'<p>Piráti v roce 2022 získali 4,90 procenta hlasů a do zastupitelstva se těsně nedostali\.</p>',
        re.S,
    )
    section = (
        '<h2>Nezávislí s podporou Pirátů, nikoli Pirátská strana</h2>'
        '<p>Podle písemného vyjádření kandidátky <strong>Elišky Hladové</strong> nebude v Kadani '
        'kandidovat Česká pirátská strana jako samostatná volební strana. Kandidovat má sdružení '
        'nezávislých kandidátů s její podporou. Úplné složení a pořadí listiny zatím nejsou úředně '
        'potvrzené.</p>'
        '<p>Původní verze článku nesprávně použila stránku „Kandidáti“ na webu Pirátů Kadaň jako '
        'zdroj pro rok 2026. Stránka ve skutečnosti zachycuje kandidátku z komunálních voleb 2022. '
        'Proto z aktuálního přehledu odstraňujeme jména, která pro letošní kandidaturu nemáme '
        'potvrzena, včetně Miloslavy Karfilátové.</p>'
        '<p>Česká pirátská strana v roce 2022 získala 4,90 procenta hlasů a do zastupitelstva se '
        'těsně nedostala. Jde však pouze o historický výsledek, nikoli o označení letošního uskupení.</p>'
    )
    if section_pattern.search(text):
        text = section_pattern.sub(section, text, count=1)
    elif "Nezávislí s podporou Pirátů, nikoli Pirátská strana" not in text:
        raise RuntimeError("Nelze najít původní sekci Pirátů.")

    old_source = (
        '<li><a href="https://kadan.pirati.cz/programy/" target="_blank" rel="noopener noreferrer">'
        'Piráti Kadaň – veřejně uvedení kandidáti</a>.</li>'
    )
    new_sources = (
        '<li><a href="https://kadan.pirati.cz/programy/" target="_blank" rel="noopener noreferrer">'
        'Piráti Kadaň – stránka kandidátů z komunálních voleb 2022; používána pouze jako historický zdroj</a>.</li>'
        '<li>Písemné vyjádření Elišky Hladové, kandidátky sdružení nezávislých kandidátů s podporou '
        'Pirátské strany, doručené redakci 5. srpna 2026.</li>'
    )
    if old_source in text:
        text = text.replace(old_source, new_sources, 1)
    elif "Písemné vyjádření Elišky Hladové" not in text:
        raise RuntimeError("Nelze opravit zdrojovou poznámku Pirátů.")

    banned = (
        "Piráti rovněž veřejně představují svůj tým",
        "Jana Hladová a další veřejně představení kandidáti",
        "Piráti ukazují jména, úřední potvrzení teprve přijde",
        "Piráti Kadaň – veřejně uvedení kandidáti",
    )
    for phrase in banned:
        if phrase in text:
            raise RuntimeError(f"V článku zůstala chybná formulace: {phrase}")
    if text.count("Miloslav") > 2:
        raise RuntimeError("Jméno Miloslavy Karfilátové zůstalo v článku mimo opravu.")

    write(ARTICLE, text)


def update_rss() -> None:
    path = ROOT / "rss.xml"
    text = path.read_text(encoding="utf-8")
    pattern = re.compile(r'<item>.*?' + re.escape(ARTICLE_URL) + r'.*?</item>', re.S)
    match = pattern.search(text)
    if not match:
        raise RuntimeError("Článek chybí v RSS.")
    item = match.group(0)
    item = re.sub(
        r'<description><!\[CDATA\[.*?\]\]></description>',
        f'<description><![CDATA[{DESC}]]></description>',
        item,
        count=1,
        flags=re.S,
    )
    if '<category>Oprava</category>' not in item:
        item = item.replace('</item>', '<category>Oprava</category>\n    </item>', 1)
    text = text[: match.start()] + item + text[match.end():]
    text = re.sub(
        r'<lastBuildDate>.*?</lastBuildDate>',
        f'<lastBuildDate>{format_datetime(datetime.fromisoformat(MODIFIED))}</lastBuildDate>',
        text,
        count=1,
        flags=re.S,
    )
    write(path, text)


def update_llms() -> None:
    path = ROOT / "llms.txt"
    text = path.read_text(encoding="utf-8")
    pattern = re.compile(r'(\[[^\n]+\]\(' + re.escape(ARTICLE_URL) + r'\)\n)\s{2}[^\n]*')
    if not pattern.search(text):
        raise RuntimeError("Článek chybí v llms.txt.")
    text = pattern.sub(r'\1  ' + DESC, text, count=1)
    write(path, text)


def update_registry() -> None:
    path = ROOT / "data" / "published-content-index.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    article = next((x for x in data.get("articles", []) if isinstance(x, dict) and x.get("url") == ARTICLE_URL), None)
    if article is None:
        raise RuntimeError("Článek chybí v registru.")
    article["modified_at"] = MODIFIED
    article["source_commit"] = "pending-editorial-correction"
    persons = [x for x in article.get("persons", []) if x != "Jana Hladová"]
    if "Eliška Hladová" not in persons:
        persons.append("Eliška Hladová")
    article["persons"] = persons
    organizations = [x for x in article.get("organizations", []) if x != "Piráti Kadaň"]
    for value in ("Sdružení nezávislých kandidátů s podporou Pirátů", "Česká pirátská strana"):
        if value not in organizations:
            organizations.append(value)
    article["organizations"] = organizations
    cases = article.setdefault("cases", [])
    correction_case = "Oprava nesprávného označení kandidujícího uskupení a kandidátů"
    if correction_case not in cases:
        cases.append(correction_case)
    topics = [x for x in article.get("topics", []) if x != "Piráti"]
    for value in ("Nezávislí s podporou Pirátů", "Oprava článku"):
        if value not in topics:
            topics.append(value)
    article["topics"] = topics

    now = datetime.now(timezone.utc).isoformat()
    validation = data.setdefault("validation", {})
    validation["repair_pending_public_verification"] = True
    validation["last_editorial_correction"] = {
        "status": "pending_public_verification",
        "checked_at": now,
        "article_url": ARTICLE_URL,
        "modified_at": MODIFIED,
        "classification": "political_candidate_list_correction",
        "corrected_claims": [
            "Kandiduje sdružení nezávislých kandidátů s podporou Pirátské strany, nikoli Pirátská strana.",
            "Miloslava Karfilátová byla nesprávně převzata z kandidátky 2022 a není uváděna jako kandidátka 2026.",
        ],
        "primary_correction_source": "Písemné vyjádření kandidátky Elišky Hladové ze dne 5. srpna 2026",
    }
    data["generated_at"] = now
    write(path, json.dumps(data, ensure_ascii=False, indent=2) + "\n")


def main() -> int:
    update_article()
    update_rss()
    update_llms()
    subprocess.run(["python3", str(ROOT / "scripts" / "enforce_all_article_visibility.py")], cwd=ROOT, check=True)
    update_registry()

    article_text = ARTICLE.read_text(encoding="utf-8")
    required = (
        'data-editorial-correction="20260805-1523"',
        "sdružení nezávislých kandidátů s podporou Pirátské strany",
        "Za chybu se omlouváme",
        MODIFIED,
    )
    for value in required:
        if value not in article_text:
            raise RuntimeError(f"Oprava se nepropsala do článku: {value}")
    print(f"Opraveno: {ARTICLE_URL} ({MODIFIED})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
