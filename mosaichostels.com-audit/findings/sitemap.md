# Sitemap Audit — mosaichostels.com

Date: 2026-08-05 (monitoring pass — supersedes prior sitemap audit in this file, which predates the blog rollout and `priority`-tag cleanup)
Source: https://www.mosaichostels.com/sitemap.xml (live, verified byte-identical to repo `sitemap.xml`)
URL count: 22 (limit 50,000 / 50MB — nowhere close, no split needed)

## Pass/Fail Summary

| Check | Result |
|---|---|
| XML well-formed | PASS — validated live + local copy with `xml.dom.minidom` |
| URL count vs 50k/50MB cap | PASS — 22 URLs |
| All URLs return HTTP 200 | PASS — 22/22, checked with `-L`, no redirects triggered |
| `loc` == canonical tag on every page | PASS — 22/22 exact match, including `/book-now` (the Aug 5 trailing-slash fix holds) |
| Trailing-slash mismatch class of bug (site-wide) | PASS — grepped all `.html` for `/book-now/`, `/gallery/`, `/about/`, `/contact/`, `/privacy/` internal hrefs; zero hits. No other page carries the bug class that hit `/book-now` |
| `priority` / `changefreq` tags | PASS — sitemap no longer emits them (previously present, now removed; nothing left to clean up) |
| Orphaned pages (crawled but missing from sitemap) | PASS — all 15 blog posts linked from `/blog/` are present in sitemap; all 7 core pages present |
| Extra pages (in sitemap but 404/redirected) | PASS — none |
| `lastmod` format validity (W3C datetime) | PASS — all `YYYY-MM-DD`, parseable |
| `lastmod` accuracy (reflects last significant change) | **FAIL on 5 URLs** — see below |
| Location-page quality gates (30+/50+ threshold) | N/A — 0 location pages on this site |

## Coverage Reconciliation

- Known pages per brief: `/`, `/gallery`, `/blog/`, `/about`, `/contact`, `/book-now`, `/privacy` (7) + "14 blog posts" = 21 expected.
- Actual: sitemap and live `/blog/` listing both have **15** blog posts (one more than the brief assumed) + 7 core pages = **22**, matching the sitemap's real count. Not a bug — the brief's blog-post count is simply slightly stale. Sitemap blog slugs, `/blog/` listing links, and local `blog/<slug>/` directories all match 1:1 — no missing or extra posts.

## Finding: Stale `lastmod` dates (Medium severity — accuracy issue, not a validity break)

Git history shows commit `b0ebf6b` (2026-08-05, "seo: entity stacking (hasMap schema) + FAQPage schema + anchor sculpting") made substantive content/structured-data changes to 5 pages *after* their current sitemap `lastmod` date:

| URL | Sitemap `lastmod` | Actual last significant change | Gap |
|---|---|---|---|
| `/` | 2026-08-03 | 2026-08-05 (added `hasMap` GBP CID schema) | 2 days stale |
| `/about` | 2026-08-03 | 2026-08-05 (added `hasMap` schema) | 2 days stale |
| `/contact` | 2026-08-03 | 2026-08-05 (added `hasMap` schema) | 2 days stale |
| `/blog/is-varanasi-safe-general-guide/` | 2026-07-29 | 2026-08-05 (added FAQPage schema + anchor retarget) | 7 days stale |
| `/blog/varanasi-solo-female-travelers-safety-travel-guide/` | 2026-05-26 | 2026-08-05 (added FAQPage schema + anchor retarget) | **71 days stale** |

These are not boilerplate touches — FAQPage/hasMap schema additions are exactly the kind of significant, crawl-worthy change `lastmod` exists to signal (they affect rich-result eligibility). Recommend regenerating `lastmod` for these 5 entries to `2026-08-05` on the next sitemap build.

The other 17 URLs (`/gallery`, `/book-now`, `/privacy`, `/blog/`, and 13 blog posts) have `lastmod` values that correctly match their last content-touching commit — no action needed there.

## No Action Taken

Read-only audit per instructions — no site files were edited.
