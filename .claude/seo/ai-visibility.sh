#!/bin/bash
# Checks whether AI platforms can actually read this site, and whether the
# indexes that feed them have it.
#
#   ./.claude/seo/ai-visibility.sh
#
# Three separate questions, because they fail independently:
#   1. Does each AI crawler get a 200? Hosts and WAFs often block AI user
#      agents silently while a normal browser sees the site fine. robots.txt
#      saying "Allow" proves nothing if the edge returns 403.
#   2. Is the URL in Common Crawl? CCBot's corpus is training input for many
#      LLMs, so presence there is the closest free proxy for "an LLM has read us".
#   3. Is it in the Google and Bing indexes? Those feed AI Overviews and
#      Microsoft Copilot respectively — retrieval-time citation, not training.
#
# Read-only. Makes no submissions and writes nothing.

set -uo pipefail
ENV_FILE="$HOME/.config/mosaic-seo/env"
# shellcheck disable=SC1090
[[ -f "$ENV_FILE" ]] && source "$ENV_FILE"
SITE_URL="${SITE_URL:-https://www.mosaichostels.com}"
TARGET="${1:-$SITE_URL/}"

echo "AI visibility for $TARGET"
echo

# --- 1. Crawler reachability -------------------------------------------------
# Real fetch per agent. A 200 with a plausible byte count is the only proof
# that matters; robots.txt is a request, not an enforcement.
echo "## Crawler reachability"
echo
printf '| Agent | Feeds | HTTP | Bytes |\n|---|---|---|---|\n'

check_ua() {
  local name="$1" feeds="$2" ua="$3"
  local out code bytes
  out=$(curl -sS -A "$ua" -o /tmp/aiv.$$ -w '%{http_code}' --max-time 25 "$TARGET" 2>/dev/null)
  code="${out:-000}"
  bytes=$(wc -c < /tmp/aiv.$$ 2>/dev/null | tr -d ' ')
  rm -f /tmp/aiv.$$
  printf '| %s | %s | %s | %s |\n' "$name" "$feeds" "$code" "$bytes"
}

check_ua "GPTBot"          "ChatGPT training"   "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko); compatible; GPTBot/1.2; +https://openai.com/gptbot"
check_ua "OAI-SearchBot"   "ChatGPT search"     "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko); compatible; OAI-SearchBot/1.0; +https://openai.com/searchbot"
check_ua "ChatGPT-User"    "ChatGPT browsing"   "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko); compatible; ChatGPT-User/1.0; +https://openai.com/bot"
check_ua "ClaudeBot"       "Claude training"    "Mozilla/5.0 (compatible; ClaudeBot/1.0; +claudebot@anthropic.com)"
check_ua "Claude-SearchBot" "Claude search"     "Mozilla/5.0 (compatible; Claude-SearchBot/1.0; +claudebot@anthropic.com)"
check_ua "PerplexityBot"   "Perplexity index"   "Mozilla/5.0 (compatible; PerplexityBot/1.0; +https://perplexity.ai/perplexitybot)"
check_ua "Perplexity-User" "Perplexity live"    "Mozilla/5.0 (compatible; Perplexity-User/1.0; +https://perplexity.ai/perplexity-user)"
check_ua "Googlebot"       "AI Overviews"       "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
check_ua "bingbot"         "Copilot"            "Mozilla/5.0 (compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm)"
check_ua "CCBot"           "Common Crawl / LLMs" "CCBot/2.0 (https://commoncrawl.org/faq/)"
check_ua "Amazonbot"       "Alexa / Rufus"      "Mozilla/5.0 (compatible; Amazonbot/0.1; +https://developer.amazon.com/support/amazonbot)"
check_ua "meta-externalagent" "Meta AI"         "meta-externalagent/1.1 (+https://developers.facebook.com/docs/sharing/webmasters/crawler)"
check_ua "Applebot"        "Apple Intelligence" "Mozilla/5.0 (compatible; Applebot/0.1; +http://www.apple.com/go/applebot)"

echo
echo "A non-200 means the edge is blocking that agent regardless of robots.txt."
echo

# --- 2. robots.txt opt-out tokens --------------------------------------------
# Google-Extended and Applebot-Extended are directives only: they never fetch.
# Their absence from robots.txt means AI training use is permitted.
echo "## Training opt-out tokens"
echo
ROBOTS=$(curl -sS --max-time 15 "$SITE_URL/robots.txt" 2>/dev/null)
for tok in Google-Extended Applebot-Extended GPTBot ClaudeBot CCBot PerplexityBot; do
  if grep -qi "^User-agent: *$tok" <<<"$ROBOTS"; then
    rule=$(awk -v t="$tok" 'BEGIN{IGNORECASE=1} $0 ~ "^User-agent: *"t {f=1;next} /^User-agent:/{f=0} f && /^(Allow|Disallow):/{print;exit}' <<<"$ROBOTS")
    echo "- $tok — declared: ${rule:-(no rule)}"
  else
    echo "- $tok — not declared (falls through to \`User-agent: *\`)"
  fi
done
echo

# --- 3. Index presence -------------------------------------------------------
echo "## Index presence"
echo
HOST=$(sed -E 's|^https?://||; s|/.*||' <<<"$SITE_URL")

# Common Crawl: the newest crawl is discovered rather than hardcoded, because
# the index name rolls over every few weeks.
CC_INDEX=$(curl -sS --max-time 30 https://index.commoncrawl.org/collinfo.json 2>/dev/null \
  | python3 -c 'import json,sys; d=json.load(sys.stdin); print(d[0]["id"] if d else "")' 2>/dev/null)
if [[ -n "$CC_INDEX" ]]; then
  CC_HITS=$(curl -sS --max-time 45 \
    "https://index.commoncrawl.org/$CC_INDEX-index?url=$HOST%2F*&output=json" 2>/dev/null \
    | grep -c '"status": *"200"')
  echo "- Common Crawl ($CC_INDEX): ${CC_HITS:-0} pages captured"
else
  echo "- Common Crawl: index list unavailable"
fi

SEO="$(ls -d "$HOME"/.claude/plugins/cache/*/claude-seo/*/scripts 2>/dev/null | sort -V | tail -1)"
SEOPY="$HOME/.config/mosaic-seo/venv/bin/python3"
if [[ -n "$SEO" && -x "$SEOPY" && -n "${GSC_PROPERTY:-}" ]]; then
  echo "- Google index: run \`\"\$SEOPY\" \"\$SEO/gsc_inspect.py\"\` per URL for coverageState"
fi
if [[ -n "${BING_WEBMASTER_API_KEY:-}" ]]; then
  BING_N=$(curl -sS --max-time 25 \
    "https://ssl.bing.com/webmaster/api.svc/json/GetUrlInfo?apikey=$BING_WEBMASTER_API_KEY&siteUrl=$SITE_URL&url=$TARGET" 2>/dev/null \
    | grep -c 'DocumentSize' )
  echo "- Bing index (feeds Copilot): $([[ "${BING_N:-0}" -gt 0 ]] && echo "present" || echo "not found")"
fi
