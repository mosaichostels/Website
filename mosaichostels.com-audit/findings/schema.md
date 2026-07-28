# Schema.org Structured Data Audit — Mosaic Hostel Varanasi (mosaichostels.com)

Audit date: 2026-07-28
Scope: Homepage, /book-now, /gallery, /contact, /blog (+ 8 blog posts), /about (referenced but missing from working tree), /privacy, and supporting templates (`blog/post.html`, `components/blog-renderer.js`).

Severity key: **Critical** (breaks parsing / factually wrong / policy risk) · **High** (missing required-for-eligibility property or real user-facing defect) · **Medium** (recommended property missing / inconsistency) · **Low/Info** (polish, enhancement, or non-blocking observation).

---

## 1. Detection Summary — Where Hostel/LocalBusiness Schema Exists

| Page | `Hostel` schema | `BreadcrumbList` | Other schema | Notes |
|---|---|---|---|---|
| `/` (index.html) | ✅ Present | ❌ Missing | — | Truncated `sameAs` (7 of 9 links), no `@id`, no `checkinTime`/`checkoutTime` |
| `/book-now` | ✅ Present (full) | ✅ Present | — | Reference/most-complete version |
| `/gallery` | ✅ Present (full) | ✅ Present | — | Matches book-now |
| `/contact` | ✅ Present (full) | ✅ Present | `Organization` + `ContactPoint` | Two overlapping business entities on one page |
| `/blog` (`blog.html`, served for `/blog` per `.htaccess`) | ✅ Present (full) | ✅ Present | `CollectionPage` listing all 8 posts | Valid JSON, correct |
| `/blog/` → `blog/index.html` (static file, reachable directly and possibly served for trailing-slash requests) | ⚠️ Present but **invalid JSON** | ❌ Missing | ❌ No CollectionPage | **Critical bug — see §2.1** |
| `/about` (about.html) | ✅ Present in git history (full, matches gallery pattern) | ✅ Present in git history | — | **File currently absent from local working tree** (`git status` shows `D about.html`) — see §5.5 |
| `/privacy` | ✅ Present (full) | Not checked in detail | — | Same Hostel block reused |
| 7 of 8 blog posts (`/blog/<slug>/index.html`, statically pre-rendered) | — | — | `BlogPosting` | Missing several recommended properties — see §3 |
| 1 of 8 blog posts (`things-to-do-varanasi-local-guide`, served dynamically via `blog/post.html`) | — | ✅ (client-injected) | `BlogPosting` (client-injected) | No static fallback — see §3.8 |

**Answer to "is Hostel/LocalBusiness schema also on the homepage and other key pages, or only on /book-now?"**
It is present on **every key page** (home, book-now, gallery, contact, blog, privacy, and about-in-git-history), which is good practice. However, the copies are **not identical** — the homepage copy is a stripped-down, out-of-sync version missing 3 properties and 2 `sameAs` links that the other five pages have (see §5.1). Because each page defines a full, independent JSON-LD object with no shared `@id`, Google has no explicit signal that these are the same business entity rather than five different “Hostel” listings.

---

## 2. Critical Findings

### 2.1 Invalid / broken JSON-LD on `blog/index.html`
`blog/index.html` (physically present at `/Users/naveenkumar/Projects/Website/blog/index.html`) contains a `Hostel` schema block with a **JSON syntax error**: a missing comma between the TripAdvisor URL and the next string in `sameAs`.

```
"https://www.tripadvisor.com/Hotel_Review-...html"
"https://www.justdial.com/",
```

Because there is no comma after the TripAdvisor string, **the entire `<script type="application/ld+json">` block fails `JSON.parse()`**. Google's Rich Results parser will discard this block entirely — the Hostel schema on this file is currently worth zero to Google.

On top of the syntax error, the `sameAs` list itself is also stale/wrong (compared to the correct file `blog.html`):
- `https://www.justdial.com/` — a bare homepage link to an unrelated aggregator, not a Mosaic Hostel profile page.
- `https://www.makemytrip.com/hotels/`, `https://www.agoda.com/`, `https://www.goibibo.com/` — generic category/homepage URLs, not the property's actual listing pages (contrast with the correct, specific URLs used in `blog.html`, `book-now.html`, etc.).
- No `BreadcrumbList` or `CollectionPage` schema at all (both are present in `blog.html`).

**Why this matters operationally:** `.htaccess` rewrites `^blog/?$` → `blog.html` when the request is *not* an existing file/directory. But `/blog/` (with a trailing slash) resolves to the **directory** `blog/`, which fails the rewrite's `!-d` (not-a-directory) condition — meaning Apache's `DirectoryIndex` takes over and serves `blog/index.html` directly for that URL variant, bypassing `blog.html` entirely. Any crawl path, internal link, or backlink that hits `/blog/` (trailing slash) risks serving this broken file instead of the correct one.

**Fix:** Either (a) delete `blog/index.html` and rely solely on the `.htaccess` rewrite to `blog.html`, or (b) if it must exist as a static fallback, replace its content with an exact, valid copy of `blog.html`'s schema. Recommendation: delete the stale file — it is dead weight that only functions as a landmine for the trailing-slash edge case.

### 2.2 `datePublished` does not match the actual publish date for 2 of 7 pre-rendered blog posts
Comparing the pre-rendered static schema in `blog/<slug>/index.html` against the source-of-truth in `blogs/<slug>.md`:

| Slug | Schema `datePublished` | Actual `**Published:**` date in markdown / on-page text | Match? |
|---|---|---|---|
| `backpackers-guide-assi-ghat-varanasi` | `2026-07-04` | `2026-04-28` | ❌ **Wrong** |
| `hostel-near-assi-ghat-varanasi` | `2026-07-04` | `2026-04-14` | ❌ **Wrong** |
| `assi-ghat-varanasi-complete-guide` | `2026-06-15` | `2026-06-15` | ✅ |
| `best-hostels-in-varanasi` | `2026-04-07` | `2026-04-07` | ✅ |
| `top-7-experiences-varanasi-traveler` | `2026-05-05` | `2026-05-05` | ✅ |
| `varanasi-solo-female-travelers-safety-travel-guide` | `2026-05-26` | `2026-05-26` | ✅ |
| `why-assi-ghat-perfect-base-varanasi-stay` | `2026-05-12` | `2026-05-12` | ✅ |

Two posts show a `datePublished` (`2026-07-04`, identical to each other) that contradicts the date visibly printed on the same page (via the leaked "Published:" text in the meta description — see §3.2) and in the source markdown. This is a factual mismatch between structured data and visible content, which Google's structured-data guidelines explicitly disallow ("don't mark up content that is not visible to users… must accurately reflect the content of the page"). It looks like a build-script regression where two posts were re-generated on `2026-07-04` and the date field defaulted to the *generation* timestamp instead of preserving the frontmatter's actual publish date.

**Fix:** Regenerate/correct `datePublished` for these two files to `2026-04-28` and `2026-04-14` respectively, and add `dateModified` set to `2026-07-04` if that is genuinely when the content was last edited.

---

## 3. High-Severity Findings — Blog / BlogPosting Schema

### 3.1 Missing required-for-eligibility properties on all 7 pre-rendered posts
The static `BlogPosting` blocks (e.g. `blog/best-hostels-in-varanasi/index.html`) contain only `headline`, `description`, `image`, `datePublished`, `author`. They are **missing**:
- `publisher` (with nested `logo` `ImageObject`) — required by Google's Article structured-data guidelines for Top Stories/Discover eligibility.
- `mainEntityOfPage`
- `dateModified`

Interestingly, the **client-rendered** template (`blog/post.html`, used only for the 8th post) *does* include all three of these. The two rendering paths are out of sync — the majority (7/8) of posts are missing properties that the minority (1/8) already has correctly implemented.

### 3.2 `description` / meta description polluted with raw frontmatter text
Every post's `description` (in both the schema `BlogPosting.description` and the HTML `<meta name="description">` / `og:description`) contains leaked frontmatter instead of a clean excerpt, e.g.:

```
"description": "Published: 2026-06-15 10:00:00 Author: Mosaic Hostel Team, Varanasi The definitive guide to Assi Ghat, Varanasi — geography, atmosphere, practical informat..."
```

Root cause: `extractExcerpt()` in `components/blog-renderer.js` strips markdown emphasis characters (`*`, `_`, `` ` ``) but does not strip the literal `**Published:** …` / `**Author:** …` lines before truncating to N characters — so the excerpt starts with metadata noise and gets cut off mid-word. This affects the schema description, the meta description tag, and `og:description` for **all 8 posts** (both the static pre-rendered ones, which appear to have been generated by an equivalent offline script with the same bug, and the client-rendered one).

**Fix:** Strip `**Published:** ...` and `**Author:** ...` lines (and the `## Summary` line if present) before excerpting; prefer using the "Summary" section content where available as the description rather than the first N raw characters.

### 3.3 Same generic image reused across every BlogPosting (and the Hostel/Organization entities)
All 8 posts' `image` property — and the site-wide `Hostel`/`Organization` `image`/`logo` — point to the same file: `https://www.mosaichostels.com/images/IMG_1928.JPG` (a photo of the common room). None of the posts have a topic-relevant hero image in their schema. This is a missed opportunity for Google Discover and rich-result visual differentiation, and dilutes the signal that these are distinct articles.

**Fix:** Assign a unique, relevant image per post (existing gallery photos in `/images/` can be reused thematically), sized ≥1200px wide, ideally supplying an array of 3 aspect ratios (16:9, 4:3, 1:1) per Google's image guidelines.

### 3.4 Author/publisher redundancy
`author` is hardcoded as `{"@type":"Organization","name":"Mosaic Hostel Varanasi"}` on the static pages (identical to `publisher.name` recommended below), even though the markdown frontmatter literally states `**Author:** Mosaic Hostel Team, Varanasi`. Using the same name for both author and publisher is valid but is a weak authorship signal. Recommend making the author name distinct (e.g., `"Mosaic Hostel Team"`) from the publisher (`"Mosaic Hostel Varanasi"`), as the markdown already intends.

### 3.5 `datePublished`/`dateModified` currently identical for every post
Because `extractDate()` only ever returns a single value, `dateModified` (where present, in `blog/post.html`) is always set equal to `datePublished`. Not a validation error (both are valid ISO 8601 dates), but it means the property carries no real signal. Recommend only emitting `dateModified` when content has genuinely been edited, and otherwise omitting it (a missing `dateModified` is safe; a fabricated one is not useful).

### 3.6 Raw frontmatter datetime string is not strict ISO 8601
The source frontmatter format is `**Published:** 2026-06-15 10:00:00` (space-separated date/time, no `T` delimiter, no timezone offset). Current extraction logic correctly truncates this to a date-only string (`2026-06-15`), which **is** valid ISO 8601 — so no live defect today. However, this is fragile: if the full timestamp is ever piped into `datePublished` verbatim in a future edit, it will fail validation (`YYYY-MM-DD HH:MM:SS` is not ISO 8601; ISO 8601 requires a `T` separator and, ideally, a timezone offset). Recommend standardizing the source frontmatter to full ISO 8601 now, e.g. `2026-06-15T10:00:00+05:30` (IST), to remove the foot-gun.

### 3.7 AggregateRating not backed by visible on-page reviews
Every page's `Hostel` schema declares `"aggregateRating": {"ratingValue": "4.9", "reviewCount": "60"}`, but no page in the crawled set (`index.html`, `book-now.html`, `gallery.html`, `contact.html`, `blog.html`) renders actual visible guest reviews or testimonials with quoted text on the page. `components/home.js` references DOM hooks named `reviewsTileLine`/`testiTileLine`, but no corresponding testimonial markup or review snippets exist in the current `index.html`. Google's structured-data guidelines require that rating/review markup reflect **content that is actually visible to users on the page** — an aggregate score with no visible reviews backing it is a real compliance risk (rich result suppression or, in egregious cases, a manual action for markup that doesn't match visible content), independent of whether the underlying 4.9/60 figure is accurate.

**Fix:** Either (a) add a visible testimonials/reviews section to the homepage (and ideally to `/book-now`) with a handful of real guest quotes, ratings, and dates, and back it with individual `Review` schema (see §6.3), or (b) if no such section is built yet, remove `aggregateRating` from the pages that don't display any reviews and keep it only on pages that do.

### 3.8 8th blog post has no static/pre-rendered fallback
`things-to-do-varanasi-local-guide` is the only one of the 8 posts without a corresponding `blog/<slug>/index.html` directory. Per `.htaccess`, requests to `/blog/things-to-do-varanasi-local-guide` fall through to `blog/post.html`, which builds its `BlogPosting` schema (and the entire visible article) **client-side after an async `fetch()`** of the markdown file completes. If Googlebot's render pass has any timing/JS issue, or the `/blogs/*.md` fetch fails, **neither the content nor the schema will be seen** for this post — unlike the other 7, which are safe because they're fully pre-rendered server-side. This creates an inconsistent, higher-risk implementation for exactly one post.

**Fix:** Generate a static `blog/things-to-do-varanasi-local-guide/index.html` matching the pattern of the other 7 pre-rendered posts (this also resolves §3.1–§3.4 for it in one pass).

### 3.9 Individual blog post URLs missing from `sitemap.xml`
`sitemap.xml` lists only 7 top-level pages (`/`, `/gallery`, `/blog`, `/about`, `/contact`, `/book-now`, `/privacy`) — none of the 8 individual blog post URLs are included. This doesn't invalidate any schema, but it reduces discovery priority for the pages that do carry `BlogPosting` markup. Recommend adding all 8 `/blog/<slug>` URLs.

---

## 4. FAQPage — No Action Recommended

No `FAQPage` schema was found on any crawled page. Per current guidance, Google retired FAQ rich results for all sites (May 2026), so **do not add new FAQPage markup for SERP benefit**. If any genuine Q&A-style content is added in the future (e.g., a guest questions page), use `QAPage` instead of `FAQPage`. No existing FAQPage markup was found to flag/deprecate on this site.

---

## 5. Medium/Low Findings — Local Business Schema Consistency & Enhancements

### 5.1 Homepage `Hostel` schema is out of sync with the other pages
`index.html`'s `Hostel` block is missing, relative to `book-now.html`/`gallery.html`/`contact.html`/`blog.html`:
- `"@id"` (book-now.html sets `"@id": "https://www.mosaichostels.com/book-now"`; homepage has none)
- `"checkinTime": "13:00"` and `"checkoutTime": "10:30"`
- Two `sameAs` entries: Cleartrip and Expedia (homepage only lists 7 of the 9 links; the other pages list all 9)

**Fix:** Sync the homepage schema to match the complete version (template provided in §6.1).

### 5.2 No shared `@id` anchoring one canonical business entity across pages
Each page defines a fully independent `Hostel` object. `book-now.html` sets a page-scoped `@id` (`.../book-now`); every other page omits `@id` entirely. Because none of them share a common, stable identifier, Google has to infer (via matching name/address/telephone) that these are the same entity rather than being told explicitly. Recommend using **one consistent `@id`** across every page, e.g. `https://www.mosaichostels.com/#hostel`, so Google's Knowledge Graph can merge signals cleanly.

### 5.3 `logo`/`image` uses a guest-room photo instead of the actual brand logo
Both the `Hostel` schema (site-wide) and the `Organization` schema (`/contact`) use `IMG_1928.JPG` — a photo of the common room — as their `image`/`logo` value. The site already has a proper logo asset in active use elsewhere: `/images/mosaic-logo-main.png`. Google's Organization/Logo guidance expects `logo` to be an actual brand mark (ideally square or landscape, ≥112×112px, plain/transparent background), not a lifestyle photo.

**Fix:** Set `Organization.logo` to `https://www.mosaichostels.com/images/mosaic-logo-main.png`; keep `Hostel.image` as a representative photograph (or an array of several).

### 5.4 No `WebSite` schema anywhere on the site
No page declares a `WebSite` entity. This is a missed opportunity for a `SearchAction` (Sitelinks Search Box eligibility) and for establishing `WebSite.publisher` → `Organization` linkage. Recommend adding once to the homepage (template in §6.2).

### 5.5 `about.html` is absent from the local working tree
`git status` shows `about.html` as deleted (`D about.html`) in the working directory, even though `git show HEAD:about.html` confirms it existed with a complete `Hostel` + `BreadcrumbList` schema matching the `gallery.html` pattern, and every page's navigation/footer links to `/about`, and `.htaccess` rewrites `/about` → `about.html`, and `sitemap.xml` lists `/about`. This is flagged here because the About page's schema (and its consistency with the rest of the site, per §5.1–§5.2) cannot currently be verified from the working directory — if this deletion reaches the live server, `/about` will 404 and its schema (along with the page itself) will disappear from the index. Recommend restoring the file (`git checkout HEAD -- about.html` or equivalent) before the next deploy, and re-running this schema check against it once restored.

### 5.6 Duplicate/overlapping entities on `/contact`
`/contact` declares both a full `Hostel` object and a separate `Organization` object with its own (different) `description` and `sameAs` list. Both are valid Google-supported types, but having two independently-maintained copies of the same business identity (address, telephone, sameAs) on one page increases the chance of future drift (exactly what happened on the homepage — see §5.1). Recommend either merging into a single `Hostel` object with `Organization`-style properties added (Hostel is a subtype that can carry `contactPoint`), or keep both but generate them from one shared data source so they can never diverge.

---

## 6. Ready-to-Use JSON-LD Recommendations

### 6.1 Corrected/synced homepage `Hostel` schema (replace the existing block in `index.html`)

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Hostel",
  "@id": "https://www.mosaichostels.com/#hostel",
  "name": "Mosaic Hostel Varanasi",
  "description": "Premium budget hostel in Varanasi with private & dorm rooms near Assi Ghat. Experience authentic hospitality with modern comfort. WiFi, AC, lockers, kitchen, hot water available.",
  "address": {
    "@type": "PostalAddress",
    "streetAddress": "B1/85C, Assi Ghat Road, Anandbagh",
    "addressLocality": "Varanasi",
    "addressRegion": "Uttar Pradesh",
    "postalCode": "221005",
    "addressCountry": "IN"
  },
  "telephone": "+91-9125492225",
  "url": "https://www.mosaichostels.com",
  "image": "https://www.mosaichostels.com/images/IMG_1928.JPG",
  "geo": {
    "@type": "GeoCoordinates",
    "latitude": 25.28726,
    "longitude": 83.00316
  },
  "aggregateRating": {
    "@type": "AggregateRating",
    "ratingValue": "4.9",
    "reviewCount": "60"
  },
  "amenityFeature": [
    {"@type": "LocationFeatureSpecification", "name": "Free WiFi", "value": true},
    {"@type": "LocationFeatureSpecification", "name": "Air Conditioning", "value": true},
    {"@type": "LocationFeatureSpecification", "name": "Hot Water", "value": true},
    {"@type": "LocationFeatureSpecification", "name": "Lockers", "value": true},
    {"@type": "LocationFeatureSpecification", "name": "Kitchen", "value": true},
    {"@type": "LocationFeatureSpecification", "name": "Rooftop Space", "value": true},
    {"@type": "LocationFeatureSpecification", "name": "24/7 Check-in", "value": true}
  ],
  "priceRange": "₹500-₹2000",
  "checkinTime": "13:00",
  "checkoutTime": "10:30",
  "openingHoursSpecification": {
    "@type": "OpeningHoursSpecification",
    "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
    "opens": "00:00",
    "closes": "23:59"
  },
  "sameAs": [
    "https://www.instagram.com/mosaichostels/",
    "https://www.booking.com/hotel/in/mosaic-hostel-varanasi.html",
    "https://www.hostelworld.com/hostels/p/335875/mosaic-hostel-varanasi/",
    "https://www.tripadvisor.com/Hotel_Review-g297685-d33877461-Reviews-Mosaic_Hostel_Varanasi-Varanasi_Varanasi_District_Uttar_Pradesh.html",
    "https://www.makemytrip.com/hotels/mosaic_hostel_varanasi-details-varanasi.html",
    "https://www.agoda.com/en-za/mosaic-hostel-varanasi/hotel/varanasi-in.html",
    "https://www.goibibo.com/hotels/mosaic-hostel-varanasi-hotel-in-varanasi-7027872656241537584/",
    "https://www.cleartrip.com/hotels/details/mosaic-hostel-varanasi-5247325",
    "https://www.expedia.com/Varanasi-Hotels-Mosaic-Hostel-Varanasi.h125053779.Hotel-Information"
  ]
}
</script>
```

Apply the same `"@id": "https://www.mosaichostels.com/#hostel"` to the `Hostel` block on every other page (book-now, gallery, contact, blog, blog/index if kept, about, privacy) so all copies resolve to one entity.

### 6.2 `WebSite` schema — add once to the homepage `<head>`

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "WebSite",
  "@id": "https://www.mosaichostels.com/#website",
  "url": "https://www.mosaichostels.com",
  "name": "Mosaic Hostel Varanasi",
  "publisher": { "@id": "https://www.mosaichostels.com/#hostel" }
}
</script>
```

(No `SearchAction` is included since the site has no internal search endpoint; add one only if a working `/search?q={query}` route is built.)

### 6.3 Corrected `Organization` schema for `/contact` (fixes §5.3 logo issue)

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Organization",
  "@id": "https://www.mosaichostels.com/#organization",
  "name": "Mosaic Hostel Varanasi",
  "url": "https://www.mosaichostels.com",
  "logo": "https://www.mosaichostels.com/images/mosaic-logo-main.png",
  "description": "Budget hostel in Varanasi near Assi Ghat offering affordable dorms and private rooms",
  "address": {
    "@type": "PostalAddress",
    "streetAddress": "B1/85C, Assi Ghat Road, Anandbagh",
    "addressLocality": "Varanasi",
    "addressRegion": "Uttar Pradesh",
    "postalCode": "221005",
    "addressCountry": "IN"
  },
  "contactPoint": {
    "@type": "ContactPoint",
    "contactType": "Customer Service",
    "telephone": "+91-9125492225",
    "email": "mosaichostels@gmail.com",
    "areaServed": "IN",
    "availableLanguage": ["en", "hi"]
  },
  "sameAs": [
    "https://www.instagram.com/mosaichostels/",
    "https://www.booking.com/hotel/in/mosaic-hostel-varanasi.html",
    "https://www.hostelworld.com/hostels/p/335875/mosaic-hostel-varanasi/",
    "https://www.tripadvisor.com/Hotel_Review-g297685-d33877461-Reviews-Mosaic_Hostel_Varanasi-Varanasi_Varanasi_District_Uttar_Pradesh.html",
    "https://www.makemytrip.com/hotels/mosaic_hostel_varanasi-details-varanasi.html",
    "https://www.agoda.com/en-za/mosaic-hostel-varanasi/hotel/varanasi-in.html",
    "https://www.goibibo.com/hotels/mosaic-hostel-varanasi-hotel-in-varanasi-7027872656241537584/",
    "https://www.cleartrip.com/hotels/details/mosaic-hostel-varanasi-5247325",
    "https://www.expedia.com/Varanasi-Hotels-Mosaic-Hostel-Varanasi.h125053779.Hotel-Information"
  ]
}
</script>
```

### 6.4 Corrected `BlogPosting` template — apply to all 8 static blog post pages

Example shown for `best-hostels-in-varanasi` (adjust `headline`, `description`, `datePublished`, `image`, and URL slug per post). Replace the existing minimal block with this complete version:

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "BlogPosting",
  "@id": "https://www.mosaichostels.com/blog/best-hostels-in-varanasi",
  "headline": "Best Hostels in Varanasi — 2025 Honest Guide",
  "description": "An honest guide to finding the best hostel in Varanasi — which neighbourhood to choose, what to look for, and why location shapes your entire experience of the city.",
  "image": "https://www.mosaichostels.com/images/IMG_1920.JPG",
  "datePublished": "2026-04-07T10:00:00+05:30",
  "dateModified": "2026-04-07T10:00:00+05:30",
  "mainEntityOfPage": {
    "@type": "WebPage",
    "@id": "https://www.mosaichostels.com/blog/best-hostels-in-varanasi"
  },
  "author": {
    "@type": "Organization",
    "name": "Mosaic Hostel Team"
  },
  "publisher": {
    "@type": "Organization",
    "name": "Mosaic Hostel Varanasi",
    "logo": {
      "@type": "ImageObject",
      "url": "https://www.mosaichostels.com/images/mosaic-logo-main.png"
    }
  }
}
</script>
```

Notes on this template:
- `description` is a hand-written clean summary (taken from the markdown's `## Summary` section, not the raw first-N-characters excerpt) — apply this fix to the excerpt generator so future posts don't need manual correction.
- `image` should be swapped per post to a topic-relevant photo from `/images/` rather than the repeated `IMG_1928.JPG`.
- `datePublished`/`dateModified` use full ISO 8601 with the `+05:30` (IST) offset — update the two posts identified in §2.2 to their correct dates first.
- `publisher.logo` points at the real logo asset, not a room photo.

### 6.5 `Review` schema — only add alongside a visible testimonials section (see §3.7)

If/when a testimonials section with real, on-page guest quotes is added (recommended location: homepage, after the stats band, and/or `/book-now`), back it with individual `Review` entries nested in the `Hostel` object, e.g.:

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Hostel",
  "@id": "https://www.mosaichostels.com/#hostel",
  "name": "Mosaic Hostel Varanasi",
  "review": [
    {
      "@type": "Review",
      "reviewRating": { "@type": "Rating", "ratingValue": "5", "bestRating": "5" },
      "author": { "@type": "Person", "name": "Guest first name / initials" },
      "datePublished": "2026-06-20",
      "reviewBody": "Exact quoted text of the review as it appears visibly on the page — do not paraphrase or fabricate."
    }
  ],
  "aggregateRating": {
    "@type": "AggregateRating",
    "ratingValue": "4.9",
    "reviewCount": "60"
  }
}
</script>
```

Do **not** copy this template with placeholder text into production — every `reviewBody`/`author`/`datePublished` must correspond to a real, visible review on the page. Populate only after the visible testimonials section exists.

### 6.6 `ImageGallery`/`ImageObject` for `/gallery` (21 photos, currently no image schema)

`gallery.html` renders 21 photos across four categories (Rooms, Entrance, Common Areas, Hostel Life) with no accompanying structured data. Add an `ImageGallery` with a representative subset of `ImageObject` entries (Google does not require every image marked up — a representative sample referencing the actual displayed images is sufficient and keeps the payload light):

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "ImageGallery",
  "@id": "https://www.mosaichostels.com/gallery#imagegallery",
  "name": "Mosaic Hostel Varanasi — Photo Gallery",
  "about": { "@id": "https://www.mosaichostels.com/#hostel" },
  "image": [
    {
      "@type": "ImageObject",
      "contentUrl": "https://www.mosaichostels.com/images/IMG_1920.JPG",
      "name": "Room View",
      "caption": "Guest room at Mosaic Hostel Varanasi, near Assi Ghat"
    },
    {
      "@type": "ImageObject",
      "contentUrl": "https://www.mosaichostels.com/images/IMG_1931-1.jpg",
      "name": "Private Room",
      "caption": "Private room with ensuite bathroom at Mosaic Hostel Varanasi"
    },
    {
      "@type": "ImageObject",
      "contentUrl": "https://www.mosaichostels.com/images/IMG_1933.JPG",
      "name": "Dorm Room",
      "caption": "Mixed dorm room with lockers and AC at Mosaic Hostel Varanasi"
    }
  ]
}
</script>
```

Extend the `image` array to cover a few photos from each of the four filter categories (Rooms, Entrance, Common Areas, Hostel Life) for broader coverage — full coverage of all 21 is not necessary.

---

## 7. Priority Action List

1. **Critical** — Fix the invalid JSON (missing comma) in `blog/index.html`, or delete the file entirely and rely on `.htaccess`'s rewrite to `blog.html`. (§2.1)
2. **Critical** — Correct `datePublished` for `backpackers-guide-assi-ghat-varanasi` (→ `2026-04-28`) and `hostel-near-assi-ghat-varanasi` (→ `2026-04-14`). (§2.2)
3. **High** — Fix the excerpt/description generator to strip `**Published:**`/`**Author:**` lines before truncating; regenerate `description`/meta description/`og:description` for all 8 posts. (§3.2)
4. **High** — Add `publisher`, `mainEntityOfPage`, `dateModified` to the 7 static `BlogPosting` blocks; generate the missing 8th static page. (§3.1, §3.8)
5. **High** — Either add a genuine, visible testimonials section backing the `aggregateRating`, or remove `aggregateRating` from pages with no visible reviews. (§3.7)
6. **Medium** — Sync homepage `Hostel` schema to match the complete version used elsewhere; adopt one shared `@id` across all pages. (§5.1, §5.2)
7. **Medium** — Point `Organization.logo` at the real logo file instead of a room photo. (§5.3)
8. **Medium** — Add `WebSite` schema to the homepage. (§5.4)
9. **Low** — Add `ImageGallery`/`ImageObject` schema to `/gallery`. (§6.6)
10. **Low** — Add per-post images to blog schema instead of the reused generic photo; add blog post URLs to `sitemap.xml`. (§3.3, §3.9)
11. **Caution (out of schema scope but blocking)** — Restore `about.html` to the working tree before the next deploy; it is currently deleted locally (`git status`) though linked from every page's navigation and listed in `sitemap.xml`/`.htaccess`. (§5.5)

---

## 8. Files Referenced

- `/Users/naveenkumar/Projects/Website/index.html`
- `/Users/naveenkumar/Projects/Website/book-now.html`
- `/Users/naveenkumar/Projects/Website/gallery.html`
- `/Users/naveenkumar/Projects/Website/contact.html`
- `/Users/naveenkumar/Projects/Website/blog.html`
- `/Users/naveenkumar/Projects/Website/blog/index.html`
- `/Users/naveenkumar/Projects/Website/blog/post.html`
- `/Users/naveenkumar/Projects/Website/blog/assi-ghat-varanasi-complete-guide/index.html`
- `/Users/naveenkumar/Projects/Website/blog/backpackers-guide-assi-ghat-varanasi/index.html`
- `/Users/naveenkumar/Projects/Website/blog/best-hostels-in-varanasi/index.html`
- `/Users/naveenkumar/Projects/Website/blog/hostel-near-assi-ghat-varanasi/index.html`
- `/Users/naveenkumar/Projects/Website/blog/top-7-experiences-varanasi-traveler/index.html`
- `/Users/naveenkumar/Projects/Website/blog/varanasi-solo-female-travelers-safety-travel-guide/index.html`
- `/Users/naveenkumar/Projects/Website/blog/why-assi-ghat-perfect-base-varanasi-stay/index.html`
- `/Users/naveenkumar/Projects/Website/blogs/*.md` (source markdown, 8 files)
- `/Users/naveenkumar/Projects/Website/components/blog-renderer.js`
- `/Users/naveenkumar/Projects/Website/.htaccess`
- `/Users/naveenkumar/Projects/Website/sitemap.xml`
- `/Users/naveenkumar/Projects/Website/privacy.html`
