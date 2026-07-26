#!/usr/bin/env python3
"""Normalize search snippets and article time metadata in built public HTML."""

from __future__ import annotations

import json
import re
from html import escape
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SKIP_DIRS = {
    ".git", ".github", ".image-parts", "deploy", "docker-entrypoint.d",
    "lms-rescue", "nahled", "newsletter", "nginx", "node_modules",
    "scripts", "sdilet", "tools",
}

TITLE_OVERRIDES = {
    "clanky/dopravni-nehoda-se-zranenim-kadan-24-cervence-2026.html":
        "Nehoda v Prunéřově se zraněním | Naše Kadaň",
    "clanky/nemocnice-kadan-software-kyberbezpecnost.html":
        "Nemocnice Kadaň: 64,7 milionu za software | Naše Kadaň",
    "clanky/nemocnice-kadan.html":
        "Nemocnice Kadaň: ztráta 46 milionů a pomoc města | Naše Kadaň",
    "clanky/petice-nemocnice-kadan.html":
        "Petice a Nemocnice Kadaň: co víme o 100 milionech | Naše Kadaň",
    "clanky/pozemky-koupaliste-kadan.html":
        "Prodej pozemků koupaliště Kadaň za 3,6 milionu | Naše Kadaň",
    "clanky/vypadek-internetu-kadan-kradez-kabelu.html":
        "Výpadek internetu v Kadani: služby obnoveny | Naše Kadaň",
    "o-webu/index.html": "O webu a redakci | Naše Kadaň",
}

DESCRIPTION_OVERRIDES = {
    "404.html": (
        "Požadovaná stránka webu Naše Kadaň nebyla nalezena. "
        "Vraťte se na úvod nebo otevřete přehled všech článků."
    ),
    "pruvodce/hradebni-okruh.html": (
        "Průvodce hradebním okruhem Kadaně: městské hradby, parkány, "
        "bašty, historické brány, Katova ulička a doporučená pěší trasa."
    ),
}

JSON_LD_RE = re.compile(
    r"<script\b[^>]*\btype=[\"']application/ld\+json[\"'][^>]*>(.*?)</script>",
    re.I | re.S,
)


def relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def public_html_files() -> list[Path]:
    result: list[Path] = []
    for path in ROOT.rglob("*.html"):
        parts = path.relative_to(ROOT).parts
        if any(part in SKIP_DIRS or part.startswith(".") for part in parts[:-1]):
            continue
        if not re.search(r"<html\b", path.read_text(encoding="utf-8", errors="replace"), re.I):
            continue
        result.append(path)
    return sorted(result)


def replace_title(text: str, title: str) -> str:
    replacement = f"<title>{escape(title)}</title>"
    return re.sub(r"<title\b[^>]*>.*?</title>", replacement, text, count=1, flags=re.I | re.S)


def replace_description(text: str, description: str) -> str:
    replacement = f'<meta name="description" content="{escape(description, quote=True)}">'
    pattern = re.compile(
        r"<meta\b(?=[^>]*\bname=[\"']description[\"'])[^>]*>",
        re.I,
    )
    if pattern.search(text):
        return pattern.sub(replacement, text, count=1)
    return text.replace("</head>", replacement + "</head>", 1)


def schema_types(node: dict[str, Any]) -> set[str]:
    value = node.get("@type")
    if isinstance(value, str):
        return {value}
    if isinstance(value, list):
        return {item for item in value if isinstance(item, str)}
    return set()


def article_node(text: str) -> dict[str, Any] | None:
    for raw in JSON_LD_RE.findall(text):
        try:
            data = json.loads(raw.strip())
        except json.JSONDecodeError:
            continue
        nodes: list[dict[str, Any]] = []
        if isinstance(data, dict):
            nodes.append(data)
            graph = data.get("@graph")
            if isinstance(graph, list):
                nodes.extend(node for node in graph if isinstance(node, dict))
        elif isinstance(data, list):
            nodes.extend(node for node in data if isinstance(node, dict))
        for node in nodes:
            if schema_types(node) & {"NewsArticle", "Article"}:
                return node
    return None


def has_meta_property(text: str, prop: str) -> bool:
    return bool(re.search(
        rf"<meta\b(?=[^>]*\bproperty=[\"']{re.escape(prop)}[\"'])[^>]*>",
        text,
        re.I,
    ))


def add_article_time_meta(text: str) -> str:
    article = article_node(text)
    if not article:
        return text
    additions: list[str] = []
    published = str(article.get("datePublished") or "").strip()
    modified = str(article.get("dateModified") or published).strip()
    if published and not has_meta_property(text, "article:published_time"):
        additions.append(
            f'<meta property="article:published_time" content="{escape(published, quote=True)}">'
        )
    if modified and not has_meta_property(text, "article:modified_time"):
        additions.append(
            f'<meta property="article:modified_time" content="{escape(modified, quote=True)}">'
        )
    if additions:
        text = text.replace("</head>", "".join(additions) + "</head>", 1)
    return text


def process(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    original = text
    name = relative(path)
    if name in TITLE_OVERRIDES:
        text = replace_title(text, TITLE_OVERRIDES[name])
    if name in DESCRIPTION_OVERRIDES:
        text = replace_description(text, DESCRIPTION_OVERRIDES[name])
    if name.startswith("clanky/") and name != "clanky/index.html":
        text = add_article_time_meta(text)
    if text != original:
        path.write_text(text, encoding="utf-8")
        return True
    return False


def main() -> None:
    changed = sum(process(path) for path in public_html_files())
    print(f"Normalizovány vyhledávací úryvky na {changed} stránkách.")


if __name__ == "__main__":
    main()
