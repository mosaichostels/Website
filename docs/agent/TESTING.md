Read when: deciding how to verify a change, or interpreting a failing check.
Verified: 2026-10-29 @ fd29588
Covers: api/lib/selftest.php,scripts/flow-test/*,scripts/e2e-booking-test.php,.claude/seo/tests/*,.claude/seo/verify.sh

# Testing

No CI (`.github/` absent) and no JS test suite. Verification is script-based and manual.

| Change type | Run | Last result |
|---|---|---|
| `api/**/*.php` | `php -d zend.assertions=1 -d assert.exception=1 api/lib/selftest.php` (deploy.sh also runs it) | PASS 2026-10-27 (adds guest values, page/server list drift, eZee error shapes). Earlier, 2026-10-23: covers HMAC signature, rename() claim, paise math, `ezee_room_total` shapes, dates, refund outcome |
| Booking flow, no live services | `scripts/flow-test/run.sh` (copies `api/` + the booking page into a temp dir, points them at a local mock of eZee and Razorpay, ~2 min, frees ports 8899/8900) | PASS 2026-10-27: 158 checks. Search, order, pay+verify, webhook, cron sweep, retries and parking, concurrency, cancel and refund, rate limits, bad/translated/oversized guest data, corrupt or unwritable order folders, slow eZee under a 30 s PHP limit. The mock encodes the eZee rules verified live on 2026-10-27 (per-night rate lists for multi-night; accepts any title/gender/country/last name). Still no proof of anything not yet probed live |
| Booking page in a browser | Playwright against `scripts/flow-test/run.sh`'s site with a fake Razorpay popup (see STATUS 2026-10-27) | PASS 2026-10-27 (14 checks): translated page still sends English values, success and "Payment Received" screens, tampered value shows a message and opens no payment window |
| Live eZee probe (create + cancel fake reservations) | See GOTCHAS "Live test method"; real site code + live eZee + mocked Razorpay worked for 26 Oct / 27 Sep / 1-night stays on 2026-10-27 | PASS 2026-10-27. Creates real reservations: cancel each at once, never post a payment |
| Booking flow end to end (live eZee) | `php -S 127.0.0.1:8899 -t .` + `php scripts/e2e-booking-test.php` | Not run: needs real eZee + `rzp_test_` secrets; never live keys; creates real reservations |
| Any HTML/sitemap/JSON-LD | `./.claude/seo/verify.sh` (changed files) or `--all` | Not run |
| SEO scripts in `.claude/seo/` | `cd .claude/seo && python3 -m unittest discover -s tests` | PASS 100 tests 2026-10-23 |
| Terminal dashboard | `python3 scripts/test_dashboard.py` | FAIL on system python3 (no Pillow); needs the missing SEO venv |
| Shared JS/CSS edits | Cache-bust consistency (COMMANDS) / skill `cache-bust-check` | Consistent now: one version per asset |
| After deploy | `python3 .claude/seo/live_check.py`, `./.claude/seo/deploy-drift.sh` | Not run (hits live site) |
| Payment stuck | Skill `.claude/skills/reconcile-payment` (diagnose before touching eZee) | n/a |
| Security review of `api/` | Agent `.claude/agents/security-reviewer.md` | n/a |

## Test data and local notes
- `selftest.php` defines a throwaway `RAZORPAY_KEY_SECRET`; needs no `secrets.php`.
- `.claude/seo/live_check.json` is the expected-status/redirect table; update on intentional URL changes.
- Razorpay test-mode results and the go-live checklist: `.planning/razorpay-live-readiness.md` (local, git-ignored; not read here).
- Gaps: no automated test for `components/*.js` (booking widget, 1132 lines), `.htaccess` rules (only `live_check.py` post-deploy), or the cancel flow (only E2E).
- Browser checks: use Playwright MCP against the live or local server; booking needs real eZee data so verify UI only up to the Razorpay step.
