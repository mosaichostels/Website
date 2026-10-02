# GA4

> Moved from SKILL.md (commit 2b335f1). Dated numbers are historical; the newest report in seo-reports/ has current values.

- **GA4 — `.claude/seo/ga4-extract.py`.** Data API v1beta: `getMetadata`,
  `runReport`, `batchRunReports`, `runPivotReport`, `runRealtimeReport`,
  `checkCompatibility`. This property exposes 376 dimensions and 89 metrics.

  Segment to organic and read landing-page engagement, not raw sessions. A
  page drawing organic sessions with poor engagement is an SXO finding: it
  ranks, then fails the visitor. GA4 lags ~2 days — never query up to today,
  the partial day reads as a traffic collapse.

  **The GA4↔Search Console link is live on this property**, so
  `organicGoogleSearchClicks/Impressions/ClickThroughRate/AveragePosition`
  join onto `landingPagePlusQueryString`. `checkCompatibility` confirms they
  are incompatible with every session-scoped dimension, so they get their own
  report and can never be split by channel or device. There is no query
  dimension — `googleSearchQuery` does not exist.

  Not in this API despite being in the UI: search query text; key-event,
  custom-dimension and data-stream *configuration* (that is the separate Admin
  API); Explorations — funnel, path, cohort, segment overlap — which are
  v1alpha only; Ads cost and ROAS; attribution and conversion paths; anything
  user-level.

  Standing findings from 2026-09-07 (90 days), re-verify rather than assume:

  - **269 sessions, 158 users.** Low traffic. Every split is small-sample —
    say so in the report instead of drawing confident conclusions from 4
    sessions.
  - **Key events changed (2026-10-01): `purchase` is now a key event** (2 in
    90 days); every other event, including `form_start` (22), reports
    `keyEvents=0` and `form_submit` does not fire at all. So a booking
    conversion is now measurable but the funnel (`begin_checkout` 16 →
    `add_payment_info` 5 → `purchase` 2 in 28 days) is tiny-sample. Key-event
    *configuration* is still the Admin API / GA4 UI, never the Data API. Flag
    it, do not attempt it. The GA4 data stream is registered to the apex
    `https://mosaichostels.com`, not `www`.
  - **July 2026 recorded zero sessions** while June had 160 and August 93. The
    tag broke or was removed for a month. Any year-over-year or trend claim
    crossing July is invalid.
  - **Roughly half of clicked organic entries never fire the tag.** `/` shows
    62 GSC clicks against 30 GA4 organic sessions;
    `/blog/is-varanasi-safe-general-guide/` 5 clicks against 0 sessions.
    Redirect, consent, or tag-placement loss. Treat GA4 organic counts as a
    floor, not truth.
  - **`AI Assistant` channel: 27 sessions at 77.8% engagement** — the
    best-engaging channel on the site. That is the AEO number; track it weekly.
  - Duplicate-URL fragmentation is visible here too (`/gallery/` vs
    `/gallery`, `/book-now` vs `/book-now/` vs `/book-now.html`), splitting
    sessions across both forms.
  - `landingPagePlusQueryString` treats `?fbclid=…` permutations as separate
    pages. The extractor drops rows under 2 sessions from the listing; the raw
    bundle keeps everything.
