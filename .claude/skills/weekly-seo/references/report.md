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
   | Browser signals | GBP/OTA reviews, Bing UI links, AI mentions | | | |

   List `tracked-queries.json` selection and its evidence window; if
   `stale_queries` is true, say why and do not call reused positions fresh.

3. **Browser deep-dive findings** — one entry per platform (GBP, GCP, GA4 UI,
   PSI/CrUX web report, Bing Webmaster UI, Clarity UI): what was fetched, what
   it showed, and whether it's new since last week. A platform skipped
   because of a login gate goes here too, `DOWN — not signed in`, not
   silently dropped from the report — PSI/CrUX has no login gate, so it
   should never carry that excuse.
4. **AI visibility** — crawler reachability table, Common Crawl capture count,
   Google and Bing index presence. The capture count is the clearest single
   number for whether LLMs can see this site; track it every week.
5. **Indexation detail** — every URL not in `Submitted and indexed`, with its
   coverage state. Call out any 404 still drawing impressions: that is live
   demand hitting a dead end and it is always worth a redirect.
6. **Fixed this week** — one line each: what changed, which file, which
   finding drove it.
7. **Deferred** — the gap, the reason, its priority score.
8. **Next week / needs a human** — anything requiring a decision, a
   credential, a deploy, or a factual claim you could not verify.
9. **Skill updated** — see "Self-improvement" in SKILL.md and `references/self-improvement.md`. One line per edit: which
   fact changed, in which section, why. Empty is a fine answer some weeks —
   don't manufacture an edit to fill this line.
10. **Pairing and scope review this run** — inside Macterm, record the paired reviewer's whole-diff scope verdict and any objections or resolutions. Outside Macterm, record the solo scope check and any user-requested paired review. For a report-only run, say that no fix diff was reviewed.

Compare against the most recent existing file in `seo-reports/`. If there is
none, say so and treat this run as the baseline.

Where a source had no data, say which source and why — quota, insufficient
CrUX sample, credential down. A blank cell with no explanation reads as zero,
and zero is a very different claim from "not measured".

## Coverage items (step h)

`coverage_ledger.py init` seeds these ids; mark each with `coverage_ledger.py mark ITEM done|skipped|blocked REASON` as the run proceeds. A reason is required for `skipped` and `blocked`.

- `extract:<source>` for gsc, ga4, bing, clarity, cwv, lighthouse, commoncrawl: set automatically from the data; mark `skipped` or `blocked` yourself when a platform is DOWN. An extractor you deliberately did not run (a subset like `extract-all.sh gsc bing`, or `--fast`) must also be marked `skipped` with that reason. Read the `coverage: N item(s) still open` line that extract-all.sh prints before step (c): a CWV or Lighthouse gap found at step (h) is too late for ranking.
- `browser:gbp`, `browser:gcp`, `browser:ga4-ui`, `browser:psi-web`, `browser:bing-ui`, `browser:clarity-ui`: the six browser reviews in `references/browser.md`.
- `audits:claude-seo-14`: the 14 concurrent audit agents; `audits:skill-3`: the three Skill-tool-only checks; `ai-visibility`: `ai-visibility.sh`.

Item 2 of the report (metric deltas) is generated: paste the output of `python3 .claude/seo/deltas.py`. `not measured` is never zero; `_90d` rows overlap between runs.
