#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import sys
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

API = "https://api.github.com"


def request(method: str, path: str, token: str, payload: dict | None = None):
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    req = Request(
        API + path,
        data=data,
        method=method,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "NaseKadanIssueBridge/1.0",
            "Content-Type": "application/json",
        },
    )
    try:
        with urlopen(req, timeout=30) as response:
            raw = response.read().decode("utf-8")
            return json.loads(raw) if raw else None
    except HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"GitHub API {method} {path} selhalo: HTTP {exc.code}: {body}") from exc


def find_issue(repo: str, fingerprint: str, token: str):
    for page in range(1, 6):
        query = urlencode({"state": "all", "per_page": 100, "page": page, "sort": "updated", "direction": "desc"})
        items = request("GET", f"/repos/{repo}/issues?{query}", token) or []
        for item in items:
            if "pull_request" in item:
                continue
            if fingerprint in str(item.get("title", "")):
                return item
        if len(items) < 100:
            break
    return None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=os.environ.get("GITHUB_REPOSITORY", ""))
    parser.add_argument("--fingerprint", required=True)
    parser.add_argument("--title", required=True)
    parser.add_argument("--body-file", required=True)
    parser.add_argument("--assignee", default="petrkotab666")
    parser.add_argument("--close", action="store_true")
    parser.add_argument("--comment-existing", action="store_true")
    args = parser.parse_args()

    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if not token:
        print("Chybí GITHUB_TOKEN/GH_TOKEN.", file=sys.stderr)
        return 2
    if not args.repo:
        print("Chybí repository.", file=sys.stderr)
        return 2

    body = open(args.body_file, encoding="utf-8").read()
    issue = find_issue(args.repo, args.fingerprint, token)

    if args.close:
        if not issue:
            print("Issue k uzavření neexistuje.")
            return 0
        if args.comment_existing and body.strip():
            request("POST", f"/repos/{args.repo}/issues/{issue['number']}/comments", token, {"body": body})
        if issue.get("state") != "closed":
            issue = request("PATCH", f"/repos/{args.repo}/issues/{issue['number']}", token, {"state": "closed", "state_reason": "completed"})
        print(json.dumps({"number": issue["number"], "url": issue["html_url"], "state": issue["state"]}))
        return 0

    if issue:
        if issue.get("state") == "closed":
            issue = request("PATCH", f"/repos/{args.repo}/issues/{issue['number']}", token, {"state": "open"})
        if args.comment_existing and body.strip():
            request("POST", f"/repos/{args.repo}/issues/{issue['number']}/comments", token, {"body": body})
        print(json.dumps({"number": issue["number"], "url": issue["html_url"], "state": issue["state"], "existing": True}))
        return 0

    payload = {"title": args.title, "body": body}
    if args.assignee:
        payload["assignees"] = [args.assignee]
    issue = request("POST", f"/repos/{args.repo}/issues", token, payload)
    print(json.dumps({"number": issue["number"], "url": issue["html_url"], "state": issue["state"], "existing": False}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
