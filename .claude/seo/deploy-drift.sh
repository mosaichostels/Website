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
# register as drift. Exit 1 means at least one page differs.

set -uo pipefail
cd "$(git rev-parse --show-toplevel)"
SITE="${SITE_URL:-https://www.mosaichostels.com}"

norm() { sed 's/[[:space:]]\{1,\}/ /g; s/^ //; s/ $//' | grep -v '^$'; }

DRIFT=0
printf '| Page | Served as | Local | Live | State |\n|---|---|---|---|---|\n'

# Root index.html plus any <dir>/index.html, since the host serves directories
# from their index file. A bare <name>.html that redirects away is not the
# canonical source for any URL and is reported separately.
FILES=$( { find . -maxdepth 1 -name '*.html'; find . -mindepth 2 -maxdepth 2 -name 'index.html'; } \
         | sed 's|^\./||' | sort )

while IFS= read -r f; do
  [[ -z "$f" ]] && continue
  case "$f" in
    index.html)   url="$SITE/" ;;
    */index.html) url="$SITE/${f%/index.html}/" ;;
    google*.html) url="$SITE/$f" ;;              # verification files keep .html
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

echo
if [[ $DRIFT -eq 1 ]]; then
  echo "Repo is ahead of production. Deploy before submitting URLs:"
  echo "  FTP_HOST=... FTP_USER=... FTP_PASS=... ./scripts/deploy.sh"
fi
exit $DRIFT
