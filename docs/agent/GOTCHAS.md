Read when: before editing anything risky: payments, deploys, redirects, cache versions, secrets, worktrees, agent config.
Verified: 2026-10-29 @ fd29588
Covers: api/lib/*.php,api/*.php,.htaccess,scripts/deploy.sh,.claude/hooks/*

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

## Accessibility baseline (from the 2026-10-10 site critique, folded from `.impeccable/critique/`)
- Found: footer address/phone ink-on-ink (1.0:1), low-contrast gold values on parchment, gallery and booking calendar not keyboard operable, no live regions, blog link contrast and 95-char measure, privacy policy missing services and date. Scores 17-26 of 32-40 per page.
- Fixed in commit `ef42a36` per its message (footer legible, keyboard gallery with focus trap, labelled date popup, step announcements, blog 68ch measure and booking band on all 14 posts then, privacy services and date). Not re-audited in this run.
- Rule: keep these when editing the footer, gallery, book-now date popup or blog template. WCAG AA as a formal requirement is still undecided (DECISIONS).
- Token source of truth is `DESIGN.md` (gold `#C8860A`, ink `#1A1208`); the removed `.impeccable/design.json` was a generated sidecar of it.

## Worktrees and branches
`git worktree list` shows one worktree (this checkout, `main`). Earlier notes mentioned SEO worktrees with their own `.codex/hooks.json`; none exist now. The real code is here. New worktrees need `.codex/hooks.json` wired.

## Booking: paid but no eZee reservation (root cause found 2026-10-27)
- **Root cause (verified live):** eZee's InsertBooking refuses ANY multi-night stay unless `baserate`, `extradultrate` AND `extrachildrate` each hold one comma-separated value per night in date order (`2099,2099,2099,2099,3500`; one night = a single value). A single number, a stay total, a dated map, or a list for `baserate` only all return `InvalidData`. `create-order.php` used to send one number (the first night's), so every multi-night booking was paid and never reserved: the 27 Sep order (2 nights) and the 26 Oct order (5 nights). Only 1-night stays ever worked. Fixed by `ezee_daywise_rates()` / `ezee_nights()` in `api/lib/ezee.php`. Verified live: the exact 27 Sep and 26 Oct stays, 1 night, 4 nights, 30 nights and a stay across new year all booked, and the total eZee stores equals what the site charges (12490.80 and 1677.90).
- The 27 Aug order failed for a different reason: its first InsertBooking attempt ran two days late (`ArrivalDate is Past date`).
- **My first theory was wrong:** translated form values ("Mâle", "M.") did NOT cause a rejection. Live eZee also accepts a blank first or last name, a blank title/gender/country, `gender=Other`, and a translated country. Still, `<select>` options need an explicit `value=` (otherwise `.value` is the visible, translated text and wrong data lands in the guest record), so `book-now.html` has them, `api/lib/guest.php` lists what the form offers, and `create-order.php` refuses anything else before any Razorpay order exists; `selftest.php` fails if the page and the lists drift. This is data hygiene only.
- `create-order.php` also trims names, requires a non-blank first name, and caps names at 60 characters, the special request at 500, the email at 254 (`guest_text_error()`). A blank last name is allowed (eZee books it). Length counting does not need mbstring.
- eZee rejects in three reply shapes, all read by `ezee_decoded_error()`. A coded rejection (`ErrorCode` / `Error Details`) is `_permanent`: `confirm_paid_order()` parks the order in `failed/` at once with `ambiguous=no`. Only the plain `Errors.ErrorMessage` reply is retried (3 attempts, 120 s apart). Transport errors and a reply without ReservationNo stay ambiguous: never retried.
- `razorpay-webhook.php` returns 500 only for `retry`. An order parked in `failed/` is answered 200: Razorpay switches an endpoint off after about 24 h of 5xx, which would silently remove the backstop.
- `confirm_paid_order()` calls `set_time_limit(120)` and writes the reservation number into the claim file right after InsertBooking succeeds. If the request still dies afterwards, the cron sweep finishes the claim into `done/` and raises an alert to check AddPayment in eZee. An unreadable or empty order record is parked at once with an alert, without calling eZee. If `done/` cannot be written the claim file is kept and an alert is raised.
- Alert emails work in production: the owner received the failure alert for the 26 Oct order (confirmed by the owner).
- Known limit, unchanged: a slow AddPayment (2 x 15 s) can outlast the browser's 25 s verify timeout, so a booked guest may see "Payment Received - confirmation pending". Fix would be to answer the guest right after InsertBooking and run AddPayment after the response is flushed.
- Known limit, unchanged: `ezee_decoded_error()` reads a top-level `ErrorCode` other than "0" as a rejection; no live success reply seen so far carries one.
- Not verified live: `cancel-booking.php` end to end. eZee's FetchSingleBooking does not return a reservation that has no payment posted yet (test reservations made without AddPayment came back "No Reservation Found" for 60 s), while paid and OTA reservations are found. A paid test (AddPayment, then cancel) would be needed, and it leaves a payment line in eZee.
- Live test method (2026-10-27): create a fake `ZZTEST` reservation (`zztest@example.com`) with the site's own `ezee.php`, then CancelBooking at once. Reservations 1764 to 1792 were created this way and all show Cancelled in eZee. Never post a payment to a test reservation.

## Agent config layout (consolidation checked 2026-10-23)
- `.claude/` is the source: `settings.json` (tracked), `settings.local.json` (machine-local, git-ignored, never symlink), `hooks/`, `agents/`, `skills/`, `seo/`.
- `.codex/hooks.json` kept: Codex-only hook format; Claude's equivalent lives in `settings.local.json`. No `.agents/` folder (no skills shared with Codex). No symlinks in the repo.
- `AGENTS.md` is the single instruction file; `CLAUDE.md` is `@AGENTS.md`. `AGENTS.md` also says "follow `~/.codex/AGENTS.md`", the global rules file.
