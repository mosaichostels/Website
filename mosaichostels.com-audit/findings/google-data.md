# Google API SEO Data — mosaichostels.com

Data source: Google API (field/production data), not static analysis. Credential tier: **2 (Full)** — PSI + CrUX + CrUX History + Search Console + URL Inspection + Sitemaps + GA4 all authenticated and working.

Collected: 2026-08-17. GSC lag ~2-3 days (window: 2026-07-20 to 2026-08-14). GA4 lag ~1 day (window: 2026-07-20 to 2026-08-16, extended to 90 days where noted). CrUX is a 28-day rolling field average.

---

## 1. PageSpeed Insights + CrUX Field Data (homepage)

**CrUX field data: unavailable.** Both the origin-level CrUX History API and the per-URL CrUX in PSI returned:
> "No CrUX data for this origin. The site likely has insufficient Chrome traffic volume for eligibility."

This is expected for a low-traffic site (GA4 shows ~2 sessions/day) — CrUX requires a minimum real-user sample size Google doesn't disclose. **Field CWV cannot be reported; lab data (Lighthouse) is the only available signal until traffic grows.**

### Lighthouse lab scores

| Strategy | Performance | Accessibility | Best Practices | SEO |
|---|---|---|---|---|
| Mobile | 79/100 | 95/100 | 100/100 | 100/100 |
| Desktop | 92/100 | 95/100 | 100/100 | 100/100 |

### Lab Core Web Vitals proxies (no field data available — use lab as directional only)

| Metric | Mobile | Desktop | Rating (mobile) |
|---|---|---|---|
| LCP | 3.8 s | 1.1 s | Needs Improvement (2.5–4.0s) |
| CLS | 0.004 | 0.002 | Good |
| TBT (proxy for INP) | 0 ms | 30 ms | Good |
| FCP | 3.8 s | 1.1 s | — |
| Speed Index | 4.5 s | 1.9 s | — |

Mobile LCP lab score (0.55) is the weak point; desktop is solid across the board (LCP 1.1s, Good).

### Top opportunity (both strategies)

- **Avoid multiple page redirects — 780ms savings on mobile, 230ms on desktop.**
  Root cause confirmed via curl: `https://mosaichostels.com` (bare apex, no www) 301-redirects to `https://www.mosaichostels.com/`. Every request to the bare domain pays a full redirect round-trip before the page starts loading. This affects any inbound link, bookmark, or typed URL using the apex domain, and disproportionately hurts mobile LCP.
  - **Priority: High.** Fix at the DNS/hosting edge (serve HTTPS + redirect natively at the CDN/DNS layer rather than via app-level redirect) or confirm the current redirect is already a fast 301 (not a redirect chain) — currently it is a single hop but still costs ~200-800ms depending on network.

---

## 2. GSC URL Inspection — Indexation Status

Property used: `https://www.mosaichostels.com/` (site is verified in GSC as **siteOwner** under the **www** variant — the bare-domain property `https://mosaichostels.com/` returned a 403 permission error, confirming www is the canonical GSC property).

| URL | Coverage state | Verdict | Notes |
|---|---|---|---|
| `/` (homepage) | Submitted and indexed | PASS | Crawled as MOBILE, 2026-08-14. Review snippet rich result detected (PASS). |
| `/gallery` | Submitted and indexed | PASS | Crawled 2026-08-06. **Rich Results: FAIL** — Breadcrumb structured data missing required `"item"` field. |
| `/about` | Discovered — currently not indexed | NEUTRAL | Google has seen the URL (referred from homepage + a blog post) but has not crawled/indexed it yet. |
| `/book-now` | URL is unknown to Google | NEUTRAL | No referring URLs recorded — Google hasn't discovered this URL at all. |
| `/blog` | URL is unknown to Google | NEUTRAL | Blog index page not discovered by Google. |
| `/contact-us`/`/contact` | URL is unknown to Google | NEUTRAL | Not discovered. |

**Important URL-structure note:** the live site serves clean URLs without `.html` (e.g. `/about`, `/book-now`, `/blog`, `/gallery`, `/contact`) — the legacy `.html` paths (`about.html`, `book-now.html`, `blog.html`) all 301-redirect to the clean versions. Inspecting the `.html` variants returns "unknown to Google" because they aren't the canonical URLs Google would index; the clean-URL results above are the accurate signal.

### Findings, prioritized

- **Critical:** `/book-now` — the primary conversion page — is completely undiscovered by Google (no referring URLs at all, not even from the homepage nav in Google's crawl graph). This is a strong candidate for the top indexation issue on the site: the booking page has zero organic discoverability. Verify the homepage's link to book-now is a crawlable `<a href>` (not JS-only) and consider requesting indexing via the Indexing API or a manual "Request Indexing" in GSC once confirmed crawlable.
- **High:** `/blog` (blog index/listing page) is also undiscovered — this could be starving individual blog posts of internal PageRank flow if `/blog` is the only place linking to older posts, and it means the blog hub itself can never rank for hub-style navigational queries.
- **High:** `/about` is discovered but not yet indexed — low urgency but worth a "Request Indexing" push since it's a core trust page.
- **Medium:** `/gallery` Breadcrumb rich-result FAIL — the breadcrumb schema is missing the required `item` field on at least one entry. Fix by ensuring every `ListItem` in the `BreadcrumbList` JSON-LD includes both `name` and `item` (URL).

---

## 3. GSC Search Performance (28 days: 2026-07-20 to 2026-08-14)

Site-wide totals (dimensionless aggregate, `totals_complete: true` — safe to use as-is):

| Clicks | Impressions | CTR | Avg. Position |
|---|---|---|---|
| 24 | 2,865 | 0.84% | 8.7 |

Row count: 362 individual query/page combinations. **Note:** per the guidance in this workflow, row-level clicks/impressions can be anonymized/omitted by Google for low-volume queries, so per-row sums (below) will not equal the totals above — only the totals block is authoritative for site-wide numbers.

### Top pages by impressions (aggregated from visible rows only, illustrative not exhaustive)

| Page | Clicks | Impressions |
|---|---|---|
| `/` (homepage) | 9 | 452 |
| `/blog/varanasi-airport-railway-to-assi-ghat-transfer-guide/` | 0 | 202 |
| `/blog/is-varanasi-safe-general-guide/` | 2 | 200 |
| `/blog/assi-ghat-vs-dashashwamedh-where-to-stay/` | 2 | 161 |
| `/blog/varanasi-solo-female-travelers-safety-travel-guide/` | 0 | 111 |
| `/blog/best-hostels-in-varanasi/` | 0 | 60 |
| `/gallery` | 0 | 22 |
| `/about` | 0 | 13 |
| `/contact` | 0 | 13 |

### Quick-win queries (meaningful impressions, zero clicks, rankable position)

| Query | Impressions | Position | Page |
|---|---|---|---|
| `hostels near assi ghat` | 60 | 13.9 | homepage |
| `is varanasi safe for women` | 50 | 7.5 | (blog, safety guide family) |
| `dormitory near assi ghat` | 17 | 11.4 | homepage |
| `mosaic hostel` (2nd ranking cluster) | 17 | 12.3 | split/duplicate ranking signal |

**Priority: High — CTR recovery.** These are the clearest low-effort wins in the whole dataset: page-1/page-2 rankings with real search volume and 0% CTR. `hostels near assi ghat` (pos 13.9, 60 impressions) and `is varanasi safe for women` (pos 7.5, 50 impressions) should get title/meta-description rewrites to earn clicks at their current rank, and modest on-page relevance work to push them from page 2 toward page 1.

**Note on brand query fragmentation:** `mosaic hostel` shows two separate ranking rows — one at position 7.7 (46 impressions, the expected homepage ranking) and one at position 12.3 (17 impressions, likely a different/weaker page or a stale ranking signal). This split for a branded query is unusual and worth checking — it can indicate URL canonicalization or duplicate-content dilution on a branded term Google should otherwise rank at position 1.

### Long-tail distance/transit query cluster (near-zero CTR, page 2+ rankings)

A large share of the 362 rows are hyper-specific "distance from X to Y" queries (e.g. "assi ghat to dashashwamedh ghat distance", "banaras station to assi ghat distance") ranking positions 30-45 with meaningful impressions (10-17 each) but zero clicks — these are informational/wiki-style queries the current blog content targets but doesn't rank competitively for. Low priority to chase individually; if the content strategy already targets these intentionally (per the `varanasi-airport-railway-to-assi-ghat-transfer-guide` and `assi-ghat-vs-dashashwamedh-where-to-stay` posts), this is a content-depth/backlink issue rather than a technical one — out of scope for this Google-API-only report.

### GSC Sitemaps

| Sitemap | Submitted | Errors | Warnings | URLs submitted |
|---|---|---|---|---|
| `sitemap.xml` | 2026-07-29 | 0 | 0 | 22 |

No sitemap errors. **Caveat per workflow guidance:** the Sitemaps API `contents[].submitted` count reflects submitted URLs only, not indexed count — cross-reference with URL Inspection (Section 2) for actual indexation truth. 22 submitted URLs is a small sitemap relative to the number of blog posts + pages visible in the crawl (17+ blog posts alone), suggesting the sitemap may not be capturing the full current site — worth auditing sitemap.xml generation against the live URL list.

---

## 4. GA4 Organic Traffic (property 507278393)

**28-day window (2026-07-20 to 2026-08-16): zero organic sessions recorded** (`organic`, `device`, `country`, and `top-pages` reports all returned empty result sets, no errors).

To confirm this wasn't a query/property misconfiguration, the same reports were re-run over a 90-day window, which did return data — confirming the GA4 property and query logic are both working correctly, and that the last 28 days are genuinely flat.

### 90-day organic traffic (2026-05-19 to 2026-08-16)

| Sessions | Users | Pageviews | Avg. daily sessions |
|---|---|---|---|
| 48 | 42 | 99 | 2.0 |

**The daily data shows the last organic session in this GA4 pull was 2026-06-26 — over 7 weeks with zero recorded organic sessions since.** This is the single most significant finding in this report.

Top organic landing pages (90-day):

| Landing page | Sessions | Bounce rate | Engagement rate |
|---|---|---|---|
| `/` | 39 | 30.8% | 69.2% |
| `/gallery` | 4 | 75.0% | 25.0% |
| `/varanasi-solo-female-travelers-safety-travel-guide` | 2 | 0.0% | 100.0% |
| `/contact-us` | 1 | 0.0% | 100.0% |

Device split (90-day): Mobile 30 sessions (46.7% bounce), Desktop 18 sessions (16.7% bounce) — desktop engagement is markedly better.
Country split (90-day): India 42, UK 3, US 3 — organic audience is almost entirely domestic.

**Priority: Critical.** GSC still shows impressions accruing through 2026-08-14 (2,865 impressions, 24 clicks in the last 28 days) but GA4 shows zero organic sessions since 2026-06-26. Two non-exclusive explanations to rule out:
1. **GA4 tracking regression** — check that the GA4 measurement tag/gtag.js is still firing on the live site (a recent deploy, CMP/consent-mode change, or CSP update could have silently broken tracking). This is the more likely cause given GSC clicks (24 in 28 days) don't reconcile with 0 GA4 organic sessions in the same window — those are two different real-world facts that should roughly agree.
2. Genuine traffic collapse — less likely given GSC clicks are still occurring.
**Action:** verify the GA4 tag is present and firing on a live page load (GA4 DebugView or browser network tab for a `collect` request) before doing any further GA4-dependent analysis — all top-pages/device/country GA4 numbers above are only reliable up to late June.

---

## Credential Tier Summary

| Service | Available | Method |
|---|---|---|
| PageSpeed Insights v5 | Yes | API key |
| CrUX / CrUX History | Yes (API works, no data returned — insufficient traffic) | API key |
| Search Console | Yes | OAuth (token auto-refreshed) |
| URL Inspection | Yes | OAuth |
| Indexing API | Yes (not exercised this run — read-only audit) | OAuth |
| GA4 Data API | Yes | OAuth |

No credential or permission errors encountered once the correct GSC property (`https://www.mosaichostels.com/`, the www variant) was used. The bare-domain property `https://mosaichostels.com/` is not verified/owned in this GSC account — do not use it for future GSC calls.

---

## Priority Summary

| Priority | Finding |
|---|---|
| Critical | GA4 shows zero organic sessions since 2026-06-26 despite GSC still recording clicks — verify GA4 tag is firing on the live site. |
| Critical | `/book-now` (booking page) is completely undiscovered by Google (GSC URL Inspection: "URL is unknown to Google"). |
| High | `/blog` index page also undiscovered by Google — may be limiting internal link equity to blog posts. |
| High | Apex domain `mosaichostels.com` redirects to `www.mosaichostels.com`, costing 780ms on mobile LCP (PSI opportunity). |
| High | CTR recovery on `hostels near assi ghat` (pos 13.9, 60 impr, 0 clicks) and `is varanasi safe for women` (pos 7.5, 50 impr, 0 clicks). |
| Medium | `/gallery` breadcrumb structured data fails rich-results validation (missing `item` field). |
| Medium | Sitemap only lists 22 URLs — audit against actual site URL count (17+ blog posts alone visible in GSC data). |
| Low | Branded query `mosaic hostel` shows a split ranking signal (pos 7.7 vs pos 12.3) — check for canonicalization/duplicate content. |
| Low | Mobile Lighthouse LCP (3.8s, lab data) is the weakest CWV proxy; desktop is solid. No field CrUX data available yet due to low traffic volume. |

No PDF report generated this run (data-collection pass only, per task scope — free APIs, no git commit). Offer to generate one via `google_report.py --type full` if a formatted deliverable is wanted.
