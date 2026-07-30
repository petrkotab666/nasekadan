#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys

sys.path.insert(0, "/opt/nasekadan/.github/scripts/nasekadan-stats")
sys.path.insert(1, "/usr/local/lib/nasekadan-stats")

import stats_metrics_v5
import stats_metrics_v6
import stats_metrics_v7
import stats_server as base

stats_metrics_v5.install(base)
stats_metrics_v6.install(base)
stats_metrics_v7.install(base)

body = base.render_dashboard().decode("utf-8", "replace")
recent = stats_metrics_v7.latest_published_articles()
assert len(recent) == 25, f"Očekáváno 25 článků, nalezeno {len(recent)}"
assert "Posledních 25 článků" in body

table = re.search(r'<table id="recent-articles">(.*?)</table>', body, re.S)
assert table, "Tabulka recent-articles chybí"
row_count = table.group(1).count("<tr>") - 1
assert row_count == 25, f"Očekáváno 25 řádků, nalezeno {row_count}"

pages = stats_metrics_v6.normalize_counter(stats_metrics_v6.read_persisted().get("pages"))
output = [
    {
        "published": item["published"].isoformat(),
        "path": item["path"],
        "title": item["title"],
        "views": pages.get(item["path"], 0),
    }
    for item in recent
]
print(json.dumps({"ok": True, "count": len(output), "articles": output}, ensure_ascii=False))
