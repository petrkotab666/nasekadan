#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ipaddress
import json
import re
import subprocess
from pathlib import Path

MARKER = "include /etc/nginx/snippets/multisite-statistiky-server.conf;"
SERVER_NAME_RE = re.compile(r"(^[ \t]*server_name\s+([^;]+);)", re.M)
SKIP_NAMES = {"_", "localhost", "localhost.localdomain"}
SKIP_SUFFIXES = (".local", ".localhost", ".internal", ".invalid")


def server_blocks(text: str):
    for match in re.finditer(r"\bserver\s*\{", text):
        start = match.start()
        brace = text.find("{", match.start())
        depth = 0
        quote = None
        escaped = False
        for index in range(brace, len(text)):
            char = text[index]
            if escaped:
                escaped = False
                continue
            if char == "\\":
                escaped = True
                continue
            if quote:
                if char == quote:
                    quote = None
                continue
            if char in {'"', "'"}:
                quote = char
                continue
            if char == "{":
                depth += 1
            elif char == "}":
                depth -= 1
                if depth == 0:
                    yield start, index + 1, text[start:index + 1]
                    break


def clean_name(raw: str) -> str:
    name = raw.strip().lower().rstrip(".")
    if name.startswith("www."):
        name = name[4:]
    return name


def public_names(raw: str) -> list[str]:
    result: list[str] = []
    for token in re.split(r"\s+", raw.strip()):
        token = token.strip()
        if not token or token.startswith("$") or "*" in token or token.startswith("~"):
            continue
        name = clean_name(token)
        if name in SKIP_NAMES or name.endswith(SKIP_SUFFIXES) or "." not in name:
            continue
        try:
            ipaddress.ip_address(name)
            continue
        except ValueError:
            pass
        if not re.fullmatch(r"[a-z0-9.-]+", name):
            continue
        result.append(name)
    return sorted(set(result))


def candidate_files() -> list[Path]:
    roots = [Path("/etc/nginx/sites-enabled"), Path("/etc/nginx/conf.d")]
    files: list[Path] = []
    seen: set[Path] = set()
    for root in roots:
        if not root.exists():
            continue
        for path in sorted(root.glob("*")):
            if path.name.startswith(".") or path.suffix in {".bak", ".disabled", ".old"}:
                continue
            if not path.is_file() and not path.is_symlink():
                continue
            try:
                real = path.resolve()
            except OSError:
                continue
            if real in seen:
                continue
            seen.add(real)
            files.append(real)
    return files


def patch_file(path: Path) -> tuple[bool, set[str]]:
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return False, set()
    replacements: list[tuple[int, str]] = []
    domains: set[str] = set()
    for start, _end, block in server_blocks(text):
        match = SERVER_NAME_RE.search(block)
        if not match:
            continue
        names = public_names(match.group(2))
        if not names:
            continue
        # Naše Kadaň má vlastní podrobnější statistický systém a zůstává beze změny.
        if any(name == "nasekadan.cz" or name.endswith(".nasekadan.cz") for name in names):
            continue
        domains.update(names)
        if MARKER in block or re.search(r"location\s+(?:=|\^~)?\s*/statistiky/?", block):
            continue
        insert_at = start + match.end(1)
        indent = re.match(r"[ \t]*", match.group(1)).group(0)
        replacements.append((insert_at, f"\n\n{indent}{MARKER}"))
    if not replacements:
        return False, domains
    for offset, addition in reversed(replacements):
        text = text[:offset] + addition + text[offset:]
    path.write_text(text, encoding="utf-8")
    return True, domains


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--reload", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    changed: list[str] = []
    domains: set[str] = set()
    for path in candidate_files():
        did_change, found = patch_file(path)
        domains.update(found)
        if did_change:
            changed.append(str(path))

    if changed:
        subprocess.run(["nginx", "-t"], check=True)
        if args.reload:
            subprocess.run(["systemctl", "reload", "nginx"], check=True)

    result = {"changed": changed, "domains": sorted(domains), "count": len(domains)}
    if args.json:
        print(json.dumps(result, ensure_ascii=False))
    else:
        print("Weby se statistikami:", ", ".join(sorted(domains)) or "žádné")
        print("Upravené konfigurace:", len(changed))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
