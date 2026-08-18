# Local SEO Audit — Mosaic Hostel Varanasi (mosaichostels.com)

Audit date: 2026-08-18
Business type: **Brick-and-mortar** (single physical location, visible street address, Google Maps embed + directions link, no service-area language)
Industry vertical: **Hospitality / Lodging** (Hostel — schema.org `Hostel`, a valid `LodgingBusiness` subtype)

Method: static review of on-disk source (`index.html`, `about.html`, `contact.html`, `gallery.html`, `blog.html`, `book-now.html`, `components/footer.html`, `components/site.js`) plus every blog post for NAP mentions. Live GBP listing content could not be rendered via WebFetch (Google Maps is JS-rendered) — see Limitations.

---

## 1. NAP Consistency — PASS (no discrepancies found)

| Source | Name | Address | Phone |
|---|---|---|---|
| `index.html` visible content + FAQ | Mosaic Hostel Varanasi | B1/85C, Assi Ghat Road, Anandbagh, Varanasi, UP 221005 | +91 91254 92225 |
| `index.html` `Hostel` JSON-LD | Mosaic Hostel Varanasi | same, structured (`Varanasi` / `Uttar Pradesh` / `221005` / `IN`) | +91-9125492225 |
| `about.html` visible + JSON-LD | same | same | same |
| `contact.html` visible + `Hostel` + `Organization` JSON-LD | same | same | same |
| `gallery.html`, `blog.html`, `book-now.html` JSON-LD | same | same | same |
| `components/footer.html` (shared, injected site-wide) | Mosaic Hostel (logo) | B1/85C, Assi Ghat Road, Anandbagh, Varanasi, UP 221005 | +91 91254 92225 |
| Blog post `assi-ghat-vs-dashashwamedh-where-to-stay` (body copy) | — | "B1/85C, Assi Ghat Road, Anandbagh, **Bhelupur**" | — |

- Phone number is consistent in every occurrence, just formatted two ways: `+91-9125492225` (schema/display) and `919125492225` (tel/`wa.me` links, no `+`/hyphens). Both are valid — not a discrepancy, both resolve to the same E.164 number.
- Postal code (221005), locality (Varanasi), region (Uttar Pradesh) and street address string are byte-identical everywhere except one blog post.
- **Minor finding (Low):** the blog post `blog/assi-ghat-vs-dashashwamedh-where-to-stay/index.html` appends `, Bhelupur` to the address in body prose — that's a real sub-locality for the area but it never appears in any NAP-of-record (schema, footer, contact page). Since it's prose, not a citation-style NAP block, risk is low, but keep the canonical address string in schema/footer as the single source of truth and avoid introducing a second locality variant in future copy.
- Google Maps CID is centralized in `components/site.js` (`GBP_CID = '10826956351092739131'`) and reused for the Maps embed, directions dialog, and review link — and it **matches** the hex place ID (`0x96411370098acc3b`) baked into the `<iframe>` embed's `pb` parameter on both `index.html` and `contact.html` (`10826956351092739131` decimal = `96411370098acc3b` hex, verified). One GBP location referenced everywhere — no split-identity risk.

**Verdict: NAP is consistent across every on-site source. This is a real strength — no fix needed here.**

---

## 2. Local Schema Markup (LodgingBusiness / Hostel)

**Correct subtype:** `@type: "Hostel"` is used consistently (index, about, contact, gallery, blog, book-now) — this is the correct, more-specific schema.org subtype rather than generic `LodgingBusiness` or `LocalBusiness`. Good.

**Required properties:** `name` ✅, `address` (full `PostalAddress`) ✅ — present on all 6 pages checked.

**Recommended properties:**
| Property | Status | Detail |
|---|---|---|
| `geo` | ✅ Present, 5-decimal precision | `lat 25.28726 / lng 83.00316` — identical on every page (index, about, contact, gallery, blog, book-now) |
| `telephone` | ✅ Present | `+91-9125492225` on all pages |
| `url` | ✅ Present | `https://www.mosaichostels.com` |
| `hasMap` | ✅ Present on index, about, contact | `https://www.google.com/maps?cid=10826956351092739131` — confirmed added Aug 15 as described. **Missing on `gallery.html`, `blog.html`, and `book-now.html`** — those three pages carry the full `Hostel` schema (address, geo, amenities, hours) but no `hasMap`. **Fix (Medium):** add the same `hasMap` line to those three schema blocks for consistency (5-line copy-paste, same value already used elsewhere). |
| `openingHoursSpecification` | ✅ Present | 24/7 (`opens: 00:00`, `closes: 23:59`) — correctly reflects "Reception Open 24 hours" claim shown in the UI |
| `checkinTime` / `checkoutTime` | ✅ Present | `13:00` / `10:30`, matches visible copy ("1:00 PM · 10:30 AM") everywhere it's shown — no drift |
| `priceRange` | ✅ Present | `₹500-₹2000` — **Low finding:** visible copy says "Dorms from ₹499/night" (index.html booking CTA) while schema floor is `₹500`. Trivial ₹1 mismatch; round schema down to `₹499-₹2000` or round visible copy up, for byte-exact consistency. |
| `@id` | ⚠️ Inconsistent | Present only on `index.html` (`"@id": "https://www.mosaichostels.com/"`). Missing on `about.html`, `contact.html`, `gallery.html`, `blog.html`, `book-now.html`. **Fix (Low-Medium):** add the same `@id` to every page's `Hostel` block so Google's Knowledge Graph collapses all instances into one entity instead of potentially treating them as distinct/duplicate `Hostel` nodes. One-line addition, same value, 5 files. |
| `image` | ✅ Present | single representative photo (`IMG_1928.JPG`) — fine, though a single generic image repeated across every schema block is a missed opportunity; richer `image` arrays (exterior, room, rooftop) strengthen entity/image-pack eligibility. Low priority. |
| `amenityFeature` | ✅ Present, good detail | WiFi, AC, hot water, lockers, kitchen, rooftop, 24/7 check-in — solid, matches on-page amenity claims. |
| `sameAs` | ✅ Present, strong | 8 links: Google Maps (GBP), Instagram, Booking.com, Hostelworld, TripAdvisor, MakeMyTrip, Agoda, Goibibo, Cleartrip, Expedia — this is a well-built entity-stacking list covering the OTAs that matter for an Indian hostel (better fit than generic Yelp/BBB, which have negligible India relevance — see §6). |
| `aggregateRating` / `reviewCount` | ✅ Confirmed absent site-wide | Grepped all HTML for `aggregateRating`, `reviewCount`, `ratingValue` — zero matches anywhere. Confirms the fake rating schema removal held; **do not reinstate synthetic ratings** — only add `aggregateRating` back once it's wired to a real, live-fetched source (see §4). |

**Additional schema present and correctly used:** `Organization` + `ContactPoint` on `contact.html` (with `email`, `areaServed: IN`, `availableLanguage: [en, hi]` — good for a hospitality/international-guest business), `BreadcrumbList` on all pages, `FAQPage` on `index.html`, `BlogPosting` on blog posts.

---

## 3. GBP (Google Business Profile) Signals on the Page

| Signal | Status |
|---|---|
| Maps embed (`<iframe>`) | ✅ Present on `index.html` and `contact.html`, correct place, `loading="lazy"` |
| Directions link | ✅ `openMapsDialog()` opens `maps?cid=...` (Google) or Apple Maps, used on address text throughout site |
| GBP CID reference | ✅ Single source of truth in `site.js`, matches embed's encoded place ID |
| "Leave a review" CTA | ⚠️ **Present but functionally weak (High priority).** `contact.html` has a "Stayed with us? → Leave us a review on Google" link, wired to `openGoogleReview()` in `site.js`. That function opens `https://www.google.com/maps?cid=10826956351092739131` — the **listing page**, not a direct review-composer deep link. A user has to land on the Maps listing and find/tap "Write a review" themselves — extra friction that measurably suppresses conversion of the CTA into an actual submitted review. **Fix:** generate a short link from GBP (Business Profile → "Ask for reviews" → `g.page/r/<id>/review`) or use `https://search.google.com/local/writereview?placeid=<PLACE_ID>` and swap that URL into `GBP_CID`-adjacent logic in `site.js` (one function, one line). Given the 18-day review-velocity ranking cliff (Sterling Sky), a low-friction one-tap review CTA is one of the highest-leverage fixes on this site. |
| GBP posts / photo evidence indicators | ❌ Not detectable from source (Posts and photo counts live entirely inside the GBP dashboard, not surfaced on-site) — see Limitations |
| Review widget embed (live pulled reviews) | ❌ None found. Only a static "4.9 ★ Tripadvisor Rating" stat block on `index.html`, linked out to TripAdvisor (real, not schema-embedded — compliant with the no-synthetic-rating requirement) |

---

## 4. Reviews & Reputation

- **No aggregateRating/reviewCount schema anywhere** — correct, matches the intentional compliance removal. Do not reinstate unless backed by a live, verifiable feed (e.g., server-side pull from Google Places API / TripAdvisor API rendered into schema at build time, not hand-typed numbers).
- **Only one real, visible review signal on-site:** the "4.9 ★ Tripadvisor Rating" stat on `index.html`, hyperlinked to the actual TripAdvisor listing (`tripadvisor.in/Hotel_Review-g297685-d33877461-...`). This is honest and verifiable — good practice — but it's a single data point with no count shown (visitors can't tell if that's 5 reviews or 500) and no equivalent widget for Google or Hostelworld.
- **No review count anywhere on-site** for any platform. Adding a real review count next to the TripAdvisor stat (e.g., "4.9 ★ · 210 reviews") strengthens trust without violating the no-synthetic-data rule, since it would be a real, periodically-updated number rather than fabricated schema.
- **Review generation funnel is weak** — see §3 GBP CTA finding. This is the dimension most within the site's direct control to fix and the one most tied to the 18-day review-velocity ranking factor.
- Could not assess: actual review count, rating trend, response rate/pattern on GBP or OTAs (requires live GBP/TripAdvisor/Booking.com data — see Limitations).

---

## 5. Local On-Page SEO & Content Depth (Assi Ghat / Varanasi context)

Strong, above-average for a small hostel site:

- Dedicated "Find Us" / location sections on `index.html`, `about.html`, and `contact.html`, each with address, check-in/out, reception hours, WhatsApp — not just a bare address dump.
- `index.html` FAQPage includes location-specific Q&A: "Where is Mosaic Hostel located?", "How far is the hostel from the railway station and airport?" — both good for both classic local-pack and AI-visibility (FAQ schema + dedicated location content are exactly the AI-visibility factors called out in the brief).
- Neighborhood framing present in multiple places: "Heart of Varanasi," "Situated steps from the Ghats," "the city's most livable ghat neighbourhood" (index philosophy section + FAQ).
- 15+ blog posts targeting hyper-local topics (Assi Ghat guide, Assi Ghat vs Dashashwamedh comparison, Sarnath day trip, Varanasi itineraries, transfer guide, safety guide, budget breakdown) — this is real location-specific content depth, not thin boilerplate, and is exactly the "dedicated service/location pages" factor Whitespark ranks as the #1 local organic factor.

**Discrepancy found (Medium): transfer-time claims don't match between the homepage FAQ and the dedicated transfer-guide blog post.**

| Claim | Home FAQ (`index.html`) | Transfer guide (`blog/varanasi-airport-railway-to-assi-ghat-transfer-guide/index.html`) |
|---|---|---|
| Airport (Lal Bahadur Shastri) | "about 45 minutes" | "25–26 km... 45 minutes to an hour" — consistent (FAQ is the low end of the blog's range) |
| Varanasi Junction railway station | "roughly 15–20 minutes away" | "about 7–8 km... a 20 to 30 minute ride" — **FAQ understates by 5–10 minutes vs. the blog's own, more detailed figure** |

**Fix:** align the homepage FAQ answer to "20–30 minutes" (or "roughly 20 minutes") to match the transfer guide it links to — a visitor who reads the FAQ, then clicks through to the guide, will notice the inconsistency. Also worth citing the km distances in the FAQ answer itself, since distance claims are a proximity-adjacent trust signal even though actual ranking proximity (55.2% of variance per Search Atlas) is outside the site's control.

---

## 6. Citation Presence (Tier 1 + Industry-Relevant Directories)

Generic "Tier 1" US directories (Yelp, BBB) have negligible relevance for an Indian hostel and were not prioritized in the `sameAs` list — correctly so, this is an example of vertical-appropriate citation choice, not an omission. What's present:

| Directory | Linked in `sameAs` | Notes |
|---|---|---|
| Google Business Profile | ✅ (via `maps?cid=`) | Central to all local signals |
| TripAdvisor | ✅ + visible on-page rating stat | Strongest review-proof on-site |
| Booking.com | ✅ | |
| Hostelworld | ✅ | Highest-intent OTA for the hostel vertical specifically |
| Agoda | ✅ | |
| MakeMyTrip | ✅ | India-market-relevant |
| Goibibo | ✅ | India-market-relevant |
| Cleartrip | ✅ | India-market-relevant |
| Expedia | ✅ | |
| Instagram | ✅ | Social, not a citation but reasonable in `sameAs` |

**Could not verify (Limitations):** whether the NAP on each of these external listings (phone/address exactly as listed) matches the site's canonical NAP — that requires live fetches/API access to each OTA, which is outside static source review. **Recommend manually spot-checking phone + address on the Google Business Profile, TripAdvisor, and Hostelworld listings against `B1/85C, Assi Ghat Road, Anandbagh, Varanasi, Uttar Pradesh 221005` / `+91 91254 92225`**, since even one stale citation (e.g., an old address from before the property's current signage) is a common, high-impact NAP-consistency failure that a code audit cannot catch.

---

## 7. Industry-Specific (Hospitality) Checks

| Check | Status |
|---|---|
| Check-in / check-out times | ✅ Present and consistent: 1:00 PM / 10:30 AM, shown on `index.html`, `about.html`, `contact.html`, and matches `checkinTime`/`checkoutTime` schema (`13:00`/`10:30`) |
| 24-hour reception | ✅ Stated consistently, matches `openingHoursSpecification` (00:00–23:59) |
| Proximity claims | ✅ "Steps from Assi Ghat" repeated across index/about/contact; backed by real geo coordinates and a dedicated transfer-time blog post (see §5 for the one internal inconsistency) |
| Transport links | ✅ Dedicated blog post covers airport + railway station transfer with realistic pricing (₹700–1,000 airport taxi, ₹150–250 auto-rickshaw from station) — good depth, unusually specific for a hostel site |
| Price transparency | ✅ "Dorms from ₹499/night · Private rooms from ₹1,500/night" shown on-page, roughly matches schema `priceRange` (₹1 float, see §2) |
| Room-type/gender-specific info | ✅ FAQ confirms female-only dorm availability — relevant differentiator surfaced in both UI and FAQPage schema |
| Amenities | ✅ WiFi, AC, hot water, lockers, kitchen, rooftop — listed both visibly and in `amenityFeature` schema, consistent |

---

## 8. Multi-Location Check

**Not applicable** — single physical location. No location-page-quality/doorway-swap-test findings to report.

---

## Local SEO Score: 78 / 100

| Dimension | Weight | Score (0-100) | Weighted |
|---|---|---|---|
| GBP Signals | 25% | 65 | 16.3 |
| Reviews & Reputation | 20% | 60 | 12.0 |
| Local On-Page SEO | 20% | 90 | 18.0 |
| NAP Consistency & Citations | 15% | 92 | 13.8 |
| Local Schema Markup | 10% | 82 | 8.2 |
| Local Link & Authority Signals | 10% | 95 | 9.5 |
| **Total** | | | **77.8 ≈ 78** |

Rationale: NAP and on-page content are genuine strengths (consistent, detailed, well-linked). GBP and Reviews are held back by one concrete, fixable gap — the review CTA doesn't deep-link to the write-review flow — plus the inability to verify live GBP category/posts/photo cadence from static source (scored conservatively, flagged in Limitations rather than penalized further). Schema is strong but has two small consistency gaps (`@id`, `hasMap` missing on 3 pages) keeping it out of the 90s.

---

## Top 10 Prioritized Actions

1. **[Critical]** Fix the "Leave us a review on Google" CTA (`components/site.js`, `openGoogleReview()`) to deep-link to the actual review composer (`g.page/r/<id>/review` short link from GBP dashboard, or `search.google.com/local/writereview?placeid=...`) instead of the generic Maps listing URL. This directly targets the 18-day review-velocity ranking cliff and is a one-function fix.
2. **[High]** Manually verify the primary GBP category is the most specific correct one (e.g., "Hostel" not "Hotel" or generic "Lodging") — Whitespark ranks primary category as the #1 ranking factor and wrong category as the #1 negative factor. Cannot be verified from static source; check directly in GBP dashboard.
3. **[High]** Spot-check NAP on Google Business Profile, TripAdvisor, and Hostelworld listings against the canonical site NAP (`B1/85C, Assi Ghat Road, Anandbagh, Varanasi, Uttar Pradesh 221005` / `+91 91254 92225`) — one stale external listing undermines the otherwise-perfect on-site consistency.
4. **[Medium]** Add `hasMap` to the `Hostel` schema on `gallery.html`, `blog.html`, and `book-now.html` (currently only on index/about/contact) — 3-line copy-paste of the existing value.
5. **[Medium]** Fix the transfer-time discrepancy: homepage FAQ says Varanasi Junction is "15–20 minutes away," the dedicated transfer-guide blog post says "20 to 30 minutes" for the same 7–8 km trip. Align the FAQ to the more detailed blog figure.
6. **[Medium]** Add a real, periodically-updated review count next to the TripAdvisor rating stat on `index.html` (e.g., "4.9 ★ · N reviews") — strengthens trust signal without reintroducing synthetic schema data.
7. **[Medium]** Establish a lightweight process (or scheduled task) to request/monitor new reviews at least every 2–3 weeks to stay ahead of the 18-day review-velocity ranking cliff — currently no on-site mechanism nudges guests beyond the one contact-page link (see #1).
8. **[Low-Medium]** Add a consistent `@id` (e.g., `"https://www.mosaichostels.com/#hostel"`) to the `Hostel` schema block on every page (currently only present on `index.html`) so Google's Knowledge Graph treats all instances as one entity.
9. **[Low]** Reconcile the ₹1 mismatch between visible pricing ("Dorms from ₹499") and schema `priceRange` (starts at ₹500).
10. **[Low]** Consider a real, non-synthetic Google review widget/embed (e.g., an iframe or lightweight API pull that renders live star rating + count) on `index.html` or `contact.html` to give visitors a second review-proof signal beyond TripAdvisor — must stay compliant with the earlier decision to avoid hand-typed/fabricated `aggregateRating` schema.

---

## Limitations Disclaimer

This audit is based entirely on static review of on-disk HTML/JS source. The following could **not** be assessed and require either paid tools, API access, or manual login to the Google Business Profile dashboard:

- Actual GBP primary/secondary category configuration (only referenceable via CID, content not fetchable — Google Maps is JS-rendered and returned no listing data via WebFetch)
- Live review count, rating trend, and review response rate/pattern on GBP, TripAdvisor, Booking.com, Hostelworld, etc.
- Review velocity / recency (the 18-day rule) — requires live review timestamps
- GBP Posts activity and photo upload cadence
- Whether external OTA/citation listings (Booking.com, Hostelworld, TripAdvisor, MakeMyTrip, Agoda, Goibibo, Cleartrip, Expedia) actually display NAP matching the canonical site NAP — only the presence of outbound links was verified, not the content of the destination pages
- Local pack ranking position or SERP visibility for target queries (would need `serp_organic_live_advanced` / DataForSEO or manual SERP checks — no such MCP tool was available in this session)
- Proximity-driven ranking variance (55.2% per Search Atlas) — outside the site's control by definition, noted for context only
