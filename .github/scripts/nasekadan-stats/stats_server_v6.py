#!/usr/bin/env python3
from __future__ import annotations

import sys

sys.path.insert(0, "/opt/nasekadan/.github/scripts/nasekadan-stats")

import stats_metrics_v5
import stats_metrics_v6
import stats_metrics_v7
import stats_metrics_v8
import stats_metrics_v9
import stats_server as base

stats_metrics_v5.install(base)
stats_metrics_v6.install(base)
stats_metrics_v7.install(base)
stats_metrics_v9.install(base)
stats_metrics_v8.install(base)
base.ThreadingHTTPServer((base.HOST, base.PORT), base.Handler).serve_forever()
