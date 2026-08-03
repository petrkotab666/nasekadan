#!/usr/bin/env bash
set -euo pipefail

SERVICE=/etc/systemd/system/nasekadan-weather.service
TIMER=/etc/systemd/system/nasekadan-weather.timer

sudo tee "$SERVICE" >/dev/null <<'UNIT'
[Unit]
Description=Aktualizace počasí pro Naše Kadaň
After=network-online.target docker.service
Wants=network-online.target
Requires=docker.service

[Service]
Type=oneshot
WorkingDirectory=/opt/nasekadan
ExecStart=/usr/bin/bash /opt/nasekadan/deploy/update-weather-data.sh
TimeoutStartSec=240
Nice=10

[Install]
WantedBy=multi-user.target
UNIT

sudo tee "$TIMER" >/dev/null <<'UNIT'
[Unit]
Description=Aktualizovat počasí Naše Kadaň každých deset minut

[Timer]
OnBootSec=45s
OnUnitActiveSec=10min
AccuracySec=30s
Persistent=true
Unit=nasekadan-weather.service

[Install]
WantedBy=timers.target
UNIT

sudo chmod +x /opt/nasekadan/deploy/update-weather-data.sh
sudo systemctl daemon-reload
sudo systemctl enable --now nasekadan-weather.timer
sudo systemctl start nasekadan-weather.service
sudo systemctl --no-pager --full status nasekadan-weather.service || true
sudo systemctl --no-pager --full status nasekadan-weather.timer || true
