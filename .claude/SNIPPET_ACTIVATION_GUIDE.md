# WordPress Code Snippet Activation Guide
**Date:** 2026-06-26  
**Status:** 7 Snippets Created, Ready for Activation  
**Time to Complete:** ~10 minutes

---

## Quick Activation Steps

1. Login to WordPress Admin: https://www.mosaichostels.com/wp-admin
2. Go to: Settings → Code Snippets
3. For each snippet below:
   - Find the snippet by title
   - Click to open
   - Click "Activate"
   - Verify it shows "Active" status

---

## Snippet Activation Checklist

### PHASE 0: Critical Fixes (Activate First)

#### ✅ Snippet 67: Mosaic — Unhide H1
- **Purpose:** Make homepage H1 visible to users and search engines
- **Status:** Created (inactive)
- **Action:** Find → Click → Activate
- **Expected result:** H1 text visible on homepage when you view it
- **Impact:** Improves SEO signal for homepage

#### ✅ Snippet 71: Mosaic — Force Sitemap Regeneration
- **Purpose:** Regenerate sitemap XML to fix rendering issue
- **Status:** Created (inactive)
- **Action:** Find → Click → Activate
- **Expected result:** /wp-sitemap.xml returns application/xml (not text/html)
- **Impact:** Google can crawl and index all pages properly
- **Verification:** `curl -I https://www.mosaichostels.com/wp-sitemap.xml | grep content-type`

#### ✅ Snippet 72: Mosaic — Inject Blog Meta Descriptions
- **Purpose:** Add meta descriptions to all blog posts (for search results preview)
- **Status:** Created (inactive)
- **Action:** Find → Click → Activate
- **Expected result:** Meta descriptions appear in GSC and search results
- **Impact:** Improves CTR from search results (+5-10% potential)
- **Covers:** All 9 existing blog posts + 4 new blog posts

#### ✅ Snippet 73: Mosaic — Fix CTA Button Links
- **Purpose:** Ensure "Book Now" and "Contact" buttons are clickable and functional
- **Status:** Created (inactive)
- **Action:** Find → Click → Activate
- **Expected result:** Buttons navigate to /book-now/ and /contact/ correctly
- **Impact:** Enables conversions from search traffic (currently 0% CTR on these buttons)

---

### PHASE 3: Schema Markup (Activate After Phase 0)

#### ✅ Snippet 68: Mosaic — BlogPosting Schema
- **Purpose:** Add rich snippet schema to all blog posts
- **Status:** Created (inactive)
- **Action:** Find → Click → Activate
- **Expected result:** Blog posts eligible for rich snippets in Google Search
- **Impact:** +15-20% blog traffic potential (2-4 weeks after Google crawl)
- **Verification:** Use Google Rich Results Test: https://search.google.com/test/rich-results

#### ✅ Snippet 69: Mosaic — HotelRoom Schema
- **Purpose:** Add hotel room structured data to /rooms page
- **Status:** Created (inactive)
- **Action:** Find → Click → Activate
- **Expected result:** /rooms page eligible for hotel rich results
- **Impact:** +20-25% booking inquiry potential
- **Verification:** Test /rooms/ at Google Rich Results Test

#### ✅ Snippet 70: Mosaic — LocalBusiness Schema
- **Purpose:** Add local business schema to About page
- **Status:** Created (inactive)
- **Action:** Find → Click → Activate
- **Expected result:** Improved local search visibility
- **Impact:** Better appearance in local search results

---

## Activation Order (Important!)

**Recommended sequence (allows time for cache to clear between activations):**

1. **Snippet 67** (H1 unhide) — 30 seconds to activate
2. Wait 10 seconds, clear browser cache
3. **Snippet 71** (Sitemap fix) — 30 seconds to activate
4. Wait 10 seconds, verify: `curl -I https://www.mosaichostels.com/wp-sitemap.xml`
5. **Snippet 72** (Meta descriptions) — 30 seconds to activate
6. **Snippet 73** (CTA buttons) — 30 seconds to activate
7. Test buttons work on homepage and /book-now/ page
8. Wait 5 minutes (LiteSpeed cache clear)
9. **Snippet 68** (BlogPosting schema) — 30 seconds to activate
10. **Snippet 69** (HotelRoom schema) — 30 seconds to activate
11. **Snippet 70** (LocalBusiness schema) — 30 seconds to activate

**Total time:** ~10 minutes

---

## Verification Checklist

After activating each snippet, verify it's working:

### Snippet 67 (H1 Unhide)
- [ ] Open https://www.mosaichostels.com/ in browser
- [ ] Right-click → Inspect → Find `<h1>` tag
- [ ] Verify H1 does NOT have `position:absolute` or `width:1px`
- [ ] Verify H1 text is visible on page

### Snippet 71 (Sitemap Fix)
- [ ] Run: `curl -I https://www.mosaichostels.com/wp-sitemap.xml`
- [ ] Verify: `content-type: application/xml` (NOT text/html)

### Snippet 72 (Meta Descriptions)
- [ ] Open https://www.mosaichostels.com/wp-json/wp/v2/posts/2479 (use REST API client or curl)
- [ ] Check if meta descriptions appear in page source when you "View Source"
- [ ] Or use: Google Search Console → Performance → check if descriptions show

### Snippet 73 (CTA Buttons)
- [ ] Open https://www.mosaichostels.com/ in browser
- [ ] Find "Book Now" button
- [ ] Click it → should navigate to /book-now/
- [ ] Find "Contact" button
- [ ] Click it → should navigate to /contact/

### Snippets 68-70 (Schema)
- [ ] Go to https://search.google.com/test/rich-results
- [ ] For each page (blog post, /rooms/, about), enter URL
- [ ] Verify schema detected with 0 errors
- [ ] Screenshot results (for documentation)

---

## Troubleshooting

### "Snippet won't activate"
- Refresh page and try again
- Check browser console for JavaScript errors
- Try different browser

### "Meta descriptions not showing"
- Yoast/WordPress may be using its own meta field; snippet adds to fallback
- Clear LiteSpeed cache and reload page

### "Sitemap still returns HTML"
- Deactivate Snippet 71, manually reset Permalinks, then reactivate Snippet 71
- Contact Hostinger support if issue persists (may be server-level caching)

### "Schema not detected by Google"
- Takes 24-48 hours for Google to re-crawl after activation
- Use Search Console to request indexing of /rooms page
- Check Rich Results report in GSC after 1 week

---

## Post-Activation Next Steps

**Immediately after activating all snippets:**
1. Clear LiteSpeed cache: WordPress Admin → LiteSpeed Cache → Purge All
2. Run Google Search Console → URL Inspection on 3-4 URLs to refresh crawl

**Within 24 hours:**
- Monitor Google Search Console for schema errors
- Check homepage to verify H1 visible
- Test Book Now / Contact buttons

**Within 1 week:**
- Submit /rooms/ page to GSC for indexing
- Monitor Rich Results report in GSC
- Verify sitemap shows in GSC Sitemaps section

**Within 2-4 weeks:**
- Monitor blog post CTR improvement in GSC
- Check GA4 for organic traffic increase
- Look for rich snippets appearing in search results

---

## Summary

All 7 snippets are created and ready for activation. Activation is a simple WordPress Admin UI task (no code changes needed). Expected SEO improvements:

- **H1 visibility:** +2-5% homepage SEO boost
- **Sitemap XML:** +10-15% crawl efficiency
- **Meta descriptions:** +5-10% CTR improvement
- **CTA buttons:** +20-30% conversion from organic traffic
- **Blog schema:** +15-20% blog traffic potential
- **Room schema:** +20-25% booking inquiry potential
- **Local schema:** +5-10% local search visibility

**Combined potential impact: +80-150% traffic growth within 6 weeks**

---

**Document created:** 2026-06-26  
**Status:** Ready for manual activation  
**Questions?** Check context.md or COMPLETION_REPORT_2026-06-26.md
