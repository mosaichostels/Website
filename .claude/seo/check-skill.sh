#!/bin/bash
# Structure gate for the weekly-seo skill. Stdlib/grep only.
# Checks: size cap, trigger phrases, reference linkage in both directions,
# required step headings, report-only and drift wording, forbidden obsolete text.
#
#   ./.claude/seo/check-skill.sh      # exit 0 = structure valid

set -uo pipefail
cd "$(git rev-parse --show-toplevel)"
D=.claude/skills/weekly-seo
S=$D/SKILL.md
fail=0
bad() { echo "FAIL: $*"; fail=1; }

[[ -f "$S" ]] || { echo "FAIL: $S missing"; exit 1; }

lines=$(wc -l < "$S" | tr -d ' ')
[[ $lines -le 200 ]] || bad "SKILL.md is $lines lines (max 200)"

fm=$(awk 'NR==1&&/^---$/{f=1;next} f&&/^---$/{exit} f' "$S")
grep -q '^name: weekly-seo$' <<<"$fm" || bad "frontmatter name is not weekly-seo"
for p in "weekly SEO" "SEO run" "SEO sweep" "audit-and-fix pass"; do
  grep -qF "$p" <<<"$fm" || bad "description lacks trigger phrase: $p"
done

for ref in $(grep -o 'references/[a-z0-9-]*\.md' "$S" | sort -u); do
  [[ -f "$D/$ref" ]] || bad "SKILL.md links $ref but the file does not exist"
done
for f in "$D"/references/*.md; do
  [[ -f "$f" ]] || continue
  grep -qF "references/$(basename "$f")" "$S" || bad "orphaned reference: $(basename "$f")"
done

for h in "## Scope lock" "## (a) Health gate" "## (b) Data pull" "## (c) Audits" \
         "## (d) Rank the gaps" "## (e) Fix" "## (f) Submit changed URLs" \
         "## (g) Re-baseline" "## (h) Report" "## Self-improvement" \
         "## Verify, then commit" "## Stop and ask"; do
  grep -qF "$h" "$S" || bad "missing heading: $h"
done

grep -qi 'report-only' "$S" || bad "report-only mode wording missing"
sec_f=$(awk '/^## \(f\) /{f=1;next} /^## /{f=0} f' "$S")
grep -qF 'deploy-drift.sh' <<<"$sec_f" || bad "step (f) does not require the drift check"
grep -qF 'gsc-sitemap-submit.py' <<<"$sec_f" || bad "step (f) does not use gsc-sitemap-submit.py"

for needle in 'deltas.py' 'coverage_ledger.py mark' 'coverage_ledger.py check'; do
  grep -qF "$needle" "$S" || bad "SKILL.md does not mention: $needle"
done
hits=$(grep -rnE 'osascript|AppleScript|Safari|safari-mcp|Herdr|HERDR|MOZ_API|indexing_notify|browser\.contexts|page\.(goto|inner_text|click|screenshot|content|frame_locator)' "$D" || true)
[[ -z "$hits" ]] || bad "obsolete text present:"$'\n'"$hits"

[[ $fail -eq 0 ]] && echo "skill structure OK ($lines lines)"
exit $fail
