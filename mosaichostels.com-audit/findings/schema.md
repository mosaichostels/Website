# Schema.org Structured Data Audit — Mosaic Hostel Varanasi (mosaichostels.com)

Audit date: **2026-08-18**
Scope: `/` (index.html), `/about`, `/book-now`, `/gallery`, `/contact`, `/privacy`, `blog.html`, `blog/index.html`, `blog/post.html` (client-rendered template), and all 15 static `blog/<slug>/index.html` posts.
Method: static extraction + `json.loads()` validation of every `<script type="application/ld+json">` block in the current local working tree, cross-checked line-by-line against raw file content (no network fetch). FAQ/Q&A question text checked against visible on-page text via substring match.

Severity key: **Critical** (breaks parsing / factually wrong / policy risk) · **High** (missing required-for-eligibility property or user-facing defect) · **Medium** (recommended property missing / inconsistency worth fixing) · **Low/Info** (polish, non-blocking).

---

## 0. Headline Result

**All 39 static JSON-LD blocks across 24 files parse as valid JSON — zero regressions, zero new parse errors.**

- `aggregateRating`/`Review` schema: **confirmed still fully absent site-wide.** Sitewide grep for `aggregateRating`, `ratingValue`, `reviewCount`, `"@type":"Review"` across every `.html`/`.js`/`.php` file (excluding the audit output dir) returns zero hits. **Do not re-add** — no visible review content backs it, and this was correctly removed as a compliance risk. No action needed.
- `hasMap` schema (added Aug 15): **present, byte-identical, and valid on all 8 pages that carry a `Hostel` block** (`index.html`, `about.html`, `book-now.html`, `gallery.html`, `contact.html`, `privacy.html`, `blog.html`, `blog/index.html`) — `"hasMap": "https://www.google.com/maps?cid=10826956351092739131"`. Correct placement inside each `Hostel` node.
- `FAQPage` schema (added Aug 15): **present on 4 pages, all 4 blocks valid JSON, and every question's `name` text still matches visible on-page text verbatim** (checked all 6 homepage questions + all 5 questions each on the 3 FAQ blog posts = 21/21 match). Per standing instruction, Google retired FAQ rich results for all sites (May 7, 2026) — these remain **Info priority only**, no SERP benefit, keep as-is, do not add more.

One correction to the prior audit's completeness claim, one still-open defect carried forward, and one new opportunity flagged below (§4).

---

## 1. `Hostel`/`LodgingBusiness` Schema Completeness — Corrected Finding

**Correction to the Aug 15 report:** re-verified directly against raw file bytes (the earlier regex-based dump undercounted properties due to a tooling artifact, not an actual site defect). The real state is **better than previously reported**:

All 8 `Hostel` blocks (`index.html`, `about.html`, `book-now.html`, `gallery.html`, `contact.html`, `privacy.html`, `blog.html`, `blog/index.html`) carry the **same complete property set**:; `name`, `description`, `address` (full `PostalAddress`), `telephone`, `url`, `hasMap`, `image`, `geo` (`GeoCoordinates`), `amenityFeature` (7 `LocationFeatureSpecification` entries), `priceRange`, `checkinTime`/`checkoutTime` (all pages except `privacy.html`), `openingHoursSpecification`, and a 10-entry `sameAs` array (9 on `privacy.html` — missing Expedia link, harmless).

✅ **No missing required or recommended `Hostel` properties on any page.** This is a clean, consistent block. Severity: **Info, confirm only** — no action needed.

---

## 2. `@id` — Not Anchored to One Canonical Entity (Open, Medium)

Only **2 of 8** `Hostel` blocks carry an `@id`, and they point at two *different* URLs instead of one shared canonical node:

| File | `@id` |
|---|---|
| `index.html` | `https://www.mosaichostels.com/` |
| `book-now.html` | `https://www.mosaichostels.com/book-now` |
| `about.html`, `gallery.html`, `contact.html`, `privacy.html`, `blog.html`, `blog/index.html` | *(none)* |

Google/schema.org best practice for a business that appears identically on multiple pages is one canonical `@id` (typically the homepage URL) reused everywhere, so crawlers merge all mentions into a single knowledge-graph entity instead of treating `book-now.html`'s copy as a distinct, unlinked `Hostel`. Right now `book-now.html` is actively fragmenting the entity graph by minting its own `@id`.

**Fix — set every `Hostel` block's `@id` to the same value** (`https://www.mosaichostels.com/#hostel` is the standard fragment-anchor convention; using the bare homepage URL also works but a `#hostel` fragment is safer since `WebSite`/`Organization` nodes may later want their own `@id` on the same URL):

```json
"@id": "https://www.mosaichostels.com/#hostel"
```
Apply this one line, no other changes, to all 8 files' `Hostel` block (replacing `index.html`'s trailing-slash-only value and `book-now.html`'s `/book-now` value, and adding it to the 6 files that have none).

---

## 3. `blog/post.html` — Still Broken, Unfixed Since Aug 5/15 (Open, Low — file is `noindex`)

`blog/post.html` (client-side render shell; `<meta name="robots" content="noindex, follow">`, real-world reach is low since all 15 current posts have static pre-rendered pages) **still has the same three defects flagged in both the Aug 5 and Aug 15 audits** — no fix has landed:

1. **Static placeholder `BreadcrumbList` (lines 34–58) uses `@id` instead of `item`:**
   ```json
   {"@type": "ListItem", "position": 1, "name": "Home", "@id": "https://www.mosaichostels.com"}
   ```
2. **JS-generated `BreadcrumbList` (lines 289–312, runs on load) copies the same `@id`-instead-of-`item` bug** — even after hydration, the schema never emits a valid `item` URL.
3. **JS-generated `BlogPosting` (lines 322–351) still uses a generic room photo (`IMG_1928.JPG`) for both `image` and `publisher.logo`**, instead of the brand logo (`mosaic-logo-main.png`, correctly used by all 15 static posts) and instead of a post-specific image.

**Fix (3 find-replace edits in `blog/post.html`):**
- Lines 43, 49, 55 and 297, 303, 309: change `"@id":` → `"item":` in every `ListItem`.
- Line 343 (`publisher.logo.url`): change `.../images/IMG_1928.JPG` → `https://www.mosaichostels.com/images/mosaic-logo-main.png`.

---

## 4. New Opportunity — `Offer` Schema for the Live Booking Engine (Medium, new since Razorpay/eZee launch)

The custom multi-room-cart booking engine (`components/book-now.js`, commits `b890200`/`0a11ef0`) is now live, and `book-now.html` **already has real visible "starting from" pricing in on-page copy**:

> line 290: `Dorms from ₹499/night · Private rooms from ₹1,500/night`

This is genuine visible content (not fabricated) and can safely back a `makesOffer` array on the `Hostel` block. Note: the *actual* per-search-date, per-room-type prices are fetched live from the eZee API by `components/book-now.js` and change per date/availability — do **not** hardcode those into static JSON-LD (that would create stale/inaccurate schema, a Google policy risk). Only the two starting-price bands already printed as static copy are safe to encode:

```json
"makesOffer": [
  {
    "@type": "Offer",
    "name": "Dorm Bed",
    "category": "Dormitory",
    "priceCurrency": "INR",
    "price": "499",
    "priceSpecification": {
      "@type": "UnitPriceSpecification",
      "price": "499",
      "priceCurrency": "INR",
      "unitText": "per night"
    },
    "availability": "https://schema.org/InStock",
    "url": "https://www.mosaichostels.com/book-now"
  },
  {
    "@type": "Offer",
    "name": "Private Room",
    "category": "Private Room",
    "priceCurrency": "INR",
    "price": "1500",
    "priceSpecification": {
      "@type": "UnitPriceSpecification",
      "price": "1500",
      "priceCurrency": "INR",
      "unitText": "per night"
    },
    "availability": "https://schema.org/InStock",
    "url": "https://www.mosaichostels.com/book-now"
  }
]
```

Add this array as a sibling property inside `book-now.html`'s existing `Hostel` block (alongside `priceRange`). **Do not** add this to the other 7 pages — it's specific to the booking page's visible offer copy, and duplicating it everywhere risks drifting out of sync with the actual live prices shown only on `/book-now`. If the "from" prices in the on-page copy ever change, this block must be updated in the same commit — treat it as a manual-sync pair, not automation (no code path currently ties JSON-LD to `book-now.js`'s live price fetch, and building one is not warranted for two static numbers).

There is currently **no Google Rich Result type for hostel/room booking Offers** (unlike Product `Offer`), so this yields no direct SERP feature — it's a knowledge-graph/entity-completeness improvement and AI/GEO signal, not a rich-result win. Flagging as Medium because it's low-effort, uses real visible content, and closes a gap the Aug 15 audit correctly identified as a future-consideration item now that the booking engine has actually shipped.

---

## 5. Other Open / Low-Priority Items (carried over, unchanged, not regressions)

### 5.1 No `BreadcrumbList` on any individual blog post page
All 15 `blog/<slug>/index.html` pages still carry only `BlogPosting`, no breadcrumb schema (the visible on-page breadcrumb UI, if any, is unaffected — this is JSON-LD only). Low/Info. If added, use `item` (not `@id`) — see §3, don't copy `blog/post.html`'s pattern.

**Template if added** (per-post, replace bracketed values):
```json
{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [
    {"@type": "ListItem", "position": 1, "name": "Home", "item": "https://www.mosaichostels.com"},
    {"@type": "ListItem", "position": 2, "name": "Blog", "item": "https://www.mosaichostels.com/blog"},
    {"@type": "ListItem", "position": 3, "name": "[Post Title]", "item": "https://www.mosaichostels.com/blog/[slug]/"}
  ]
}
```

### 5.2 All 15 `BlogPosting` blocks share one identical generic `image`
Every static blog post's `BlogPosting.image` is the same value: `https://www.mosaichostels.com/images/IMG_1928.JPG` (a hostel room photo, unrelated to most post topics — e.g. used identically on a Sarnath day-trip guide and a solo-female-safety guide). Not a validation error (the property is present and is a valid absolute image URL), but it weakens eligibility for Google's Image/Article rich results, which favor content-relevant, unique images per article. **Medium, but effort-gated**: only worth fixing if/when each post already has a distinct hero image on the page to reuse — not recommending stock-photo sourcing for 15 posts. If a per-post hero image exists already in `blog/<slug>/index.html`'s visible content, point `BlogPosting.image` at that instead of the generic room photo.

### 5.3 `WebSite` schema on homepage remains minimal
```json
{"@context": "https://schema.org", "@type": "WebSite", "name": "Mosaic Hostel Varanasi", "url": "https://www.mosaichostels.com/"}
```
No `@id`, no `publisher` back-link to the `Hostel`/`Organization` entity, no `SearchAction` (correctly omitted — no working site search exists, do not add a fake one). Low priority — optional 2-line addition once §2's canonical `@id` convention is settled:
```json
"@id": "https://www.mosaichostels.com/#website",
"publisher": {"@id": "https://www.mosaichostels.com/#hostel"}
```

### 5.4 `blog.html` vs `blog/index.html` — duplicate, drifting-order post lists
Both carry an identical-content `CollectionPage.mainEntity` array of all 15 posts, in different order, with a trailing-slash inconsistency between the two (`blog.html`'s `BlogPosting.url` entries have no trailing slash, `blog/index.html`'s do — matches each file's own canonical convention, so not wrong, just worth knowing both exist). Cosmetic, Low priority, unchanged since Aug 5.

---

## 6. Deprecated / Retired Types Check

No `HowTo`, `SpecialAnnouncement`, `CourseInfo`, `EstimatedSalary`, or `LearningVideo` schema found anywhere on the site. Clean.

## 7. Format Compliance Checklist

| Check | Result |
|---|---|
| `@context` is `https://schema.org` (not `http`) | ✅ all 39 blocks |
| `@type` valid, not deprecated | ✅ all blocks |
| Required properties present | ✅ `Hostel` blocks complete (§1); `BlogPosting` complete; `BreadcrumbList` complete on all pages that carry one |
| No Microdata/RDFa in use | ✅ confirmed — no `itemscope`/`itemtype`/`vocab=` found anywhere |
| URLs absolute | ✅ no relative URLs in any `url`/`@id`/`item`/`image`/`logo` field on indexable pages |
| Dates ISO 8601 | ✅ e.g. `datePublished: "2026-06-15"` |
| No placeholder text | ⚠️ `blog/post.html`'s static pre-JS breadcrumb placeholder reads `"name": "Post Title"` — immediately overwritten by JS, page is `noindex`, not a real-world defect (§3) |
| No duplicate/conflicting `@id` | ⚠️ Not duplicate, but **not unified** — `index.html` and `book-now.html` mint two different `@id`s for what should be one entity (§2) |

## 8. Priority Action List

1. **Medium** — Unify `@id` to `https://www.mosaichostels.com/#hostel` across all 8 `Hostel` blocks (currently 2 conflicting values, 6 missing). (§2)
2. **Medium** — Add `makesOffer` (Dorm Bed / Private Room, using the real visible "from ₹499" / "from ₹1,500" copy) to `book-now.html`'s `Hostel` block only. Manual-sync with the visible price copy, not automated. (§4)
3. **Low** — Fix `@id`→`item` (6 spots) and the room-photo `publisher.logo`/`image` bug in `blog/post.html`'s static + JS-generated schema. `noindex` page, cosmetic/consistency only. (§3)
4. **Low** — Consider `BreadcrumbList` on the 15 individual blog posts, using `item` syntax. (§5.1)
5. **Low** — Consider swapping the shared generic `BlogPosting.image` for a post-specific image where one already exists on the page. (§5.2)
6. **Low** — Optional `WebSite` → `Hostel` `@id` cross-link once §2 lands. (§5.3)
7. **Info, confirm only** — `aggregateRating`/`Review` schema fully absent site-wide, no compliance risk remains. No action. (§0)
8. **Info, confirm only** — `hasMap` correct and consistent on all 8 pages. No action. (§0)
9. **Info, no action required** — `FAQPage` (homepage + 3 posts) valid and content-accurate; no Google SERP benefit (retired May 2026); do not add more without genuine backing content, and use `QAPage` (not `FAQPage`) for any future genuine user Q&A page. (§0)
10. **Info** — `Hostel` block property completeness (address/geo/priceRange/amenityFeature/image) confirmed clean on all 8 pages — corrects an undercount in the prior Aug 15 report caused by a tooling artifact, not a site defect. (§1)

## 9. Files Checked

`index.html`, `about.html`, `book-now.html`, `gallery.html`, `contact.html`, `privacy.html`, `blog.html`, `blog/index.html`, `blog/post.html` (static + JS-injected path), and all 15 `blog/<slug>/index.html`:
`assi-ghat-varanasi-complete-guide`, `assi-ghat-vs-dashashwamedh-where-to-stay`, `best-hostels-in-varanasi`, `best-time-to-visit-varanasi-month-by-month`, `co-working-spaces-cafes-assi-ghat`, `dorm-vs-private-room-varanasi-hostel`, `is-varanasi-safe-general-guide`, `sarnath-day-trip-guide-varanasi`, `things-to-do-varanasi-local-guide`, `top-7-experiences-varanasi-traveler`, `varanasi-2-day-itinerary-backpackers`, `varanasi-3-5-day-itinerary-slow-travel`, `varanasi-airport-railway-to-assi-ghat-transfer-guide`, `varanasi-backpacker-budget-daily-cost-breakdown`, `varanasi-solo-female-travelers-safety-travel-guide`.

39/39 JSON-LD blocks parse as valid JSON. 0 parse errors, 0 deprecated types, 0 relative URLs, 0 rating/review schema.
