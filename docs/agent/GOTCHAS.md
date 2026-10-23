Read when: before editing anything risky: payments, deploys, redirects, cache versions, secrets, worktrees, agent config.
Verified: 2026-10-23 @ 7118c3f

# Gotchas

| Pitfall | What to do |
|---|---|
| `api/secrets.php` holds live production credentials | Never read, print or edit. Hook blocks Write/Edit. It is git-ignored and uploaded by hand: `./scripts/deploy.sh all` excludes it |
| Stale JS/CSS for 30 days | Bump `?v=` on every referencing HTML. Today `navbar.js?v=20261028` is dated AFTER today (2026-10-23): harmless but means a "bump to today" gives a SMALLER string; any different string works |
| `.htaccess` conds bind to one next rule only | Repeat `!-f`, `!-d`, `!/blogs/` before each clean-URL rewrite |
| Redirect targets that are directories | End the target with `/` or mod_dir issues a second 301 (2-hop) |
| `RewriteCond %{THE_REQUEST}` guard on `/blog/index.html` | Without it the rule loops with `DirectoryIndex` |
| Debug files deployed to prod once | Never deploy files named diag/debug/test; hook blocks the command pattern |
| `eZee` total in two places once disagreed -> every booking 502 | Only edit `ezee_room_total()` (`api/lib/ezee.php:28`) |
| eZee error shapes differ | `CancelBooking` returns Errors as an OBJECT, `AddPayment` as a LIST (`api/lib/booking.php:11`, `api/cancel-booking.php`) |
| Server TZ is UTC | `config.php` sets hotel-local time; the 72 h refund line and "today" depend on it |
| `config.php` missing from a PHP `require` chain silently broke payment resolution once | Every endpoint requires it first |
| `selftest.php` does not need `secrets.php`; real endpoints do | Do not require `config.php` from the test (it exits without secrets) |
| `scripts/deploy.sh` with `.php` files runs selftest and aborts without `php` | Install PHP or deploy non-PHP separately |
| `OpenMontage/` is untracked (via `.git/info/exclude`), large, vendored | Do not search it for site code, do not commit it |
| `blogs/*.md` are not the posts | Live posts are `blog/<slug>/index.html`; markdown is stale (14 vs 16) |
| Missing SEO venv | `~/.config/mosaic-seo/venv` not found 2026-10-23; extractors and dashboard fail until `setup-platforms.sh` is rerun |
| Data lag | Google data lags 2-3 days; Clarity allows about 10 calls/day |
| Submitting IndexNow before the deploy is live | Wait for `deploy-drift.sh` clean |
| Copy claims (reviews, guest counts) | Owner-supplied, unverifiable from the repo; do not extend |
| Scratch dirs ignored by git | `.planning/`, `instagram-media/`, `screenshots/`, `.playwright-mcp/`, SEO cache and run dirs |
| Sensitive docs ignored by git | `docs/eZee-Connectivity-API.md` and other vendor/payment audits may exist locally only; cited line numbers (`~L5531`) point there |

## Worktrees and branches
`git worktree list` shows one worktree (this checkout, `main`). Earlier notes mentioned SEO worktrees with their own `.codex/hooks.json`; none exist now. The real code is here. New worktrees need `.codex/hooks.json` wired.

## Agent config layout (consolidation checked 2026-10-23)
- `.claude/` is the source: `settings.json` (tracked), `settings.local.json` (machine-local, git-ignored, never symlink), `hooks/`, `agents/`, `skills/`, `seo/`.
- `.codex/hooks.json` kept: Codex-only hook format; Claude's equivalent lives in `settings.local.json`. No `.agents/` folder (no skills shared with Codex). No symlinks in the repo.
- `AGENTS.md` is the single instruction file; `CLAUDE.md` is `@AGENTS.md`. `AGENTS.md` also says "follow `~/.codex/AGENTS.md`", the global rules file.
