# Sitemap Audit — mosaichostels.com

**Audited:** 2026-08-18
**Source:** live `https://www.mosaichostels.com/sitemap.xml` (HTTP 200) and local
`/Users/naveen/Projects/hostel/Website/sitemap.xml` — byte-identical, confirmed via diff.
**Scope:** 22 URLs (7 core pages + 15 blog posts).

## Summary

| Check | Result |
|---|---|
| XML well-formed | PASS |
| Per-file limits (≤50k URLs / ≤50MB) | PASS (22 URLs, 2,933 bytes) |
| `priority` / `changefreq` present | PASS — absent, nothing to remove |
| Canonical `www` host consistency | PASS |
| URL status codes (all 22) | PASS — all 200, zero redirects |
| Coverage vs. live site (orphans/missing) | PASS — 1:1 |
| `lastmod` accuracy | **FAIL** — 2 stale entries, 1 critical |

---

## 1. XML Structure & Format — PASS

- `xmllint --noout sitemap.xml` → well-formed, no errors.
- Correct `<?xml version="1.0" encoding="UTF-8"?>` declaration, no BOM (verified via hex dump).
- Single `<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">`, standard `<url><loc><lastmod>` structure.
- `lastmod` values are valid W3C date format (`YYYY-MM-DD`).

## 2. Deprecated Tags — PASS (nothing to fix)

`grep -c '<priority>|<changefreq>'` → **0 matches**. Google ignores both signals anyway; this sitemap never had them, so there's nothing to strip. No action needed.

## 3. Scale Limits — PASS

22 `<loc>` entries, 2,933 bytes uncompressed. Nowhere close to the 50,000-URL / 50MB cap (or the 1,000-URL `news:` cap — not applicable, no `news:` namespace used).

## 4. Canonical Host Consistency — PASS

All 22 `<loc>` entries use `https://www.mosaichostels.com/...` (https, www, no trailing double-slashes). Cross-checked against:
- `robots.txt`: `Sitemap: https://www.mosaichostels.com/sitemap.xml` — matches.
- Homepage `<link rel="canonical" href="https://www.mosaichostels.com/">` — matches.
- `.htaccess`: `RewriteCond %{HTTP_HOST} ^mosaichostels\.com$` → 301 to `www` — apex is correctly consolidated, not left as a second indexable host.

Live-tested every one of the 22 sitemap URLs with `curl -A "Mozilla/5.0"`: **all 22 return HTTP 200 directly on the exact `loc` given, with zero redirect hops.** No sitemap URL points at a 301/404/soft-404. Sitemaps should list only final, canonical URLs — this one does.

Sanity-checked adjacent cases to confirm the redirect chain is clean everywhere else too: apex→www (301), `.html`→clean URL (301), missing trailing slash on blog posts (301) — all single-hop, all landing on the exact URLs the sitemap lists.

## 5. Coverage — PASS, no orphans, no extras

Local file inventory: 7 core `.html` files (`index`, `gallery`, `blog/index`, `about`, `contact`, `book-now`, `privacy`) + 15 blog post directories under `blog/` (not 14 — `co-working-spaces-cafes-assi-ghat` brings the count to 15; sitemap and directory listing agree).

7 + 15 = 22 = exact `<loc>` count in the sitemap. Every file on disk has exactly one sitemap entry and every sitemap entry resolves to a real page:

- No orphans (crawlable pages missing from the sitemap): none found.
- No extras (sitemap URLs that 404/redirect): none found.
- `blog.html` and raw `.html` filenames are correctly **excluded** — the sitemap lists the clean, canonicalized URLs (`/`, `/blog/`, `/about`, etc.) that `.htaccess` treats as authoritative, not the `.html` variants that 301 away. This avoids a duplicate-URL sitemap, which is a common failure mode.
- `google93f3367f3d9f7ac4.html` (Search Console verification file) is correctly omitted — not a content page.

## 6. `lastmod` Accuracy — FAIL (2 issues)

Method: for each URL, found the most recent **substantive** (non-boilerplate) commit touching that file — i.e. excluded the site-wide `global.css?v=YYYYMMDD` cache-bust bump (appears in nearly every file's most recent commit but changes zero visible/crawlable content) — and compared that date to the sitemap's `lastmod`.

**What's working correctly (worth noting, so the fixes below aren't miscalibrated):** 5 blog posts (`best-hostels-in-varanasi`, `top-7-experiences-varanasi-traveler`, `things-to-do-varanasi-local-guide`, `is-varanasi-safe-general-guide`, `varanasi-solo-female-travelers-safety-travel-guide`) received real edits on 2026-08-05 (stale "2025"→"2026" in titles, a factual price/distance correction, BreadcrumbList schema fix) and their `lastmod` was correctly bumped to `2026-08-05`, matching their own JSON-LD `dateModified` field exactly. The other 10 posts only received a 1-line, invisible `og:url` meta tag on the same day — correctly **not** bumped, since that's boilerplate, not a significant change. So the generation logic is capable of telling the two apart; the two failures below are inconsistencies, not a broken process.

### 🛑 CRITICAL — `book-now` lastmod is 15+ days stale, missed two major rewrites

- **Sitemap says:** `lastmod = 2026-08-03`
- **Reality:** the booking page/widget has been substantively rewritten twice since:
  - `b890200` (2026-08-09, "custom booking engine (eZee + Razorpay), multi-room cart") — +602 lines across `book-now.html`/`components/book-now.js`, replaced the entire booking widget with a multi-stage cart flow.
  - `0a11ef0` (2026-08-10, "booking engine InsertBooking WAF/Void-status bugs + price extraction") — restructured the guest-info form (dropped upfront adults/children/rooms fields, added per-room guest capture).
- **Confirmed live/deployed:** `curl https://www.mosaichostels.com/book-now` currently serves the rebuilt widget (`id="bookingWidget"`, `id="stageSearch"` present in the live HTML, matching the local working tree exactly, including today's `global.css?v=20260818` cache-bust). So the *deployed* page is materially newer than what the sitemap claims by two weeks, on the site's primary conversion page.
- **Fix:** set `lastmod` to the actual date of the last deployed content change (≥ `2026-08-10`, or today's date if last deploy was more recent — confirm against `deploy.sh`/host logs). Since this is the money page, it's the highest-value entry to keep accurate for crawl-freshness prioritization.

### ⚠️ MEDIUM — `privacy` lastmod missed a real visible content fix

- **Sitemap says:** `lastmod = 2026-08-03`
- **Reality:** commit `ccd6f0d` (2026-08-05) corrected the **publicly displayed address text** on this exact page — `B1/85C Assi Ghat Road, Varanasi 221001` → `B1/85C, Assi Ghat Road, Anandbagh, Varanasi 221005` (wrong postal code, missing neighborhood — a real NAP-consistency fix, not boilerplate).
- **Inconsistency:** in the *same commit*, `index.html`, `about.html`, and `contact.html` were bumped to `lastmod = 2026-08-05` for a lesser change (schema-only `hasMap` addition, no visible text change). `privacy.html` had the more significant, user-visible edit and was left un-bumped.
- **Fix:** set `privacy` `lastmod` to `2026-08-05` (or later, matching #1's re-check) for consistency with how the other three pages in that same commit were handled.

### ℹ️ INFO — borderline, no action required
`gallery` and `blog/index` also stayed at `2026-08-03` despite receiving a schema-only `hasMap` addition on 2026-08-05 — same class of change that got `index`/`about`/`contact` bumped. Defensible either way (structured-data-only changes are invisible to users), but the current split is inconsistent. Recommend picking one rule going forward — e.g. "bump lastmod only for changes to visible text/markup, never for `<script type=\"application/ld+json\">`-only edits" — and applying it uniformly; right now 3 pages follow it and 2 don't for the identical change.

## 7. Uncommitted working-tree state (informational)

At time of audit, `git status` shows nearly every HTML file as locally modified (uncommitted), but `sitemap.xml` itself has **zero** uncommitted diff. Whatever content work is currently pending has not yet been reflected in `lastmod` values either way — re-run this check once that work is committed/deployed, since it will likely require another `lastmod` pass on top of the two fixes above.

---

## Fixes (copy-paste ready)

In `sitemap.xml`:

```xml
<url>
  <loc>https://www.mosaichostels.com/book-now</loc>
  <lastmod>2026-08-10</lastmod>  <!-- was 2026-08-03; confirm exact last-deploy date -->
</url>
...
<url>
  <loc>https://www.mosaichostels.com/privacy</loc>
  <lastmod>2026-08-05</lastmod>  <!-- was 2026-08-03 -->
</url>
```

## Quality Gates (location-page doorway check)

Not applicable — site has zero programmatic/location-swapped pages. 7 core pages + 15 hand-written, distinct-topic blog posts. No 30+/50+ threshold concern.
