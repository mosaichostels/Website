# Code Snippets Audit & Refactoring Report
**Date:** 2026-06-26  
**Audited:** 15 active snippets  
**Status:** Analysis complete, awaiting action

---

## Executive Summary

- **Keep as-is:** 11 snippets (all working, minimal bloat)
- **Refactor:** 1 snippet (#46 SEO Suite — 16KB, mixed concerns)
- **Delete:** 2 snippets (#81 image update + #87 deactivated)

**Result:** 13 clean active snippets after cleanup

---

## Detailed Findings

### ✅ KEEP (No changes needed)
- **34:** Navigation Helper — lean, focused
- **49-52:** Page templates — necessary, base64 required
- **55:** Blog template — large but necessary, risky to split
- **65:** Redirect + AI rules — clean, functional
- **66:** llms.txt generator — minimal, working
- **70-74:** CSS/JS optimizations — all excellent

### ⚠️ REFACTOR
**Snippet 46: SEO Suite** (282 lines, 16KB)

**Issues:**
1. Mixed responsibilities: security headers + schemas + page configs
2. Code duplication: `mosaic_hostel_schema()` reused (home + book-now)
3. Hardcoded blog URLs in llms.txt (should be dynamic)
4. Large file harder to maintain

**Refactoring Plan:**
Split into 3 focused snippets:
- **46a:** Security headers (HSTS, CSP, X-Frame-Options, etc.)
- **46b:** Schema helper functions (Hostel schema, breadcrumbs, blog schema)
- **46c:** Page SEO configs (page head tags, blog post tags)

**Benefit:** Easier to update, modify, and maintain  
**Risk:** LOW — all logic preserved, tested migration possible  
**Effort:** 45 minutes

### ❌ DELETE
- **81:** Female Dorm Image Update (one-off task completed)
- **87:** Home Page (deactivated, superseded)

---

## Implementation Plan

**Phase 1: Cleanup (5 min)**
1. Delete snippet 81
2. Delete snippet 87
→ Result: 13 active snippets

**Phase 2: Refactor 46 (Optional, 45 min)**
1. Create snippet 46a (security headers code)
2. Create snippet 46b (schema helpers code)
3. Create snippet 46c (page SEO config code)
4. Delete original snippet 46
→ Result: 15 active snippets (cleaner organization)

---

## Next Steps

Wait for user decision:
- Delete 81 + 87 only?
- Or also refactor 46?
