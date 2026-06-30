# Fluent Snippets Migration Design
**Date:** 2026-06-27  
**Goal:** Simplify website snippet management by migrating from Code Snippets plugin to Fluent Snippets with manual audit and quality review.

---

## Overview

Migrate 16 existing Code Snippets to Fluent Snippets with:
- **Manual code review** — inspect each snippet for bugs, security, performance issues
- **Type-based organization** — divide mixed-language snippets and organize by type
- **Quality gates** — fix issues before creating in Fluent Snippets
- **Clean structure** — 4 language groups (HTML, CSS, JavaScript, PHP)

**Outcome:** Audited, organized, maintainable snippet library ready for daily use.

---

## Current State

**Source:** WordPress Code Snippets plugin (16 snippets)  
**Languages:** Mix of PHP, JavaScript, HTML, CSS (need separation)  
**Issues:** Unknown (requires audit)  
**Target:** Fluent Snippets plugin (already installed)

---

## Target State

**Organization:**
- **Groups:** HTML, CSS, JavaScript, PHP (one per language type)
- **Snippets:** Clean, audited code organized by type
- **Tags:** Optional secondary labeling (e.g., "SEO", "navigation", "performance")

**Quality standards:**
- No security vulnerabilities
- Proper error handling
- Performance optimized
- Documented purpose/usage

---

## Process

### Phase 1: Extraction & Analysis
1. Query Code Snippets via REST API (`/code-snippets/v1/snippets`)
2. Extract all 16 snippet details (name, code, description, scope)
3. Audit each snippet:
   - Identify language type(s) (PHP, JS, HTML, CSS)
   - Detect mixed-language snippets (separate into multiple)
   - Flag bugs, security issues, gaps

### Phase 2: Quality Review
Use superpowers (systematic-debugging, code-review):
- Fix identified bugs/vulnerabilities
- Add missing error handling
- Optimize performance
- Document fixes applied

### Phase 3: Migration
1. Create 4 Groups in Fluent Snippets: HTML, CSS, JavaScript, PHP
2. For each audited snippet:
   - Create new Fluent Snippet
   - Assign to correct Group
   - Add metadata/tags
3. Verify creation success
4. Mark Code Snippets as deprecated (optional: delete after verification)

### Phase 4: Verification
- Test snippets in staging (if applicable)
- Verify all 16→N snippets created (N = total after separation)
- Document any skipped/problematic snippets
- Clean up old Code Snippets plugin

---

## Timeline
- **Phase 1:** ~45 min (extraction + analysis)
- **Phase 2:** ~60 min (quality review + fixes)
- **Phase 3:** ~30 min (migration + verification)
- **Total:** 2.5–3 hours

---

## Success Criteria
✓ All 16 snippets extracted and audited  
✓ Any bugs/issues documented and fixed  
✓ Snippets created in Fluent Snippets organized by type  
✓ All snippets verified working in Fluent Snippets  
✓ Old Code Snippets plugin optional: removed or disabled  

---

## Risks & Mitigations
| Risk | Mitigation |
|------|-----------|
| Mixed-language snippets break on separation | Audit phase identifies these; test before deployment |
| Security issues in existing code | Quality review phase catches and fixes |
| API access failures during extraction | Have admin WordPress access as fallback |
| Fluent Snippets creation fails | Verify Fluent Snippets API working; test with 1 snippet first |

---

## Rollback Plan
- Code Snippets plugin untouched until full verification
- Can revert to Code Snippets if Fluent Snippets migration fails
- Backup WordPress database before starting

---

## Next Step
Invoke writing-plans skill to create detailed implementation plan with step-by-step tasks.
