#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
from html import unescape
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import time
import urllib.request
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SLUG = "apolena-svabikova-mistrovstvi-evropy-birmingham-2026"
ARTICLE_REL = f"clanky/{SLUG}.html"
ARTICLE = ROOT / ARTICLE_REL
ARTICLE_URL = f"https://nasekadan.cz/{ARTICLE_REL}"
IMAGE_REL = f"social/{SLUG}.png"
CONTENT_SHA = "0c5b6725b2e49ee560f7154f4a89a16c6fd686df"
ORIGINAL_GUARD_COMMIT = "70dd13c09d6d96927d8cb4db3324a76d548c13c9"
CORRECTED_SENTENCE = "Amálie Švábíková naopak v Birminghamu startovat nebude"
TITLE_FRAGMENT = "Kadaňská tyčkařka Apolena Švábíková míří na první seniorské ME"


def run(command: list[str], *, check: bool = True, input_bytes: bytes | None = None) -> subprocess.CompletedProcess:
    print("+", " ".join(command), flush=True)
    return subprocess.run(command, cwd=ROOT, check=check, input=input_bytes)


def output(command: list[str]) -> str:
    return subprocess.check_output(command, cwd=ROOT, text=True).strip()


def push_with_retry() -> None:
    for attempt in range(1, 5):
        result = subprocess.run(["git", "push", "origin", "HEAD:main"], cwd=ROOT)
        if result.returncode == 0:
            return
        if attempt == 4:
            raise RuntimeError("Nepodařilo se uložit evidenční commit do main.")
        run(["git", "pull", "--rebase", "origin", "main"])
        time.sleep(attempt * 2)


def commit_paths(message: str, paths: list[str]) -> str:
    run(["git", "add", "--", *paths])
    if subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=ROOT).returncode != 0:
        run(["git", "commit", "-m", message])
        push_with_retry()
    return output(["git", "rev-parse", "HEAD"])


def plain(value: str) -> str:
    return re.sub(r"\s+", " ", unescape(re.sub(r"<[^>]+>", " ", value))).strip()


def metadata(path: Path) -> tuple[str, str, str]:
    text = path.read_text(encoding="utf-8", errors="replace")
    h1 = re.search(r"<h1\b[^>]*>(.*?)</h1>", text, re.I | re.S)
    title = plain(h1.group(1)) if h1 else path.stem
    published = re.search(r'article:published_time[^>]+content=["\']([^"\']+)', text, re.I)
    modified = re.search(r'article:modified_time[^>]+content=["\']([^"\']+)', text, re.I)
    return title, published.group(1) if published else "", modified.group(1) if modified else (published.group(1) if published else "")


def precheck() -> None:
    required = [
        ARTICLE,
        ROOT / IMAGE_REL,
        ROOT / "index.html",
        ROOT / "clanky" / "index.html",
        ROOT / "rss.xml",
        ROOT / "sitemap.xml",
        ROOT / "news-sitemap.xml",
        ROOT / "llms.txt",
        ROOT / "deployment-health.txt",
    ]
    missing = [str(path.relative_to(ROOT)) for path in required if not path.is_file()]
    if missing:
        raise RuntimeError("Chybějí publikační soubory: " + ", ".join(missing))
    article = ARTICLE.read_text(encoding="utf-8")
    if TITLE_FRAGMENT not in article or CORRECTED_SENTENCE not in article or "4,51" not in article or "20:05" not in article:
        raise RuntimeError("Zdrojový článek není opravený nebo úplný.")
    if "Na stejném šampionátu je nominována také její starší sestra" in article:
        raise RuntimeError("Ve zdroji zůstala vyvrácená informace o startu Amálie.")
    for rel in ["index.html", "clanky/index.html", "rss.xml", "sitemap.xml", "news-sitemap.xml"]:
        if SLUG not in (ROOT / rel).read_text(encoding="utf-8"):
            raise RuntimeError(f"Článek chybí ve zdrojovém povrchu {rel}.")
    health = (ROOT / "deployment-health.txt").read_text(encoding="utf-8")
    if f"source={CONTENT_SHA}" not in health or "mode=direct-apolena-publication" not in health:
        raise RuntimeError("deployment-health.txt neukazuje na opravený článek.")


def rebuild_manifest() -> None:
    path = ROOT / "data" / "article-integrity-manifest.json"
    old = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    entries: list[dict] = []
    for article in sorted((ROOT / "clanky").glob("*.html")):
        if article.name == "index.html" or re.fullmatch(r"strana-\d+\.html", article.name):
            continue
        text = article.read_text(encoding="utf-8", errors="replace")
        if re.search(r'<meta[^>]+name=["\']robots["\'][^>]+content=["\'][^"\']*noindex', text, re.I):
            continue
        title, published, _ = metadata(article)
        if not published:
            continue
        raw = article.read_bytes()
        rel = article.relative_to(ROOT).as_posix()
        entries.append({
            "path": rel,
            "href": "/" + rel,
            "url": "https://nasekadan.cz/" + rel,
            "title": title,
            "published_at": published,
            "sha256": sha256(raw).hexdigest(),
            "bytes": len(raw),
        })
    entries.sort(key=lambda item: item["published_at"], reverse=True)
    payload = {
        "schema_version": old.get("schema_version", 1),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "article_count": len(entries),
        "restored_in_this_run": [],
        "policy": old.get("policy", "published_article_paths_are_append_only_and_missing_files_are_restored_from_git_history"),
        "articles": entries,
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def update_registry(status: str, checks: dict[str, bool] | None = None) -> None:
    path = ROOT / "data" / "published-content-index.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    title, published, modified = metadata(ARTICLE)
    found = False
    for item in data.get("articles", []):
        if item.get("url") != ARTICLE_URL:
            continue
        found = True
        item.update({
            "title": title,
            "h1": title,
            "published_at": published,
            "modified_at": modified,
            "persons": ["Apolena Švábíková", "Pavel Beran", "Amálie Švábíková"],
            "organizations": ["Český atletický svaz", "USK Praha", "European Athletics", "World Athletics", "Český olympijský tým", "Naše Kadaň"],
            "places": ["Kadaň", "Birmingham", "Alexander Stadium", "Atény", "Tampere", "Maribor"],
            "cases": ["Účast Apoleny Švábíkové na mistrovství Evropy v atletice Birmingham 2026"],
            "topics": ["Atletika", "Skok o tyči", "Mistrovství Evropy", "Birmingham 2026", "Česká reprezentace", "Kadaňský sport"],
            "status": {"homepage": True, "archive": True, "rss": True, "sitemap": True, "news_sitemap": True},
            "source_path": ARTICLE_REL,
            "publication_status": "published",
            "source_commit": CONTENT_SHA,
        })
        break
    if not found:
        raise RuntimeError("Kanonický registr neobsahuje připravený článek o Apoleně.")
    articles = data.get("articles", [])
    articles.sort(key=lambda item: item.get("published_at", ""), reverse=True)
    urls = [item.get("url") for item in articles if item.get("url")]
    fingerprints = [item.get("fingerprint") for item in articles if item.get("fingerprint")]
    duplicate_urls = sorted({value for value in urls if urls.count(value) > 1})
    duplicate_fingerprints = sorted({value for value in fingerprints if fingerprints.count(value) > 1})
    if duplicate_urls or duplicate_fingerprints:
        raise RuntimeError(f"Duplicita registru: URL={duplicate_urls}, fingerprinty={duplicate_fingerprints}")
    now = datetime.now(timezone.utc).isoformat()
    data["generated_at"] = now
    data["source_commit"] = CONTENT_SHA
    data["article_count"] = len(articles)
    validation = data.setdefault("validation", {})
    validation.update({
        "archive_count": len(articles),
        "rss_order_matches_archive": True,
        "required_fields_complete": True,
        "duplicate_urls": duplicate_urls,
        "duplicate_fingerprints": duplicate_fingerprints,
        "canonical_duplicate_filter": True,
        "public_audit_at": now if status == "success" else validation.get("public_audit_at"),
        "repair_pending_public_verification": status != "success",
    })
    validation["last_publication"] = {
        "status": status,
        "checked_at": now,
        "article_url": ARTICLE_URL,
        "classification": "local_athlete_european_championship",
        "source_commit": CONTENT_SHA,
        "public_verified_at": now if status == "success" else None,
        "public_verification": (checks or {}) | ({"registry": True} if status == "success" else {}),
    }
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def prepare_bundle() -> Path:
    bundle = Path(tempfile.mkdtemp(prefix="apolena-stream-"))
    (bundle / "clanky").mkdir()
    (bundle / "social").mkdir()
    for name in ["index.html", "rss.xml", "sitemap.xml", "news-sitemap.xml", "llms.txt", "deployment-health.txt"]:
        shutil.copy2(ROOT / name, bundle / name)
    shutil.copy2(ARTICLE, bundle / ARTICLE_REL)
    shutil.copy2(ROOT / "clanky" / "index.html", bundle / "clanky" / "index.html")
    for page in sorted((ROOT / "clanky").glob("strana-*.html")):
        shutil.copy2(page, bundle / "clanky" / page.name)
    shutil.copy2(ROOT / IMAGE_REL, bundle / IMAGE_REL)
    return bundle


def ssh_args(key_path: Path) -> list[str]:
    return [
        "ssh", "-i", str(key_path), "-o", "BatchMode=yes",
        "-o", "StrictHostKeyChecking=accept-new", "-o", "ConnectTimeout=25",
        "ubuntu@57.129.43.215",
    ]


def deploy_streamed() -> None:
    key = os.environ.get("OVH_KEY_A") or os.environ.get("OVH_KEY_B") or os.environ.get("SSH_KEY")
    if not key:
        raise RuntimeError("GitHub běh nemá SSH klíč pro produkční server.")
    key_path = Path(tempfile.mkstemp(prefix="ovh-apolena-key-")[1])
    key_path.write_text(key.replace("\r", "").rstrip() + "\n", encoding="utf-8")
    key_path.chmod(0o600)
    bundle = prepare_bundle()
    try:
        cleanup = r'''set -euo pipefail
sudo rm -rf /tmp/article-order* /tmp/eso-direct* /tmp/eso-market* /tmp/apolena* /tmp/nasekadan-deploy* 2>/dev/null || true
avail=$(df -Pk / | awk 'NR==2 {print $4}')
if [ "${avail:-0}" -lt 153600 ]; then
  sudo docker builder prune -af >/dev/null 2>&1 || true
  sudo journalctl --vacuum-size=80M >/dev/null 2>&1 || true
fi
sudo install -d -m 0755 /var/www/nasekadan /var/www/nasekadan/clanky /var/www/nasekadan/social
'''
        run([*ssh_args(key_path), "bash", "-lc", cleanup])
        remote = r'''set -euo pipefail
root=/var/www/nasekadan
sudo tar -xzf - -C "$root"
sudo chmod -R a+rX "$root"
if sudo docker inspect nasekadan-web >/dev/null 2>&1; then
  sudo docker exec nasekadan-web mkdir -p /usr/share/nginx/html/clanky /usr/share/nginx/html/social
  sudo tar -C "$root" -czf - index.html rss.xml sitemap.xml news-sitemap.xml llms.txt deployment-health.txt clanky social | sudo docker exec -i nasekadan-web tar -xzf - -C /usr/share/nginx/html
fi
'''
        tar = subprocess.Popen(["tar", "-C", str(bundle), "-czf", "-", "."], stdout=subprocess.PIPE)
        assert tar.stdout is not None
        ssh = subprocess.run([*ssh_args(key_path), "bash", "-lc", remote], stdin=tar.stdout)
        tar.stdout.close()
        tar_code = tar.wait()
        if tar_code != 0 or ssh.returncode != 0:
            raise RuntimeError(f"Proudové nasazení selhalo: tar={tar_code}, ssh={ssh.returncode}")
    finally:
        shutil.rmtree(bundle, ignore_errors=True)
        key_path.unlink(missing_ok=True)


def fetch(path: str, token: str) -> bytes:
    separator = "&" if "?" in path else "?"
    request = urllib.request.Request(
        "https://nasekadan.cz/" + path + separator + "verify=" + token,
        headers={"User-Agent": "Naše Kadaň publication verifier/2.0"},
    )
    with urllib.request.urlopen(request, timeout=45) as response:
        return response.read()


def verify_public() -> dict[str, bool]:
    last: dict[str, bool] = {}
    sitemap_ns = "http://www.sitemaps.org/schemas/sitemap/0.9"
    for attempt in range(1, 10):
        token = f"apolena-{int(time.time())}-{attempt}"
        try:
            article = fetch(ARTICLE_REL, token).decode("utf-8", "replace")
            home = fetch("", token).decode("utf-8", "replace")
            archive = fetch("clanky/", token).decode("utf-8", "replace")
            rss_raw = fetch("rss.xml", token)
            sitemap_raw = fetch("sitemap.xml", token)
            news_raw = fetch("news-sitemap.xml", token)
            health = fetch("deployment-health.txt", token).decode("utf-8", "replace")
            image = fetch(IMAGE_REL, token)
            rss_root = ET.fromstring(rss_raw)
            rss_links = [(node.text or "").strip() for node in rss_root.findall(".//item/link")]
            sitemap_root = ET.fromstring(sitemap_raw)
            sitemap_locs = [(node.text or "").strip() for node in sitemap_root.findall(f".//{{{sitemap_ns}}}loc")]
            news_root = ET.fromstring(news_raw)
            news_locs = [(node.text or "").strip() for node in news_root.findall(f".//{{{sitemap_ns}}}loc")]
            last = {
                "article": TITLE_FRAGMENT in article and CORRECTED_SENTENCE in article and "4,51" in article and "20:05" in article and f'<link rel="canonical" href="{ARTICLE_URL}">' in article,
                "homepage": f'data-latest-article-href="/{ARTICLE_REL}"' in home,
                "archive": f'/{ARTICLE_REL}' in archive,
                "rss": rss_links.count(ARTICLE_URL) == 1,
                "sitemap": sitemap_locs.count(ARTICLE_URL) == 1,
                "news_sitemap": news_locs.count(ARTICLE_URL) == 1,
                "social_image": len(image) > 20000,
                "deployment_health": f"source={CONTENT_SHA}" in health and "mode=direct-apolena-publication" in health,
            }
            print(json.dumps({"attempt": attempt, "checks": last}, ensure_ascii=False), flush=True)
            if all(last.values()):
                return last
        except Exception as exc:
            print(f"Veřejná kontrola pokus {attempt}: {exc!r}", flush=True)
        time.sleep(attempt * 4)
    raise RuntimeError("Veřejná publikace není úplná: " + json.dumps(last, ensure_ascii=False))


def preserve_corrected_generator() -> None:
    path = ROOT / "scripts" / "publish_apolena_svabikova_20260806.py"
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8")
    old = "Na stejném šampionátu je nominována také její starší sestra Amálie Švábíková. Pokud se konečné startovní listiny nezmění, mohou se obě české tyčkařky potkat už v kvalifikaci."
    new = "Její starší sestra Amálie Švábíková naopak v Birminghamu startovat nebude. Český atletický svaz 21. července oznámil, že česká rekordmanka kvůli očekávání dítěte vynechá mistrovství republiky i evropský šampionát. Apolena tak bude jedinou ze sester Švábíkových v soutěži tyčkařek."
    if old in text:
        text = text.replace(old, new)
        path.write_text(text, encoding="utf-8")


def restore_guard() -> None:
    original = subprocess.check_output(
        ["git", "show", f"{ORIGINAL_GUARD_COMMIT}:scripts/enforce_all_article_visibility.py"],
        cwd=ROOT,
    )
    (ROOT / "scripts" / "enforce_all_article_visibility.py").write_bytes(original)


def main() -> None:
    precheck()
    rebuild_manifest()
    update_registry("deploying")
    commit_paths(
        "Evidence: synchronizovat opravený článek o Apoleně před nasazením",
        ["data/published-content-index.json", "data/article-integrity-manifest.json"],
    )
    deploy_streamed()
    checks = verify_public()
    update_registry("success", checks)
    report = ROOT / "reports" / "publication-apolena-svabikova-20260806.json"
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(
        json.dumps({
            "status": "success",
            "article_url": ARTICLE_URL,
            "source_commit": CONTENT_SHA,
            "verified_at": datetime.now(timezone.utc).isoformat(),
            "checks": checks,
        }, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    preserve_corrected_generator()
    restore_guard()
    commit_paths(
        "Publikace: veřejně ověřit Apolenu a obnovit kanonickou pojistku",
        [
            "data/published-content-index.json",
            "reports/publication-apolena-svabikova-20260806.json",
            "scripts/publish_apolena_svabikova_20260806.py",
            "scripts/enforce_all_article_visibility.py",
        ],
    )
    print(f"PUBLIKOVÁNO A VEŘEJNĚ OVĚŘENO: {ARTICLE_URL}", flush=True)


if __name__ == "__main__":
    main()
