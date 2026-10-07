# Search Console

> Moved from SKILL.md (commit 2b335f1). Dated numbers are historical; the newest report in seo-reports/ has current values.

- **Search Console — full sweep.** One command pulls everything the API has:

  ```bash
  source ~/.config/mosaic-seo/env && "$SEOPY" .claude/seo/gsc-extract.py 90
  ```

  Raw bundle lands in `seo-reports/gsc/YYYY-MM-DD.json`; the run prints a gap
  analysis. Takes ~1s per inspected URL.

  **Know what the API cannot give you**, and never imply otherwise in a report.
  It exposes exactly four surfaces — `sites`, `sitemaps`, `searchanalytics`
  (6 dimensions × 6 result types), and `urlInspection`. The aggregate Coverage
  report, every Enhancements report, Core Web Vitals, manual actions, security
  issues, the links report, and removals are **UI-only**. URL Inspection is the
  substitute: per-URL coverage state plus detected rich results, one URL at a
  time, capped at 2000/day. Core Web Vitals come from CrUX instead.

  Read these out of the result, in this order:

  1. **Indexation by coverage state.** `Discovered - currently not indexed`
     means Google knows the URL and chose not to spend crawl budget — an
     authority and internal-linking problem, not a technical one. `URL is
     unknown to Google` on a page that has impressions means it was dropped
     from the index. `Crawled - currently not indexed` means Google fetched it
     and judged it not worth keeping.
  2. **URLs with impressions that are not in the sitemap.** A URL that 301s to
     a canonical page belongs here and is correct — never add a redirect to a
     sitemap. What matters is any such URL whose state is `Not found (404)`:
     that is live search demand hitting a dead end, and a 301 in `.htaccess`
     reclaims it.
  3. **`searchAppearance` row count.** Zero means no rich result has ever
     appeared for this site, regardless of what markup validates. Compare
     against the rich result types URL Inspection detects — markup that
     validates but never appears is worth understanding before adding more.
  4. **Striking distance, positions 5-20.** One nudge from page one. Rank by
     impressions, not by position.
  5. **Ranked well but not clicked** — position ≤3 with CTR under 10%. This is
     a title, meta description, and SERP-presentation problem, never a ranking
     problem. Do not try to fix it by chasing rank.
  6. **Sitemap state** — errors and warnings, and `lastSubmitted` age.

  Standing findings from 2026-09-07, re-verify rather than assume:

  - 18 of 22 sitemap URLs indexed. `/about`, `/privacy`, `/blog/`, and
    `/blog/dorm-vs-private-room-varanasi-hostel/` are discovered but not
    indexed; `/contact` was `URL is unknown to Google`.
  - `searchAppearance` returned **0 rows over 90 days** while URL Inspection
    detected Breadcrumbs on 6 pages. Every blog post carries `FAQPage`, and as
    of 2026-05-07 Google **fully retired the FAQ rich result for all sites**
    (superseding the earlier "restricted to gov/health sites since 2023"
    note) — so that markup earns nothing in the SERP for anyone now, not just
    non-exempt sites. Keep it for AI extraction; do not count it as a
    rich-result win, and do not add new FAQPage blocks expecting one.
  - Branded CTR is the largest single gap by volume: `mosaic hostel varanasi`
    drew 652 impressions at position 1.3 for 34 clicks (5.2%), and
    `mosaic hotel varanasi` 127 impressions at position 1.0 for 2 clicks
    (1.6%). Some of that is the Business Profile absorbing the click, so
    diagnose before rewriting the title.
  - Best non-branded opportunity: `hostels near assi ghat`, 149 impressions at
    position 15.0, zero clicks. High commercial intent, stuck on page two.

## Properties (verified in the Search Console UI, 2026-10-06)

Only the URL-prefix property `https://www.mosaichostels.com/` exists for this account (plus an Instagram channel). There is no `sc-domain:mosaichostels.com` property, so any call to it returns 403 for every account: do not try `sc-domain:` names or other host variants. `mosaic-seo-weekly@ai-seo-manager.iam.gserviceaccount.com` is Owner on the URL-prefix property; `GSC_PROPERTY` and `~/.config/claude-seo/google-api.json` already point at it.

## Added 2026-10-07

- **`gsc-sitemap-submit.py --submit` now resubmits both `sitemap.xml` and `sitemap-images.xml`.** Before this, a changed image sitemap was never resubmitted (it was missed on 2026-10-07). `--self-check` is unchanged.
- URL Inspection "Request indexing" is not in any API. It was done through the owner's signed-in Chrome for `/blog/dorm-vs-private-room-varanasi-hostel/`, `/about`, `/contact` and `/blog/` (see `browser-audit.md` for the procedure). Re-inspect with the API about a week later.
- The Search Console UI knows **9 external links from 8 sites**, which corrects any earlier "no inbound links" claim. The 28 non-indexed pages are mostly legacy WordPress URLs that already 301 on the live site; check live status before acting on a coverage row.
- The `mosaic-gsc` MCP is unauthenticated (use the service-account scripts), and the service account is Owner on the URL-prefix property only.
