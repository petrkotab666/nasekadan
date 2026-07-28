#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path
from urllib.parse import urljoin, urlsplit, urlunsplit, parse_qsl, urlencode
from urllib.request import Request, urlopen


def with_cache_bust(url: str, key: str) -> str:
    parts = urlsplit(url)
    query = dict(parse_qsl(parts.query, keep_blank_values=True))
    query["verify"] = key
    return urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(query), parts.fragment))


def fetch(base: str, path: str, key: str) -> str:
    url = with_cache_bust(urljoin(base.rstrip("/") + "/", path.lstrip("/")), key)
    req = Request(
        url,
        headers={
            "User-Agent": "NaseKadanReleaseVerifier/2.0",
            "Cache-Control": "no-cache, no-store, max-age=0",
            "Pragma": "no-cache",
            "Accept-Language": "cs,en;q=0.7",
        },
    )
    with urlopen(req, timeout=30) as response:
        if response.status != 200:
            raise RuntimeError(f"{url} vrátil HTTP {response.status}")
        return response.read().decode(response.headers.get_content_charset() or "utf-8", errors="replace")


def article_links(text: str) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for href in re.findall(r'href=["\']([^"\']+)["\']', text, re.I):
        path = urlsplit(href).path
        if not path.endswith(".html") or "/clanky/" not in path:
            continue
        if not path.startswith("/"):
            path = "/" + path.lstrip("./")
        path = re.sub(r"/+", "/", path)
        if path not in seen:
            seen.add(path)
            out.append(path)
    return out


def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def main() -> int:
    parser = argparse.ArgumentParser(description="Ověří skutečně veřejnou verzi Naše Kadaň proti aktuálnímu main.")
    parser.add_argument("--base", default="https://nasekadan.cz")
    parser.add_argument("--root", default=".")
    parser.add_argument("--expected-sha", required=True)
    parser.add_argument("--cache-key", default=str(int(time.time())))
    args = parser.parse_args()

    root = Path(args.root).resolve()
    errors: list[str] = []

    try:
        home = fetch(args.base, "/", args.cache_key)
        archive = fetch(args.base, "/clanky/", args.cache_key)
        rss = fetch(args.base, "/rss.xml", args.cache_key)
        sitemap = fetch(args.base, "/sitemap.xml", args.cache_key)
        health = fetch(args.base, "/deployment-health.txt", args.cache_key)
    except Exception as exc:
        print(f"CHYBA: základní veřejné stránky nelze načíst: {exc}", file=sys.stderr)
        return 2

    match = re.search(r"(?m)^source=([0-9a-f]{40})\s*$", health)
    public_sha = match.group(1) if match else ""
    require(bool(public_sha), "deployment-health.txt neobsahuje platný 40znakový source commit", errors)
    require(public_sha == args.expected_sha, f"veřejný source {public_sha or 'chybí'} neodpovídá main {args.expected_sha}", errors)

    manifest_path = root / "production-content-manifest.json"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"CHYBA: nelze načíst {manifest_path}: {exc}", file=sys.stderr)
        return 3

    for asset in manifest.get("required_assets", []):
        try:
            fetch(args.base, "/" + str(asset).lstrip("/"), args.cache_key)
        except Exception as exc:
            errors.append(f"povinný asset {asset} není veřejně dostupný: {exc}")

    required_tokens = [str(x) for x in manifest.get("required_article_tokens", [])]
    for item in manifest.get("required_articles", []):
        rel = str(item.get("path", "")).lstrip("/")
        needle = str(item.get("needle", ""))
        if not rel:
            errors.append("manifest obsahuje článek bez path")
            continue
        public_path = "/" + rel
        try:
            article = fetch(args.base, public_path, args.cache_key)
        except Exception as exc:
            errors.append(f"článek {rel} není veřejně dostupný: {exc}")
            continue
        require(not needle or needle in article, f"článek {rel} neobsahuje očekávaný text: {needle}", errors)
        for token in required_tokens:
            require(token in article, f"článek {rel} neobsahuje povinný token {token}", errors)
        if item.get("must_be_on_home"):
            require(rel in home or public_path in home, f"titulní stránka neobsahuje {rel}", errors)
        if item.get("must_be_in_archive"):
            require(rel in archive or public_path in archive, f"archiv neobsahuje {rel}", errors)
        require(rel in sitemap or public_path in sitemap, f"sitemap neobsahuje {rel}", errors)

    local_home = (root / "index.html").read_text(encoding="utf-8", errors="replace")
    local_archive = (root / "clanky" / "index.html").read_text(encoding="utf-8", errors="replace")
    home_links = article_links(local_home)
    archive_links = article_links(local_archive)

    for path in home_links:
        rel = path.lstrip("/")
        require(path in home or rel in home, f"veřejná titulní stránka postrádá aktuální odkaz {path}", errors)
        require(path in sitemap or rel in sitemap, f"sitemap postrádá aktuální odkaz {path}", errors)
        require(path in rss or rel in rss, f"RSS postrádá aktuální odkaz z titulní stránky {path}", errors)

    for path in archive_links:
        rel = path.lstrip("/")
        require(path in archive or rel in archive, f"veřejný archiv postrádá odkaz {path}", errors)
        require(path in sitemap or rel in sitemap, f"sitemap postrádá archivní odkaz {path}", errors)

    if errors:
        print("VEŘEJNÁ KONTROLA SELHALA:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(
        f"OVĚŘENO: veřejný web podává main {args.expected_sha}; "
        f"titulka ({len(home_links)} odkazů), archiv ({len(archive_links)} odkazů), RSS, sitemap, články a assety souhlasí."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
