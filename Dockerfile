FROM nginx:1.27-alpine
COPY nginx/default.conf /etc/nginx/conf.d/default.conf
COPY . /usr/share/nginx/html
# Upravit datum článku jako datum prvního vydání a vynutit načtení aktuálního site.js bez cache.
RUN find /usr/share/nginx/html -type f -name '*.html' -exec sed -i \
  -e 's#ZDRAVOTNICTVÍ · KOMUNÁLNÍ POLITIKA · AKTUALIZOVÁNO 23. ČERVENCE 2026#ZDRAVOTNICTVÍ · KOMUNÁLNÍ POLITIKA · 23. ČERVENCE 2026#g' \
  -e 's#<p class="updated">Aktualizováno: 23. 7. 2026</p>#<p class="updated">Publikováno: 23. 7. 2026</p>#g' \
  -e 's#<script src="/site.js" defer></script>#<script src="/site.js?v=20260723-petice-4" defer></script>#g' {} +
RUN rm -rf /usr/share/nginx/html/.git /usr/share/nginx/html/.github /usr/share/nginx/html/nginx /usr/share/nginx/html/Dockerfile /usr/share/nginx/html/docker-compose.yml
EXPOSE 80
HEALTHCHECK --interval=30s --timeout=3s --retries=3 CMD wget -qO- http://127.0.0.1/healthz || exit 1
