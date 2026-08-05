#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
path = ROOT / "scripts" / "enforce_all_article_visibility.py"
text = path.read_text(encoding="utf-8")
marker = "VISIBILITY-WHITESPACE-NORMALIZATION-20260805"
if marker not in text:
    function = '''\n\ndef normalize_generated_text_files() -> None:\n    """Odstraní koncové mezery z kanonicky generovaných veřejných souborů.\n\n    VISIBILITY-WHITESPACE-NORMALIZATION-20260805\n    """\n    paths = [\n        ROOT / "index.html",\n        ROOT / "clanky" / "index.html",\n        ROOT / "rss.xml",\n        ROOT / "sitemap.xml",\n        ROOT / "news-sitemap.xml",\n        ROOT / "llms.txt",\n    ]\n    paths.extend(sorted((ROOT / "clanky").glob("strana-*.html")))\n    for generated in paths:\n        if not generated.is_file():\n            continue\n        original = generated.read_text(encoding="utf-8", errors="replace")\n        normalized = "\\n".join(line.rstrip() for line in original.splitlines()) + "\\n"\n        if normalized != original:\n            generated.write_text(normalized, encoding="utf-8", newline="\\n")\n'''
    needle = "\ndef main() -> int:\n"
    if needle not in text:
        raise SystemExit("Nenalezen začátek funkce main.")
    text = text.replace(needle, function + needle, 1)
    print_needle = '    print(\n        f"Viditelnost obnovena:'
    if print_needle not in text:
        raise SystemExit("Nenalezen závěrečný výpis generátoru.")
    text = text.replace(print_needle, '    normalize_generated_text_files()\n\n' + print_needle, 1)
    path.write_text(text, encoding="utf-8", newline="\n")
    print("Generátor byl doplněn o trvalou normalizaci mezer.")
else:
    print("Generátor již obsahuje trvalou normalizaci mezer.")
