# Schema.org Structured Data Audit — Mosaic Hostel Varanasi (mosaichostels.com)

Audit date: **2026-08-05** (monitoring pass — supersedes 2026-07-28 audit below)
Scope: homepage, about, contact, privacy, gallery, book-now, blog.html, blog/index.html, blog/post.html, and all **15** blog posts (`blog/<slug>/index.html`).
Method: static extraction + `json.loads()` validation of every `<script type="application/ld+json">` block in the current working tree, cross-checked against visible on-page HTML and `blogs/<slug>.md` source frontmatter.

Severity key: **Critical** (breaks parsing / factually wrong / policy risk) · **High** (missing required-for-eligibility property or real user-facing defect) · **Medium** (recommended property missing / inconsistency) · **Low/Info** (polish, non-blocking).

---

## 0. Headline Result

**All 33 JSON-LD blocks across all 24 files parse as valid JSON.** No syntax errors found anywhere (the July 28 `blog/index.html` invalid-JSON bug is fixed). One genuine **new** defect found (BreadcrumbList `item` property), plus a few still-open items carried over from July 28 that have not regressed.

---

## 1. Confirmed: Previous Fixes Hold

| Previous finding (2026-07-28) | Status now |
|---|---|
| §2.1 Invalid JSON in `blog/index.html` (missing comma) | ✅ **Fixed.** Valid JSON, matches `blog.html` content (Hostel + BreadcrumbList + CollectionPage, all 15 posts listed). |
| §3.1 7/8 posts missing `publisher`/`mainEntityOfPage`/`dateModified` | ✅ **Fixed for all 15 current posts.** Every `BlogPosting` block has `headline`, `image`, `datePublished`, `dateModified`, `author`, `publisher` (with nested `logo` ImageObject), `mainEntityOfPage`. |
| §2.2 `datePublished` mismatched vs. markdown source (2 posts) | ✅ **Fixed / not reproduced.** Checked all 15 posts' `datePublished` against `blogs/<slug>.md` `**Published:**` frontmatter — **all 15 match exactly.** |
| §3.8 8th post (`things-to-do-varanasi-local-guide`) had no static fallback | ✅ **Fixed.** Now statically pre-rendered at `blog/things-to-do-varanasi-local-guide/index.html` with complete `BlogPosting` schema. |
| §3.9 Blog post URLs missing from `sitemap.xml` | ✅ **Fixed.** All 15 post URLs + `/blog/` now present in `sitemap.xml` (16 `/blog/` entries total). |
| §5.3 `Organization.logo` was a room photo, not the brand logo | ✅ **Fixed.** `contact.html` → `"logo": "https://www.mosaichostels.com/images/mosaic-logo-main.png"`. |
| §5.5 `about.html` missing from working tree | ✅ **Fixed.** Present, with full `Hostel` + `BreadcrumbList` schema. |
| §5.4 No `WebSite` schema anywhere | ✅ **Fixed (partial).** `index.html` now has a `WebSite` block. (No `@id`/`publisher` link back to the Hostel entity, and no `SearchAction` — see §4.4, unchanged in severity/low priority.) |

---

## 2. New Since Aug 3–5 Changes — Validated

### 2.1 `hasMap` (Google Maps CID deep-link) — index.html, about.html, contact.html
All three pages carry an identical, valid `hasMap` value:
```
"hasMap": "https://www.google.com/maps?cid=10826956351092739131"
```
Also duplicated as the first entry in each page's `sameAs` array. Value is byte-identical across all three pages (no typo/CID drift). **Valid.** `hasMap` is a machine-readable enhancement (not required to appear as visible link text), so no visible-content match check applies — pass.

### 2.2 FAQPage on `index.html` (6 questions)
All 6 `Question`/`acceptedAnswer` pairs in the schema were cross-checked word-for-word against the visible `<details><summary>` FAQ accordion (lines ~320–327 of `index.html`, under "Frequently Asked Questions"). **All 6 match** — no orphaned or fabricated content. Valid JSON, correct `@type`.

### 2.3 FAQPage on `blog/best-hostels-in-varanasi/index.html` (5 questions)
All 5 questions match visible `<h3>` headings + surrounding body copy on the same page. **Valid, no mismatch.**

### 2.4 FAQPage on `blog/is-varanasi-safe-general-guide/index.html` (5 questions) — NEW Aug 5
Checked each of the 5 schema questions ("Is Varanasi safe to visit?", "What are the most common scams in Varanasi?", "Are the burning ghats safe to visit?", "Is it safe to walk around Varanasi at night?", "What food and water precautions should I take in Varanasi?") against the page's own HTML — **all 5 found verbatim in the visible body text.** No orphaned schema. Valid.

### 2.5 FAQPage on `blog/varanasi-solo-female-travelers-safety-travel-guide/index.html` (5 questions) — NEW Aug 5
Same check: all 5 questions ("Is Varanasi safe for solo female travellers?", "Where should solo female travellers stay in Varanasi?", "What should I wear in Varanasi as a woman?", "Is it safe to visit the ghats alone as a woman?", "How should solo female travellers get around Varanasi safely?") **found verbatim in the page's own visible content.** No orphaned/cross-contaminated schema (verified these did not leak from the other FAQ post, and vice versa). Valid.

**All 4 FAQPage blocks (homepage + 3 posts) are individually valid and content-accurate.** Per your instructions, these are flagged as **Info priority only** — Google retired FAQ rich results for all sites (May 2026), so there is no SERP benefit; any AI/GEO benefit is unconfirmed. No action needed since they're already implemented correctly, but do not add more expecting a SERP feature.

### 2.6 `aggregateRating` on `index.html` only (not site-wide)
Confirmed `aggregateRating` (`ratingValue: 4.9`, `reviewCount: 200`, `bestRating: 5`) exists **only** on `index.html`'s `Hostel` block — `about.html`, `contact.html`, `gallery.html`, `book-now.html`, `privacy.html` do **not** carry it. This is a narrower blast radius than the July 28 finding (which flagged it on all 5 pages at 4.9/60).

**Still open / worth flagging (Medium, not new but worth re-confirming):** the homepage has no visible reviews, quotes, or a reviews section — only one stat tile (`4.9 ★ — Tripadvisor Rating`, sourced from a Tripadvisor outbound link) and unrelated stats (`1000+ Happy Guests`, `5 Room Types`, `2025 Est. Varanasi`). **`reviewCount: 200` has no visible on-page number backing it at all** — visitors never see "200" anywhere on the page. This is the same underlying compliance risk as §3.7 in the July 28 audit (Google requires review/rating markup to reflect content visible to users), now scoped to one page instead of five. Per your instructions, not recommending adding fabricated `Review` entries — the fix is either (a) add a genuine visible reviews/testimonial section with a visible count near 200, or (b) drop `reviewCount` (or the whole `aggregateRating` block) until one exists.

---

## 3. New Finding — BreadcrumbList missing required `item` property (6 of 7 pages)

**Severity: High** (not previously flagged in the July 28 audit, which only checked breadcrumb *presence*, not per-`ListItem` property correctness).

Every `BreadcrumbList` on the site follows one of two patterns:

```json
// Correct — privacy.html only
{"@type": "ListItem", "position": 2, "name": "Privacy Policy", "item": "https://www.mosaichostels.com/privacy"}

// Incorrect — about.html, contact.html, gallery.html, book-now.html, blog.html, blog/index.html
{"@type": "ListItem", "position": 2, "name": "Gallery", "@id": "https://www.mosaichostels.com/gallery"}
```

`@id` is a JSON-LD keyword that assigns an identifier to the `ListItem` *node itself* — it does **not** populate schema.org's `item` property, which is what Google's Rich Results parser reads for the breadcrumb's URL. Per Google's breadcrumb structured-data guidelines, `item` (the URL) is a required property on every `ListItem` except optionally the last one. Because these 6 pages use `@id` instead of `item`, **every `ListItem` on those pages is missing its required URL property** — `name` will still parse, but the breadcrumb entries have no destination URL from Google's perspective, risking the breadcrumb rich result being dropped or rendered incorrectly.

**Affected files:** `about.html`, `contact.html`, `gallery.html`, `book-now.html`, `blog.html`, `blog/index.html`.
**Not affected:** `privacy.html` (added Aug 3 with correct `item` syntax — this is the reference pattern).

**Fix:** replace `"@id": "<url>"` with `"item": "<url>"` in every `ListItem` on the 6 affected pages/files (6 files × 2 `ListItem`s each = 12 edits). `privacy.html` is the template to copy.

---

## 4. Other Open / Low-Priority Items (carried over, unchanged, not regressions)

### 4.1 No shared `@id` anchoring one canonical Hostel entity across pages
Still inconsistent: `index.html` → `"@id": "https://www.mosaichostels.com/"`, `book-now.html` → `"@id": "https://www.mosaichostels.com/book-now"`, and `about.html`/`contact.html`/`gallery.html`/`privacy.html` have **no `@id` at all** on their `Hostel` block. Google can still merge these via matching name/address/phone, but an explicit shared `@id` (e.g. `https://www.mosaichostels.com/#hostel`) would be a stronger, unambiguous signal. Medium/Low priority, unchanged from July 28 §5.2.

### 4.2 `blog.html` vs `blog/index.html` — same 15 posts, different order and trailing-slash convention
Content is fully in sync (all 15 posts, all fields match) but list order differs and `blog/index.html` uses trailing-slash URLs (`/blog/best-hostels-in-varanasi/`) while `blog.html` does not (`/blog/best-hostels-in-varanasi`). Not a validation error — both are internally consistent, valid JSON — but worth normalizing to avoid two different canonical-URL conventions for the same posts existing in structured data. Low priority, cosmetic.

### 4.3 No `BreadcrumbList` on any individual blog post page
All 15 `blog/<slug>/index.html` pages carry only a `BlogPosting` block — none has a `BreadcrumbList` (Home → Blog → Post), unlike `blog.html`/`blog/index.html` which do. This is a missed-opportunity gap (not a defect) that existed before Aug 3–5 and wasn't flagged in the July 28 audit either. Low/Info priority — add once the `item` property is fixed everywhere (§3) so the new breadcrumbs use the correct pattern from day one.

### 4.4 `WebSite` schema on homepage has no `@id`/`publisher` link, no `SearchAction`
```json
{"@context": "https://schema.org", "@type": "WebSite", "name": "Mosaic Hostel Varanasi", "url": "https://www.mosaichostels.com/"}
```
Valid but minimal — no `@id`, no `publisher` reference back to the Hostel entity, no `SearchAction` (correctly omitted since there's no working site-search endpoint). Low priority.

### 4.5 No blog post has genuine, unmarked Q&A content that should get FAQPage
Scanned all 12 non-FAQ posts for question-style `<h2>`/`<h3>` headings as a proxy for hidden FAQ content. Only 2 hits, both in `things-to-do-varanasi-local-guide` ("How Long to Stay?", "Ready to Experience Varanasi?") — these are narrative section headers, not discrete Q&A pairs, so **no FAQPage opportunity identified.** Consistent with your instruction not to fabricate FAQ schema without genuine content.

---

## 5. Deprecated / Retired Types Check

No `HowTo`, `SpecialAnnouncement`, `CourseInfo`, `EstimatedSalary`, or `LearningVideo` schema found anywhere on the site. Clean.

---

## 6. Priority Action List

1. **High** — Fix `BreadcrumbList` `ListItem`s on `about.html`, `contact.html`, `gallery.html`, `book-now.html`, `blog.html`, `blog/index.html`: replace `"@id": "<url>"` with `"item": "<url>"` (copy `privacy.html`'s pattern). (§3)
2. **Medium** — Either add a genuine visible reviews section to the homepage with a real, visible count backing `reviewCount: 200`, or remove `reviewCount`/`aggregateRating` until one exists. (§2.6)
3. **Low** — Adopt one shared `@id` (e.g. `#hostel`) across all `Hostel` blocks site-wide. (§4.1)
4. **Low** — Normalize `blog.html` vs `blog/index.html` post order and trailing-slash URL convention. (§4.2)
5. **Low** — Add `BreadcrumbList` (Home → Blog → Post) to the 15 individual blog post pages, using the corrected `item` syntax. (§4.3)
6. **Info, no action required** — FAQPage blocks (homepage + 3 posts) are valid and content-accurate; do not expect Google SERP benefit (retired May 2026); do not add more without genuine Q&A content backing them.

---

## 7. Files Checked

`index.html`, `about.html`, `contact.html`, `privacy.html`, `gallery.html`, `book-now.html`, `blog.html`, `blog/index.html`, `blog/post.html`, and all 15 `blog/<slug>/index.html` files, cross-referenced against `blogs/<slug>.md` and `sitemap.xml`.

Full list of `blog/<slug>/`: `assi-ghat-varanasi-complete-guide`, `assi-ghat-vs-dashashwamedh-where-to-stay`, `best-hostels-in-varanasi`, `best-time-to-visit-varanasi-month-by-month`, `co-working-spaces-cafes-assi-ghat`, `dorm-vs-private-room-varanasi-hostel`, `is-varanasi-safe-general-guide`, `sarnath-day-trip-guide-varanasi`, `things-to-do-varanasi-local-guide`, `top-7-experiences-varanasi-traveler`, `varanasi-2-day-itinerary-backpackers`, `varanasi-3-5-day-itinerary-slow-travel`, `varanasi-airport-railway-to-assi-ghat-transfer-guide`, `varanasi-backpacker-budget-daily-cost-breakdown`, `varanasi-solo-female-travelers-safety-travel-guide`.
