#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.request
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SLUG = "apolena-svabikova-mistrovstvi-evropy-birmingham-2026"
ARTICLE_REL = f"clanky/{SLUG}.html"
ARTICLE = ROOT / ARTICLE_REL
URL = f"https://nasekadan.cz/{ARTICLE_REL}"
TITLE_FRAGMENT = "Kadaňská tyčkařka Apolena Švábíková míří na první seniorské ME"
ORIGINAL_GUARD_COMMIT = "70dd13c09d6d96927d8cb4db3324a76d548c13c9"


def run(command: list[str], *, check: bool = True, cwd: Path = ROOT, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    print("+", " ".join(command), flush=True)
    return subprocess.run(command, cwd=cwd, env=env, check=check, text=True)


def output(command: list[str], *, cwd: Path = ROOT) -> str:
    return subprocess.check_output(command, cwd=cwd, text=True).strip()


def push_with_retry() -> None:
    for attempt in range(1, 5):
        result = subprocess.run(["git", "push", "origin", "HEAD:main"], cwd=ROOT, text=True)
        if result.returncode == 0:
            return
        if attempt == 4:
            raise RuntimeError("Nepodařilo se uložit publikační commit do main.")
        run(["git", "pull", "--rebase", "origin", "main"])
        time.sleep(attempt * 2)


def commit_paths(message: str, paths: list[str]) -> str:
    run(["git", "add", "--", *paths])
    changed = subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=ROOT).returncode != 0
    if changed:
        run(["git", "commit", "-m", message])
        push_with_retry()
    return output(["git", "rev-parse", "HEAD"])


def install_pillow() -> None:
    try:
        import PIL  # noqa: F401
        return
    except ImportError:
        pass
    run([sys.executable, "-m", "pip", "install", "--quiet", "Pillow"])


def prepare_source() -> str:
    install_pillow()
    env = os.environ.copy()
    env["ARTICLE_SOURCE_COMMIT"] = output(["git", "rev-parse", "HEAD"])
    run([sys.executable, "scripts/publish_apolena_svabikova_20260806.py"], env=env)
    paths = [
        ARTICLE_REL,
        f"social/{SLUG}.png",
        "index.html",
        "clanky/index.html",
        "rss.xml",
        "sitemap.xml",
        "news-sitemap.xml",
        "llms.txt",
        "data/published-content-index.json",
        "data/article-integrity-manifest.json",
    ]
    paths.extend(sorted(path.relative_to(ROOT).as_posix() for path in (ROOT / "clanky").glob("strana-*.html")))
    return commit_paths("Publikovat Apolenu Švábíkovou na seniorském ME", paths)


def update_source_commit(content_sha: str) -> str:
    registry = ROOT / "data" / "published-content-index.json"
    data = json.loads(registry.read_text(encoding="utf-8"))
    for item in data.get("articles", []):
        if item.get("url") == URL:
            item["source_commit"] = content_sha
            break
    else:
        raise RuntimeError("Článek Apoleny chybí v kanonickém registru.")
    data["source_commit"] = content_sha
    data["generated_at"] = datetime.now(timezone.utc).isoformat()
    validation = data.setdefault("validation", {})
    validation["repair_pending_public_verification"] = True
    last = validation.setdefault("last_publication", {})
    last.update({"status": "deploying", "article_url": URL, "source_commit": content_sha, "public_verified_at": None})
    registry.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    health = ROOT / "deployment-health.txt"
    health.write_text(
        "site=nasekadan.cz\n"
        f"source={content_sha}\n"
        f"generated={datetime.now(timezone.utc).isoformat()}\n"
        "mode=direct-apolena-publication\n",
        encoding="utf-8",
    )
    return commit_paths("Evidence: přiřadit zdrojový commit článku o Apoleně", ["data/published-content-index.json", "deployment-health.txt"])


def prepare_bundle() -> Path:
    bundle = Path(tempfile.mkdtemp(prefix="apolena-publish-"))
    for name in ["index.html", "rss.xml", "sitemap.xml", "news-sitemap.xml", "llms.txt", "deployment-health.txt"]:
        shutil.copy2(ROOT / name, bundle / name)
    (bundle / "clanky").mkdir()
    (bundle / "social").mkdir()
    shutil.copy2(ARTICLE, bundle / ARTICLE_REL)
    shutil.copy2(ROOT / "clanky" / "index.html", bundle / "clanky" / "index.html")
    for page in sorted((ROOT / "clanky").glob("strana-*.html")):
        shutil.copy2(page, bundle / "clanky" / page.name)
    shutil.copy2(ROOT / "social" / f"{SLUG}.png", bundle / "social" / f"{SLUG}.png")
    return bundle


def ssh_base(key_path: Path) -> list[str]:
    return [
        "ssh", "-i", str(key_path), "-o", "BatchMode=yes",
        "-o", "StrictHostKeyChecking=accept-new", "-o", "ConnectTimeout=25",
        "ubuntu@57.129.43.215",
    ]


def deploy_streamed() -> None:
    key = os.environ.get("OVH_KEY_A") or os.environ.get("OVH_KEY_B") or os.environ.get("SSH_KEY")
    if not key:
        raise RuntimeError("Publikační běh nemá dostupný SSH klíč pro OVH.")
    key_path = Path(tempfile.mkstemp(prefix="ovh-key-")[1])
    key_path.write_text(key.replace("\r", "").rstrip() + "\n", encoding="utf-8")
    key_path.chmod(0o600)
    bundle = prepare_bundle()
    try:
        cleanup = r'''set -euo pipefail
sudo rm -rf /tmp/article-order* /tmp/eso-direct* /tmp/eso-market* /tmp/apolena* /tmp/nasekadan-deploy* 2>/dev/null || true
avail=$(df -Pk / | awk 'NR==2 {print $4}')
if [ "${avail:-0}" -lt 102400 ]; then
  sudo docker builder prune -af >/dev/null 2>&1 || true
  sudo journalctl --vacuum-size=100M >/dev/null 2>&1 || true
fi
sudo install -d -m 0755 /var/www/nasekadan /var/www/nasekadan/clanky /var/www/nasekadan/social
'''
        run([*ssh_base(key_path), "bash", "-lc", cleanup])

        remote = f'''set -euo pipefail
root=/var/www/nasekadan
sudo tar -xzf - -C "$root"
sudo chmod -R a+rX "$root"
if sudo docker inspect nasekadan-web >/dev/null 2>&1; then
  sudo docker exec nasekadan-web mkdir -p /usr/share/nginx/html/clanky /usr/share/nginx/html/social
  for f in index.html rss.xml sitemap.xml news-sitemap.xml llms.txt deployment-health.txt; do
    sudo docker cp "$root/$f" "nasekadan-web:/usr/share/nginx/html/$f"
  done
  sudo docker cp "$root/clanky/{SLUG}.html" "nasekadan-web:/usr/share/nginx/html/clanky/{SLUG}.html"
  sudo docker cp "$root/clanky/index.html" nasekadan-web:/usr/share/nginx/html/clanky/index.html
  for f in "$root"/clanky/strana-*.html; do
    [ -e "$f" ] || continue
    sudo docker cp "$f" "nasekadan-web:/usr/share/nginx/html/clanky/$(basename "$f")"
  done
  sudo docker cp "$root/social/{SLUG}.png" "nasekadan-web:/usr/share/nginx/html/social/{SLUG}.png"
fi
'''
        tar = subprocess.Popen(["tar", "-C", str(bundle), "-czf", "-", "."], stdout=subprocess.PIPE)
        assert tar.stdout is not None
        ssh = subprocess.run([*ssh_base(key_path), "bash", "-lc", remote], stdin=tar.stdout)
        tar.stdout.close()
        tar_code = tar.wait()
        if tar_code != 0 or ssh.returncode != 0:
            raise RuntimeError(f"Přímé proudové nasazení selhalo: tar={tar_code}, ssh={ssh.returncode}")
    finally:
        shutil.rmtree(bundle, ignore_errors=True)
        key_path.unlink(missing_ok=True)


def fetch(path: str, token: str) -> bytes:
    separator = "&" if "?" in path else "?"
    request = urllib.request.Request(
        "https://nasekadan.cz/" + path + separator + "verify=" + token,
        headers={"User-Agent": "Naše Kadaň Apolena publication verifier/1.0"},
    )
    with urllib.request.urlopen(request, timeout=45) as response:
        return response.read()


def public_verify(content_sha: str) -> dict[str, bool]:
    last: dict[str, bool] = {}
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
            image = fetch(f"social/{SLUG}.png", token)
            rss_root = ET.fromstring(rss_raw)
            rss_links = [(node.text or "").strip() for node in rss_root.findall(".//item/link")]
            sitemap_root = ET.fromstring(sitemap_raw)
            sitemap_locs = [(node.text or "").strip() for node in sitemap_root.findall("{http://www.sitemaps.org/schemas/sitemap/0.9}url/{http://www.sitemaps.org/schemas/sitemap/0.9}loc")]
            news_root = ET.fromstring(news_raw)
            news_locs = [(node.text or "").strip() for node in news_root.findall("{http://www.sitemaps.org/schemas/sitemap/0.9}url/{http://www.sitemaps.org/schemas/sitemap/0.9}loc")]
            last = {
                "article": TITLE_FRAGMENT in article and "4,51" in article and "20:05" in article and f'<link rel="canonical" href="{URL}">' in article,
                "homepage": f'data-latest-article-href="/clanky/{SLUG}.html"' in home,
                "archive": f'/clanky/{SLUG}.html' in archive,
                "rss": rss_links.count(URL) == 1,
                "sitemap": sitemap_locs.count(URL) == 1,
                "news_sitemap": news_locs.count(URL) == 1,
                "social_image": len(image) > 20000,
                "deployment_health": "mode=direct-apolena-publication" in health and f"source={content_sha}" in health,
            }
            print(json.dumps({"attempt": attempt, "checks": last}, ensure_ascii=False), flush=True)
            if all(last.values()):
                return last
        except Exception as exc:
            print(f"Veřejná kontrola pokus {attempt}: {exc!r}", flush=True)
        time.sleep(attempt * 4)
    raise RuntimeError("Veřejná publikace nebyla úplná: " + json.dumps(last, ensure_ascii=False))


def close_registry(content_sha: str, checks: dict[str, bool]) -> None:
    now = datetime.now(timezone.utc).isoformat()
    registry = ROOT / "data" / "published-content-index.json"
    data = json.loads(registry.read_text(encoding="utf-8"))
    validation = data.setdefault("validation", {})
    validation["repair_pending_public_verification"] = False
    validation["public_audit_at"] = now
    validation["last_publication"] = {
        "status": "success",
        "checked_at": now,
        "article_url": URL,
        "classification": "local_athlete_european_championship",
        "source_commit": content_sha,
        "public_verified_at": now,
        "public_verification": checks | {"registry": True},
    }
    data["generated_at"] = now
    registry.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report = ROOT / "reports" / "publication-apolena-svabikova-20260806.json"
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(json.dumps({"status": "success", "article_url": URL, "source_commit": content_sha, "verified_at": now, "checks": checks}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    commit_paths("Evidence: veřejně ověřit článek o Apoleně Švábíkové", ["data/published-content-index.json", "reports/publication-apolena-svabikova-20260806.json"])


def restore_guard() -> None:
    guard = ROOT / "scripts" / "enforce_all_article_visibility.py"
    original = subprocess.check_output(["git", "show", f"{ORIGINAL_GUARD_COMMIT}:scripts/enforce_all_article_visibility.py"], cwd=ROOT)
    guard.write_bytes(original)
    commit_paths("Obnovit kanonickou pojistku po jednorázové publikaci Apoleny", ["scripts/enforce_all_article_visibility.py"])


def run_bootstrap() -> None:
    # Po úspěšné publikaci je běh idempotentní a už nic znovu nevytváří.
    report = ROOT / "reports" / "publication-apolena-svabikova-20260806.json"
    if ARTICLE.exists() and report.exists():
        print("Apolena je už zdrojově i veřejně evidována; bootstrap se přeskakuje.")
        return
    content_sha = prepare_source()
    update_source_commit(content_sha)
    deploy_streamed()
    checks = public_verify(content_sha)
    close_registry(content_sha, checks)
    restore_guard()
    print(f"PUBLIKOVÁNO A VEŘEJNĚ OVĚŘENO: {URL}")
