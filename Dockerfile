FROM python:3.12-alpine AS discovery
WORKDIR /site
COPY . .

# Pillow je potřeba pro jedinečné 1200×630 sociální obrázky jednotlivých článků.
# Instalace přes pip zaručí, že se knihovna nahraje do stejného Pythonu 3.12,
# ve kterém následně běží generátor obrázků.
RUN pip install --no-cache-dir Pillow

# Každá veřejná stránka musí mít už ve statickém HTML stejnou patičku a stejný
# footer.css. JavaScript je pouze druhá pojistka, ne podmínka správného vzhledu.
RUN python scripts/normalize_footers.py --write --check

# Každý článek musí před sestavením projít jedinou společnou konstrukcí.
# Normalizátor sjednotí article-shell, přímý pravý panel, reklamní slot i skripty
# a následná kontrola zastaví build, pokud by některý článek pravidlo porušil.
RUN python scripts/normalize_articles.py --write --check

# Každý článek dostane vlastní Facebook/OG obrázek s novou URL odvozenou
# z názvu a metadat. Generický social-card.png se u článků nepoužívá.
RUN python scripts/generate_social_cards.py --write --check

# Při každém sestavení vytvořit a doplnit strojově čitelné podklady pro
# vyhledávače, Google News a odpovědi AI. Skript zachovává individuální OG
# obrázky a metadata jednotlivých článků.
RUN python scripts/prepare_discovery.py

# Zkrátit nevhodně dlouhé titulky, doplnit popisy a přesné časové značky článků.
RUN python scripts/normalize_search_snippets.py

# Kritická SEO/AI chyba musí zastavit sestavení ještě před přepnutím produkce.
RUN python scripts/seo_ai_audit.py --strict

# Ověření vlastnictví služby https://nasekadan.cz/ v Google Search Console.
# Značka musí zůstat v produkčním <head>, jinak se vlastnictví časem ztratí.
RUN sed -i 's#<head>#<head>\n  <meta name="google-site-verification" content="bFnU5Qjvk0Y52HY6N4d-b9_yy_IZ8DkY5LkoQsLAk8M">#' /site/index.html


FROM nginx:1.27-alpine
COPY nginx/default.conf /etc/nginx/conf.d/default.conf
COPY --from=discovery /site /usr/share/nginx/html
COPY docker-entrypoint.d/40-indexnow.sh /docker-entrypoint.d/40-indexnow.sh
RUN chmod +x /docker-entrypoint.d/40-indexnow.sh


# Mobilní pravidla přidat přímo do hlavního CSS. Tím nejsou závislá na načtení dalšího souboru.
RUN printf '\n\n/* Mobilní pravidla vložená při produkčním sestavení */\n' >> /usr/share/nginx/html/style.css \
 && cat /usr/share/nginx/html/mobile.css >> /usr/share/nginx/html/style.css

# Reklamní balík už vložil jediný normalizátor článků. Zde se upravují pouze
# obecné soubory webu a jednou se doplní navigace a upoutávky.
RUN find /usr/share/nginx/html -type f -name '*.html' -exec sed -i \
  -e 's#style.css"#style.css?v=20260724-mobile-2"#g' \
  -e 's#site.js"#site.js?v=20260724-nemocnice-7"#g' \
  -e 's#<script src="[^"]*navigation\.js[^"]*"[^>]*></script>##g' \
  -e 's#<script src="[^"]*upoutavky\.js[^"]*"[^>]*></script>##g' \
  -e 's#</body>#<script src="/navigation.js?v=20260726-unified-footer-1" defer></script><script src="/upoutavky.js?v=20260724-nemocnice-cyber-1" defer></script></body>#g' {} +

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
