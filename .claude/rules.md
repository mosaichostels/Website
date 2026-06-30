# Rules

## 2026-06-27: Code Snippet Backup After Each Update
**Rule:** After each successful snippet update (manual or automated), run backup: `python3 backup-snippets.py`
**Why:** Data loss protection. Snippets contain 16+ critical site functions (schema, homepage, routing, etc.). Accidental deletion/corruption requires recovery.
**How to apply:**
- Manual update → WordPress Admin → Code Snippets → Edit → Save → Run backup script
- Automated update → Use `update-snippet-with-backup.py` script (auto-backs up on success)
- Location: `snippet-backups/` folder, files named `snippet-[ID]-[NAME].txt` (e.g., `snippet-73-mosaic-home-page.txt`)
- Backup includes: full snippet JSON (name, code, scope, active status, etc.)
**Tools:**
- `backup-snippets.py` — fetches all 16 snippets via REST API, saves individually
- `update-snippet-with-backup.py <ID> <field> <value>` — update + auto-backup wrapper
**Verification:** Check project root for `snippet-*.txt` files after update

## 2026-06-26: Code Modification Method Constraint
**Rule:** All code modifications via WordPress Admin UI only. No mu-plugins, SSH, or direct file access.
**Why:** Code Snippets REST API has limitations (cannot modify existing snippets). SSH/mu-plugins rejected by user preference.
**How to apply:** Use WordPress Admin Dashboard → Code Snippets → Edit snippet directly. Avoid REST API for modifications, use Admin UI.

## 2026-06-28: Email Address for All Project Operations
**Rule:** Always use mosaichostels@gmail.com for all project authentication, credentials, and operations.
**Why:** Single source of truth for project access. Prevents credential confusion across multiple accounts.
**How to apply:** 
- WordPress REST API calls: Use `mosaichostels@gmail.com` + app password
- Any external integrations, API calls, or backups: Use this email
- If credential prompts appear, use this email automatically

## 2026-06-28: Code Snippets Hook Execution Constraint
**Rule:** Do NOT create new Code Snippets that rely on wp_head, wp_footer, or wp_enqueue_scripts hooks. These hooks execute but output is suppressed/not rendered by plugin.
**Why:** Tested 5 separate snippets (73-77) using these hooks for CSS injection. All were active with no errors, but CSS never appeared in page output or was applied. Root cause is Code Snippets plugin-level issue, not code syntax.
**How to apply:**
- For CSS injection: Use WordPress Admin UI manual edit to existing, proven snippets (don't create new ones)
- For hook-based modifications: If absolutely necessary, modify existing snippet via Admin UI with database persistence verification
- Avoid trying to add new wp_head/wp_footer snippets entirely — they silently fail
**Exception:** If CSS must be injected, only use method: manual WordPress Admin edit to existing Snippet 53/55/etc with verification

## Prior Rule (superseded): All Page Changes via Code Snippets REST API
**Status:** Deprecated. REST API proven non-viable for modifications.
**Lesson:** Code Snippets plugin blocks REST API updates via validation layer. Manual edits required.
