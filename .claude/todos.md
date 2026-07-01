# Project Todos — Mosaic Hostel Static Website Redesign

**Current Session:** 8 (2026-07-01)  
**Status:** Phase 3 (Homepage Fixes) — Navbar/Stats/Scroll indicator  
**Goal:** Fix homepage issues, restore navbar visibility, style stats grid, hide scroll text

---

## PHASE 3 HOMEPAGE FIXES — ✅ COMPLETE (2026-07-01)

### ✅ HomePage DevTools Analysis & Fixes
- [x] Chrome DevTools MCP analysis complete
- [x] Found: 8 duplicate navbars, 2 duplicate footers, CORS-blocked image, missing favicon
- [x] Fixed: Removed inline navbar/footer from index.html, fixed CORS URL, added favicon
- [x] Committed: 7fecdb9
- [x] Pushed to GitHub (origin/main)
- [x] Deployed to Hostinger via FTP (IP 147.93.17.169)
- [x] Verified on live site (mosaichostels.com) — all fixes confirmed
- [ ] Run Lighthouse audit post-deployment (optional)

---

## REMAINING WORK (Post-Phase 3)

### Session 9: Documentation & Cleanup
- [ ] Remove stale files from repo root:
  - [ ] `navbar.html` (duplicate, component version exists)
  - [ ] `footer.html` (duplicate, component version exists)
  - [ ] `DEPLOYMENT-*.md` (outdated, docs in .claude/CLAUDE.md now)
  - [ ] `HOMEPAGE-*.md` (outdated, no longer relevant)
  - [ ] `*.png` screenshots (large files, not needed in repo)
- [ ] Verify no broken links or 404s on production
- [ ] Final Lighthouse audit all 7 pages
- [ ] Document git commit history for reference

### Session 10+: Feature Enhancements (Optional)
- [ ] Image click-to-enlarge modal (components/modal.js enhancement)
- [ ] Booking form backend integration (if needed)
- [ ] Blog post dynamic loading
- [ ] Contact form email submission
- [ ] SEO schema markup enhancements
