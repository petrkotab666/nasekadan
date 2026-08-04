#!/usr/bin/env bash
set -euo pipefail

MODE="${1:?Použití: commit_monitoring_state.sh urgent|hourly|daily}"
case "$MODE" in
  urgent|hourly|daily) ;;
  *) echo "Neplatná vrstva: $MODE" >&2; exit 2 ;;
esac

git config user.name 'github-actions[bot]'
git config user.email '41898282+github-actions[bot]@users.noreply.github.com'
git add \
  data/monitoring-registry.json \
  "data/monitoring-state-${MODE}.json" \
  "data/monitoring-status-${MODE}.json"

if git diff --cached --quiet; then
  echo "Jednotný monitoring ${MODE}: bez strukturální změny stavu."
  exit 0
fi

git commit -m "Aktualizovat jednotný monitoring Kadaňska: ${MODE} [skip ci]"
for attempt in 1 2 3 4 5; do
  if git pull --rebase origin main && git push origin HEAD:main; then
    exit 0
  fi
  echo "Pokus ${attempt} o uložení stavu vrstvy ${MODE} selhal; opakuji." >&2
  git rebase --abort 2>/dev/null || true
  sleep $((attempt * 3))
done

echo "Stav vrstvy ${MODE} se nepodařilo bezpečně uložit." >&2
exit 1
