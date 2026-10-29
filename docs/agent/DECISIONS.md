Read when: proposing a change that might contradict an earlier choice, or asking why something is the way it is.
Verified: 2026-10-29 @ fd29588
Covers: -

# Decisions

| Date | Decision | Why / evidence |
|---|---|---|
| 2025-26 | Static HTML + PHP endpoints, manual FTP deploy to Hostinger | Simplicity; "assumed to continue", not declared binding (`PRODUCT.md`) |
| 2026-09 | Blog posts are static pages `blog/<slug>/index.html`, no client-side markdown | Crawlability; `blogs/*.md` left as dead legacy (removed 2026-10-29) |
| 2026-10-06 | Removed `/blog/<anything>` -> `blog.html` route and `blog/post.html` template | Slug route returned 200 noindex for unknown URLs (soft 404); `.htaccess` comment |
| 2026-09 / 10 | Legacy WordPress and AI-invented URLs get 301s (about-us, contact-us, experiences, malformed slugs, policies) | Reclaim impressions seen in GSC/GA4/Bing; each has a dated comment in `.htaccess` |
| 2026-09-08 | Merged 3 Assi Ghat posts into `assi-ghat-varanasi-complete-guide`; `top-7-experiences` into `things-to-do` | Cannibalization audit |
| - | `?v=` query on shared JS/CSS because of 30-day immutable caching | `.htaccess:75-82` |
| - | Razorpay/eZee mode controlled only by server-side keys, no code branch | Fewer ways to misconfigure |
| - | Client never sends a price; server re-fetches eZee RoomList | Price-integrity (`api/create-order.php` docblock) |
| - | Three confirm paths (client, webhook, cron) share one atomic `rename()` claim | Guest may close tab; webhook may be unregistered |
| - | Orders stuck in `processing/` are parked in `failed/` and a human is alerted, not retried | Could double-book |
| - | Pending orders stored outside the docroot, not in a DB | Never web-reachable, untouched by FTP deploy |
| 2026-10-21 | "steps from Assi Ghat" replaced by owner-confirmed "100 m" on 17 pages | Owner confirmation |
| 2026-10-21 | `sameAs` experiment on `/about` only: 6 thin aggregator links removed (F-0056) | LLMO test; outcome still to measure |
| 2026-10-20 | "24-hour reception" wording aligned | Commit `2d41655` |
| 2026-10-23 | New `/dorms/` page for "dormitory near Assi Ghat" (F-0058, owner approved) | ~135 impressions/90d at pos 10-13, 0 clicks |
| 2026-10-23 | Single `AGENTS.md`; `CLAUDE.md` is `@AGENTS.md`; `.claude/` holds the real skills, no `.agents/` folder | Consolidation (`a02ca7c`); opencli skill removed |
| - | Positioning copy stays as the SEO work set it | `PRODUCT.md` principle 5 |

## Open
- WCAG AA as a formal requirement (undecided).
- Whether Hostinger/FTP stays the platform (assumed).
- 2026-10-29: owner decided to retire `blogs/*.md` (14 unused files); removed from git the same day. `.htaccess` keeps its `!/blogs/` guards (harmless).
- Guest email: the PHP sends no guest email (only `booking_alert` mail to the owner, `api/lib/config.php:69`), yet `components/book-now.js:766` tells the guest "A confirmation has been sent to your email". Unknown whether eZee sends one itself; verify with a test booking before changing the sentence or building email.
- No booking-modify endpoint (`api/modify-booking.php` absent): changes go through WhatsApp. Not planned.
- `razorpay_create_order` has no idempotency key (`api/lib/razorpay.php:12`); a repeated POST makes a second unpaid Razorpay order. Accepted: the widget reuses the last order on retry and unpaid orders expire unused.
- AddPayment has one retry and no outbox (`api/lib/booking.php:217`, ponytail note): a double failure raises an alert for a manual post in eZee. Upgrade path is an outbox plus a cron, only if failures appear in pairs.
- Whether `/dorms/` should be in the navbar: unknown; currently linked from the home page only.
