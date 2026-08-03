"""One-shot safety shim for the scheduled FVE EPR publication.

The original workflow prepares the correct publication bundle but leaves unrelated
unstaged discovery changes behind, which prevents its later `git pull --rebase`.
During this one publication only, commit and push the explicitly approved bundle
at the end of enforce_article_visibility.py, then discard unrelated unstaged
changes so the workflow can continue with the canonical OVH deploy and checks.
"""
from __future__ import annotations

import atexit
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
TARGET_SCRIPT = "enforce_article_visibility.py"
TARGET_WORKFLOW = "Zveřejnit FVE EPR Letiště 3. 8. 2026 v 10:30"
FILES = [
    "clanky/fve-epr-letiste-bess-kadan-2026.html",
    "social/fve-epr-letiste-baterie-kadan-20260803.png",
    "index.html",
    "clanky/index.html",
    "rss.xml",
    "sitemap.xml",
    "news-sitemap.xml",
    "llms.txt",
]


def run(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        list(args), cwd=ROOT, text=True, check=check,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
    )


def finalize_publication_commit() -> None:
    if os.environ.get("GITHUB_ACTIONS") != "true":
        return
    if os.environ.get("GITHUB_WORKFLOW") != TARGET_WORKFLOW:
        return

    run("git", "config", "user.name", "Naše Kadaň publikační automat")
    run("git", "config", "user.email", "info@nasekadan.cz")
    run("git", "add", "-A", "--", *FILES)

    staged = run("git", "diff", "--cached", "--quiet", check=False)
    if staged.returncode == 0:
        return

    run("git", "commit", "-m", "Publikovat: solární park EPR Letiště a baterie")
    # prepare_discovery.py may touch unrelated pages. They are deliberately not
    # part of this publication bundle and must not block the clean rebase.
    run("git", "reset", "--hard", "HEAD")

    pushed = False
    for _ in range(5):
        pull = run("git", "pull", "--rebase", "origin", "main", check=False)
        if pull.returncode == 0:
            push = run("git", "push", "origin", "HEAD:main", check=False)
            if push.returncode == 0:
                pushed = True
                break
        run("git", "rebase", "--abort", check=False)
    if not pushed:
        raise SystemExit("Jednorázová pojistka nedokázala publikaci zapsat do main.")


if (
    Path(sys.argv[0]).name == TARGET_SCRIPT
    and os.environ.get("GITHUB_WORKFLOW") == TARGET_WORKFLOW
):
    atexit.register(finalize_publication_commit)
