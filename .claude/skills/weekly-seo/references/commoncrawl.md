# Common Crawl

> Moved from SKILL.md (commit 2b335f1). Dated numbers are historical; the newest report in seo-reports/ has current values.

- **Common Crawl — `.claude/seo/commoncrawl-extract.py`.** No auth, no quota.
  Checks how many pages the corpus holds for this domain across recent crawls.
  Because Common Crawl is training input for many LLMs, the capture count is
  the single most direct free measure of whether LLMs can see this site at
  all. Track it every week. **Standing finding: zero captures across
  CC-MAIN-2026-12 through CC-MAIN-2026-34** (re-confirmed 2026-10-01 across
  the 12 newest crawls, CCBot served 200 on every URL), verified against a control
  domain, while CCBot itself returns 200 — a discovery problem driven by a
  thin backlink profile, not a technical block.
