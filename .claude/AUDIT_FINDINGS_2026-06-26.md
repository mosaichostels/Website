# Website Audit Findings — Post-Restore Issues
**Date:** 2026-06-26 11:45 AM  
**Status:** 6 Critical Issues Found  
**Impact:** Phase 1 fixes partially reverted, critical gaps introduced

---

## Critical Issues (Must Fix Before Implementation)

### 1. ❌ SITEMAP BROKEN — Returns HTML, Not XML

**Status:** CRITICAL  
**URL:** https://www.mosaichostels.com/wp-sitemap.xml  
**Issue:** Content-Type: text/html (should be application/xml)  
**Impact:** Google cannot parse sitemap — 0% crawl efficiency

**Evidence:**
```
curl -I https://www.mosaichostels.com/wp-sitemap.xml
HTTP/2 200
content-type: text/html
```

**Root Cause:** LiteSpeed cache misconfiguration OR XML rendering broken after restore  
**Fix:** Rebuild sitemap + unblock from LiteSpeed cache exclusions

---

### 2. ❌ HOMEPAGE H1 STILL HIDDEN — CSS Display:None

**Status:** CRITICAL  
**Issue:** H1 has CSS: `position:absolute; width:1px; height:1px; overflow:hidden`  
**Impact:** H1 invisible to users + reduced SEO weight  
**Expected:** Phase 1.2 was supposed to unhide this

**Evidence:**
```
curl https://www.mosaichostels.com/ | grep h1
<h1 style="position:absolute;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap;border:0">Hostel in Varanasi Near Assi Ghat</h1>
```

**Root Cause:** Phase 1.2 H1 unhide snippet either:
- Never deployed, OR
- Was reverted during restore

**Fix:** Deploy H1 unhide code snippet immediately

---

### 3. ❌ /rooms PAGE DOES NOT EXIST

**Status:** CRITICAL  
**Issue:** /rooms/ URL doesn't exist in WordPress  
**Impact:** Cannot deploy HotelRoom schema, blocks Phase 2 entirely

**Evidence:**
```
curl https://www.mosaichostels.com/wp-json/wp/v2/pages?slug=rooms
(returns empty)

Existing pages:
- blog, contact, about, gallery, book-now, home
- NO "rooms" page
```

**Root Cause:** Restore did not include /rooms page OR page was deleted

**Fix:** Create /rooms page from scratch with ACF room data integration

---

### 4. ❌ ALL BLOG POSTS MISSING METADATA

**Status:** CRITICAL  
**Issue:** All blog posts have yoast_meta = null (no meta descriptions, titles)  
**Impact:** GSC displays auto-generated snippets (poor CTR), no SEO optimization

**Evidence:**
```
curl https://www.mosaichostels.com/wp-json/wp/v2/posts
Post 2479: yoast_meta: null
Post 2478: yoast_meta: null
Post 2477: yoast_meta: null
... (all 10 posts)
```

**Root Cause:** Restore stripped Yoast metadata OR plugin not active

**Fix:** Populate all blog post meta descriptions (155-160 chars, keyword-focused)

---

### 5. ❌ CODE SNIPPETS CORRUPTED — No Titles, Unknown Purpose

**Status:** HIGH  
**Issue:** Active snippets (IDs 34, 49-52) have null titles — cannot identify purpose  
**Impact:** Cannot debug which snippets are for what; cannot modify safely

**Evidence:**
```
curl /wp-json/code-snippets/v1/snippets
ID 34: name: null, active: true
ID 49: name: null, active: true
ID 50: name: null, active: true
ID 51: name: null, active: true
ID 52: name: null, active: true
```

**Root Cause:** Restore corrupted snippet metadata

**Fix:** Inventory all active snippets, identify purpose, re-name if needed

---

### 6. ⚠️ NO BLOG POST SCHEMA — BlogPosting & HotelRoom Missing

**Status:** HIGH  
**Issue:** Homepage has Hostel + WebSite schema; blog posts have NO schema  
**Impact:** No rich snippets on blog SERPs, no schema on future rooms page

**Evidence:**
```
curl https://www.mosaichostels.com/ | grep -o "BlogPosting\|HotelRoom"
(returns nothing)

curl https://www.mosaichostels.com/ | grep "schema.org"
✅ schema.org present (Hostel + WebSite)
❌ No BlogPosting found
❌ No HotelRoom found
```

**Root Cause:** Never deployed OR reverted during restore

**Fix:** Deploy BlogPosting schema to all blog posts + HotelRoom to /rooms page

---

## Secondary Issues (Non-Blocking)

### 7. WP Smush Plugin Status Unknown
- Need to verify: Is WP Smush installed?
- If not: Install + optimize images
- Impact: Page speed optimization

### 8. Scroll Animations Not Fully Removed
- Homepage CSS has `scroll-behavior: smooth` and scroll reveal classes
- Impact: Content may still be hidden on scroll
- Fix: Deploy scroll animation removal snippet

---

## Summary Table

| Issue | Severity | Status | Fix Effort | Blocker |
|-------|----------|--------|-----------|---------|
| 1. Sitemap broken (HTML) | CRITICAL | Not fixed | 30 min | GSC crawl blocked |
| 2. H1 hidden | CRITICAL | Not fixed | 15 min | SEO impact |
| 3. /rooms page missing | CRITICAL | Not fixed | 2 hours | Schema blocked |
| 4. Blog meta missing | CRITICAL | Not fixed | 1 hour | CTR impact |
| 5. Snippet titles corrupted | HIGH | Identify | 30 min | Safety risk |
| 6. Blog/Room schema missing | HIGH | Not deployed | 2 hours | Traffic blocked |
| 7. WP Smush unknown | MEDIUM | Check | 0-30 min | Speed optimization |
| 8. Scroll animations active | MEDIUM | Check | 15 min | Indexability |

---

## Priority: Fix Before Implementation Plan

**Must Fix First (Blocking):**
1. Rebuild sitemap (fix XML rendering)
2. Unhide H1
3. Identify active snippets (safety check)
4. Add blog meta descriptions
5. Create /rooms page
6. Deploy schema markup

**Can Parallelize:**
- WP Smush verification
- Scroll animation removal
- Blog content writing

---

## Next Steps

1. Audit sitemap cache settings (LiteSpeed configuration)
2. Deploy H1 unhide snippet
3. Run full snippet audit + naming pass
4. Create /rooms page + ACF integration
5. Bulk update blog post meta descriptions
6. Deploy BlogPosting + HotelRoom schemas
7. Verify all fixes live
8. Run revised GSC audit
9. Proceed to full implementation plan

---

**Audit Complete:** 2026-06-26 11:45 AM  
**Ready for Plan Revision:** YES
