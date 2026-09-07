#!/bin/bash
# Verifies every data platform with a real read call and prints a status table.
# Read-only: makes no submissions, writes nothing but its own report.
#
#   ./.claude/seo/health-check.sh            # table to stdout
#   ./.claude/seo/health-check.sh --quiet    # exit 1 if any platform is DOWN

ENV_FILE="$HOME/.config/mosaic-seo/env"
# shellcheck disable=SC1090
[[ -f "$ENV_FILE" ]] && source "$ENV_FILE"

SEO="$(ls -d "$HOME"/.claude/plugins/cache/*/claude-seo/*/scripts 2>/dev/null | sort -V | tail -1)"
# Homebrew python is PEP 668 externally-managed; claude-seo deps live in a venv.
SEOPY="$HOME/.config/mosaic-seo/venv/bin/python3"
export SEOPY
SITE_URL="${SITE_URL:-https://www.mosaichostels.com}"
ROWS=(); FAILED=0

# check <platform> <auth method> <feeds> <command...>
check() {
  local name="$1" auth="$2" feeds="$3"; shift 3
  local out status
  out=$("$@" 2>&1); rc=$?
  if [[ $rc -eq 0 ]]; then status="LIVE"; else status="DOWN"; FAILED=1; fi
  ROWS+=("| $name | $auth | $status | $feeds |")
  [[ "$status" == DOWN ]] && printf '\033[31m%s DOWN:\033[0m %s\n' "$name" "$(echo "$out" | tail -3)" >&2
}

check "Site (health gate)" "none" "step (a) — blocks fixes on non-200" \
  bash -c 'curl -sSf -o /dev/null --max-time 20 "$0"' "$SITE_URL"

check "GSC Search Analytics" "service account" "step (b) — query/page/CTR/position deltas" \
  bash -c '[[ -n "${GSC_PROPERTY:-}" ]] && "$SEOPY" "$0/gsc_query.py" --property "$GSC_PROPERTY" --days 7 --limit 1 >/dev/null' "$SEO"

check "GSC URL Inspection" "service account" "step (b) — indexation coverage" \
  bash -c '"$SEOPY" "$0/google_auth.py" --check gsc --json | grep -q "\"available\": true"' "$SEO"

check "Google Indexing API" "service account" "step (f) — push changed URLs" \
  bash -c '"$SEOPY" "$0/google_auth.py" --check indexing --json | grep -q "\"available\": true"' "$SEO"

check "GA4 Data API" "service account" "step (b) — organic sessions" \
  bash -c '[[ -n "${GA4_PROPERTY_ID:-}" ]] && "$SEOPY" "$0/google_auth.py" --check ga4 --json | grep -q "\"available\": true"' "$SEO"

check "PageSpeed Insights" "API key" "step (b) — lab CWV" \
  bash -c '"$SEOPY" "$0/google_auth.py" --check psi --json | grep -q "\"available\": true"' "$SEO"

check "CrUX field data" "API key" "step (b) — real-user CWV + 25wk history" \
  bash -c '"$SEOPY" "$0/google_auth.py" --check crux --json | grep -q "\"available\": true"' "$SEO"

check "Bing Webmaster Tools" "API key" "step (b) — crawl stats, inbound links" \
  bash -c '[[ -n "${BING_WEBMASTER_API_KEY:-}" ]] && curl -sSf --max-time 20 -o /dev/null \
    "https://ssl.bing.com/webmaster/api.svc/json/GetUserSites?apikey=$BING_WEBMASTER_API_KEY"' 

check "IndexNow" "public key file" "step (f) — Bing/Yandex/Seznam ping" \
  bash -c 'curl -sSf --max-time 15 "$0" | grep -q "$1"' "$INDEXNOW_KEY_LOCATION" "$INDEXNOW_KEY"

check "Microsoft Clarity" "bearer token" "step (b) — rage/dead-click pages" \
  bash -c '[[ -n "${CLARITY_API_TOKEN:-}" ]] && curl -sSf --max-time 20 -o /dev/null \
    -H "Authorization: Bearer $CLARITY_API_TOKEN" \
    "https://www.clarity.ms/export-data/api/v1/project-live-insights?numOfDays=1"'

check "Moz (free tier)" "API key" "seo-backlinks — referring domains, DA" \
  bash -c '[[ -n "${MOZ_API_KEY:-}" ]]'

check "Common Crawl" "none" "seo-backlinks — link graph" \
  bash -c 'curl -sSf --max-time 25 -o /dev/null "https://index.commoncrawl.org/collinfo.json"'

check "Unlighthouse" "none (local)" "step (c) — multi-page Lighthouse" \
  bash -c 'command -v unlighthouse >/dev/null'

check "claude-seo venv" "none (local)" "every claude-seo script" \
  bash -c '"$SEOPY" -c "import requests, bs4, google.auth"'

check "Drift store" "none (local)" "step (g) — regression baselines" \
  bash -c '[ -L "$HOME/.cache/claude-seo/drift" ] && [ -f "$HOME/.cache/claude-seo/drift/baselines.db" ]'

if [[ "${1:-}" != "--quiet" ]]; then
  echo
  echo "| Platform | Auth method | Health | What it feeds |"
  echo "|---|---|---|---|"
  printf '%s\n' "${ROWS[@]}"
  echo
  [[ $FAILED -eq 1 ]] && echo "Repair DOWN rows with: ./.claude/seo/setup-platforms.sh"
fi
exit $FAILED
