
# Local SEO Audit — Mosaic Hostel Varanasi (mosaichostels.com)

Audit date: 2026-07-28
Scope: Source code audit of the repository at `/Users/naveenkumar/Projects/Website` (homepage, book-now, contact, gallery, blog index + 7 blog posts, privacy, and the deleted-but-still-referenced about page), plus limited live web verification (OTA/GBP pages block automated fetch — see Limitations).

---

## Local SEO Score: 48 / 100 — Needs Significant Work

| Dimension | Weight | Score | Weighted | Notes |
|---|---|---|---|---|
| GBP Signals | 25% | 45/100 | 11.3 | Real Maps embed + place ID exist; no on-site reinforcement (no review CTA, no GBP deep link, category unverifiable) |
| Reviews & Reputation | 20% | 35/100 | 7.0 | Aggregate-only, static, unverifiable count; on-page review showcase was built 6x then deleted; zero live social proof |
| Local On-Page SEO | 20% | 50/100 | 10.0 | Strong hyperlocal keyword strategy sitewide, undercut by 3 broken/missing "Assi Ghat" money pages and a deleted About page |
| NAP Consistency & Citations | 15% | 65/100 | 9.75 | Name/Address/Phone text is consistent everywhere checked; `sameAs` completeness and a legacy duplicate file are not |
| Local Schema Markup | 10% | 55/100 | 5.5 | Correct `Hostel` type, 5-decimal geo, good amenities — but JSON-LD is **invalid/unparseable** on 2 of 7 blog pages |
| Local Link & Authority | 10% | 40/100 | 4.0 | 8 real OTA citations exist; no local press/tourism links; two of the strongest link-worthy blog assets are broken |
| **Total** | 100% | | **47.55 ≈ 48** | |

---

## 1. Business Type & Industry Vertical

- **Business type: Hybrid**, leaning brick-and-mortar. Full street address (`B1/85C, Assi Ghat Road, Anandbagh, Varanasi, UP 221005`) is visible in every footer, a live Google Maps `<iframe>` embed is present on `/contact`, and a "Get Directions" dialog exists. There is no "we come to you" / service-area language — guests travel to a fixed physical location, which is the correct model for a hostel.
- **Industry vertical: Home/Hospitality — Hostel** (a `LodgingBusiness` subtype). Signals: room types (dorm/private), check-in/check-out times, amenities (WiFi, lockers, kitchen, rooftop), direct-booking CTA, and listings on Booking.com/Hostelworld/Agoda/MakeMyTrip/Goibibo/Cleartrip/TripAdvisor/Expedia.
- **Competitive reality (per brief):** the hostel is fighting on two fronts — other independent hostels near Assi Ghat, and its own OTA listings (Booking.com, Hostelworld, etc.), which usually outrank a small operator's own domain for "hostel near Assi Ghat" / "budget stay Varanasi" queries. This context shapes several recommendations below (own the long-tail/branded and hyper-specific queries the OTAs can't target as precisely).

---

## 2. NAP Consistency Audit

### Core NAP (Name / Street Address / Phone) — text comparison across sources

| Source | Name | Street Address | Phone |
|---|---|---|---|
| Homepage footer (visible HTML) | Mosaic Hostel | B1/85C, Assi Ghat Road, Anandbagh, Varanasi, UP 221005 | +91 91254 92225 |
| Contact page — Find Us card (visible HTML) | — | B1/85C, Assi Ghat Road, Anandbagh, Varanasi, Uttar Pradesh 221005 | — |
| `Hostel` JSON-LD (index, book-now, contact, gallery, blog, privacy) | Mosaic Hostel Varanasi | B1/85C, Assi Ghat Road, Anandbagh / Varanasi / Uttar Pradesh / 221005 / IN | +91-9125492225 |
| `Organization` JSON-LD (contact page) | Mosaic Hostel Varanasi | B1/85C, Assi Ghat Road, Anandbagh / Varanasi / Uttar Pradesh / 221005 / IN | +91-9125492225 |
| WhatsApp links (`wa.me/919125492225`) | — | — | 919125492225 |
| Google Maps embed CID (`0x398e31ef166d9b91:0x96411370098acc3b`) | "Mosaic Hostel Varanasi" (label in iframe URL) | matches lat/long 25.2872587 / 83.0031634 | — |

**Finding (Info/Positive):** Core NAP text is highly consistent across every page and schema block checked. Only cosmetic variance exists ("UP" vs "Uttar Pradesh"), which is not a real discrepancy risk.

**Finding (High) — `sameAs` / citation array inconsistency across pages.** The `sameAs` array (which functions as the site's citation/entity-linking signal) is **not the same on every page**:

| Page | `sameAs` entries | Missing vs. canonical (9) |
|---|---|---|
| `book-now.html`, `contact.html`, `gallery.html`, `blog.html`, `privacy.html`, `about.html` (last committed) | 9 (Instagram, Booking, Hostelworld, TripAdvisor, MakeMyTrip, Agoda, Goibibo, Cleartrip, Expedia) | none |
| **`index.html` (homepage)** | 7 | **Cleartrip, Expedia missing** |
| **`blog/index.html`** (legacy duplicate blog page, see §7) | 5, and **wrong URLs**: `justdial.com/` (bare homepage, no listing), `makemytrip.com/hotels/` (truncated, no property slug), `agoda.com/` and `goibibo.com/` (bare homepages, not the actual listing pages used elsewhere) | Instagram, Hostelworld, Cleartrip, Expedia missing; 3 of the 5 present are broken/generic |

The homepage is the page most likely to be crawled and treated as the canonical entity page — it should carry the fullest, not a partial, citation list. The `blog/index.html` file is actively harmful: it associates the business's structured data with dead-end generic OTA homepages and an incomplete JustDial reference, which weakens rather than strengthens the citation graph if this file is served instead of (or alongside) `blog.html`.

---

## 3. LocalBusiness / Hostel Schema Validation

**Type used:** `Hostel` (correct — a proper `LodgingBusiness` subtype, not a generic/deprecated `LocalBusiness`). Good choice.

| Property | Status | Notes |
|---|---|---|
| `name` | Present | Consistent |
| `address` (PostalAddress) | Present | Consistent, all sub-fields populated |
| `telephone` | Present | Consistent E.164-style format |
| `url` | Present | — |
| `geo` | Present, **5-decimal precision** | `25.28726, 83.00316` — meets best-practice precision |
| `openingHoursSpecification` | Present | 00:00–23:59 all week, matches "24/7 Check-in" amenity claim |
| `checkinTime` / `checkoutTime` | **Inconsistent** | Present on book-now, contact, gallery, blog, privacy, about; **missing on the homepage (`index.html`)** — the page most likely to be treated as canonical |
| `priceRange` | Present | `₹500-₹2000` |
| `amenityFeature` | Present, good detail | WiFi, AC, hot water, lockers, kitchen, rooftop, 24/7 check-in |
| `aggregateRating` | Present | `4.9` / `60` reviews — **only an aggregate, see §4** |
| Individual `Review` objects | **Absent everywhere** | No `review` array anywhere in the codebase — only `aggregateRating` |
| `sameAs` | Present but **inconsistent**, see §2 | |

**Finding (Critical) — Invalid JSON-LD on 2 of 7 blog posts.** `blog/hostel-near-assi-ghat-varanasi/index.html` and `blog/backpackers-guide-assi-ghat-varanasi/index.html` contain `BlogPosting` JSON-LD with literal `\'` escape sequences (e.g. `"headline":"Backpacker\'s Complete Guide..."`). `\'` is **not a valid JSON escape sequence** (JSON only permits `\" \\ \/ \b \f \n \r \t \uXXXX`). Verified by parsing both blocks with a JSON parser — both fail:
```
blog/hostel-near-assi-ghat-varanasi/index.html: Invalid \escape: line 1 column 240
blog/backpackers-guide-assi-ghat-varanasi/index.html: Invalid \escape: line 1 column 78
```
Google's Rich Results parser will silently discard this block entirely — these two pages currently emit **zero valid structured data**. This is a templating/generation bug (JS-escaped strings written directly into static HTML without un-escaping) and very likely affects the title tag, meta description, and og:description on the same two pages, all of which show the same raw `\'` artifact.

**Finding (High) — Same two pages have no rendered content at all.** Both files are **32 lines long, end immediately after `</head>` with no `<body>` content** — no nav, no article text, no footer. A visitor or Googlebot landing on `/blog/hostel-near-assi-ghat-varanasi` or `/blog/backpackers-guide-assi-ghat-varanasi` sees a blank page. These are precisely the two URLs whose slugs most directly target the client's stated priority query ("hostel near Assi Ghat"). This looks like an incomplete migration — a companion markdown source (`/blogs/*.md`) likely exists but was never rendered into the static HTML the way the other 5 posts were (compare: `why-assi-ghat-perfect-base-varanasi-stay/index.html` is fully built with ~500 words of genuinely hyperlocal content).

**Finding (Medium) — Referenced blog post 404s.** `blog.html`'s `CollectionPage` schema `mainEntity` list and `components/blog-renderer.js`'s `getAllBlogSlugs()` both reference `things-to-do-varanasi-local-guide`, but no `blog/things-to-do-varanasi-local-guide/` directory or page exists on disk (only a source markdown file `/blogs/things-to-do-varanasi-local-guide.md` exists, never rendered to HTML). This is a broken internal link surfaced in the site's own structured data.

**Finding (Low) — Static `aggregateRating` never varies.** `4.9` / `60` is hardcoded identically across every page and every commit touched in this repo's history. Git history shows **six separate attempts** to pull *live* Google reviews (CORS-proxy fetch, Google Places API, an embedded Maps widget) before the team gave up and hardcoded the aggregate and then deleted the review UI entirely (see §4). A number that never updates, sourced from no visible citation, is a plausibility risk if a visitor cross-checks it against the actual GBP/OTA listings — recommend re-verifying 4.9/60 against live Google Business Profile and OTA dashboards now, and building a lightweight manual (not automated-scrape) update process, e.g. updating the number once a month by hand from the GBP dashboard.

---

## 4. Review Health Snapshot

- **Displayed rating/count:** 4.9 ★ / 60 reviews (schema `aggregateRating` on every page; also surfaced as a homepage stat-band tile "4.9 ★ Average Rating").
- **Individual review schema:** None. No `Review` objects, no reviewer names/dates/text in structured data.
- **On-page review showcase: none — and this is a regression, not an oversight.** Git history shows a full "What Guests Say" / "Real Reviews from Real Travellers" section existed on the homepage and went through this sequence:
  1. `92ca181`/`2ec5179` — static hardcoded testimonial cards (3 quotes, attributed to **"Priya S., Mumbai"**, **"James L., London"**, **"Aiko T., Tokyo"** — first name + initial only, no dates, no source link, no photo — i.e., **unverifiable, generic-sounding placeholder testimonials** that carried real trust/E-E-A-T risk if ever scrutinized as fabricated).
  2. `65378ef` — replaced with an "official" Google Maps embed.
  3. `9960c2a` — replaced with styled cards claiming "Verified Reviews from Google" badge, while still showing the same 3 unverifiable local quotes (a "Google Verified" badge on unverified content is itself a trust-signal risk).
  4. `fd6e50c` / `13c1aaa` / `1c1aaa`-family commits — attempted live fetch via a third-party CORS proxy (`api.allorigins.win`) and the Google Places API, both fragile/unofficial patterns unsuitable for production.
  5. `a39f544` (2026-07-06, ~3 weeks before this audit) — **the entire reviews section was deleted**, leaving only the small aggregate stat tile.
- **Net result today:** the homepage has **zero on-page social proof** beyond a bare "4.9 ★" number with no context, no names, no platform attribution, and no way for a visitor to click through and verify it.
- **Review velocity / "18-day rule":** Cannot be assessed from source code — this requires live GBP review timestamps. Flagged as a **Limitation** (see §9). Given the business only opened in 2025, review count and velocity should be actively monitored; a hostel this new is exactly the profile most vulnerable to a ranking cliff if review velocity stalls for 3+ weeks.
- **Review solicitation:** No "Leave us a review" / "Rate us on Google" CTA found anywhere on the site (homepage, contact, book-now, footer, or post-stay touchpoints like the WhatsApp/email confirmations referenced in copy). This is a significant missed opportunity — the site already has a working WhatsApp channel that could carry a post-checkout review-request message and a direct GBP review link.
- **Response-to-reviews pattern:** Cannot be assessed without live GBP/OTA access (see Limitations).

---

## 5. GBP (Google Business Profile) Signals Detected On-Site

| Signal | Status |
|---|---|
| Maps embed (iframe) | Present on `/contact` only, with a real CID/place ID (`0x398e31ef166d9b91:0x96411370098acc3b`) matching the geo-coordinates in schema — good, this confirms a real, claimed GBP listing exists |
| "Get Directions" link | Present (`openMapsDialog()` in `components/site.js`), but it builds a generic `https://maps.google.com/?q=<address text>` search link rather than linking to the specific GBP place (the place ID is already in the codebase, in the iframe, and is not reused here) — a missed opportunity to send users straight to the verified listing (and its reviews) |
| "Leave a review" deep link | **Absent** |
| GBP Posts indicator | Not surfaced/not detectable from source |
| Photo evidence tied to GBP | Not surfaced — the Gallery page hosts its own 21 photos independently; there's no cross-reference to "as seen on our Google listing" |
| Primary GBP category correctness | **Cannot verify from source** — this is the single highest-weighted local ranking factor (Whitespark 2026, score 193) and the highest-weighted negative factor if wrong (score 176). Requires direct GBP dashboard check. |
| NAP match between GBP and site | Address/phone in the Maps embed's coordinates match the schema; full cross-check requires live GBP pull (Limitation) |

---

## 6. Citation Presence (Tier 1 for this vertical)

For a hostel, the OTA listings **are** the Tier-1 hospitality citations (more relevant here than BBB/Yelp, which are thin-to-absent for Indian hospitality businesses). Status:

| Platform | Present in canonical `sameAs` | Notes |
|---|---|---|
| Google Business Profile | Implied (Maps embed CID) | Direct profile URL never linked from the site |
| Booking.com | Yes | Full listing URL |
| Hostelworld | Yes | Full listing URL |
| Agoda | Yes | Full listing URL (canonical pages) / **broken bare-domain link in `blog/index.html`** |
| TripAdvisor | Yes | Full listing URL |
| MakeMyTrip | Yes | Full listing URL (canonical pages) / **broken/truncated link in `blog/index.html`** |
| Goibibo | Yes | Full listing URL (canonical pages) / **broken bare-domain link in `blog/index.html`** |
| Cleartrip | Yes (canonical pages only) | **Missing from homepage and `blog/index.html`** |
| Expedia | Yes (canonical pages only) | **Missing from homepage and `blog/index.html`** |
| Instagram | Yes | Social profile, not a directory citation but reinforces entity |
| JustDial (major India local directory) | **No real listing** — only a stray bare-homepage URL in the broken legacy `blog/index.html` file | Recommend a proper JustDial Free/paid listing — high-value for the domestic "budget stay Varanasi" searcher persona named in the brief |
| Sulekha / IndiaMART / other India-specific directories | Not present anywhere | Same rationale as JustDial |
| BBB | N/A for this market/vertical | Not a meaningful signal for an Indian hostel |
| Yelp | Not present | Low priority in this market, optional |

**Net assessment:** OTA citation coverage is genuinely strong (8 major global platforms), which is good baseline entity consistency. The gap is (a) inconsistent completeness of that same list across the site's own pages/schema, (b) zero India-specific local-directory presence beyond a broken placeholder, and (c) no direct link from the site to the GBP profile itself.

---

## 7. Location Page Quality

Single physical location — the multi-location doorway-page/unique-content checks in the brief do not apply in their usual form. However, an equivalent duplicate-content issue exists:

**Finding (Medium) — Duplicate/legacy blog index page.** `blog.html` (root) and `blog/index.html` are two different files with overlapping purpose (both are the "blog listing" page, both carry `Hostel` + `BreadcrumbList`-adjacent schema). `blog/index.html` is stale: missing favicons, missing `og:type`/`og:site_name`, missing `checkinTime`/`checkoutTime`, and — critically — carrying the broken/generic `sameAs` list documented in §2 and §6. If both are reachable/indexable (`/blog` vs `/blog/`), this is a duplicate-content and duplicate-schema situation that dilutes rather than reinforces the entity's local signals. Recommend deleting `blog/index.html` (or 301-redirecting it to `/blog`) and keeping a single canonical source.

---

## 8. Local Content Signals: Does the Site Reinforce Assi Ghat Specifically?

**Positive:** The site's hyperlocal content strategy, where it works, is genuinely good and well above what most small hostel sites do:
- Titles/meta descriptions across the site consistently say "near Assi Ghat," not just "in Varanasi."
- The (currently deleted, see §9) About page had strong hyperlocal copy: *"We sit steps from Assi Ghat — the southern anchor of Varanasi's waterfront."*
- Two fully-built blog posts are excellent, specific, Assi-Ghat-only content, not generic Varanasi filler: `why-assi-ghat-perfect-base-varanasi-stay` (geography: "about 3 km south of the busy Dashashwamedh area," proximity to BHU, the Subah-e-Banaras sunrise ceremony, neighbourhood safety profile) and `assi-ghat-varanasi-complete-guide`. This is exactly the "dedicated service/topical page" pattern called out in the brief as the #1 local organic ranking factor and #2 AI-visibility factor.
- Homepage copy: "Situated steps from the Ghats," "Watch the Ganga Aarti from our rooftop" — reinforces geographic specificity without being generic.

**Negative — and this is the single biggest content gap:**
- **The About page (`about.html`) — the page carrying the richest hyperlocal narrative, the team bio, and the founding story — currently does not exist on disk.** `git status` shows it as a deleted, uncommitted working-tree change (`D about.html`), alongside deletion of `styles/global.css` (the entire site's stylesheet). Every single page's navbar and footer (all 8+ HTML files checked) still link to `/about`. If this state is deployed as-is, `/about` 404s sitewide and every other page renders unstyled (no CSS at all). This must be resolved (restore the file, or confirm the deletion was intentional as part of an in-progress migration) before anything else in this report is actioned.
- The two most directly "money-keyword" blog posts for the client's stated target query — `hostel-near-assi-ghat-varanasi` and `backpackers-guide-assi-ghat-varanasi` — are blank pages (§3). This is a direct, avoidable loss of exactly the hyperlocal relevance signal the brief asks about.
- Several posts show a **published-date mismatch** between the visible on-page text and the schema/meta date — e.g. `why-assi-ghat-perfect-base-varanasi-stay` shows "Published: 2026-03-15" in the visible hero but `datePublished: 2026-05-12` in JSON-LD and meta description; the two broken posts show "Published: 2026-04-14"/"2026-04-28" in their meta description text vs. `datePublished: 2026-07-04` in JSON-LD. Freshness signals should be internally consistent.
- Beyond the two Assi-Ghat-specific posts and the About page, most remaining copy says "Varanasi" broadly (e.g., "7 Experiences Only Varanasi Can Offer," "Things to Do in Varanasi") rather than tying back to Assi Ghat/the immediate neighbourhood — a missed opportunity to reinforce hyperlocal relevance in every post, not just two of them.

---

## Top 10 Prioritized Actions

1. **[Critical]** Resolve the `about.html` / `styles/global.css` deletions before any deploy. Confirm whether this is an intentional in-progress migration; if not, restore both files (`git checkout -- about.html styles/global.css` after backing up any pending work) so `/about` and site-wide styling don't break. Every nav/footer on the site links to `/about`.
2. **[Critical]** Fix the two broken blog pages (`blog/hostel-near-assi-ghat-varanasi`, `blog/backpackers-guide-assi-ghat-varanasi`): rebuild the missing `<body>` content from the source markdown (`/blogs/*.md`) the same way the 5 working posts were built, and fix the `\'` → `'` escaping bug so the JSON-LD parses. These two URLs target the client's #1 stated query intent and currently return blank pages with zero valid structured data.
3. **[High]** Build the missing `things-to-do-varanasi-local-guide` page (source markdown already exists at `/blogs/things-to-do-varanasi-local-guide.md`) or remove its reference from `blog.html`'s `CollectionPage` schema and `getAllBlogSlugs()` — currently a self-inflicted 404 referenced in the site's own structured data.
4. **[High]** Reinstate a genuine, verifiable review showcase on the homepage — but sourced honestly this time. Pull real reviews (with permission) from Google/Hostelworld/Booking.com, show reviewer first name + platform + approximate date, and link each card to its source. Do not reintroduce unattributed placeholder quotes like the previous "Priya S./James L./Aiko T." set. Given six failed automation attempts in the git history, a simple manual quarterly refresh of 4-6 real quoted reviews will outperform another fragile live-fetch attempt.
5. **[High]** Add a direct "Leave us a review on Google" CTA (deep-linked to the GBP listing using the place ID already embedded in the Maps iframe: CID `0x398e31ef166d9b91:0x96411370098acc3b`) on the contact page, book-now confirmation flow, and ideally a post-stay WhatsApp follow-up message. This directly targets review-velocity risk (the "18-day rule").
6. **[High]** Verify the primary GBP category directly in the Google Business Profile dashboard. This is the #1 local ranking factor and #1 negative factor if wrong — it cannot be assessed from the codebase and should be checked immediately.
7. **[Medium]** Standardize the `sameAs` array to the full 9-entry canonical list on every page (currently the homepage is missing Cleartrip/Expedia, and `blog/index.html` has an entirely different, partly-broken 5-entry list). Delete or 301-redirect the legacy `blog/index.html` duplicate to `/blog`.
8. **[Medium]** Add `checkinTime`/`checkoutTime` to the homepage's `Hostel` schema (present everywhere else, missing on `index.html`, the most likely canonical entity page). Also unify the mismatched "Published" dates (visible text vs. schema `datePublished`) across blog posts.
9. **[Medium]** Get a real JustDial listing (and consider Sulekha) — currently only a broken bare-homepage reference exists in the legacy `blog/index.html` file, with no actual profile anywhere. These India-specific directories matter for the domestic "budget stay Varanasi" walk-in searcher persona named in the brief, a segment OTAs serve less precisely than Google/JustDial local search.
10. **[Low]** Add per-post internal links from every blog article back to the About/location content and to each other's Assi-Ghat-specific posts (currently only `why-assi-ghat-perfect-base-varanasi-stay` has a "Read Next" cross-link block); extend the Assi-Ghat-specific framing (not just "Varanasi" broadly) into the remaining generic posts ("Top 7 Experiences," "Things to Do") to reinforce hyperlocal relevance sitewide, not just on two pages. Also swap the generic `maps.google.com/?q=<address>` "Get Directions" link for a place-ID-specific Maps deep link so users land on the actual verified GBP listing (and its reviews) rather than a plain address search.

---

## Limitations Disclaimer

This audit is based on the site's source code and one-time automated fetch attempts; it could **not** verify the following without paid/authenticated tooling or manual login access:
- **Live Google Business Profile data**: actual primary/secondary category, verification status, Q&A, Posts activity, photo count/recency, and whether the profile's NAP exactly matches the site (the Maps embed's CID/coordinates match the site's schema, which is a good sign, but the GBP dashboard itself was not accessible).
- **Live review counts/ratings** on Google, TripAdvisor, Booking.com, Hostelworld, Agoda, MakeMyTrip, Goibibo, Cleartrip, and Expedia — automated fetches to these platforms returned 403/blocked responses (bot protection). The `4.9`/`60` figures baked into every page's schema could not be independently cross-verified against any live source and should be checked manually against each platform's current dashboard.
- **Review velocity / the "18-day rule"** — requires timestamped review data from the live GBP dashboard, not available from source code.
- **Review response rate/pattern** — same limitation.
- **Local pack position / "near me" SERP visibility** — no DataForSEO or live SERP tool was available in this session; recommend running `serp_organic_live_advanced` (or manual incognito searches from a Varanasi IP/location) for "hostel near Assi Ghat," "budget hostel Varanasi," and branded queries to see how the site's own pages perform relative to its own OTA listings.
- **Whether `blog/index.html` (vs. `blog.html`) is actually the file served in production at `/blog`** — this depends on server/hosting configuration not present in this repository; flagged as a duplicate-content risk to be confirmed against the live deployment.
- **Deployment state** — because `about.html` and `styles/global.css` show as uncommitted deletions in the working tree, it is unclear whether the currently *live* site matches what's on disk here. All findings above describe the repository's current working-tree state, not confirmed live-site behavior.
