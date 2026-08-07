FROM python:3.12-alpine AS discovery
WORKDIR /site
COPY . .

# Texty bez výslovného souhlasu editora nesmějí vstoupit do veřejného sestavení.
RUN python scripts/remove_unpublished_articles.py

# Schválený článek AVIES už nesmí záviset na zmeškaném GitHub plánu.
# Skript vytvoří veřejnou verzi přímo z redakčního návrhu ještě před normalizací.
RUN python scripts/publish_avies_article.py

# MONOTONIC-PUBLICATION-GUARD-V1
# Po odstranění explicitně neschválených textů uložit neměnný vstupní otisk všech
# již publikovaných článků. Každý pozdější krok buildu musí tuto množinu zachovat.
RUN python scripts/verify_published_article_set.py \
    --source . \
    --write-manifest /tmp/published-before-build.json \
    --write-manifest-only

# Online petice byla spuštěna na soukromém portálu e-petice.cz. Článek musí
# staticky rozlišit tuto platformu od státní ePetice v Portálu občana.
RUN python scripts/update_online_petition_status.py
RUN python scripts/update_petition_verified_details.py

# Pillow je potřeba pro jedinečné 1200×630 sociální obrázky jednotlivých článků.
# Instalace přes pip zaručí, že se knihovna nahraje do stejného Pythonu 3.12,
# ve kterém následně běží generátor obrázků.
RUN pip install --no-cache-dir Pillow

# Původní facebookové SVG obálky obsahovaly malé rastrové náhledy a jeden z nich
# některé prohlížeče vůbec nevykreslily. Při sestavení je proto převést na ostré,
# samostatné WebP soubory a přepsat na ně odkazy v článku.
RUN python scripts/prepare_kos_sharp_images.py

# Každá veřejná stránka musí mít už ve statickém HTML stejnou patičku a stejný
# footer.css. JavaScript je pouze druhá pojistka, ne podmínka správného vzhledu.
RUN python scripts/normalize_footers.py --write --check

# Každý článek musí před sestavením projít jedinou společnou konstrukcí.
# Normalizátor sjednotí article-shell, přímý pravý panel, reklamní slot i skripty
# a následná kontrola zastaví build, pokud by některý článek pravidlo porušil.
RUN python scripts/normalize_articles.py --write --check

# Sezónní blok pro horké dny patří pouze do veřejných článků. Zároveň sjednotit
# cache verzi hlavního letního reklamního balíku na všech stránkách.
RUN python scripts/enable_heat_feed.py
RUN python scripts/ensure_summer_ad_rotation.py --write --check

# Každý článek dostane vlastní Facebook/OG obrázek s novou URL odvozenou
# z názvu a metadat. Generický social-card.png se u článků nepoužívá.
RUN python scripts/generate_social_cards.py --write --check
RUN python scripts/harden_facebook_meta.py --write --check

# Nejnovější týdenní přehled akcí se automaticky stane hlavním článkem,
# zapíše se do archivu, RSS a sitemap. Skript používá metadata přímo z článku.
RUN python scripts/publish_weekly_events.py

# AVIES vyšel později než týdenní přehled. Druhý idempotentní běh ho proto
# vrátí na správné první místo a do RSS zapíše už vygenerovaný OG obrázek.
RUN python scripts/publish_avies_article.py

# Publikační skripty mohly znovu sestavit archiv nebo kartu na titulce. Proto
# stav online petice promítnout ještě jednou do všech výsledných přehledů.
RUN python scripts/update_online_petition_status.py
RUN python scripts/update_petition_verified_details.py

# Všechny dnešní schválené články musejí být chronologicky na titulce, v archivu
# a RSS ještě před generováním sitemapy a před blokujícím auditem.
RUN python scripts/enforce_current_article_order.py

# Starý AVIES publikátor mohl vedle automatické karty vložit ještě druhou ruční.
# Před auditem proto musí na titulce i v archivu zůstat právě jedna karta článku.
RUN python scripts/dedupe_avies_cards.py

# Doplnit canonical, robots, Open Graph a Twitter metadata také všem starším
# průvodcovským stránkám. Přísný audit tak neblokuje nové články kvůli historickým
# souborům, kterým metadata dříve chyběla.
RUN python scripts/finalize_launch.py

# Publikační kroky výše mohly přepsat konstrukci některého článku nebo titulky.
# Letní rotaci proto obnovit ještě jednou těsně před vyhledávacími audity.
RUN python scripts/normalize_articles.py --write --check
RUN python scripts/enable_heat_feed.py
RUN python scripts/ensure_summer_ad_rotation.py --write --check

# Blokující kontrola reklamních podkladů: build nesmí projít s historickým feedem,
# starým JS ani neúplným seznamem cestovních a letních partnerů.
RUN python -m json.tool assets/affiliate-site-travel-overlay.json >/dev/null \
 && grep -Fq 'reklamy-oprava-obrazku.js?v=20260730-pojistime-rotation-4' index.html \
 && grep -Fq 'reklamy-oprava-obrazku.js?v=20260730-pojistime-rotation-4' clanky/kadan-tropicke-dny-koupaliste-cervenec-2026.html \
 && grep -Fq 'horko-feed.js?v=20260730-heat-rotation-1' clanky/kadan-tropicke-dny-koupaliste-cervenec-2026.html \
 && ! grep -Fq 'lastminuteslevy-cz' reklamy-oprava-obrazku.js \
 && grep -Fq 'apollostore-cz' reklamy-oprava-obrazku.js \
 && grep -Fq 'installFeaturedSeasonalBanner' reklamy-oprava-obrazku.js \
 && grep -Fq 'horko-apollostore' horko-feed.js \
 && grep -Fq 'rotatingItems' horko-feed.js \
 && grep -Fq 'ceskekormidlo-cz' assets/affiliate-site-travel-overlay.json \
 && grep -Fq 'proalergiky-cz' assets/affiliate-site-travel-overlay.json

# Neveřejné rešeršní exporty a pracovní kopie dokumentů nesmějí vstoupit do
# sitemapy, SEO auditu ani výsledného produkčního obrazu.
RUN rm -rf research

# Při každém sestavení vytvořit a doplnit strojově čitelné podklady pro
# vyhledávače, Google News a odpovědi AI. Skript zachovává individuální OG
# obrázky a metadata jednotlivých článků.
RUN python scripts/prepare_discovery.py

# Zkrátit nevhodně dlouhé titulky, doplnit popisy a přesné časové značky článků.
RUN python scripts/normalize_search_snippets.py

# Fragmenty článků a ověřovací HTML Googlu nejsou samostatné veřejné stránky.
# Generátory je proto před auditem odstraní z hlavní sitemapy.
RUN python scripts/clean_sitemap_technical_entries.py

RUN python scripts/harden_facebook_meta.py --write --check

# MONOTONIC-PUBLICATION-GUARD-V1
# Kandidát buildu musí stále obsahovat úplně všechny články z předbuildového
# manifestu a zároveň musí mít úplné přehledy pro všechny aktuálně publikované
# texty. Při ztrátě jediného článku Docker build okamžitě končí chybou.
RUN python scripts/verify_published_article_set.py \
      --target . --manifest /tmp/published-before-build.json \
 && python scripts/verify_published_article_set.py \
      --source . --target . --write-manifest published-articles-manifest.json

# Kritická SEO/AI chyba musí zastavit sestavení ještě před přepnutím produkce.
# Stránkované archivní stránky jsou webové přehledy, nikoli NewsArticle.
RUN python scripts/seo_ai_audit_runtime.py --strict

# Ověření vlastnictví služby https://nasekadan.cz/ v Google Search Console.
# Značka musí zůstat v produkčním <head>, jinak se vlastnictví časem ztratí.
RUN sed -i 's#<head>#<head>\n  <meta name="google-site-verification" content="bFnU5Qjvk0Y52HY6N4d-b9_yy_IZ8DkY5LkoQsLAk8M">#' /site/index.html


FROM nginx:1.27-alpine
COPY nginx/default.conf /etc/nginx/conf.d/default.conf
COPY --from=discovery /site /usr/share/nginx/html
COPY docker-entrypoint.d/40-indexnow.sh /docker-entrypoint.d/40-indexnow.sh
RUN chmod +x /docker-entrypoint.d/40-indexnow.sh


# Mobilní pravidla a opravy kolizí článkových karet vložit přímo do hlavního CSS.
# Články tak nejsou závislé na načtení dalšího souboru a třída .event z titulní
# stránky už nemůže rozbít odstavce uvnitř týdenního přehledu.
RUN printf '\n\n/* Mobilní pravidla vložená při produkčním sestavení */\n' >> /usr/share/nginx/html/style.css \
 && cat /usr/share/nginx/html/mobile.css >> /usr/share/nginx/html/style.css \
 && printf '\n\n/* Opravy rozvržení článků vložené při produkčním sestavení */\n' >> /usr/share/nginx/html/style.css \
 && cat /usr/share/nginx/html/article-layout-fixes.css >> /usr/share/nginx/html/style.css

# Reklamní balík už vložil jediný normalizátor článků. Zde se upravují pouze
# obecné soubory webu a jednou se doplní navigace a upoutávky.
RUN find /usr/share/nginx/html -type f -name '*.html' -exec sed -i \
  -e 's#style.css"#style.css?v=20260805-event-layout-2"#g' \
  -e 's#site.js"#site.js?v=20260724-nemocnice-7"#g' \
  -e 's#<script src="[^"]*navigation\.js[^"]*"[^>]*></script>##g' \
  -e 's#<script src="[^"]*upoutavky\.js[^"]*"[^>]*></script>##g' \
  -e 's#</body>#<script src="/navigation.js?v=20260726-unified-footer-1" defer></script><script src="/upoutavky.js?v=20260726-home-fix-1" defer></script></body>#g' {} +

# Zkopírovat neveřejný redakční návrh KZK do heslem chráněné sekce /nahled/.
RUN mkdir -p /usr/share/nginx/html/nahled \
 && cp /usr/share/nginx/html/.github/drafts/kulturni-zarizeni-kadan.html \
       /usr/share/nginx/html/nahled/kulturni-zarizeni-kadan-8c7f3e.html

RUN rm -rf /usr/share/nginx/html/.git \
           /usr/share/nginx/html/.github \
           /usr/share/nginx/html/.image-parts \
           /usr/share/nginx/html/docker-entrypoint.d \
           /usr/share/nginx/html/nginx \
           /usr/share/nginx/html/research \
           /usr/share/nginx/html/scripts \
           /usr/share/nginx/html/tools \
           /usr/share/nginx/html/article-layout-fixes.css \
           /usr/share/nginx/html/Dockerfile \
           /usr/share/nginx/html/docker-compose.yml

EXPOSE 80
HEALTHCHECK --interval=30s --timeout=3s --retries=3 CMD wget -qO- http://127.0.0.1/healthz || exit 1