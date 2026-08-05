# Local SEO Audit — Mosaic Hostel Varanasi (mosaichostels.com)

Audit date: 2026-08-05
Scope: Full source review of all 8 top-level pages (`index`, `about`, `contact`, `book-now`, `gallery`, `blog.html`, `blog/index.html`, `privacy`) + 16 individual blog posts, plus `components/footer.html` and `components/site.js`. WebFetch was available this session and used to verify 3 live external sources: the rendered `/contact` page, the TripAdvisor listing, and the Google Maps CID URL (JS-rendered, no data returned — see Limitations).

This is a delta pass on top of two prior audits:
- `mosaichostels.com-audit/findings/local.md` (2026-07-28, scored 48/100 — most items since fixed, see below)
- `MAPS-ANALYSIS-mosaichostels.com.md` (2026-07-31, scored 58/100 website-readiness, GBP-live dimensions marked N/A — read first, not duplicated here)

**Confirmed closed since the 07-28 audit:** `blog/index.html`'s broken/generic `sameAs` links (JustDial bare homepage, truncated MakeMyTrip URL) are fixed — it now carries the same 10-entry citation array as every other page. The homepage's short 7-entry `sameAs` is fixed — `index.html` now has the full 10-entry array including `cleartrip` and `expedia`. `hasMap` (item #5 from the Maps report) is closed on 3 of 8 pages, but not site-wide (new finding below).

---

## Local SEO Score: 58 / 100 — Needs Work

| Dimension | Weight | Score /100 | Weighted | Notes |
|---|---|---|---|---|
| GBP Signals | 25% | 60 | 15.0 | CID consistently linked (`sameAs`, `hasMap`, review/directions deep-links); one live Maps embed on `/contact`; primary category, hours-as-published, photos, posts, Q&A all unverifiable from JS-rendered Maps page |
| Reviews & Reputation | 20% | 25 | 5.0 | Schema `aggregateRating` on `index.html` claims **200 reviews**; live TripAdvisor shows **8 reviews** (4.9★, matches) — a 25x count mismatch that risks a structured-data manual action |
| Local On-Page SEO | 20% | 80 | 16.0 | Strong hyperlocal keyword pairing ("Budget Hostel near Assi Ghat" in title/H1/meta), FAQ schema mirrors visible FAQ, 15 geo-relevant blog posts reinforce neighborhood entities |
| NAP Consistency & Citations | 15% | 67 | 10.05 | Name/phone/schema-address consistent on 7/8 pages + footer + all 16 blog posts; `privacy.html`'s **visible** contact-block address is wrong (wrong postal code, missing locality) |
| Local Schema Markup | 10% | 60 | 6.0 | Correct `Hostel` subtype, 5-decimal geo, `openingHoursSpecification` — but `hasMap` only on 3/8 pages, `image` is still a single string (not an array) on every page, and the fabricated `aggregateRating` (above) lives here too |
| Local Link & Authority | 10% | 60 | 6.0 | 8 real OTA/TripAdvisor citations in every page's `sameAs`; no Facebook Page, no Bing Places, no local press — unchanged from prior audit, still can't assess backlink profile without DataForSEO |
| **Total** | 100% | | **58.05 ≈ 58** | |

---

## 1. Business Type & Industry Vertical

- **Business type: Hybrid, leaning brick-and-mortar.** Full street address visible in every page footer, live Google Maps `<iframe>` embed on `/contact` (confirmed present and pointing at the correct place ID — see §2), "Get Directions" dialog present. No service-area language; this is correctly modeled as a fixed-location business.
- **Industry vertical: Hospitality — Hostel**, a `LodgingBusiness` subtype. Signals: room types, check-in/out times, amenities, direct-booking CTA, 8 OTA listings. `Hostel` is the correct schema `@type` (not the deprecated/generic `LocalBusiness`).

---

## 2. NAP Consistency Audit

### Core NAP — source comparison

| Source | Name | Street Address | Phone | Verdict |
|---|---|---|---|---|
| `index`, `about`, `contact`, `book-now`, `gallery`, `blog.html`, `blog/index.html` footers (visible HTML) | Mosaic Hostel | B1/85C, Assi Ghat Road, Anandbagh, Varanasi, UP 221005 | +91 91254 92225 | Consistent |
| `Hostel` JSON-LD, all 8 pages | Mosaic Hostel Varanasi | B1/85C, Assi Ghat Road, Anandbagh / Varanasi / Uttar Pradesh / 221005 / IN | +91-9125492225 | Consistent |
| 16 individual blog post footers | Mosaic Hostel | B1/85C, Assi Ghat Road, Anandbagh, Varanasi, UP 221005 | +91 91254 92225 | Consistent |
| `contact.html` Maps `<iframe>` embed | "Mosaic Hostel Varanasi" (label) | place ID `0x398e31ef166d9b91:0x96411370098acc3b` → decodes to CID `10826956351092739131` | — | **Matches** the CID used everywhere else in `sameAs`/`hasMap` — confirmed via hex→decimal conversion |
| **`privacy.html` visible contact block** | — | **"B1/85C Assi Ghat Road, Varanasi 221001, India"** | +91 91254 92225 (correct) | **Discrepancy — wrong postal code (221001 vs 221005), missing "Anandbagh" locality** |

**Finding (High) — `privacy.html` visible address is wrong, confirmed live.** Fetched the rendered page directly: the Contact-Us block under the Privacy Policy shows `B1/85C Assi Ghat Road, Varanasi 221001, India` — a different postal code than the correct `221005` used everywhere else, and it drops the `Anandbagh` locality entirely. The link's `onclick` handler (`openMapsDialog`) still points to the correct CID/address internally, so users who click through land in the right place — but the visible text itself is a genuine NAP inconsistency an AI crawler or citation-scraper could pick up. `privacy.html`'s own JSON-LD `Hostel` block (line 36-40) has the *correct* address — only the human-readable paragraph text is wrong. Single-line fix.

**Finding (Low) — `privacy.html` `sameAs` is 2 entries short.** It carries 8 of the canonical 10 links (missing Cleartrip and Expedia), while every other page has all 10. Low impact since Privacy is not a page search engines weight for local entity signals, but worth aligning for consistency.

---

## 3. GBP Optimization Checklist

| Signal | Status | Detail |
|---|---|---|
| CID present & consistent | ✅ | `10826956351092739131`, used in `sameAs`, `hasMap`, `openMapsDialog()`, `openGoogleReview()` in `components/site.js` |
| Maps `<iframe>` embed | ⚠️ Partial | Present on `contact.html` only; not on `about.html`, `index.html`, or `book-now.html` where directions-intent traffic also lands |
| `hasMap` schema property | ⚠️ Partial | Present on `index.html`, `about.html`, `contact.html` only — **missing on `book-now.html`, `gallery.html`, `blog.html`, `blog/index.html`, `privacy.html`** (5 of 8 pages). Item #5 from the Maps report is only partially closed. |
| Review deep-link CTA | ✅ | `openGoogleReview()` opens the CID Maps URL directly |
| Primary GBP category | ❌ Unverifiable | Google Maps CID URL is JS-rendered client-side (empty on fetch) — still requires manual dashboard login or DataForSEO, as flagged in the prior report |
| Live review count/rating on GBP | ❌ Unverifiable | Same JS-rendering limitation |
| Photos, Posts, Q&A, attributes | ❌ Unverifiable | Requires GBP dashboard login or DataForSEO `business_listings_search` |
| Facebook Page in `sameAs` | ❌ Missing | Still open from prior report |
| Bing Places / Apple Business Connect | ❌ Unverified | No API access; manual claim still recommended |

---

## 4. Review Health Snapshot

| Metric | Value | Source |
|---|---|---|
| TripAdvisor rating | 4.9 / 5 | Live-fetched `tripadvisor.com` listing page, confirmed |
| TripAdvisor review count | **8 reviews** | Live-fetched listing page ("#43 of 244 Specialty lodging in Varanasi") |
| On-page stat display | "4.9 ★ Tripadvisor Rating" | `index.html` and `about.html`, correctly attributed and linked to TripAdvisor — accurate |
| Schema `aggregateRating` (`index.html` only) | `ratingValue: 4.9`, **`reviewCount: 200`** | `Hostel` JSON-LD, no `itemReviewed`/source attribution |
| Google review count/velocity | Unverifiable | GBP CID page is JS-rendered; needs DataForSEO or manual dashboard check |

**Finding (Critical) — fabricated/stale `reviewCount` in schema, live-verified mismatch.** `index.html`'s `Hostel` schema carries `"aggregateRating": {"ratingValue": "4.9", "reviewCount": "200"}`. The `4.9` matches the live TripAdvisor rating, but TripAdvisor currently shows **8 reviews**, not 200 — a 25x discrepancy. This number isn't traceable to any visible on-page count (Google review count also can't be confirmed, but 200 total across TripAdvisor+Google+OTAs combined seems implausible for a listing ranked #43/244 with only 8 TripAdvisor reviews). The prior Maps-analysis report (§8) explicitly recommended **not** adding `aggregateRating` to this schema at all, on the grounds that "Google disregards self-published review markup on your own domain; it only trusts reviews it collects directly." That recommendation was not followed — worse, an unverifiable number was added. This is also inconsistent: `about.html`, `contact.html`, `book-now.html`, `gallery.html`, `blog.html`, and `blog/index.html` all use the identical `Hostel` schema block **without** `aggregateRating` — only `index.html` has it. Recommend either removing it or replacing `200` with the actual, currently-accurate combined/Google review count, and applying the same choice consistently across all 8 pages rather than leaving one page as an outlier.

---

## 5. Local Schema Validation

**Type:** `Hostel` (correct `LodgingBusiness` subtype) on all 8 top-level pages. `BlogPosting` + `FAQPage` on individual blog posts (appropriate — no `LocalBusiness` schema needed there).

| Property | Status | Detail |
|---|---|---|
| `name`, `address` (required) | ✅ | Present, consistent, correct on all 8 pages |
| `geo` (5-decimal precision) | ✅ | `25.28726, 83.00316` — identical on every page, correct precision |
| `telephone` | ✅ | `+91-9125492225` consistent |
| `url` | ✅ | Present, consistent |
| `openingHoursSpecification` | ✅ | Present on 7/8 pages (missing `checkinTime`/`checkoutTime` on `privacy.html` only — low impact, Privacy isn't a conversion page) |
| `hasMap` (recommended) | ⚠️ | 3/8 pages only (see §3) |
| `image` (recommended, array) | ❌ Still open | Single string (`IMG_1928.JPG`) on **every** page, not an array. This was flagged in the prior Maps report (§8) and is still unaddressed — same single photo referenced sitewide. |
| `aggregateRating` | ⚠️ New issue | Present on `index.html` only, with an unverified/mismatched count (§4) — inconsistent with the other 7 pages and contradicts the prior report's explicit recommendation against adding it |
| `@id` | ⚠️ Inconsistent | Present on `index.html` (`.../`) and `book-now.html` (`.../book-now`) only; absent on `about`, `contact`, `gallery`, `blog.html`, `blog/index.html`, `privacy` — minor, helps entity disambiguation when present everywhere |

---

## 6. Local On-Page Relevance Signals

- Title/H1/meta pairing "Budget Hostel near Assi Ghat" on `index.html` — strong, unchanged from prior audit.
- `FAQPage` schema mirrors a visible on-page FAQ section (`<details>` elements) — good practice, avoids the "hidden structured data" red flag.
- 15 published blog posts are all geo-anchored to Varanasi/Assi Ghat neighborhoods (Sarnath day trip, Assi Ghat vs Dashashwamedh, transfer guides, itineraries) — this is a meaningful local-relevance and topical-authority signal that a single-location competitor without a blog wouldn't have. Each post links back to `/book-now` and carries the same NAP footer, reinforcing entity consistency at scale (16 pages × correct NAP = a strong consistency signal, undercut only by the one `privacy.html` outlier).
- No dedicated "neighborhoods we serve" or multi-location pages — not applicable, single physical location.

---

## 7. Citation Presence

Tier-1 US directories (Yelp, BBB) are not relevant citation sources for an Indian hospitality business — correctly out of scope, as in the prior report. Relevant tier-1 sources for this vertical/geography are the travel OTAs, which are present and consistent:

| Platform | Status | Live-verified? |
|---|---|---|
| Google Maps/GBP | ✅ Claimed, CID consistent everywhere | Embed confirmed live on `/contact`, CID confirmed matching via hex decode |
| TripAdvisor | ✅ Listed, live-verified 4.9★/8 reviews | Fetched directly, confirmed |
| Booking.com, Hostelworld, MakeMyTrip, Agoda, Goibibo, Cleartrip, Expedia | ✅ All in `sameAs` on 7/8 pages (`privacy.html` missing 2) | Not individually live-checked this pass |
| Instagram | ✅ In `sameAs` | — |
| Facebook | ❌ Still missing | Unchanged from prior audit |
| Bing Places, Apple Business Connect, OSM | ❓ Unverified | No API access; unchanged from prior audit |

---

## 8. Top 10 Prioritized Actions

| # | Priority | Action | Why |
|---|---|---|---|
| 1 | **Critical** | Fix or remove the `reviewCount: 200` in `index.html`'s `aggregateRating` — live TripAdvisor shows 8 reviews, a 25x mismatch | Fabricated/unverifiable review counts in schema risk a Google structured-data manual action; also directly contradicts the prior audit's explicit "do not add this" recommendation |
| 2 | **High** | Fix the visible address text in `privacy.html`'s contact block (`221001` → `221005`, add "Anandbagh") | Confirmed-live NAP inconsistency; the only page (of 8 + 16 blog posts) with wrong visible address text |
| 3 | **High** | Log into GBP dashboard, confirm primary category is "Hostel" and check live review count/velocity | Still unverifiable from source/WebFetch (Maps CID page is JS-rendered) — carried over as the #1 unresolved item from the 07-31 report |
| 4 | **Medium** | Add `hasMap` to the remaining 5 pages (`book-now.html`, `gallery.html`, `blog.html`, `blog/index.html`, `privacy.html`) | Item #5 from the Maps report is only 3/8 closed, not sitewide |
| 5 | **Medium** | Expand `image` from a single string to an array of 3-5 photos in the `Hostel` schema, across all 8 pages | Still open since the 07-31 report; Google favors multiple images for rich results |
| 6 | **Medium** | Decide sitewide: either add a verified `aggregateRating` everywhere or nowhere — don't leave `index.html` as the only page carrying one | Inconsistent schema across near-identical pages looks unintentional/erroneous to crawlers |
| 7 | **Medium** | Add the Maps `<iframe>` embed to `about.html` and `index.html`, not just `/contact` | Reinforces address/geo relevance on the two highest-traffic pages |
| 8 | **Low** | Add Cleartrip and Expedia to `privacy.html`'s `sameAs` to match the other 7 pages | Minor citation-array inconsistency |
| 9 | **Low** | Add `checkinTime`/`checkoutTime` to `privacy.html`'s schema (present everywhere else) | Completeness/consistency only, low traffic-impact page |
| 10 | **Low** | Add Facebook Page to `sameAs` if one exists; claim Bing Places for Business | Unchanged from prior audit, still free and easy |

---

## 9. Limitations Disclaimer

WebFetch was available and used this session (unlike the 07-31 Maps-focused audit, which had none). It successfully verified the live rendered `/contact` page and the live TripAdvisor listing. It **could not** retrieve data from the Google Maps CID URL — that page is client-side/JS-rendered and returned no listing content on fetch. As a result, the following remain unverified, consistent with both prior reports:

- Primary GBP category (single strongest local ranking factor — still needs manual dashboard confirmation)
- Live Google review count, rating, and review velocity/18-day-rule check
- GBP photo count/recency, Posts cadence, Q&A, attributes
- Geo-grid rank / Share of Local Voice, competitor radius mapping
- Bing Places / Apple Maps / OpenStreetMap listing status
- Backlink/citation authority profile beyond the `sameAs` links already visible in source

These require either a DataForSEO MCP connection (`business_data_business_listings_search`, `serp_organic_live_advanced`) or manual GBP dashboard login. Everything else in this report — all 8 top-level pages, 16 blog posts, footer, and `site.js` — was fully read and cross-checked, plus 3 live external fetches (contact page, TripAdvisor, Maps CID).
