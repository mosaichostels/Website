# Emergency Rollback Procedure

If any snippet causes issues (redirect loop, styling problems, JS errors):

## Quick Rollback (2 minutes)

1. **Deactivate problematic snippet:**
   - WordPress Admin → Settings → Code Snippets
   - Find the problematic snippet (75, 78, 79, or 81)
   - Click → Deactivate
   - Verify: Checkmark removed

2. **If all snippets have issues:**
   - Deactivate ALL 4:
     - Snippet 81 (CSS) → Deactivate
     - Snippet 75 (Navbar) → Deactivate
     - Snippet 78 (Footer) → Deactivate
     - Snippet 79 (JavaScript) → Deactivate

3. **Clear cache:**
   ```bash
   curl -X POST "https://www.mosaichostels.com/?litespeed_purge_all=1"
   ```

4. **Clear browser cache:**
   - Ctrl+Shift+Delete (Windows)
   - Cmd+Shift+Delete (Mac)

5. **Test pages:**
   - Visit https://www.mosaichostels.com/
   - Verify pages load without errors

## If Pages Still Broken

If pages show blank or error after deactivating snippets, the original page HTML may need restoration from backup.

**Backup available:**
- Location: `/Users/naveen/Documents/Github/personal/Website/.claude/backups/website_backup_june23_20260629/`
- Contains: Full page HTML backups (home.html, gallery.html, about.html, contact.html, book-now.html)

Contact developer to restore from backup if needed.

## Snippet Reference

For reference, the created snippets:

| ID | Name | Type | Hook | Function |
|----|------|------|------|----------|
| 2526 | Core / Styles [CSS] | CSS | wp_head | Global styles, colors, navbar, footer, gallery layout |
| 2527 | Core / Navbar [HTML] | HTML | wp_head | Navigation bar with logo, menu links, hamburger |
| 2528 | Core / Footer [HTML] | HTML | wp_footer | Footer with logo, links, copyright |
| 2529 | Core / Interactions [JS] | JavaScript | wp_footer | Gallery filters, lightbox, menu toggle, animations |

## Testing After Rollback

After deactivating snippets, verify:
- [ ] Pages load (no blank pages)
- [ ] No redirect loop
- [ ] Content visible
- [ ] No JavaScript errors in console
