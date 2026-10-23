Read when: writing or editing pages, copy, blog posts, shared JS/CSS, PHP, or commits.
Verified: 2026-10-23 @ 7118c3f

# Conventions

## Rules
| Rule | Detail |
|---|---|
| No build step | Static pages, plain JS in `components/`, one CSS file. Do not add bundlers, npm or frameworks |
| Cache bust | After editing any `components/*.js` or `styles/global.css`, change the `?v=` string on EVERY HTML file referencing it (25 files today, includes `dorms/` and `blog/*`). Format `YYYYMMDD` (+ suffix like `r6`). Skill `cache-bust-check`. Check: all references to one asset show a single version (COMMANDS) |
| Clean URLs | Link to `/about`, `/book-now`, `/gallery`, `/contact`, `/privacy`, `/blog/`, `/dorms/` (no `.html`, folders keep trailing slash) |
| Copy claims | Owner-supplied only: "100 m from Assi Ghat", "1500+ guests", "4.8 (427 reviews)", "60+ countries". Never invent reviews, ratings, prices, counts, distances |
| Policy wording | Only what `PRODUCT.md` says: check-in from 1:00 PM, check-out by 10:30 AM, 24-hour reception, free cancellation up to 72 h before check-in |
| Rooms | Exactly the 5 owner-confirmed types (OVERVIEW). Common room is not a room type |
| Positioning | Keep "Premium budget hostel near Assi Ghat" and SEO-established copy structure unless the owner says otherwise |
| Scope lock (SEO runs) | Touch only html, `styles/`, `components/`, `sitemap.xml`, `robots.txt`, `llms.txt`, verified SEO 301s in `.htaccess`, `seo-reports/` |
| Debug files | Never deploy diagnostic/debug/test files (a hook blocks the obvious names) |
| Credentials | Never edit or print `api/secrets.php`; hook blocks Write/Edit (`.claude/hooks/block-creds-edit`) |

## New blog post checklist
1. `blog/<slug>/index.html` with canonical `https://www.mosaichostels.com/blog/<slug>/`, JSON-LD, Read Next links; copy an existing post as the template.
2. Add to `blog/index.html` and `sitemap.xml` (and `sitemap-images.xml` if it has images); mention in `llms.txt` if relevant.
3. Do not create a `blogs/<slug>.md`; those 14 files are legacy and not rendered.
4. `./.claude/seo/verify.sh`, then deploy (COMMANDS), then `python3 .claude/seo/live_check.py`, add the URL to `.claude/seo/live_check.json` if it tracks pages, then `scripts/indexnow-submit.sh --since <ref>`.

## New page checklist
Folder + `index.html` (like `dorms/`) needs no `.htaccess` rule. A root `.html` page needs the three rewrite pieces in `.htaccess` (`foo.html` -> `/foo` 301, `foo/` -> `/foo` 301, `foo` -> `foo.html` with the `!-f`,`!-d`,`!/blogs/` conds). Add to `sitemap.xml`, link from `components/navbar.js`/`footer.js` if it should be navigable (`/dorms/` currently is not in the navbar).

## Code style seen in repo
- JS: IIFE per file, `function` declarations, `window.MOSAIC` for shared helpers, `fetch` with timeouts via `fetchJson` (`components/book-now.js:252`).
- PHP: docblock at top stating method, body and the trust boundary; `require __DIR__ . '/lib/config.php'` first; `require_method()`, `rate_limit()`, `json_error()/json_ok()` helpers; comments explain past incidents.
- Money: integer paise math, never floats; client never supplies a price.

## Commits
SEO work: `chore(seo): <what> (F-00xx)` or `feat(seo): ...`. Docs: `docs(agent): ...`. Conventional-commit prefixes are used throughout (`chore:`, `docs:`, `feat:`).
