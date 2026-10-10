#!/bin/sh
# Loop one dashboard panel forever: scripts/dashboard-run.sh <panel> [seconds]
# Loads the SEO credentials (never printed) and uses the venv that has the Google libraries.
cd "$(dirname "$0")/.." || exit 1
set -a
. "$HOME/.config/mosaic-seo/env"
set +a
PY="$HOME/.config/mosaic-seo/venv/bin/python3"
[ -x "$PY" ] || PY=python3
PANEL="${1:?panel name or ui}"
if [ "$PANEL" = "ui" ]; then exec "$PY" scripts/dashboard-ui.py; fi
if [ "$PANEL" = "gfx" ]; then exec "$PY" scripts/dashboard-gfx.py; fi
if [ "$PANEL" = "png" ]; then exec "$PY" scripts/dashboard-gfx.py --png "${2:?output dir}"; fi
EVERY="${2:-60}"
while :; do
  # The panel is captured before clearing so the screen never flashes empty; re-read the
  # pane width each round so charts follow a resized pane.
  COLUMNS="$(tput cols 2>/dev/null || echo 70)"
  export COLUMNS
  OUT="$("$PY" scripts/dashboard.py "$PANEL" 2>&1)"
  printf '\033[2J\033[H%s\n' "$OUT"
  sleep "$EVERY"
done
