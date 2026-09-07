#!/bin/bash
# One-time platform wiring for the weekly SEO automation.
# Idempotent: safe to re-run. Reads ~/.config/mosaic-seo/env, never writes
# secrets into this repo.
#
#   ./.claude/seo/setup-platforms.sh
#
# Anything needing a browser is printed as a numbered manual step instead of
# being attempted. Enables only free-tier Google APIs (no billing account
# required for PSI, CrUX, Search Console, Indexing, or GA4 Data API).

set -euo pipefail

ENV_FILE="$HOME/.config/mosaic-seo/env"
SA_JSON="$HOME/.config/mosaic-seo/gcp-sa.json"
SEO_CFG="$HOME/.config/claude-seo/google-api.json"
SA_NAME="mosaic-seo-weekly"

[[ -f "$ENV_FILE" ]] || { echo "Missing $ENV_FILE — see the weekly-seo skill." >&2; exit 1; }
# shellcheck disable=SC1090
source "$ENV_FILE"

say()  { printf '\n\033[1m== %s\033[0m\n' "$1"; }
todo() { printf '  \033[33mMANUAL\033[0m  %s\n' "$1"; }
ok()   { printf '  \033[32mOK\033[0m      %s\n' "$1"; }

say "Local toolchain"
# Homebrew's python is PEP 668 externally-managed, so claude-seo's deps cannot
# be pip-installed into it. A dedicated venv keeps them off the system python.
VENV="$HOME/.config/mosaic-seo/venv"
if [[ ! -x "$VENV/bin/python3" ]]; then
  python3 -m venv "$VENV"
  "$VENV/bin/pip" install -q --upgrade pip
fi
if ! "$VENV/bin/python3" -c 'import requests, bs4, google.auth' 2>/dev/null; then
  "$VENV/bin/pip" install -q requests beautifulsoup4 google-auth \
    google-auth-oauthlib google-api-python-client
fi
ok "claude-seo venv at $VENV"

# The plugin hardcodes ~/.cache/claude-seo/drift, and a cache wipe already
# destroyed one set of baselines. Redirect it somewhere that survives.
mkdir -p "$HOME/.local/share/mosaic-seo/drift" "$HOME/.cache/claude-seo"
if [[ ! -L "$HOME/.cache/claude-seo/drift" ]]; then
  [[ -d "$HOME/.cache/claude-seo/drift" ]] && \
    mv "$HOME/.cache/claude-seo/drift"/* "$HOME/.local/share/mosaic-seo/drift/" 2>/dev/null
  rmdir "$HOME/.cache/claude-seo/drift" 2>/dev/null
  ln -s "$HOME/.local/share/mosaic-seo/drift" "$HOME/.cache/claude-seo/drift"
fi
ok "drift baselines -> $HOME/.local/share/mosaic-seo/drift"

command -v unlighthouse >/dev/null && ok "unlighthouse $(unlighthouse --version 2>/dev/null)" \
  || todo "Install Unlighthouse:  npm install -g unlighthouse"

say "Google Cloud"
if ! gcloud auth list --filter=status:ACTIVE --format='value(account)' 2>/dev/null | grep -q .; then
  todo "Run this, then re-run this script:  gcloud auth login"
  exit 1
fi
ACCOUNT=$(gcloud auth list --filter=status:ACTIVE --format='value(account)' | head -1)
ok "authenticated as $ACCOUNT"

if [[ -z "${GCP_PROJECT_ID:-}" ]]; then
  GCP_PROJECT_ID="mosaic-seo-$(date +%s | tail -c 6)"
  echo "  creating project $GCP_PROJECT_ID"
  gcloud projects create "$GCP_PROJECT_ID" --name="Mosaic SEO"
  sed -i '' "s|^export GCP_PROJECT_ID=.*|export GCP_PROJECT_ID=\"$GCP_PROJECT_ID\"|" "$ENV_FILE"
fi
gcloud config set project "$GCP_PROJECT_ID" >/dev/null
ok "project $GCP_PROJECT_ID"

say "Enabling free-tier APIs"
for api in searchconsole.googleapis.com indexing.googleapis.com \
           analyticsdata.googleapis.com pagespeedonline.googleapis.com \
           chromeuxreport.googleapis.com; do
  if gcloud services list --enabled --format='value(config.name)' | grep -qx "$api"; then
    ok "$api already enabled"
  else
    gcloud services enable "$api" && ok "$api enabled"
  fi
done

say "Service account (unattended auth for GSC / Indexing / GA4)"
SA_EMAIL="${SA_NAME}@${GCP_PROJECT_ID}.iam.gserviceaccount.com"
if ! gcloud iam service-accounts describe "$SA_EMAIL" >/dev/null 2>&1; then
  gcloud iam service-accounts create "$SA_NAME" --display-name="Mosaic weekly SEO"
fi
ok "service account $SA_EMAIL"

if [[ ! -f "$SA_JSON" ]]; then
  gcloud iam service-accounts keys create "$SA_JSON" --iam-account="$SA_EMAIL"
  chmod 600 "$SA_JSON"
  ok "key written to $SA_JSON (chmod 600)"
else
  ok "key already at $SA_JSON"
fi

say "Wiring claude-seo"
mkdir -p "$(dirname "$SEO_CFG")"
cat > "$SEO_CFG" <<JSON
{
  "api_key": "${GOOGLE_API_KEY:-}",
  "service_account_path": "$SA_JSON",
  "gsc_property": "${GSC_PROPERTY:-}",
  "ga4_property_id": "${GA4_PROPERTY_ID:-}"
}
JSON
chmod 600 "$SEO_CFG"
ok "$SEO_CFG"

say "Manual steps (browser required — nothing else can do these)"
[[ -n "${GOOGLE_API_KEY:-}" ]] || todo \
  "Create a PSI/CrUX API key: https://console.cloud.google.com/apis/credentials?project=$GCP_PROJECT_ID
            then set GOOGLE_API_KEY in $ENV_FILE and re-run this script."
todo "Grant GSC access — https://search.google.com/search-console/users
            Add user: $SA_EMAIL
            Permission: Owner. 'Full' is enough for Search Analytics and URL
            Inspection, but the Indexing API rejects anything below Owner."
todo "Grant GA4 read access — Admin > Property access management
            Add: $SA_EMAIL   Role: Viewer
            Then set GA4_PROPERTY_ID (Admin > Property details) in $ENV_FILE"
[[ -n "${BING_WEBMASTER_API_KEY:-}" ]] || todo \
  "Bing WMT API key — https://www.bing.com/webmasters/ > Settings > API access > API key
            Set BING_WEBMASTER_API_KEY in $ENV_FILE"
[[ -n "${CLARITY_API_TOKEN:-}" ]] || todo \
  "Clarity token — https://clarity.microsoft.com > Settings > Data Export
            Set CLARITY_API_TOKEN in $ENV_FILE"

say "Next"
echo "  ./.claude/seo/health-check.sh    # verify every platform with a real read call"
