#!/usr/bin/env python3
from pathlib import Path

path = Path(__file__).with_name("full_site_audit_20260805.py")
text = path.read_text(encoding="utf-8")
replacements = {
    "r'<link\\b[^>]*rel=[\\\"']canonical[\\\"'][^>]*href=[\\\"']([^\\\"']+)'": "r\"<link\\b[^>]*rel=[\\\"']canonical[\\\"'][^>]*href=[\\\"']([^\\\"']+)\"",
    "r'href=[\\\"']([^\\\"']*?/clanky/[^\\\"']+\\.html)'": "r\"href=[\\\"']([^\\\"']*?/clanky/[^\\\"']+\\.html)\"",
    "r'href=[\\\"'](/clanky/strana-\\d+\\.html)[\\\"']'": "r\"href=[\\\"'](/clanky/strana-\\d+\\.html)[\\\"']\"",
    "r'<a\\b[^>]*class=[\\\"'][^\\\"']*\\bread-more\\b[^\\\"']*[\\\"'][^>]*href=[\\\"']([^\\\"']+)'": "r\"<a\\b[^>]*class=[\\\"'][^\\\"']*\\bread-more\\b[^\\\"']*[\\\"'][^>]*href=[\\\"']([^\\\"']+)\"",
    "r'href=[\\\"']([^\\\"']+)'": "r\"href=[\\\"']([^\\\"']+)\"",
    "r'<article\\b[^>]*class=[\\\"'][^\\\"']*\\barticle-card\\b[^\\\"']*[\\\"'][^>]*>.*?</article>'": "r\"<article\\b[^>]*class=[\\\"'][^\\\"']*\\barticle-card\\b[^\\\"']*[\\\"'][^>]*>.*?</article>\"",
}
for old, new in replacements.items():
    text = text.replace(old, new)
path.write_text(text, encoding="utf-8", newline="\n")
print("Zdroj úplného auditu byl syntakticky normalizován.")
