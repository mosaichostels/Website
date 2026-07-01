# OpenCLI Homepage Analysis — Mosaic Hostel

**Generated:** 2026-07-01  
**Adapter:** `/Users/naveen/.opencli/clis/mosaichostels/homepage.js`  
**URL:** https://mosaichostels.com

## Analysis Summary

### Navigation Structure
- **Status:** Active
- **Links:** Rooms, Gallery, About, Contact
- **Implementation:** Navbar visible and functional

### Page Headings (16 total)
| Level | Heading | Status |
|-------|---------|--------|
| H1 | Each Guest a Piece. Each Story a Tile. | ✓ Found |
| H2 | Every Room, a Unique Tile | ✓ Found |
| H2 | Why Travelers Choose Mosaic | ✓ Found |
| H3 | Heart of Varanasi | ✓ Found |
| H3 | Community First | ✓ Found |
| H3 | Safe & Comfortable | ✓ Found |
| H2 | More Than a Place to Sleep | ✓ Found |
| H2 | Begin Your Mosaic Story | ✓ Found |
| H3 | Mosaic Hostel | ✓ Found |
| H3 | Explore | ✓ Found |
| H3 | Connect | ✓ Found |
| H3 | Legal | ✓ Found |

### Call-to-Actions (CTAs)
| CTA | Status | Visibility |
|-----|--------|-----------|
| Book Now | Present | Visible |
| Book Now | Present | Visible |
| Hidden CTA | Present | Hidden |
| Hidden CTA | Present | Hidden |

**Finding:** 2 primary visible CTAs (Book Now), 2 hidden CTAs (possibly modal/interactive)

### Media
- **Total Images:** 9
- **Status:** Counted and loaded

### Forms
- **Count:** 0 active forms on page
- **Note:** Booking likely handled via CTA buttons/modal

### Meta Information
- **Title:** Mosaic Hostel Varanasi — Premium Stays in Sacred Varanasi
- **Description:** Stay at Mosaic Hostel, Varanasi's premier hostel steps from...
- **Status:** ✓ Properly set for SEO

## Structural Assessment

✓ **Strengths:**
- Clear information hierarchy with proper H1 → H2 → H3 structure
- Navigation is minimal but covers key sections
- Strong CTAs with visible "Book Now" buttons
- Meta title/description optimized for SEO
- Image assets integrated

⚠️ **Observations:**
- 0 traditional forms (booking handled via modal/external)
- Some hidden CTAs suggest modal-based interactions
- Gallery/content pages accessible via nav but not analyzed in this scope

## Run This Analysis Again

```bash
opencli mosaichostels homepage -f json      # JSON output
opencli mosaichostels homepage -f yaml      # YAML format
opencli mosaichostels homepage -f table     # Table format
opencli mosaichostels homepage --limit 50   # Increase row limit
```

## Extend This Analysis

To add more fields (links, accessibility, performance, etc.):
```bash
# Edit the adapter
nano /Users/naveen/.opencli/clis/mosaichostels/homepage.js

# Verify changes
opencli browser verify mosaichostels/homepage

# Re-run
opencli mosaichostels homepage
```
