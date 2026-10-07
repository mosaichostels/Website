# Microsoft Clarity

> Moved from SKILL.md (commit 2b335f1). Dated numbers are historical; the newest report in seo-reports/ has current values.

- **Microsoft Clarity — `.claude/seo/clarity-extract.py`.** Behavioural, not
  search, data. Rage clicks, dead clicks, quick-back clicks, scroll depth and
  engagement time, broken down by URL. These are the SXO signals: a page can
  rank perfectly and still fail every visitor who lands on it. **Hard quota of
  10 requests per project per day** and `numOfDays` accepts only 1-3 — budget
  the calls deliberately and never retry carelessly, because burning the quota
  costs a full day of data.

## Added 2026-10-07

- The dashboard, recordings, heatmaps, **AI Visibility tab (Copilot citations, share of authority)**, the Google Analytics tab and Settings (Setup, Masking, IP blocking, Funnels, Smart events) are UI-only and were read through Chrome. Paths, snapshot numbers and findings are in `browser-audit.md`. The extractor's 10 requests per day quota does not apply to the UI.
- Project id `xh249om5vt`. The dashboard excludes bot sessions (435 bot versus 346 human over 30 days on 2026-10-07). Smart events exist for Book, Checkout, Submit form, Check availability, Contact us and Outbound click; **no funnels and no IP blocking are configured**, so the owner's own visits are recorded. Creating a funnel or an IP block is a setting change the classifier blocks: owner action.
