#!/usr/bin/env python3
from pathlib import Path

path = Path(__file__).with_name("full_site_audit_20260805.py")
text = path.read_text(encoding="utf-8")

# Starší verze auditu obsahovala několik raw řetězců uzavřených apostrofem,
# přestože regulární výraz současně obsahoval znak '. Přepiš je bezpečně
# na raw řetězce uzavřené trojitými uvozovkami.
replacements = {
    "return re.findall(r'<article\\b[^>]*class=[\\\"'][^\\\"']*\\barticle-card\\b[^\\\"']*[\\\"'][^>]*>.*?</article>', text, re.I | re.S)":
    "return re.findall(r'''<article\\b[^>]*class=[\\\"'][^\\\"']*\\barticle-card\\b[^\\\"']*[\\\"'][^>]*>.*?</article>''', text, re.I | re.S)",
    "re.search(r'<link\\b[^>]*rel=[\\\"']canonical[\\\"'][^>]*href=[\\\"']([^\\\"']+)', text, re.I)":
    "re.search(r'''<link\\b[^>]*rel=[\\\"']canonical[\\\"'][^>]*href=[\\\"']([^\\\"']+)''', text, re.I)",
    "re.findall(r'href=[\\\"']([^\\\"']*?/clanky/[^\\\"']+\\.html)', archive_text, re.I)":
    "re.findall(r'''href=[\\\"']([^\\\"']*?/clanky/[^\\\"']+\\.html)''', archive_text, re.I)",
    "re.findall(r'href=[\\\"'](/clanky/strana-\\d+\\.html)[\\\"']', text, re.I)":
    "re.findall(r'''href=[\\\"'](/clanky/strana-\\d+\\.html)[\\\"']''', text, re.I)",
    "re.search(r'<a\\b[^>]*class=[\\\"'][^\\\"']*\\bread-more\\b[^\\\"']*[\\\"'][^>]*href=[\\\"']([^\\\"']+)', block, re.I)":
    "re.search(r'''<a\\b[^>]*class=[\\\"'][^\\\"']*\\bread-more\\b[^\\\"']*[\\\"'][^>]*href=[\\\"']([^\\\"']+)''', block, re.I)",
    "re.findall(r'href=[\\\"']([^\\\"']+)', block, re.I)":
    "re.findall(r'''href=[\\\"']([^\\\"']+)''', block, re.I)",
}
for old, new in replacements.items():
    text = text.replace(old, new)
path.write_text(text, encoding="utf-8", newline="\n")
print("Zdroj úplného auditu byl syntakticky opraven.")
