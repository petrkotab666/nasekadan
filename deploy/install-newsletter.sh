#!/usr/bin/env bash
set -euo pipefail
APP_DIR=/opt/nasekadan
ENV_FILE=/etc/nasekadan-newsletter.env
sudo install -d -m 750 -o www-data -g www-data /var/lib/nasekadan-newsletter
sudo tee /etc/systemd/system/nasekadan-newsletter.service >/dev/null <<'EOF'
[Unit]
Description=Newsletter Naše Kadaň
After=network-online.target
Wants=network-online.target
[Service]
Type=simple
User=www-data
Group=www-data
EnvironmentFile=-/etc/nasekadan-newsletter.env
ExecStart=/usr/bin/python3 /opt/nasekadan/newsletter/server.py
Restart=on-failure
RestartSec=5
PrivateTmp=true
ProtectSystem=strict
ReadWritePaths=/var/lib/nasekadan-newsletter
NoNewPrivileges=true
[Install]
WantedBy=multi-user.target
EOF
if [[ ! -f "$ENV_FILE" ]]; then
 sudo tee "$ENV_FILE" >/dev/null <<'EOF'
NEWSLETTER_BASE_URL=https://nasekadan.cz
NEWSLETTER_FROM=info@nasekadan.cz
NEWSLETTER_DB=/var/lib/nasekadan-newsletter/newsletter.sqlite3
SMTP_HOST=
SMTP_PORT=587
SMTP_USER=
SMTP_PASSWORD=
SMTP_TLS=1
EOF
 sudo chmod 600 "$ENV_FILE"
fi
sudo tee /etc/caddy/sites-enabled/nasekadan.caddy >/dev/null <<'EOF'
nasekadan.cz, www.nasekadan.cz {
    handle_path /api/newsletter/* {
        reverse_proxy 127.0.0.1:8765
    }
    handle {
        root * /var/www/nasekadan
        file_server
        encode gzip zstd
    }
}
EOF
sudo systemctl daemon-reload
sudo systemctl enable --now nasekadan-newsletter.service
sudo caddy validate --config /etc/caddy/Caddyfile
sudo systemctl reload caddy
echo "Newsletter backend nainstalován. Doplňte SMTP údaje v $ENV_FILE a spusťte: sudo systemctl restart nasekadan-newsletter"
