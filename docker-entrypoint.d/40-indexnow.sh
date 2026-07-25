#!/bin/sh
set -eu

# Spustí se na pozadí, aby už při ověření klíče byla nová verze webu dostupná.
(
  sleep 30

  ROOT=/usr/share/nginx/html
  KEY=4779abb8964b2f9f65ae960f08f74e6a
  SITEMAP="$ROOT/sitemap.xml"
  KEY_FILE="$ROOT/$KEY.txt"

  [ -f "$SITEMAP" ] || exit 0
  [ -f "$KEY_FILE" ] || exit 0

  URL_LIST="$(
    sed -n 's:.*<loc>\(.*\)</loc>.*:\1:p' "$SITEMAP" \
      | sed 's/&amp;/\&/g' \
      | awk '
        BEGIN { printf "["; separator="" }
        {
          gsub(/\\/, "\\\\")
          gsub(/\"/, "\\\"")
          printf "%s\"%s\"", separator, $0
          separator="," 
        }
        END { printf "]" }
      '
  )"

  [ "$URL_LIST" != "[]" ] || exit 0

  PAYLOAD="$(printf '{\"host\":\"nasekadan.cz\",\"key\":\"%s\",\"keyLocation\":\"https://nasekadan.cz/%s.txt\",\"urlList\":%s}' "$KEY" "$KEY" "$URL_LIST")"

  wget -q -O /tmp/indexnow-response.txt \
    --header='Content-Type: application/json; charset=utf-8' \
    --post-data="$PAYLOAD" \
    'https://api.indexnow.org/indexnow' \
    || true
) &

exit 0
