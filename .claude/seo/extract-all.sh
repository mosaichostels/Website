#!/bin/bash
# Runs every free-data extractor in one pass and tees each report to disk.
#
#   ./.claude/seo/extract-all.sh            # standard depth
#   ./.claude/seo/extract-all.sh --fast     # skip the slow sweeps (PSI, Unlighthouse)
#   ./.claude/seo/extract-all.sh gsc bing   # only the named extractors
#
# Every extractor writes a raw JSON bundle under seo-reports/<name>/ and prints
# its own gap analysis. This wrapper adds nothing to the analysis — it only
# sequences the runs, records timing, and keeps one extractor's failure from
# taking down the rest.
#
# Ordering is deliberate: cheap and fast first, so a broken credential surfaces
# in seconds rather than after a ten-minute Lighthouse sweep.

set -uo pipefail
cd "$(git rev-parse --show-toplevel)"

ENV_FILE="$HOME/.config/mosaic-seo/env"
[[ -f "$ENV_FILE" ]] || { echo "Missing $ENV_FILE — run .claude/seo/setup-platforms.sh" >&2; exit 1; }
# shellcheck disable=SC1090
source "$ENV_FILE"

PY="$HOME/.config/mosaic-seo/venv/bin/python3"
[[ -x "$PY" ]] || { echo "Missing venv at $PY — run .claude/seo/setup-platforms.sh" >&2; exit 1; }

FAST=0
WANT=()
for a in "$@"; do
  case "$a" in
    --fast) FAST=1 ;;
    *)      WANT+=("$a") ;;
  esac
done

LOG_DIR="seo-reports/runs/$(date +%F)"
mkdir -p "$LOG_DIR"

# name | slow? | command
EXTRACTORS=(
  "commoncrawl|0|$PY .claude/seo/commoncrawl-extract.py"
  "gsc|0|$PY .claude/seo/gsc-extract.py 90"
  "ga4|0|$PY .claude/seo/ga4-extract.py 90"
  "bing|0|$PY .claude/seo/bing-extract.py"
  "clarity|0|$PY .claude/seo/clarity-extract.py"
  "cwv|1|$PY .claude/seo/cwv-extract.py"
  "lighthouse|1|$PY .claude/seo/lighthouse-drift-extract.py"
)

wanted() {
  [[ ${#WANT[@]} -eq 0 ]] && return 0
  for w in "${WANT[@]}"; do [[ "$w" == "$1" ]] && return 0; done
  return 1
}

RAN=(); SKIPPED=(); FAILED=()
for spec in "${EXTRACTORS[@]}"; do
  IFS='|' read -r name slow cmd <<< "$spec"
  script=$(awk '{print $2}' <<< "$cmd")

  wanted "$name"                        || { SKIPPED+=("$name (not requested)"); continue; }
  [[ -f "$script" ]]                    || { SKIPPED+=("$name (no $script)"); continue; }
  [[ "$slow" == 1 && $FAST -eq 1 ]]     && { SKIPPED+=("$name (--fast)"); continue; }

  printf '\n\033[1m===== %s =====\033[0m\n' "$name"
  start=$(date +%s)
  if $cmd 2>&1 | tee "$LOG_DIR/$name.txt"; then
    RAN+=("$name ($(( $(date +%s) - start ))s)")
  else
    FAILED+=("$name")
    echo "  (continuing — one extractor failing must not abort the sweep)"
  fi
done

printf '\n\033[1m===== summary =====\033[0m\n'
printf 'reports: %s\n' "$LOG_DIR"
[[ ${#RAN[@]}     -gt 0 ]] && printf 'ran:      %s\n' "$(IFS=', '; echo "${RAN[*]}")"
[[ ${#SKIPPED[@]} -gt 0 ]] && printf 'skipped:  %s\n' "$(IFS=', '; echo "${SKIPPED[*]}")"
[[ ${#FAILED[@]}  -gt 0 ]] && printf 'FAILED:   %s\n' "$(IFS=', '; echo "${FAILED[*]}")"
[[ ${#FAILED[@]}  -gt 0 ]] && exit 1
exit 0
