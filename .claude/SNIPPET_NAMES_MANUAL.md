# Snippet Title Setup (Manual WordPress Admin Required)

**Issue:** REST API cannot save snippet titles (Code Snippets plugin limitation).

**Solution:** Update titles manually in WordPress Admin.

---

## Required Names for Snippets 69-75

| Snippet ID | Required Title |
|-----------|----------------|
| 69 | Mosaic — HotelRoom Schema |
| 70 | Mosaic — LocalBusiness Schema |
| 71 | Mosaic — Force Sitemap Regeneration |
| 72 | Mosaic — Inject Blog Meta Descriptions |
| 73 | Mosaic — Fix CTA Button Links |
| 74 | Mosaic — Unhide Homepage H1 |
| 75 | Mosaic — BlogPosting Schema for Posts |

---

## Manual Update Steps

1. Login to WordPress Admin: https://www.mosaichostels.com/wp-admin
2. Go to: **Settings → Code Snippets**
3. For each snippet (69-75):
   - Click the snippet ID to open
   - Edit the title field at the top
   - Paste the required name from the table above
   - Click "Update" or "Save"
4. Verify all 7 snippets show correct names

---

## Why This Matters

- Clear naming prevents accidental deactivation of critical snippets
- Easier to manage/maintain in the future
- Matches documentation (SNIPPET_CLEANUP_REPORT.md, SNIPPET_ACTIVATION_GUIDE.md)
- WordPress Admin UI shows descriptive names instead of just IDs

---

## Time Required

~2 minutes (30 seconds per snippet × 7)

---

**Status:** Awaiting manual title entry  
**Impact:** None (functionality works without titles, this is for clarity only)
