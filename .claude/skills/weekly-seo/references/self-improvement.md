# Self-improvement

> Moved from SKILL.md (commit 2b335f1). Dated numbers are historical; the newest report in seo-reports/ has current values.

## Self-improvement

Two different things live in this file, and only one of them updates itself:

- **Facts about the world** — standing-finding blocks, discovered URL
  patterns, DOM quirks, resolved gaps. These decay by design and are meant to
  be overwritten. Update these every run, right in this file.
- **Rules about behavior** — the scope lock, the read-only/exceptions list in
  the browser deep-dive, anything that would need a permission grant. These
  never self-update. A rule changes only when the owner asks for it in
  conversation, the same way every boundary in this file changed so far.
  Earlier attempts in this skill's own history to have it grant itself new
  capabilities were correctly blocked by the harness — self-modifying its own
  permissions is not something this workflow does on its own initiative,
  ever, no matter how reasonable the edit seems in the moment.

Before the verify/commit step, fold what this run learned into the file:

1. Any "Standing finding from `<date>`" block re-verified this run — update
   the date and numbers in place. If it changed, say it changed; if it held,
   write "confirmed" rather than leaving a stale date sitting there.
2. Any newly-discovered technical fact that saves the next run real work — a
   URL pattern (e.g. Bing's `/webmasters/<page>?siteUrl=...`), a DOM quirk
   (e.g. Bing's Configuration nav being Shadow DOM and needing a manual click
   to expand before its children exist in the DOM), a platform's exact
   settings path once found. Add it next to where that platform is already
   discussed — don't create a new junk-drawer section for it.
3. Any line in "Known standing gaps" or the deferred list that this run
   actually fixed — remove it. If the fix needs a sentence of context for
   next time, fold that into whatever finding replaced it.
4. Anything in this file that turned out to be flatly wrong (a moved script
   path, a changed flag, a fact that no longer holds) — correct just that,
   not the surrounding prose.

This edit rides in the same commit as everything else and goes through the
same review the site changes do — nothing here is silent or separate.
`verify.sh` doesn't check markdown, so a SKILL.md edit isn't gated by it, but
it's still a real diff in the same `git add -A` — if it looks wrong, `git
restore` it same as any other file, and say so in the report instead of
forcing a "self-improvement" that didn't actually improve anything.
