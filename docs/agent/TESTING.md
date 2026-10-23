Read when: deciding how to verify a change, or interpreting a failing check.
Verified: 2026-10-23 @ 7118c3f

# Testing

No CI (`.github/` absent) and no JS test suite. Verification is script-based and manual.

| Change type | Run | Last result |
|---|---|---|
| `api/**/*.php` | `php -d zend.assertions=1 -d assert.exception=1 api/lib/selftest.php` (deploy.sh also runs it) | PASS 2026-10-23: covers HMAC signature, rename() claim, paise math, `ezee_room_total` shapes, dates, refund outcome |
| Booking flow end to end | `php -S 127.0.0.1:8899 -t .` + `php scripts/e2e-booking-test.php` | Not run: needs real eZee + `rzp_test_` secrets; never live keys |
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
