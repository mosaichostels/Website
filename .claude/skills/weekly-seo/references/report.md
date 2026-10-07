# Report layout (step h)

> Moved from SKILL.md (commit 2b335f1). Dated numbers are historical; the newest report in seo-reports/ has current values.

## (h) Report

Write `seo-reports/YYYY-MM-DD.md`:

1. **Platform status** — the table from step (a), plus the deploy-drift table.
   Lead with drift if any page is out of sync; every finding below it is
   provisional until production matches the repo.
2. **Metric deltas vs last week**, one row per source so a regression in any
   one of them is visible at a glance:

   | Source | Metric | This week | Last week | Δ |
   |---|---|---|---|---|
   | GSC | clicks, impressions, CTR, avg position | | | |
   | GSC | URLs indexed / total in sitemap | | | |
   | GA4 | organic sessions, engagement rate | | | |
   | CrUX | LCP, INP, CLS (field, mobile) | | | |
   | Bing | indexed URLs, inbound links | | | |
   | Clarity | rage clicks, dead clicks | | | |
   | Common Crawl | pages captured | | | |
   | Lighthouse | perf / a11y / best-practices / SEO | | | |
   | Booking probe | GET status and latency | | | |

   List `tracked-queries.json` selection and its evidence window; if
   `stale_queries` is true, say why and do not call reused positions fresh.

3a. **Google Business Profile** (`gbp-extract.py`, see `gbp.md`): rating and review count, unanswered reviews, impressions, direction requests, calls, website clicks, top keywords, and the profile gaps it prints. Review replies and profile edits are MCP writes and only on the owner's ask.
3b. **Platform UI findings** (Search Console coverage and links, GA4 Admin settings, Clarity AI Visibility and settings, Bing Recommendations and AI Performance): include when the owner asked for a browser audit; procedure and last snapshot in `browser-audit.md`. Settings the classifier blocked go under "Needs a human".
3. **AI visibility** — crawler reachability table, Common Crawl capture count,
   Google and Bing index presence. The capture count is the clearest single
   number for whether LLMs can see this site; track it every week.
4. **Indexation detail** — every URL not in `Submitted and indexed`, with its
   coverage state. Call out any 404 still drawing impressions: that is live
   demand hitting a dead end and it is always worth a redirect.
5. **Fixed this week** — one line each: what changed, which file, which
   finding drove it.
6. **Deferred** — the gap, the reason, its priority score.
7. **Next week / needs a human** — anything requiring a decision, a
   credential, a deploy, or a factual claim you could not verify.
8. **Skill updated** — see "Self-improvement" in SKILL.md and `references/self-improvement.md`. One line per edit: which
   fact changed, in which section, why. Empty is a fine answer some weeks —
   don't manufacture an edit to fill this line.
9. **Scope review this run** — record the solo whole-diff scope check, or the paired reviewer's verdict and objections when the owner requested pairing. For a report-only run, say that no fix diff was reviewed.

Compare against the most recent existing file in `seo-reports/`. If there is
none, say so and treat this run as the baseline.

Where a source had no data, say which source and why — quota, insufficient
CrUX sample, credential down. A blank cell with no explanation reads as zero,
and zero is a very different claim from "not measured".

## Coverage items (step h)

`coverage_ledger.py init` seeds these ids; mark each with `coverage_ledger.py mark ITEM done|skipped|blocked REASON` as the run proceeds. A reason is required for `skipped` and `blocked`.

- `extract:<source>` for gsc, ga4, bing, clarity, cwv, lighthouse, commoncrawl: set automatically from the data; mark `skipped` or `blocked` yourself when a platform is DOWN. An extractor you deliberately did not run (a subset like `extract-all.sh gsc bing`, or `--fast`) must also be marked `skipped` with that reason. Read the `coverage: N item(s) still open` line that extract-all.sh prints before step (c): a CWV or Lighthouse gap found at step (h) is too late for ranking.
- `audits:claude-seo-14`: the 14 concurrent audit agents; `audits:skill-3`: the three Skill-tool-only checks; `ai-visibility`: `ai-visibility.sh`.

Item 2 of the report (metric deltas) is generated: paste the output of `python3 .claude/seo/deltas.py`. `not measured` is never zero; `_90d` rows overlap between runs.
