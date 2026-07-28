# Sitemap Architecture Audit — Mosaic Hostel Varanasi
`https://www.mosaichostels.com/sitemap.xml`

## TL;DR

The sitemap itself has only minor, mechanical problems (no `lastmod`, unnecessary `priority` tags). The **real problem is upstream**: all 8 blog posts fail to produce unique, crawlable HTML in production at all, so adding their URLs to the sitemap right now would not fix indexing — it would actively hand Google 8 URLs whose raw HTML response is byte-for-byte identical (empty content shell, blank canonical tag, placeholder title). That is a duplicate/thin-content signal, not a coverage gap. **Fix the routing/deploy problem first; add to sitemap second.**

---

## 1. Current Sitemap — As Fetched

```xml
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url><loc>https://www.mosaichostels.com/</loc><priority>1.0</priority></url>
  <url><loc>https://www.mosaichostels.com/gallery</loc><priority>0.8</priority></url>
  <url><loc>https://www.mosaichostels.com/blog</loc><priority>0.8</priority></url>
  <url><loc>https://www.mosaichostels.com/about</loc><priority>0.7</priority></url>
  <url><loc>https://www.mosaichostels.com/contact</loc><priority>0.7</priority></url>
  <url><loc>https://www.mosaichostels.com/book-now</loc><priority>0.9</priority></url>
  <url><loc>https://www.mosaichostels.com/privacy</loc><priority>0.5</priority></url>
</urlset>
```

Confirmed: valid XML, 7 URLs, well under the 50,000-URL / 50MB limit. All 7 URLs return HTTP 200 live. No `changefreq` present (fine — already correctly omitted). `priority` values present on all 7 (ignored by Google, harmless but should be removed for cleanliness).

---

## 2. Findings (severity-tagged)

| # | Severity | Finding | Evidence |
|---|----------|---------|----------|
| 1 | **CRITICAL** | All 8 blog post URLs (`/blog/<slug>`) return HTTP 200 but the **raw HTML response is byte-for-byte identical** (13,178 bytes) across all 8 — the generic `blog/post.html` shell, not the actual post. Title is the placeholder `"Blog Post — Mosaic Hostel Varanasi"`, `<link id="canonical" rel="canonical" href="">` is **empty**, and `<div id="post-body">` is **empty** — real content is injected only after client-side JS fetches `/blogs/<slug>.md` and runs it through `marked.js`. | `curl` of raw HTML for all 8 live slugs — identical byte count, identical placeholder title, empty canonical, empty post-body, confirmed for `/blog/<slug>` and `/blog/<slug>/`. |
| 2 | **CRITICAL** | Locally, 7 of 8 posts have a fully pre-rendered, SEO-correct static page at `blog/<slug>/index.html` (unique `<title>`, non-empty `<link rel="canonical">`, full body copy, correct `BlogPosting` JSON-LD). **These are not what's live.** If they were deployed, `.htaccess`'s `RewriteCond %{REQUEST_FILENAME} !-d` would make Apache serve the real directory `index.html` instead of rewriting to `blog/post.html`. Since production serves the shell for every slug, these directories effectively do not exist on the server. | `.htaccess` rewrite rule `RewriteRule ^blog/([a-zA-Z0-9-]+)/?$ blog/post.html [QSA,L]` gated by `!-d`; live curl output contradicts what local static files would produce if deployed. |
| 3 | **HIGH** | Root cause traced to `deploy.sh`: it walks all `.html` files with `find` and runs `put $f` in `lftp`, with no `-o`/`-O` remote-path argument. `lftp`'s default remote filename is the **basename** of the local file (confirmed via `lftp -c "help put"`), not the full relative path. Every `blog/<slug>/index.html` shares the literal basename `index.html`, so running `deploy.sh all` would upload all of them as plain `index.html` into the FTP session's current remote directory (the site root per the README's documented remote path) — **silently colliding with, and threatening to overwrite, the homepage**, with only the last one processed by `find`'s traversal order surviving. This is a distinct, urgent deployment-pipeline defect, separate from the sitemap itself, and it explains why the pre-rendered posts never reached production. | `deploy.sh` source; `lftp -c "help put"` output confirming `-o <rfile>` defaults to `basename of lfile`. |
| 4 | **HIGH** | 0 of 8 blog posts are in the sitemap. In addition, `things-to-do-varanasi-local-guide` is not just missing from the sitemap — it is **orphaned from internal navigation entirely**. It's listed in `blog-renderer.js`'s `knownSlugs` array but absent from `getAllBlogsMetadata()` (the function that actually populates the `/blog` listing page via `components/blog.js`), and it has no local static folder either. It is reachable only by directly guessing/typing the URL. | `components/blog-renderer.js` — `knownSlugs` (8 entries) vs. `getAllBlogsMetadata()` (5 entries, missing `backpackers-guide-assi-ghat-varanasi`, `hostel-near-assi-ghat-varanasi`, `things-to-do-varanasi-local-guide`). |
| 5 | **MEDIUM** | Two of the stale local static snapshots have `lastmod`/`datePublished` values that **don't match** their own markdown source of truth: `hostel-near-assi-ghat-varanasi` static JSON-LD says `2026-07-04`, but the markdown (`blogs/hostel-near-assi-ghat-varanasi.md`) says `**Published:** 2026-04-14`. Same mismatch for `backpackers-guide-assi-ghat-varanasi` (static: `2026-07-04`, markdown: `2026-04-28`). This indicates the static builds are stale snapshots that drifted from the source content. | Grep of `datePublished` in `blog/*/index.html` vs. `**Published:**` lines in `blogs/*.md`. |
| 6 | **MEDIUM** | None of the current 7 sitemap URLs have a `<lastmod>` tag at all. Google cannot use crawl-priority signals from freshness for any page on the site via the sitemap. | Sitemap XML inspection. |
| 7 | **LOW / INFO** | `<priority>` values are present on all 7 URLs. Google has confirmed it ignores this tag. Not harmful, but adds noise and false signal for anyone reading the sitemap manually. Removing is optional but recommended for cleanliness. | Sitemap XML inspection. |
| 8 | **LOW** | `about.html` and `styles/global.css` are marked deleted (`D`) in the current git working tree, but the live `/about` page still returns HTTP 200 (the deletion hasn't been deployed yet). If this deletion ships without a corresponding sitemap/redirect update, `/about` would go from a valid sitemap entry to a 404/500, or `global.css` removal could break page rendering site-wide (including the blog shell) depending on what depends on it. Verify intent before next deploy and update the sitemap accordingly if `/about` is being removed or restructured. | `git status` showing `D about.html`, `D styles/global.css`; live curl of `/about` returning 200. |
| 9 | **INFO** | No location-page quality-gate thresholds are triggered by volume — there are only 8 blog posts total (well under the 30-page warning and 50-page hard-stop thresholds for programmatic location pages). However, the *effect* of finding #1 (identical raw HTML across 8 distinct URLs) is functionally similar to a doorway-page/duplicate-content problem, even though the root cause here is a rendering/deployment defect rather than deliberate content scaling. | Manual count of `blogs/*.md` (8 files). |

---

## 3. Direct Answer to the Core Question

**What are the actual live URLs for individual blog posts?**
`https://www.mosaichostels.com/blog/<slug>` (path-based, no trailing slash required — both `/blog/<slug>` and `/blog/<slug>/` resolve identically), for all 8 slugs:
- `/blog/best-hostels-in-varanasi`
- `/blog/assi-ghat-varanasi-complete-guide`
- `/blog/top-7-experiences-varanasi-traveler`
- `/blog/varanasi-solo-female-travelers-safety-travel-guide`
- `/blog/why-assi-ghat-perfect-base-varanasi-stay`
- `/blog/backpackers-guide-assi-ghat-varanasi`
- `/blog/hostel-near-assi-ghat-varanasi`
- `/blog/things-to-do-varanasi-local-guide` (orphaned — no internal links point to it)

`blog/post.html`'s inline script also supports `?slug=` query-string routing as a fallback (`new URLSearchParams(window.location.search).get('slug')`), but the canonical, production routing is the clean path form via the `.htaccess` rewrite rule — the query-string form should **not** be used for links or sitemap entries (it would create a duplicate-URL-with-parameter problem on top of everything else).

**Are these URLs sitemap-eligible right now?**
**Not yet, in practice — even though they return HTTP 200.** Every one of them currently serves client-side-injected content with no server-side/static HTML fallback in production:
- The raw HTML (what any non-JS-executing crawler, or the *first pass* of Google's two-wave indexing, sees) is a generic, empty shell — identical across all 8 URLs.
- The `<title>` is the placeholder `"Blog Post — Mosaic Hostel Varanasi"` until JS runs.
- The `<link rel="canonical">` is **empty** in the raw HTML and only gets a value via JS (`document.getElementById('canonical').href = ...`) — this is a serious problem independent of JS-rendering ability, because some crawlers/bots (per `robots.txt`, `CCBot` is disallowed but `GPTBot`, `OAI-SearchBot`, `ClaudeBot`, `PerplexityBot` are explicitly allowed) do not execute JavaScript and will index/ingest a page with a blank canonical tag and no body content.
- Even for Google, which does render JS on a second pass, an empty canonical tag in the initial HTML is a known risk signal, and having 8 URLs whose first-pass HTML is 100% identical is the classic pattern that can trigger Google to canonicalize/consolidate all 8 into a single URL, or otherwise suppress indexing of the ones it treats as duplicates of another.

This is a **deeper technical problem than "add to sitemap."** Adding these URLs to the sitemap today would not make Google index 8 distinct, valuable blog posts — it would submit 8 URLs that currently fail the most basic test of unique server-visible content.

---

## 4. Recommended Fix Sequence (before sitemap changes)

1. **Fix deployment so the real per-post static HTML is actually served.** The pre-rendered pages in `blog/<slug>/index.html` already have everything needed (unique title, real canonical, full content, correct JSON-LD) — they simply never reached production due to the `deploy.sh` basename-collision bug (Finding #3). Fix `deploy.sh` to preserve relative paths (e.g., `lftp mirror -R` instead of looped `put`, or `put -O <remote-dir>` per file) and redeploy.
2. **Verify server behavior via raw `curl`, not a browser**, after redeploying — a browser will always show rendered content regardless of what the server actually returns, which is exactly how this defect went unnoticed. Confirm each `/blog/<slug>` and `/blog/<slug>/` returns the real static page, not the shell.
3. **Ensure every post has a hardcoded, non-empty `<link rel="canonical">` in the raw HTML** — do not rely on JS to set it after load.
4. **Generate the missing 8th static page** (`things-to-do-varanasi-local-guide`) and add it to `getAllBlogsMetadata()` in `components/blog-renderer.js` so it's linked from `/blog` (Finding #4).
5. **Reconcile the two mismatched dates** (Finding #5) so `lastmod`/`datePublished` reflects the true last significant edit, sourced from the markdown `**Published:**` field (or a real edit-tracking date, once one exists).
6. **Only then**, add all 8 URLs to the sitemap with accurate `lastmod` values, and resubmit the sitemap in Google Search Console / Bing Webmaster Tools.

---

## 5. Corrected/Expanded `sitemap.xml` Recommendation

Two versions below — use whichever matches where you are in the fix sequence.

### 5a. Immediate fix (mechanical only — apply now, independent of the blog issue)
Removes `priority`, adds accurate `lastmod` to the 7 existing pages, sourced from each page's last meaningful git commit date:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://www.mosaichostels.com/</loc>
    <lastmod>2026-07-28</lastmod>
  </url>
  <url>
    <loc>https://www.mosaichostels.com/gallery</loc>
    <lastmod>2026-07-28</lastmod>
  </url>
  <url>
    <loc>https://www.mosaichostels.com/blog</loc>
    <lastmod>2026-07-28</lastmod>
  </url>
  <url>
    <loc>https://www.mosaichostels.com/about</loc>
    <lastmod>2026-07-28</lastmod>
  </url>
  <url>
    <loc>https://www.mosaichostels.com/contact</loc>
    <lastmod>2026-07-28</lastmod>
  </url>
  <url>
    <loc>https://www.mosaichostels.com/book-now</loc>
    <lastmod>2026-07-28</lastmod>
  </url>
  <url>
    <loc>https://www.mosaichostels.com/privacy</loc>
    <lastmod>2026-07-09</lastmod>
  </url>
</urlset>
```
> Note: `/about` is currently deleted (`D`) in the working git tree but not yet deployed — confirm intent before shipping this sitemap; if `/about` is being retired, remove this entry and add a 301 redirect instead.

### 5b. Target state — after the blog routing/deploy fix is confirmed live (Section 4 complete)
Adds all 8 blog posts with `lastmod` sourced from each post's markdown `**Published:**` date (the actual content source of truth):

```xml
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://www.mosaichostels.com/</loc>
    <lastmod>2026-07-28</lastmod>
  </url>
  <url>
    <loc>https://www.mosaichostels.com/gallery</loc>
    <lastmod>2026-07-28</lastmod>
  </url>
  <url>
    <loc>https://www.mosaichostels.com/blog</loc>
    <lastmod>2026-07-28</lastmod>
  </url>
  <url>
    <loc>https://www.mosaichostels.com/about</loc>
    <lastmod>2026-07-28</lastmod>
  </url>
  <url>
    <loc>https://www.mosaichostels.com/contact</loc>
    <lastmod>2026-07-28</lastmod>
  </url>
  <url>
    <loc>https://www.mosaichostels.com/book-now</loc>
    <lastmod>2026-07-28</lastmod>
  </url>
  <url>
    <loc>https://www.mosaichostels.com/privacy</loc>
    <lastmod>2026-07-09</lastmod>
  </url>
  <url>
    <loc>https://www.mosaichostels.com/blog/best-hostels-in-varanasi</loc>
    <lastmod>2026-04-07</lastmod>
  </url>
  <url>
    <loc>https://www.mosaichostels.com/blog/hostel-near-assi-ghat-varanasi</loc>
    <lastmod>2026-04-14</lastmod>
  </url>
  <url>
    <loc>https://www.mosaichostels.com/blog/backpackers-guide-assi-ghat-varanasi</loc>
    <lastmod>2026-04-28</lastmod>
  </url>
  <url>
    <loc>https://www.mosaichostels.com/blog/top-7-experiences-varanasi-traveler</loc>
    <lastmod>2026-05-05</lastmod>
  </url>
  <url>
    <loc>https://www.mosaichostels.com/blog/why-assi-ghat-perfect-base-varanasi-stay</loc>
    <lastmod>2026-05-12</lastmod>
  </url>
  <url>
    <loc>https://www.mosaichostels.com/blog/varanasi-solo-female-travelers-safety-travel-guide</loc>
    <lastmod>2026-05-26</lastmod>
  </url>
  <url>
    <loc>https://www.mosaichostels.com/blog/assi-ghat-varanasi-complete-guide</loc>
    <lastmod>2026-06-15</lastmod>
  </url>
  <url>
    <loc>https://www.mosaichostels.com/blog/things-to-do-varanasi-local-guide</loc>
    <lastmod>2026-07-26</lastmod>
  </url>
</urlset>
```
**Do not deploy 5b until Section 4, steps 1–3 are verified live via raw `curl`.** Submitting these 8 URLs while the routing defect is still present would submit 8 duplicate-shell pages to Google, not 8 real posts.

---

## 6. Missing vs. Extra Pages (crawl vs. sitemap comparison)

- **Missing from sitemap, present on site (200, crawlable content once the routing fix ships):** all 8 `/blog/<slug>` URLs.
- **Missing from sitemap, present on site but with no internal links (orphan):** `/blog/things-to-do-varanasi-local-guide` — exists as an accessible URL but has zero discovery path other than direct URL entry; also needs to be added to `getAllBlogsMetadata()`.
- **In sitemap, live and fine:** all 7 current URLs (`/`, `/gallery`, `/blog`, `/about`, `/contact`, `/book-now`, `/privacy`) — all return 200.
- **In sitemap, at deployment risk:** `/about` — file deleted in local working tree, not yet deployed; confirm before next push.
- **Extra/404/redirected pages in sitemap:** none found.

---

## 7. Quality Gate Check (Location Pages)

Not applicable at current scale — only 8 blog posts total, no location-page pattern detected, well under the 30-page warning / 50-page hard-stop thresholds. No user justification required at this time. Revisit this gate if the site later adds per-city or per-neighbourhood landing pages at scale.
