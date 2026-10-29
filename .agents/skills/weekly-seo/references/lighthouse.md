# Unlighthouse and drift

> Moved from SKILL.md (commit 2b335f1). Dated numbers are historical; the newest report in seo-reports/ has current values.

- **Unlighthouse and drift — `.claude/seo/lighthouse-drift-extract.py`.**
  Multi-page Lighthouse across the sitemap plus the claude-seo drift
  comparison. Flags: `--key-pages` (3 routes, ~1 min vs ~5), `--skip-sweep`,
  `--skip-drift`, `--refresh-baselines`, `--self-check`.

  **`unlighthouse-ci` only deletes per-page `lighthouse.json` when you pass
  `--build-static`** — that flag globs and `rm`s them after building the
  static HTML, which is how an earlier run lost all its detail. The extractor
  never passes it; it runs into a temp dir with `--reporter jsonExpanded`,
  harvests every LHR into the bundle, and cleans up in a `finally`. The bundle
  is the durable artifact. Do not add `--build-static`.

  Two more traps it already handles: scored metric audits (LCP, TTI, SI, FCP)
  otherwise show up as "failing audits" and pollute the fix queue — filtered by
  dropping `auditRefs.group` of `metrics` or `hidden`, since they are already
  in the metrics block. And `unlighthouse-ci` **exits non-zero on a budget
  failure**, so exit code alone is not a success signal; a written
  `ci-result.json` is.

  Unlighthouse gives 4 category scores, every audit with savings, and lab
  metrics for many URLs in one pass. It cannot give field data, stable
  performance scores (±10 run to run; a11y/best-practices/SEO are
  deterministic), or real INP (TBT is a proxy). Route count is
  sampling-dependent, so page counts differ between runs and sweeps are not
  directly comparable page-for-page.

  claude-seo drift gives a SQLite snapshot per URL (title, meta, canonical,
  robots, headings, JSON-LD, OG/Twitter, status, content hash) graded by 17
  rules at CRITICAL/WARNING/INFO. It cannot tell you anything about a page
  that has no baseline — it is a diff, not a crawler — nor about rankings,
  traffic, or index state, and it reads raw HTML, never the rendered DOM.

  Standing findings from the 2026-09-07 sweep (15 routes), re-verify:

  - **SEO 100/100 on all 15.** Averages: performance 92, accessibility 92,
    best-practices 76. Worst performance `/about` at 79.
  - Failing on 15/15, with savings summed across pages: `unused-javascript`
    (2650 ms, 1116 KiB — the single biggest win on the site),
    `image-delivery-insight` (2550 ms, 704 KiB), `render-blocking-insight`
    (1150 ms), `cache-insight` (840 KiB). Also 15/15 but unquantified:
    third-party cookies, colour contrast, inspector issues, network dependency
    tree.
  - `landmark-one-main` fails on 12/15, `lcp-discovery-insight` on 9/15,
    `errors-in-console` on 4/15, `frame-title` on 3/15.
  - **Drift comparison: CLEAN** — 0 CRITICAL, 0 WARNING, 0 INFO across all
    three baselines. Symlink verified intact.
