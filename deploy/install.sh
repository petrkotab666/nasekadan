#!/usr/bin/env bash
set -euo pipefail

REPO_URL="https://github.com/petrkotab666/nasekadan.git"
APP_DIR="/opt/nasekadan"
WEB_DIR="/var/www/nasekadan"
SITE_CONF="/etc/nginx/sites-available/nasekadan.cz"

export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get install -y nginx git rsync curl certbot python3-certbot-nginx

if [ -d "$APP_DIR/.git" ]; then
  git -C "$APP_DIR" fetch origin main
  git -C "$APP_DIR" reset --hard origin/main
else
  rm -rf "$APP_DIR"
  git clone --depth 1 "$REPO_URL" "$APP_DIR"
fi

mkdir -p "$WEB_DIR"
rsync -a --delete \
  --exclude '.git' \
  --exclude '.github' \
  --exclude 'deploy' \
  --exclude 'Dockerfile' \
  --exclude 'docker-compose.yml' \
  --exclude 'nginx' \
  "$APP_DIR/" "$WEB_DIR/"

cat > "$SITE_CONF" <<'NGINX'
server {
    listen 80;
    listen [::]:80;
    server_name nasekadan.cz www.nasekadan.cz;

    root /var/www/nasekadan;
    index index.html;
    charset utf-8;

    location / {
        try_files $uri $uri/ $uri.html =404;
    }

    location = /healthz {
        access_log off;
        add_header Content-Type text/plain;
        return 200 'ok';
    }

    location ~* \.(css|js|jpg|jpeg|png|webp|svg|ico)$ {
        expires 7d;
        add_header Cache-Control "public, max-age=604800";
    }

    gzip on;
    gzip_types text/plain text/css application/javascript application/json image/svg+xml;
}
NGINX

rm -f /etc/nginx/sites-enabled/default
ln -sfn "$SITE_CONF" /etc/nginx/sites-enabled/nasekadan.cz
nginx -t
systemctl enable nginx
systemctl reload nginx

if curl -fsS --max-time 10 http://nasekadan.cz/healthz >/dev/null 2>&1; then
  certbot --nginx --non-interactive --agree-tos --redirect \
    -m admin@nasekadan.cz \
    -d nasekadan.cz -d www.nasekadan.cz || true
fi

echo "Naše Kadaň je nasazena. Ověření: http://nasekadan.cz/healthz"
