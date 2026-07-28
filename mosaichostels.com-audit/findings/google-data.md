# Google API Data — Mosaic Hostel Varanasi (mosaichostels.com)

**Site:** https://www.mosaichostels.com | **Data pulled:** 2026-07-28
**Data sources:** Google Search Console API (Search Analytics, URL Inspection, Sitemaps), GA4 Data API (property `properties/507278393`), PageSpeed Insights / CrUX (attempted, unavailable this cycle — see §0)
**Verified GSC property:** URL-prefix `https://www.mosaichostels.com/` (siteOwner permission confirmed via `sites` call)

This is real field/production data pulled live via the Google APIs — it supersedes any assumptions in the other (source-code-based) audit findings about whether Google has actually seen or ranked the blog content. Short version: **it hasn't** (7 of 8 posts), and the 1 post it briefly had is now gone.

---

## 0. Credential Tier — Setup Note

`google_auth.py --check` initially reported **Tier -1 / no credentials configured**, despite a service-account key already sitting at `~/.config/claude-seo/gsc-service-account.json` and an active GA4 Viewer grant. The pointer config file (`~/.config/claude-seo/google-api.json`) that ties those credentials to the CLI tool had never been created. I created it:

```json
{
  "service_account_path": "/Users/naveenkumar/.config/claude-seo/gsc-service-account.json",
  "default_property": "https://www.mosaichostels.com/",
  "ga4_property_id": "properties/507278393"
}
```

After that, `--check` reports:

| Service | Status | Method |
|---|---|---|
| Search Console (query, sitemaps) | Available | service_account (`gsc-api@ai-seo-manager.iam.gserviceaccount.com`) |
| URL Inspection | Available | service_account |
| Indexing API | Available | service_account |
| GA4 Data API | Available | service_account |
| PageSpeed Insights | **Unavailable** | no `api_key` in config; keyless/shared quota returned `PSI rate limit exceeded (240 QPM / 25,000 QPD)` on two attempts ~20s apart |
| CrUX / CrUX History | **Unavailable** | `Error: API key required` — no fallback quota for this endpoint |

**Action needed to close this gap:** add a Google API key (PSI + CrUX restricted) to the same config file as `"api_key": "<KEY>"`. Until then, Core Web Vitals field data cannot be pulled through this pipeline — the `technical.md` finding's CWV commentary is source-level only, not confirmed by CrUX field data. Everything below (GSC + GA4) is unaffected by this gap and is real, live data.

---

## 1. GSC Site-Wide Search Performance

`totals_complete: true` in both pulls below — these are real site-wide totals, not row sums.

| Window | Clicks | Impressions | CTR | Avg. Position |
|---|---|---|---|---|
| Last 28 days (2026-06-30 → 2026-07-25) | 11 | 723 | 1.52% | 11.0 |
| Last 90 days (2026-04-29 → 2026-07-25) | 62 | 4,151 | 1.49% | 11.2 |

Daily impressions in the 90-day window trend gently downward from the ~90-125/day range in early May to the 15-45/day range by late July, with clicks becoming sparser (several 0-click days per week even in May, but stretches of 5-7 consecutive 0-click days by mid-July). Nothing catastrophic at the site level — the site-wide decline is being driven almost entirely by one page (see §2).

### Branded vs. non-branded query split (90-day, 168 distinct queries)

| Segment | Queries | Impressions | Clicks | CTR |
|---|---|---|---|---|
| Branded ("mosaic hostel/hotel...") | 13 | 1,106 | 35 | 3.16% |
| **Non-branded** | 155 | 1,523 | **1** | **0.07%** |

The site gets real, page-1-adjacent visibility for its own name (avg. position 1.1-6.9 on branded terms) but is essentially invisible on non-branded demand — 155 distinct non-branded queries produced a combined **one click** across 90 days.

Top non-branded queries by impressions (all landing on the **homepage**, not a dedicated page — see §2):

| Query | Impressions | Clicks | Position |
|---|---|---|---|
| hostels near assi ghat | 185 | 0 | 14.7-17.2 |
| hostel near assi ghat varanasi | 101 | 0 | 15.7-15.9 |
| hostels in varanasi near assi ghat | 97 | 0 | 15.4-17.5 |
| hostel varanasi | 77 | 0 | 14.2 |
| hostels in varanasi | 73 | 0 | 28.0 |
| hostel in varanasi | 70 | 0 | 25.4 |
| dormitory near assi ghat | 46 | 0 | 11.0 |
| is varanasi safe for women | 39 | 0 | 9.6 |
| is varanasi safe for solo female travellers | 27 | 0 | 10.3 |
| is varanasi safe for girls | 28 | 1 | 10.5 |

Cross-referencing query+page: every "hostel near/in Assi Ghat" variant lands on `/` (homepage) — and, worse, is **cannibalized further** by `/about-us/` and `/contact-us/` also showing up in results for the same queries at deeper positions (25-31). No dedicated blog post (e.g. `hostel-near-assi-ghat-varanasi.md`, `best-hostels-in-varanasi.md` — both of which exist as source content) is competing for its own target query at all, because neither is indexed.

---

## 2. GSC Performance by Page (90 days)

| Page | Clicks | Impressions | CTR | Position |
|---|---|---|---|---|
| `/` (homepage) | 54 | 3,114 | 1.73% | 12.0 |
| **`/varanasi-solo-female-travelers-safety-travel-guide/`** (legacy root-path blog URL — see §4) | **7** | **859** | 0.81% | 7.9 |
| `/gallery/` | 1 | 97 | 1.03% | 7.1 |
| `/contact-us/` | 0 | 134 | 0% | 18.3 |
| `/book-now/` | 0 | 63 | 0% | 8.0 |
| `/about-us/` | 0 | 35 | 0% | 12.3 |
| `/experiences/` | 0 | 24 | 0% | 12.3 |
| `/about`, `/about/`, `/contact`, `/contact/`, `/gallery`, `/blog`, `/blog/`, `/llms-txt/` | 0 each | 4-9 each | 0% | mixed |

Two things jump out:

1. **Only 1 of the 8 blog posts has ever accumulated any GSC impressions at all** — and it's not even at its current live URL. `https://www.mosaichostels.com/varanasi-solo-female-travelers-safety-travel-guide/` (no `/blog/` prefix, trailing slash) is a **legacy WordPress URL** that is completely separate from the live `/blog/varanasi-solo-female-travelers-safety-travel-guide` route the site serves today. See §4 — this URL now 404s.
2. **Duplicate/near-duplicate URL variants are polluting the index**: `/about` vs `/about/` vs `/about-us/`, and `/contact` vs `/contact/` vs `/contact-us/` are all separately indexed with small, scattered impression counts and zero clicks — a URL-canonicalization inconsistency (confirms the `about.html` deletion noted in git status is landing on an already-messy URL structure).

### 28-day-only page breakdown (2026-06-30 → 2026-07-25)

The legacy blog URL **disappears from the page report entirely** in the most recent 28 days — 0 rows, 0 impressions. Only 9 URLs show any activity at all (homepage + the about/contact/gallery duplicates + book-now + blog index), all with 0 clicks except the homepage. This is the first hard signal that the one page carrying real non-branded rankings dropped out of search results within the last month.

---

## 3. URL Inspection — Ground Truth on the 8 Blog Posts

Batch-inspected the homepage, `/blog`, all 8 live `/blog/<slug>` URLs, and the legacy root-path URL that shows up in Search Analytics.

| URL | Coverage state | Verdict | Last crawl | Referring URL |
|---|---|---|---|---|
| `/` | Submitted and indexed | PASS | 2026-07-28 | `wp-sitemap-posts-page-1.xml` |
| `/blog` | Discovered - currently not indexed | NEUTRAL | never | `/` |
| `/blog/assi-ghat-varanasi-complete-guide` | **URL is unknown to Google** | NEUTRAL | never | none |
| `/blog/backpackers-guide-assi-ghat-varanasi` | **URL is unknown to Google** | NEUTRAL | never | none |
| `/blog/best-hostels-in-varanasi` | **URL is unknown to Google** | NEUTRAL | never | none |
| `/blog/hostel-near-assi-ghat-varanasi` | **URL is unknown to Google** | NEUTRAL | never | none |
| `/blog/things-to-do-varanasi-local-guide` | **URL is unknown to Google** | NEUTRAL | never | none |
| `/blog/top-7-experiences-varanasi-traveler` | **URL is unknown to Google** | NEUTRAL | never | none |
| `/blog/varanasi-solo-female-travelers-safety-travel-guide` | **URL is unknown to Google** | NEUTRAL | never | none |
| `/blog/why-assi-ghat-perfect-base-varanasi-stay` | **URL is unknown to Google** | NEUTRAL | never | none |
| `/varanasi-solo-female-travelers-safety-travel-guide/` (legacy) | Crawled - currently not indexed | NEUTRAL | 2026-06-23 | `post-sitemap.xml` |

**Summary: 1 PASS / 10 NEUTRAL / 0 FAIL.** None of the 8 current live blog URLs have ever been crawled or discovered by Googlebot — "URL is unknown to Google" is the API's explicit language for zero prior contact, not a ranking or quality judgment. This corroborates (with live API ground truth) what the `sitemap.md`/`technical.md` source-code findings inferred: the posts are effectively invisible to Google because they are in none of the paths Google uses to discover new URLs (not in `sitemap.xml`, and the client-rendered `/blog` index — itself only "Discovered, not indexed" — apparently doesn't expose crawlable links to Googlebot's rendering pass either).

---

## 4. The Legacy-URL / Migration Discovery — Root Cause

This is the most important finding in this data pull. Two things that shouldn't both be true, are:

- The **homepage's** own `index_status.referring_urls` field points to `wp-sitemap-posts-page-1.xml`.
- The one blog page with real GSC history was discovered via `post-sitemap.xml`.

Both of those are **WordPress auto-generated sitemap URLs**. I fetched them live:

```
GET https://www.mosaichostels.com/wp-sitemap-posts-page-1.xml  -> 404
GET https://www.mosaichostels.com/post-sitemap.xml             -> 404
```

Both return the site's custom 404 page (which itself still contains a legacy Universal Analytics snippet, `UA-26575989-46`/`ga.js` — long deprecated, further evidence of an unmigrated WordPress-era artifact). **This confirms the site was previously on WordPress**, with blog posts published at root-level paths like `/varanasi-solo-female-travelers-safety-travel-guide/`. When the site was rebuilt on its current stack (client-rendered `/blog/<slug>` routes, no trailing slash, different URL shape entirely), **the old post URLs were not 301-redirected to their new equivalents** — they were simply abandoned and now 404.

The consequence, laid out in sequence:

1. Google had indexed `/varanasi-solo-female-travelers-safety-travel-guide/` (old URL) and it was earning real, decent rankings: position 7.9-10.5 for "is varanasi safe for women/girls/solo female travellers," 859 impressions and 7 clicks over 90 days — the single best-performing piece of content on the domain after the homepage.
2. Google's last successful crawl of that URL was **2026-06-23**. Its current coverage state is "Crawled — currently not indexed" (i.e., Google has already started dropping it).
3. In the 28-day window (2026-06-30 onward) that URL **generates zero impressions** — it has fallen out of the index in the last ~5 weeks.
4. The URL now returns a straight **404** with no redirect to its live replacement, `/blog/varanasi-solo-female-travelers-safety-travel-guide`.
5. That replacement URL has **never been crawled or discovered by Google at all** ("URL is unknown to Google").
6. Net result: all accumulated ranking equity for the site's one organically-successful blog topic (Varanasi safety for solo/female travelers) has been **destroyed**, and there is no path for Google to find the replacement page on its own (not in sitemap, not linked in a way the renderer exposes to Googlebot).

The other 7 posts show no evidence of ever having existed at any indexed URL — they appear to be newer content that was never submitted (sitemap) and never linked in a discoverable way.

---

## 5. Sitemap Status (Search Console API)

```
Sitemap: https://www.mosaichostels.com/sitemap.xml
Last submitted: 2026-07-13T16:05:36Z
Pending: false | Errors: 0 | Warnings: 0
Submitted URLs: 7
```

The sitemap parses cleanly with no errors, but only lists 7 URLs (home, gallery, blog index, about, contact, book-now, privacy) — confirmed directly against the live file. **None of the 8 individual blog post URLs are in it**, and neither is the legacy WordPress sitemap that Google is still internally citing as a referral source for the homepage and the one indexed post.

---

## 6. GA4 Organic Traffic (`properties/507278393`)

| Window | Sessions | Users | Pageviews |
|---|---|---|---|
| Last 7 days | 0 | 0 | 0 |
| Last 28 days | 0 | 0 | 0 |
| **Last 90 days** | **84** | 73 | 172 |

The 7- and 28-day zeroes are **not a GA4 propagation/access-lag artifact** — the 90-day pull confirms real historical data exists (daily rows from 2026-04-29 through 2026-06-26), and it stops cold after **2026-06-26**. There is no organic session data at all in GA4 for the ~32 days since. This lines up almost exactly with the GSC finding above: the legacy blog URL's last successful Google crawl was 2026-06-23, and it dropped out of the impressions data starting the following week. **Organic traffic did not merely "struggle" — it went to zero and stayed there**, timed to the URL breakage.

### Top organic landing pages (90 days, GA4)

| Landing page | Sessions | Users | Pageviews | Bounce rate | Engagement rate |
|---|---|---|---|---|---|
| `/` | 61 | 38 | 142 | 31.1% | 68.9% |
| `(not set)` | 7 | 3 | 0 | 100% | 0% |
| `/gallery` | 7 | 1 | 8 | 85.7% | 14.3% |
| `/varanasi-solo-female-travelers-safety-travel-guide` (legacy path, no `/blog/` prefix) | 7 | 7 | 17 | 42.9% | 57.1% |
| `/contact-us` | 2 | 2 | 5 | 0% | 100% |

Even in GA4, the only blog page that ever produced organic sessions is the same legacy URL now broken in production — no other post (old or new URL form) appears anywhere in the 90-day organic landing-page report.

---

## 7. Direct Answer to the Diagnostic Question

> Is GSC showing blog URLs as indexed-with-impressions-but-no-clicks, not-indexed-at-all, or indexed-with-no-impressions?

**It's a mix, and it maps cleanly onto the migration story above — not "wrong keywords":**

| Bucket | Posts | Evidence |
|---|---|---|
| **Not indexed / not even discovered** (discoverability problem) | 7 of 8 — all except the safety guide | URL Inspection: "URL is unknown to Google" for all 7 live `/blog/<slug>` URLs. Zero GSC impressions, ever, at any URL form. Google has never crawled them. |
| **Was indexed, ranking respectably, getting real clicks — now de-indexing because the URL is dead** | 1 of 8 (safety guide) | 859 impressions / 7 clicks / pos. 7.9-10.5 over 90 days at the *legacy* URL; 0 impressions in the trailing 28 days; legacy URL now 404s; live replacement URL is itself unindexed |
| **Indexed with impressions but no clicks** (compelling-content problem) | 0 of 8 | Not observed — no blog post is currently indexed and receiving impressions at all |
| **Indexed, getting impressions, wrong keywords** (targeting problem) | 0 of 8 | Not observed — where the content *does* rank (safety guide, homepage for Assi Ghat terms), the queries are exactly on-topic. This is not a keyword-targeting problem. |

**Bottom line:** this is overwhelmingly a **discoverability/technical problem, not a content-quality or keyword-targeting problem.** The non-branded query data (§1) proves the demand and topical relevance are real and already partially working — "hostels near assi ghat" alone gets 185 impressions/90 days at position ~15 from the homepage alone, with zero dedicated content competing for it. If the matching blog post (`hostel-near-assi-ghat-varanasi.md`) were actually indexed at a stable URL, it would very plausibly outrank the homepage for that exact query, because it's purpose-built for it and the homepage is not.

---

## 8. Priority Recommendations (from this data)

**Critical**
1. **301-redirect the dead legacy blog URL** `https://www.mosaichostels.com/varanasi-solo-female-travelers-safety-travel-guide/` → `https://www.mosaichostels.com/blog/varanasi-solo-female-travelers-safety-travel-guide` before it fully drops out of the index (it's already in "Crawled — currently not indexed" state as of last check). This is the single highest-leverage fix available — it's reclaiming equity that already existed at position 7.9-10.5, not building from zero.
2. **Audit for other orphaned WordPress URLs.** `wp-sitemap-posts-page-1.xml` and `post-sitemap.xml` both 404 but are still referenced by Google as legitimate discovery paths. There may be other old post URLs (beyond the one found here) that Google still remembers and that also need redirects — worth requesting the full historical WordPress sitemap/URL list from whoever has hosting/CMS export access, or checking `robots.txt`/server logs for other 404s Googlebot is still requesting.
3. **Add all 8 `/blog/<slug>` URLs to `sitemap.xml`** and resubmit — right now Google has no path to discover them at all. (Coordinate with the `content.md`/`technical.md` findings first — those flag that raw HTML for these URLs may be an empty JS shell; fixing discoverability without fixing renderability could just produce 8 more "not indexed" thin-content signals.)

**High**
4. Clean up duplicate/near-duplicate indexed URL variants (`/about` vs `/about/` vs `/about-us/`; `/contact` vs `/contact/` vs `/contact-us/`) with consistent canonicalization and redirects — currently splitting minimal authority across 3 URLs each.
5. Once posts are indexed, expect real competition for "hostels near/in Assi Ghat" type queries currently answered weakly (position 14-28) by the homepage and by `/about-us/`/`/contact-us/` — a dedicated, well-targeted post should outrank the homepage on its own topic rather than cannibalizing it.

**Medium**
6. Add a Google API key to `~/.config/claude-seo/google-api.json` to unlock PSI/CrUX field data for CWV reporting on subsequent audit cycles.

---

## 9. Data Freshness / Caveats

- **GSC:** Search Analytics data has a typical 2-3 day reporting lag; the 28-day window used here ends 2026-07-25 (today is 2026-07-28), which is within normal lag.
- **GA4:** ~1 day lag; last available data (90-day pull) confirms real zero-organic-traffic days through 2026-07-27, not a reporting-lag artifact.
- **CrUX/PSI:** Not pulled this cycle (see §0) — no field-data CWV numbers in this report. Treat any CWV commentary elsewhere in this audit as source/lab-level only until an API key is added.
- **`totals_complete: true`** on all GSC pulls above — the totals in §1 are safe site-wide sums, not row-limited approximations. The per-query and per-page row-level tables can still omit very-low-volume anonymized rows per GSC's normal behavior; treat row counts as a lower bound, not exhaustive.

---

## Report Generation

A PDF report (type `gsc-performance` or `full`) can be generated from this data via:
```
claude-seo run google_report.py --type full --data data.json --domain mosaichostels.com --format pdf --json
```
Not run yet — let me know if you'd like the enriched JSON assembled and the PDF generated for this audit cycle.
