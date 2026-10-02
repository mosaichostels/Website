# Microsoft Clarity

> Moved from SKILL.md (commit 2b335f1). Dated numbers are historical; the newest report in seo-reports/ has current values.

- **Microsoft Clarity — `.claude/seo/clarity-extract.py`.** Behavioural, not
  search, data. Rage clicks, dead clicks, quick-back clicks, scroll depth and
  engagement time, broken down by URL. These are the SXO signals: a page can
  rank perfectly and still fail every visitor who lands on it. **Hard quota of
  10 requests per project per day** and `numOfDays` accepts only 1-3 — budget
  the calls deliberately and never retry carelessly, because burning the quota
  costs a full day of data.
