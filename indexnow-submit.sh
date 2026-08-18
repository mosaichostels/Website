#!/bin/bash
# Submits every URL in sitemap.xml to IndexNow (Bing/Yandex/Seznam — Google not
# yet a participant). Run once after each production deploy that changes content.
# Key file (140ef5ae933ea27ef5ec39a4c06690e1.txt) must be live at the site root
# so IndexNow can verify ownership before accepting submissions.

set -euo pipefail

HOST="www.mosaichostels.com"
KEY="140ef5ae933ea27ef5ec39a4c06690e1"
SITEMAP="$(dirname "$0")/sitemap.xml"

urls=$(grep -oE '<loc>[^<]+</loc>' "$SITEMAP" | sed -e 's/<loc>//' -e 's#</loc>##')

url_list=$(printf '%s\n' "$urls" | sed 's/.*/"&"/' | paste -sd, -)

curl -s -X POST "https://api.indexnow.org/indexnow" \
  -H "Content-Type: application/json; charset=utf-8" \
  -d "{\"host\":\"$HOST\",\"key\":\"$KEY\",\"keyLocation\":\"https://$HOST/$KEY.txt\",\"urlList\":[$url_list]}"
