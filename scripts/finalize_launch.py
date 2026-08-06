#!/usr/bin/env python3
"""Finalize public Naše Kadaň pages without destroying article SEO metadata."""

from __future__ import annotations

from html import escape
from pathlib import Path
import importlib.util
import re
import subprocess
import sys
from ensure_favicon import normalize_favicon_html

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://nasekadan.cz"
DEFAULT_OG_IMAGE = f"{BASE}/social-preview.png"
EXCLUDE_DIRS = {
    ".git", ".github", "deploy", "docker-entrypoint.d", "lms-rescue",
    "nahled", "newsletter", "nginx", "parts", "research", "scripts", "sdilet", "tools",
}


def relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def is_public_html(path: Path) -> bool:
    return not any(part in EXCLUDE_DIRS for part in path.relative_to(ROOT).parts)


def canonical_for(path: Path) -> str:
    rel = relative(path)
    if rel == "index.html":
        return f"{BASE}/"
    if rel.endswith("/index.html"):
        return f"{BASE}/{rel[:-10]}"
    return f"{BASE}/{rel}"


def title_from_html(text: str) -> str:
    match = re.search(r"<title\b[^>]*>(.*?)</title>", text, re.I | re.S)
    if not match:
        return "Naše Kadaň"
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", match.group(1))).strip()


def desc_from_html(text: str) -> str:
    for match in re.finditer(r"<meta\b[^>]*>", text, re.I):
        tag = match.group(0)
        if not re.search(r'\bname=["\']description["\']', tag, re.I):
            continue
        content = re.search(r'\bcontent=["\']([^"\']*)', tag, re.I)
        if content:
            return content.group(1).strip()
    return "Aktuální informace, události, praktické rady a příběhy z Kadaně."


def has_meta(text: str, *, name: str | None = None, prop: str | None = None) -> bool:
    for match in re.finditer(r"<meta\b[^>]*>", text, re.I):
        tag = match.group(0)
        if name and re.search(rf'\bname=["\']{re.escape(name)}["\']', tag, re.I):
            return True
        if prop and re.search(rf'\bproperty=["\']{re.escape(prop)}["\']', tag, re.I):
            return True
    return False


def has_canonical(text: str) -> bool:
    return bool(re.search(
        r'<link\b(?=[^>]*\brel=["\'][^"\']*\bcanonical\b[^"\']*["\'])[^>]*>',
        text,
        re.I,
    ))


def is_noindex(text: str) -> bool:
    return bool(re.search(
        r'<meta\b(?=[^>]*\bname=["\']robots["\'])(?=[^>]*\bcontent=["\'][^"\']*\bnoindex\b)',
        text,
        re.I,
    ))


def is_archive_page(path: Path) -> bool:
    return path.parent == ROOT / "clanky" and (
        path.name == "index.html" or bool(re.fullmatch(r"strana-\d+\.html", path.name))
    )


def ensure_head_meta(text: str, path: Path) -> str:
    title = title_from_html(text)
    description = desc_from_html(text)
    canonical = canonical_for(path)
    is_article = path.parent == ROOT / "clanky" and not is_archive_page(path)
    is_404 = path.name == "404.html"
    additions: list[str] = []

    if not has_canonical(text) and not is_404:
        additions.append(f'<link rel="canonical" href="{escape(canonical, quote=True)}">')
    if not has_meta(text, name="robots"):
        robots = "noindex,follow,noarchive" if is_404 else (
            "index,follow,max-image-preview:large,max-snippet:-1,max-video-preview:-1"
        )
        additions.append(f'<meta name="robots" content="{robots}">')

    defaults = {
        "og:type": "article" if is_article else "website",
        "og:locale": "cs_CZ",
        "og:site_name": "Naše Kadaň",
        "og:title": title,
        "og:description": description,
        "og:url": canonical,
        "og:image": DEFAULT_OG_IMAGE,
    }
    for prop, value in defaults.items():
        if not has_meta(text, prop=prop):
            additions.append(
                f'<meta property="{prop}" content="{escape(value, quote=True)}">'
            )

    twitter = {
        "twitter:card": "summary_large_image",
        "twitter:title": title,
        "twitter:description": description,
        "twitter:image": DEFAULT_OG_IMAGE,
    }
    for name, value in twitter.items():
        if not has_meta(text, name=name):
            additions.append(
                f'<meta name="{name}" content="{escape(value, quote=True)}">'
            )

    if additions:
        text = text.replace("</head>", "".join(additions) + "</head>", 1)
    return text


def add_analytics(text: str) -> str:
    if "/analytics.js" not in text:
        text = text.replace(
            "</body>", '<script src="/analytics.js" defer></script></body>', 1
        )
    return text


def add_footer_links(text: str) -> str:
    links = (
        '<span class="legal-links"><a href="/o-webu/">O webu</a> · '
        '<a href="/ochrana-osobnich-udaju/">Ochrana osobních údajů</a> · '
        '<a href="/navstevnost/">Návštěvnost</a></span>'
    )
    if "/o-webu/" in text and "/navstevnost/" in text:
        return text
    if "</footer>" in text:
        return text.replace(
            "</footer>", f'<div class="wrap footer-legal">{links}</div></footer>', 1
        )
    return text


def process_html(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    text = text.replace(
        "/pruvodce/mirove-namesti.html", "/pruvodce/mestske-namesti.html"
    )
    text = ensure_head_meta(text, path)
    text = normalize_favicon_html(text)
    text = add_analytics(text)
    text = add_footer_links(text)
    path.write_text(text, encoding="utf-8")


def ensure_support_files() -> None:

    error = ROOT / "404.html"
    if not error.exists():
        error.write_text(
            '<!doctype html><html lang="cs"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1">'
            '<title>Stránka nenalezena | Naše Kadaň</title>'
            '<meta name="description" content="Požadovaná stránka nebyla nalezena.">'
            '<meta name="robots" content="noindex,follow,noarchive">'
            '<link rel="icon" href="/favicon.svg" type="image/svg+xml">'
            '<link rel="stylesheet" href="/style.css"></head><body>'
            '<header><div class="wrap head"><a class="logo" href="/">'
            '<span class="logo-mark">NK</span><span>NAŠE <b>KADAŇ</b></span>'
            '</a></div></header><main class="wrap section"><p class="tag">CHYBA 404</p>'
            '<h1>Stránka nebyla nalezena</h1><p class="section-intro">'
            'Odkaz mohl být změněn nebo stránka už neexistuje.</p>'
            '<p><a class="btn" href="/">Zpět na úvodní stránku</a></p></main>'
            '<footer><div class="wrap">© 2026 Naše Kadaň</div></footer></body></html>',
            encoding="utf-8",
        )


def update_privacy_and_style() -> None:
    privacy = ROOT / "ochrana-osobnich-udaju" / "index.html"
    if privacy.exists():
        text = privacy.read_text(encoding="utf-8")
        if "Měření návštěvnosti" not in text:
            insert = (
                "<h2>Měření návštěvnosti</h2><p>Pro základní souhrnné statistiky "
                "zaznamenáváme navštívenou cestu, čas a anonymizovaný denní "
                "identifikátor odvozený z IP adresy. Nepoužíváme reklamní cookies "
                "ani nevytváříme uživatelské profily.</p>"
            )
            text = text.replace("<h2>Vaše práva</h2>", insert + "<h2>Vaše práva</h2>")
            privacy.write_text(text, encoding="utf-8")

    style = ROOT / "style.css"
    if style.exists():
        css = style.read_text(encoding="utf-8")
        if ".footer-legal" not in css:
            css += (
                " .footer-legal{padding-top:22px;margin-top:22px;border-top:"
                "1px solid #ffffff1a;font-size:14px;color:#aebbc2}"
                ".footer-legal a{display:inline;color:inherit}"
                ".legal-links{display:block}"
            )
            style.write_text(css, encoding="utf-8")


def write_sitemap() -> int:
    urls: list[str] = []
    for path in sorted(ROOT.rglob("*.html")):
        if not is_public_html(path) or path.name == "404.html":
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        if is_noindex(text):
            continue
        urls.append(canonical_for(path))
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "".join(f"  <url><loc>{escape(url)}</loc></url>\n" for url in sorted(set(urls)))
        + "</urlset>\n"
    )
    (ROOT / "sitemap.xml").write_text(xml, encoding="utf-8")
    return len(set(urls))


def ensure_robots() -> None:
    path = ROOT / "robots.txt"
    text = path.read_text(encoding="utf-8") if path.exists() else ""
    required_blocks = [
        "User-agent: *\nAllow: /\nDisallow: /api/\nDisallow: /data/\nDisallow: /statistiky/",
        "User-agent: OAI-SearchBot\nAllow: /\nDisallow: /api/\nDisallow: /data/\nDisallow: /statistiky/",
    ]
    for block in required_blocks:
        agent = block.splitlines()[0]
        if agent not in text:
            text = text.rstrip() + "\n\n" + block + "\n"
    for line in (
        f"Sitemap: {BASE}/sitemap.xml",
        f"Sitemap: {BASE}/news-sitemap.xml",
    ):
        if line not in text:
            text = text.rstrip() + "\n" + line + "\n"
    path.write_text(text.lstrip(), encoding="utf-8")


def run_discovery() -> None:
    module_path = ROOT / "scripts" / "prepare_discovery.py"
    spec = importlib.util.spec_from_file_location("prepare_discovery", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Nelze načíst scripts/prepare_discovery.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.main()


def audit_changed_articles() -> None:
    try:
        output = subprocess.check_output(
            ["git", "diff", "--name-only"], cwd=ROOT, text=True
        )
    except (OSError, subprocess.CalledProcessError):
        return
    paths = [
        line.strip()
        for line in output.splitlines()
        if line.startswith("clanky/")
        and line.endswith(".html")
        and line != "clanky/index.html"
        and not re.fullmatch(r"clanky/strana-\d+\.html", line)
    ]
    if not paths:
        return
    command = [
        sys.executable,
        str(ROOT / "scripts" / "seo_ai_audit.py"),
        "--strict",
        "--paths",
        *paths,
    ]
    subprocess.run(command, cwd=ROOT, check=True)


def main() -> None:
    ensure_support_files()
    update_privacy_and_style()
    for path in sorted(ROOT.rglob("*.html")):
        if is_public_html(path):
            process_html(path)
    ensure_robots()
    run_discovery()
    count = write_sitemap()
    audit_changed_articles()
    print(f"Finalizováno {count} indexovatelných stránek bez přepisování článkových metadat.")


if __name__ == "__main__":
    main()
