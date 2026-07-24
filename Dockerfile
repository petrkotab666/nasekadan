FROM nginx:1.27-alpine
COPY nginx/default.conf /etc/nginx/conf.d/default.conf
COPY . /usr/share/nginx/html

# Mobilní pravidla přidat přímo do hlavního CSS. Tím nejsou závislá na načtení dalšího souboru.
RUN printf '\n\n/* Mobilní pravidla vložená při produkčním sestavení */\n' >> /usr/share/nginx/html/style.css \
 && cat /usr/share/nginx/html/mobile.css >> /usr/share/nginx/html/style.css

# Na všech stránkách vynutit stažení nové verze hlavního CSS a JavaScriptu bez staré cache.
RUN find /usr/share/nginx/html -type f -name '*.html' -exec sed -i \
  -e 's#style.css"#style.css?v=20260724-mobile-2"#g' \
  -e 's#site.js"#site.js?v=20260724-mobile-2"#g' {} +

# Připravit nemocniční článek k prvnímu vydání 24. 7. 2026.
RUN sed -i \
  -e 's#ZDRAVOTNICTVÍ · KOMUNÁLNÍ POLITIKA · AKTUALIZOVÁNO 23. ČERVENCE 2026#ZDRAVOTNICTVÍ · KOMUNÁLNÍ POLITIKA · 24. ČERVENCE 2026#g' \
  -e 's#<p class="updated">Aktualizováno: 23. 7. 2026</p>#<p class="updated">Publikováno: 24. 7. 2026</p>#g' \
  -e 's#"datePublished":"2026-07-23"#"datePublished":"2026-07-24"#g' \
  -e 's#"dateModified":"2026-07-23"#"dateModified":"2026-07-24"#g' \
  -e 's#Stav informací k 23. červenci 2026.#Stav informací k 24. červenci 2026.#g' \
  /usr/share/nginx/html/clanky/nemocnice-kadan.html

RUN rm -rf /usr/share/nginx/html/.git /usr/share/nginx/html/.github /usr/share/nginx/html/nginx /usr/share/nginx/html/Dockerfile /usr/share/nginx/html/docker-compose.yml
EXPOSE 80
HEALTHCHECK --interval=30s --timeout=3s --retries=3 CMD wget -qO- http://127.0.0.1/healthz || exit 1