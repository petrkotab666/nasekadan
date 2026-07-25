FROM python:3.12-alpine AS discovery
WORKDIR /site
COPY . .

# Při každém sestavení vytvořit a doplnit strojově čitelné podklady pro
# vyhledávače, Google News a odpovědi AI. Skript zachovává individuální OG
# obrázky a metadata jednotlivých článků.
RUN python scripts/prepare_discovery.py


FROM nginx:1.27-alpine
COPY nginx/default.conf /etc/nginx/conf.d/default.conf
COPY --from=discovery /site /usr/share/nginx/html
COPY docker-entrypoint.d/40-indexnow.sh /docker-entrypoint.d/40-indexnow.sh
RUN chmod +x /docker-entrypoint.d/40-indexnow.sh


# Mobilní pravidla přidat přímo do hlavního CSS. Tím nejsou závislá na načtení dalšího souboru.
RUN printf '\n\n/* Mobilní pravidla vložená při produkčním sestavení */\n' >> /usr/share/nginx/html/style.css \
 && cat /usr/share/nginx/html/mobile.css >> /usr/share/nginx/html/style.css

# Na všech stránkách vynutit stažení nové verze hlavního CSS a JavaScriptu bez staré cache.
# Současně do každé HTML stránky vložit jednotnou navigaci, patičku, časované upoutávky a opravu nedostupných reklamních obrázků.
RUN find /usr/share/nginx/html -type f -name '*.html' -exec sed -i \
  -e 's#style.css"#style.css?v=20260724-mobile-2"#g' \
  -e 's#site.js"#site.js?v=20260724-nemocnice-7"#g' \
  -e 's#reklamy\.js[^\"]*"#reklamy.js?v=20260725-travel-ads-1"#g' \
  -e 's#</body>#<script src="/navigation.js?v=20260725-inzerce-footer-2" defer></script><script src="/upoutavky.js?v=20260724-nemocnice-cyber-1" defer></script><script src="/reklamy-oprava-obrazku.js?v=20260725-travel-image-fallback-6" defer></script></body>#g' {} +

# Zkopírovat neveřejný redakční návrh KZK do heslem chráněné sekce /nahled/.
RUN mkdir -p /usr/share/nginx/html/nahled \
 && cp /usr/share/nginx/html/.github/drafts/kulturni-zarizeni-kadan.html \
       /usr/share/nginx/html/nahled/kulturni-zarizeni-kadan-8c7f3e.html

RUN rm -rf /usr/share/nginx/html/.git \
           /usr/share/nginx/html/.github \
           /usr/share/nginx/html/.image-parts \
           /usr/share/nginx/html/docker-entrypoint.d \
           /usr/share/nginx/html/nginx \
           /usr/share/nginx/html/scripts \
           /usr/share/nginx/html/tools \
           /usr/share/nginx/html/Dockerfile \
           /usr/share/nginx/html/docker-compose.yml

EXPOSE 80
HEALTHCHECK --interval=30s --timeout=3s --retries=3 CMD wget -qO- http://127.0.0.1/healthz || exit 1
