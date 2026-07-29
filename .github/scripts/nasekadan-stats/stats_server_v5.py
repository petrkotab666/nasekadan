#!/usr/bin/env python3
from __future__ import annotations

import stats_metrics_v5
import stats_server as base

stats_metrics_v5.install(base)

# Kompatibilní trvalé rozšíření: i kdyby starší instalátor nebo systemd jednotka
# znovu spustily wrapper v5, dashboard, SQLite persistence a článkové statistiky
# v6 zůstanou aktivní. Chybějící v6 nesmí shodit nouzový původní přehled.
try:
    import stats_metrics_v6
except ImportError:
    stats_metrics_v6 = None

if stats_metrics_v6 is not None:
    stats_metrics_v6.install(base)

base.ThreadingHTTPServer((base.HOST, base.PORT), base.Handler).serve_forever()
