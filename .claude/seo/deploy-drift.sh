#!/bin/bash
# Compares the committed repo against what is actually served, page by page.
#
#   ./.claude/seo/deploy-drift.sh
#
# Deployment is a manual FTP push (scripts/deploy.sh), so the repo routinely runs ahead
# of production. That gap matters twice over: audits read the live site while
# fixes are written against local files, and submitting a URL to IndexNow or
# the Indexing API before the change is live asks Google to re-crawl a page
# that has not changed.
#
# Whitespace is normalised before comparison so indentation churn does not
# register as drift. Exit 1 means at least one page or API file differs.
#
# PHP under api/ is executed by the host, so HTTP cannot return its source. When
# FTP_HOST, FTP_USER and FTP_PASS are set, those files are read back over FTP
# (read-only) and compared too; without them the API check is skipped.

set -uo pipefail
cd "$(git rev-parse --show-toplevel)"
SITE="${SITE_URL:-https://www.mosaichostels.com}"

norm() { sed 's/[[:space:]]\{1,\}/ /g; s/^ //; s/ $//' | grep -v '^$'; }

DRIFT=0
printf '| Page | Served as | Local | Live | State |\n|---|---|---|---|---|\n'

# Root index.html plus any <dir>/index.html, since the host serves directories
# from their index file. A bare <name>.html that redirects away is not the
# canonical source for any URL and is reported separately.
# Blog posts live at blog/<slug>/index.html (depth 3). The crawler-facing static files
# (sitemaps, robots.txt, llms.txt) are compared too: a stale sitemap misleads crawlers.
FILES=$( { find . -maxdepth 1 -name '*.html'; find . -mindepth 2 -maxdepth 3 -name 'index.html' -not -path './node_modules/*' -not -path './.*';
           find . -maxdepth 1 \( -name 'sitemap*.xml' -o -name robots.txt -o -name llms.txt \); } \
         | sed 's|^\./||' | sort )

while IFS= read -r f; do
  [[ -z "$f" ]] && continue
  case "$f" in
    index.html)   url="$SITE/" ;;
    */index.html) url="$SITE/${f%/index.html}/" ;;
    google*.html) url="$SITE/$f" ;;              # verification files keep .html
    *.xml|*.txt)  url="$SITE/$f" ;;               # sitemaps, robots.txt, llms.txt
    *)            url="$SITE/${f%.html}" ;;
  esac

  # A local file whose URL redirects elsewhere does not back that URL.
  code=$(curl -sS -o /dev/null -w '%{http_code}' --max-time 25 "$url" 2>/dev/null)
  if [[ "$code" == 3?? ]]; then
    dest=$(curl -sS -o /dev/null -w '%{redirect_url}' --max-time 25 "$url" 2>/dev/null)
    printf '| %s | %s | — | — | not canonical (%s to %s) |\n' "$f" "$url" "$code" "${dest#$SITE}"
    continue
  fi

  live=$(curl -sS -L --max-time 25 -H 'Cache-Control: no-cache' "$url?cb=$RANDOM" 2>/dev/null)
  [[ -z "$live" ]] && { printf '| %s | %s | — | — | UNREACHABLE |\n' "$f" "$url"; DRIFT=1; continue; }

  lb=$(norm < "$f" | wc -c | tr -d ' ')
  vb=$(printf '%s' "$live" | norm | wc -c | tr -d ' ')

  if diff -q <(norm < "$f") <(printf '%s' "$live" | norm) >/dev/null 2>&1; then
    printf '| %s | %s | %s | %s | in sync |\n' "$f" "${url#$SITE}" "$lb" "$vb"
  else
    n=$(diff <(norm < "$f") <(printf '%s' "$live" | norm) | grep -c '^[<>]')
    printf '| %s | %s | %s | %s | **DRIFT (%s lines)** |\n' "$f" "${url#$SITE}" "$lb" "$vb" "$n"
    DRIFT=1
  fi
done <<< "$FILES"

if [[ -n "${FTP_HOST:-}" && -n "${FTP_USER:-}" && -n "${FTP_PASS:-}" ]]; then
  # selftest.php and secrets.example.php are repo-only helpers, not part of a release.
  API=$(git ls-files 'api/*.php' 'api/**/*.php' | grep -v -E 'api/lib/selftest\.php|secrets\.example\.php')
  TMP=$(mktemp -d); trap 'rm -rf "$TMP"' EXIT
  { echo 'set net:timeout 30'; echo 'set ssl:verify-certificate no'; echo "open $FTP_HOST"; echo "user $FTP_USER $FTP_PASS"
    while IFS= read -r f; do mkdir -p "$TMP/$(dirname "$f")"; echo "get -O $TMP/$(dirname "$f") $f"; done <<< "$API"
    echo bye; } | lftp >/dev/null 2>&1
  printf '\n| API file (FTP read-back) | Local | Live | State |\n|---|---|---|---|\n'
  while IFS= read -r f; do
    if [[ ! -f "$TMP/$f" ]]; then printf '| %s | — | — | **NOT ON HOST** |\n' "$f"; DRIFT=1; continue; fi
    lb=$(norm < "$f" | wc -c | tr -d ' '); vb=$(norm < "$TMP/$f" | wc -c | tr -d ' ')
    if diff -q <(norm < "$f") <(norm < "$TMP/$f") >/dev/null 2>&1; then
      printf '| %s | %s | %s | in sync |\n' "$f" "$lb" "$vb"
    else
      printf '| %s | %s | %s | **DRIFT** |\n' "$f" "$lb" "$vb"; DRIFT=1
    fi
  done <<< "$API"
else
  echo; echo "API files not compared: set FTP_HOST, FTP_USER and FTP_PASS to read them back over FTP."
fi

echo
if [[ $DRIFT -eq 1 ]]; then
  echo "Repo is ahead of production. Deploy before submitting URLs:"
  echo "  FTP_HOST=... FTP_USER=... FTP_PASS=... ./scripts/deploy.sh"
fi
exit $DRIFT
