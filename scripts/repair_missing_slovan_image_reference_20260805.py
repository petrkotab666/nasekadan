#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OLD = "assets/slovan-detail-20260724.jpg"
NEW = "social/slovan-druhy-pokus-e2e4356bbb.png"
PATHS = [
    ROOT / "clanky" / "slovan-druhy-pokus.html",
    ROOT / "clanky" / "parts" / "slovan-01.html",
    ROOT / ".github" / "drafts" / "slovan-druhy-pokus.html",
    ROOT / "scripts" / "publish_slovan_article.py",
    ROOT / "scripts" / "publish_slovan_20260805.py",
]

changed = []
for path in PATHS:
    if not path.is_file():
        continue
    text = path.read_text(encoding="utf-8", errors="replace")
    current = text.replace(OLD, NEW)
    if current != text:
        path.write_text(current, encoding="utf-8", newline="\n")
        changed.append(str(path.relative_to(ROOT)))

# Veřejný článek musí používat jedinou dostupnou sociální grafiku také v JSON-LD.
article = ROOT / "clanky" / "slovan-druhy-pokus.html"
if article.is_file():
    text = article.read_text(encoding="utf-8")
    current = text.replace(
        "https://nasekadan.cz/social/slovan-druhy-pokus-20260805.png",
        "https://nasekadan.cz/social/slovan-druhy-pokus-e2e4356bbb.png",
    )
    if current != text:
        article.write_text(current, encoding="utf-8", newline="\n")
        if str(article.relative_to(ROOT)) not in changed:
            changed.append(str(article.relative_to(ROOT)))

remaining = []
for path in PATHS:
    if path.is_file() and OLD in path.read_text(encoding="utf-8", errors="replace"):
        remaining.append(str(path.relative_to(ROOT)))
if remaining:
    raise SystemExit("Mrtvý odkaz zůstal v: " + ", ".join(remaining))
if not (ROOT / NEW).is_file():
    raise SystemExit(f"Náhradní obrázek neexistuje: {NEW}")

# Generátor chronologie může vložit mezery na jinak prázdné řádky. Odstraň je,
# aby git diff --check nezastavil bezpečnou obsahovou opravu.
NORMALIZE = [ROOT / "index.html", ROOT / "clanky" / "index.html"]
NORMALIZE.extend(sorted((ROOT / "clanky").glob("strana-*.html")))
NORMALIZE.extend([ROOT / "rss.xml", ROOT / "sitemap.xml", ROOT / "news-sitemap.xml", ROOT / "llms.txt"])
for path in NORMALIZE:
    if not path.is_file():
        continue
    text = path.read_text(encoding="utf-8", errors="replace")
    normalized = "\n".join(line.rstrip() for line in text.splitlines()) + "\n"
    if normalized != text:
        path.write_text(normalized, encoding="utf-8", newline="\n")
        rel = str(path.relative_to(ROOT))
        if rel not in changed:
            changed.append(rel)

print("Opravené soubory:", ", ".join(changed) if changed else "žádné – stav už byl opraven")
