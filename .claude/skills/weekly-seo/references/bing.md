# Bing Webmaster Tools

> Moved from SKILL.md (commit 2b335f1). Dated numbers are historical; the newest report in seo-reports/ has current values.

- **Bing Webmaster Tools — `.claude/seo/bing-extract.py`.** Bing's index feeds
  Microsoft Copilot, so this is answer-engine data, not a Google afterthought.
  It also exposes **inbound link data that Google's API does not** — given
  this site's backlink profile is the root cause of both its Common Crawl
  absence and its crawl-budget starvation, that link data is the most valuable
  thing Bing offers here. Also read crawl errors and index coverage, and
  compare against Google's indexation: a URL indexed in one engine but not the
  other is a finding worth chasing.

## Added 2026-10-07

- The Bing UI exposes data the API does not: Recommendations (SEO and GEO checks), **AI Performance (Copilot citations and grounding queries)**, Site Scan, IndexNow history, Site Explorer crawl counts (Indexed / Error / Warning / Excluded) and the backlinks view. Paths, snapshot numbers and findings are in `browser-audit.md`.
- `GetLinkCounts` and `mosaic-bing get_link_counts` return an empty list although the UI lists 2 referring domains. Read backlinks in the UI.
- Only `sitemap.xml` was registered with Bing; `sitemap-images.xml` was submitted through the UI on 2026-10-07 (Processing). Re-check that Bing reads it.
- Bing returned HTTP 429 to bingbot at the Hostinger CDN edge (rate limit on bursts of bot user agents, see `fix.md`), which probably explains the six blog URLs Bing stored as 0 B or 795 B stubs. After the cache purge bingbot gets 200.
