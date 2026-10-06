#!/bin/bash
# Submits URLs to IndexNow (Bing/Yandex/Seznam/Naver; Google is not a participant).
#
#   ./scripts/indexnow-submit.sh --since <git-ref>   pages changed since that commit (normal call after a deploy)
#   ./scripts/indexnow-submit.sh /about /blog/x/     explicit paths or full URLs
#   ./scripts/indexnow-submit.sh --all               every URL in sitemap.xml
#   add --dry-run to any of them to print the URLs without sending anything
#
# Only URLs listed in sitemap.xml are sent in --since mode (redirected or noindex pages never are).
# Run after the changes are LIVE (deploy-drift.sh clean), never before. Prints the HTTP status:
# 200/202 means accepted. Key file (140ef5ae933ea27ef5ec39a4c06690e1.txt) must be live at the site root.

set -euo pipefail
cd "$(dirname "$0")/.."

HOST="www.mosaichostels.com"
KEY="140ef5ae933ea27ef5ec39a4c06690e1"

usage() { sed -n '2,10p' "$0" | sed 's/^# \{0,1\}//'; exit 2; }

sitemap_urls() { grep -oE '<loc>[^<]+</loc>' sitemap.xml | sed -e 's/<loc>//' -e 's#</loc>##'; }

# repo file -> served URL (same mapping as .claude/seo/deploy-drift.sh)
file_to_url() {
  case "$1" in
    index.html)   echo "https://$HOST/" ;;
    */index.html) echo "https://$HOST/${1%/index.html}/" ;;
    google*.html) echo "https://$HOST/$1" ;;
    *.html)       echo "https://$HOST/${1%.html}" ;;
  esac
}

# explicit argument -> full URL (a path like /about or a full https URL)
arg_to_url() {
  case "$1" in
    http*) echo "$1" ;;
    *)     echo "https://$HOST/${1#/}" ;;
  esac
}

DRY=0; MODE=""; REF=""; ARGS=()
while [ $# -gt 0 ]; do
  case "$1" in
    --dry-run) DRY=1 ;;
    --all)     MODE=all ;;
    --since)   MODE=since; REF="${2:?--since needs a git ref}"; shift ;;
    -h|--help) usage ;;
    *)         MODE=${MODE:-list}; ARGS+=("$1") ;;
  esac
  shift
done
[ -n "$MODE" ] || usage

case "$MODE" in
  all)   urls=$(sitemap_urls) ;;
  since) git rev-parse --verify --quiet "$REF^{commit}" >/dev/null || { echo "unknown git ref: $REF" >&2; exit 2; }
         known=$(sitemap_urls); urls=""; changed=$(git diff --name-only "$REF" -- '*.html')
         for f in $changed; do
           u=$(file_to_url "$f"); [ -n "$u" ] && grep -qxF "$u" <<<"$known" && urls+="$u"$'\n'
         done ;;
  list)  urls=$(for a in "${ARGS[@]}"; do arg_to_url "$a"; done) ;;
esac
urls=$(printf '%s\n' "$urls" | sed '/^$/d' | sort -u)

n=$(printf '%s\n' "$urls" | sed '/^$/d' | wc -l | tr -d ' ')
[ "$n" -gt 0 ] || { echo "nothing to submit"; exit 0; }
printf '%s\n' "$urls" | sed 's/^/  /'

if [ "$DRY" -eq 1 ]; then echo "dry run: $n URL(s), nothing sent"; exit 0; fi

url_list=$(printf '%s\n' "$urls" | sed 's/.*/"&"/' | paste -sd, -)
code=$(curl -s -o /dev/null -w '%{http_code}' -X POST "https://api.indexnow.org/indexnow" \
  -H "Content-Type: application/json; charset=utf-8" \
  -d "{\"host\":\"$HOST\",\"key\":\"$KEY\",\"keyLocation\":\"https://$HOST/$KEY.txt\",\"urlList\":[$url_list]}")
echo "IndexNow HTTP $code for $n URL(s)"
[[ "$code" == 200 || "$code" == 202 ]]
