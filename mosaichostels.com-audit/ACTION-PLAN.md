# Action Plan — Mosaic Hostel Varanasi
Sequenced by dependency, not just severity — several "Critical" items will actively backfire if shipped out of order. See FULL-AUDIT-REPORT.md's root-cause chain diagram before starting.

## Phase 1: Critical Fixes — Do Not Deploy Anything Until This Phase Is Done (sequence matters)

1. **Resolve `about.html` / `styles/global.css` deletion.** Confirm with yourself whether this was intentional (in-progress migration?) or accidental. If accidental: `git checkout HEAD -- about.html styles/global.css`. Every page links to `/about`; losing `global.css` breaks all site styling. **Do this first — it blocks everything else safely shipping.**
2. **Fix `deploy.sh`'s basename-collision bug.** Change the `put $f` loop to preserve relative paths (e.g., `put "$f" -o "/$f"`, or switch to `lftp mirror -R` for the whole tree). Verify with a dry run before the next real deploy — this bug can silently overwrite your homepage.
3. **Fix the `.htaccess` RewriteCond scoping bug.** Give the blog-slug rewrite rule its own `RewriteCond %{REQUEST_FILENAME} !-d` guard so it stops shadowing the real static directories:
   ```apache
   RewriteCond %{REQUEST_FILENAME} !-f
   RewriteCond %{REQUEST_FILENAME} !-d
   RewriteRule ^blog/([a-zA-Z0-9-]+)/?$ blog/post.html [QSA,L]
   ```
4. **Regenerate the 2 corrupted static blog files** (`hostel-near-assi-ghat-varanasi`, `backpackers-guide-assi-ghat-varanasi`) from their source markdown — they currently cut off mid-`<head>` with invalid JSON. Fix the `\'` escaping bug in the generation script so it doesn't recur.
5. **Build the missing 9th static page** (`things-to-do-varanasi-local-guide`) matching the pattern of the other 7.
6. **Fix `getAllBlogsMetadata()` in `components/blog-renderer.js`** to include all 8 (soon 9) posts — currently hardcoded to 5, orphaning 3 from the `/blog` listing.
7. **Deploy, then verify with raw `curl` (not a browser)** that every `/blog/<slug>` URL now returns real, unique title/canonical/content — not the generic shell.
8. **Add all 8 blog URLs to `sitemap.xml`** with `lastmod` dates from each post's markdown `**Published:**` field. Use the target-state sitemap already drafted in `findings/sitemap.md` §5b.
9. **301-redirect the legacy WordPress URL** `/varanasi-solo-female-travelers-safety-travel-guide/` → `/blog/varanasi-solo-female-travelers-safety-travel-guide`. This reclaims real, already-earned ranking equity (was at position 7.9–10.5) — the single highest-leverage fix available. Also audit `wp-sitemap-posts-page-1.xml` / `post-sitemap.xml` (both currently 404 but still referenced by Google) for other orphaned legacy URLs.
10. **Fix or delete `blog/index.html`'s invalid JSON-LD** (missing comma) — recommend deleting the file entirely and relying on the `.htaccess` rewrite to `blog.html`.
11. **Resolve the reviews/aggregateRating policy risk:** either add a genuine, visible testimonials section with real reviewer names/dates/platform (do not reintroduce placeholder quotes — see git history warning in `findings/local.md` §4) or remove `aggregateRating` from pages that show no visible reviews.
12. **Fix IndexNow:** pick one key, publish it as a literal `<key>.txt` file at the site root, remove the mismatched `.indexnow-key`/`IndexNow.xml`. Resubmit sitemap in GSC once live.

## Phase 2: High-Impact Improvements (Weeks 2–3)

- Consolidate the 3 near-duplicate "Assi Ghat" posts into one canonical page; 301-redirect the other two slugs.
- Convert every "Read Next"/"Further Reading" bullet into a real hyperlink; add a contextual link to `/book-now` in every post (currently 0 of 8 have one).
- Hyperlink the existing unlinked booking CTA copy inside blog posts (no new copy needed — just wrap existing text in `<a>` tags per the 3 examples in `findings/sxo.md` §4).
- Fix the unsized footer `<img>` sitewide (add `width`/`height`) — eliminates Blog/Mobile's POOR CLS and defuses the same risk on other pages.
- Add `<link rel="preconnect">` for Google Fonts (or self-host the ~90KB of woff2 files).
- Promote the real value-prop H1 into visible hero copy on the homepage (currently hidden off-screen).
- Move the WhatsApp CTA above the mobile fold on `/book-now`.
- Add `FAQPage` schema to posts with existing FAQ content (best-hostels-in-varanasi already has one).
- Fix the excerpt/meta-description generator bug leaking raw `Published:/Author:` text into all 8 posts' meta tags.
- Add `publisher`, `mainEntityOfPage`, `dateModified` to the 7 static BlogPosting blocks; correct the 2 wrong `datePublished` dates.
- Verify `mosaichostels.com` in Bing Webmaster Tools (free, ~10 min).
- Add a visible price + review-count anchor to `/book-now` and homepage (e.g., "Dorms from ₹499 · 4.9★ (60 reviews)").
- Add a "Get Directions" link + map thumbnail to `/book-now` (currently only on `/contact`).

## Phase 3: Content & Authority (Month 2)

- Build out the 3-pillar content architecture from `findings/cluster.md`: "Where to Stay," "Things to Do / Trip Planning," "Safety & Solo Travel" — with new spokes filling confirmed keyword gaps (seasonal timing, itineraries, transportation, budget breakdown, general safety, local/walk-in audience content).
- Pursue third-party citation/backlink outreach using the existing blog content as bait (Assi Ghat guides → tourism/travel round-ups; solo-female-safety guide → women's travel community sites) — see `findings/backlinks.md` §7 for specific targets.
- Add named authorship (real team member, bio, photo) to blog posts instead of the generic "Mosaic Hostel Team" byline.
- Sync homepage `Hostel` schema to match other pages (`@id`, checkin/checkout, full sameAs list); add `WebSite` schema; fix `Organization.logo`.
- Get a real JustDial listing and consider Sulekha — currently only a broken placeholder reference exists.
- Begin building YouTube/Reddit presence — the two channels most correlated with AI citation and currently entirely absent.

## Phase 4: Monitoring & Iteration (Ongoing)

- Re-run `/seo google` (PSI/CrUX) now that the API key is restored, to replace lab-only performance data with real field data.
- Set a monthly cadence to manually re-verify the 4.9★/60-review figure against live GBP/OTA dashboards (git history shows 6 failed automation attempts — a manual quarterly refresh is more reliable than another live-fetch attempt).
- Watch GSC impressions/clicks for the previously-ranking safety-guide URL post-redirect, and for the other 7 posts post-fix, to confirm indexation recovery.
- Run `/seo drift baseline https://www.mosaichostels.com` now to capture a baseline snapshot, so future audits can measure regression/progress against this one.
- Verify GBP primary category directly in the Google Business Profile dashboard (highest-weighted local ranking factor; cannot be checked from source code).

---

**Offer:** A professional PDF report (with charts, executive summary, and this action plan formatted for sharing) can be generated via `claude-seo run google_report.py --type full --data mosaichostels.com-audit/audit-data.json --domain mosaichostels.com --output-dir mosaichostels.com-audit/`.
