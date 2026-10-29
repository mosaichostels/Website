# Core Web Vitals

> Moved from SKILL.md (commit 2b335f1). Dated numbers are historical; the newest report in seo-reports/ has current values.

- **Core Web Vitals — `.claude/seo/cwv-extract.py`.** Three APIs with
  different meanings, and the distinction decides which number to trust:
  PageSpeed Insights returns **lab** data (a simulated load on synthetic
  hardware), CrUX returns **field** data (what real Chrome users experienced),
  and CrUX History returns 25 weekly points. Field wins whenever they disagree.

  Defaults to 5 key pages × 2 strategies (~4 min); `--all-pages` widens to all
  22 × 2. CrUX is cheap so it always sweeps every URL — *which* pages have
  field data is itself the finding.

  **Standing finding: this origin has ZERO CrUX data at every scope.** Origin
  ALL/PHONE/DESKTOP/TABLET → 404, origin history → 404, 0 of 22 URLs → 404.
  Control-tested against `web.dev`, which returns a full record, so the key
  and both APIs are fine — this origin has simply never crossed the sampling
  threshold. PSI agrees from the other direction: `originLoadingExperience` is
  `null`.

  Three consequences, and stating them wrongly is worse than omitting them:
  the field trend is **absent, not "stable"**; GSC's Core Web Vitals report
  will also be empty, so do not go looking for it; and every CWV number this
  workflow can produce is **unvalidated lab simulation**. Label it as such in
  the report every single time.

  **Lighthouse ≥13 moved the savings fields** — both the PSI and Unlighthouse
  extractors hit this independently, so it is not a fluke. The classic
  `details.overallSavingsMs` / `overallSavingsBytes` are gone from the new
  `*-insight` audits: milliseconds now live in `audit.metricSavings`
  (per-metric LCP/FCP/TBT/CLS), and the byte figure survives **only as prose
  in `displayValue`** ("Est savings of 97 KiB"). Any extractor keyed on the old
  field reports "no opportunities" — which is flatly wrong. Both scripts read
  both shapes; do not "simplify" that away.
