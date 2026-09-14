# Book-Now Flow — Verified Audit (second pass)

**Date:** 2026-09-13
**Scope:** `book-now.html` → `components/book-now.js` → `api/*.php` → `api/lib/*.php` → eZee / Razorpay
**Method:** Static line-by-line trace of all 2,123 lines in the chain. No live run —
no PHP runtime and no `api/secrets.php` in this environment, so nothing here was
confirmed against a live eZee or Razorpay response.
**Relationship to `book-now-gaps-and-issues.md`:** this is an independent second pass.
Section 1 corrects that document; sections 2–4 are findings it does not contain.

The missing email infrastructure (its B1 / C3) is **deliberately excluded** — known,
tracked there, left alone by instruction.

---

## 0. Status

| Finding | Status | Where |
|---|---|---|
| **N1** price resolver divergence | **Fixed** | `ezee_room_total()` / `ezee_room_base_total()` in `api/lib/ezee.php`; both callers now use it. Guarded by `selftest.php` assertions 4 |
| **N2** unchecked pending write | **Fixed** | `create-order.php` checks the write and 503s before returning an `order_id` |
| **N9** cancellation refund | **Fixed** (decision + work item; no automated refund) | `cancel-booking.php` computes the 72h window from our own `done/` record, returns `refund_note`, logs `payment=` + `amount=` + `refund_due=` |
| **N13** date entry unusable by keyboard | **Fixed** | `readonly` dropped; calendar days are `role=button` + `tabindex=0` + Enter/Space; Escape closes; `:focus-visible` ring added site-wide |
| **N3** badge contradicts failure copy | **Fixed** | `showConfirmStage()` in `book-now.js` sets badge + title + body as one unit — they can no longer drift. New `.direct-badge.is-pending` (teal) variant |
| **N4** confirmed booking reported as failure | **Fixed** | `verifyPayment()` polls on 409 and network error over ~16s (covers eZee's 15s timeout); 502/400/malformed stay terminal. Pay button disabled for the duration so the longer window can't produce a second order (partial N11) |
| **C1, C2** confirmation stage is a dead end | **Fixed** | `showConfirmStage()` renders an action row: "Make another booking" (→ `resetWidget()`) + "Return to home". The pending state deliberately omits "Make another booking" — that guest has already paid |
| **P1** no retry after payment failure | **Fixed** | `Try Payment Again` button surfaced by `offerRetry()` on `payment.failed` and `ondismiss` |
| **N11** repeated failures orphan orders | **Fixed** | A retry reopens the *same* Razorpay order. A new one is created only if the payload changed or the order is over 10 min old, so price and inventory still get re-validated |
| **C5 / part of N19** no booking details on confirmation | **Fixed** (same function as C1/C2 — one step past the brief, flagged) | Dates, nights, rooms and **Total paid** taken from the server-priced order amount, not the client cart sum |
| Timezone (found while fixing N9) | **Fixed** | `date_default_timezone_set('Asia/Kolkata')` in `lib/config.php` — the 72h boundary and `new DateTime('today')` were running on host-default UTC |
| **N5** validation asymmetry | **Fixed** | `validate_stay_dates()` in new `api/lib/dates.php`, shared by both endpoints. Past dates and the 30-night cap now enforced on `create-order.php` too |
| **N6** lenient date parsing | **Fixed** | `parse_strict_date()` uses the `!` format prefix and checks `getLastErrors()`; `parseISO()` in `book-now.js` tightened to match. Guarded by `selftest.php` assertions 5 |
| **N22** private rooms booked as 1 adult | **Fixed**, capped at base occupancy | `base_adults` surfaced by `availability.php`, guests stepper in the results list, re-validated server-side against eZee's `base_adult_occupancy`. See §0b for why the cap is base and not max |
| `Last_Name` empty on a Mandatory eZee field | **Fixed** (found during the eZee check) | `required` added to `#gLastName` |
| `CancelBooking` error shape | **Fixed** (found during the eZee check) | Read as the documented object, not `Errors[0]` |
| **N12** selftest covers nothing, nothing runs it | **Fixed** | Assertions 4–6 added (eZee price resolution, strict dates, refund window); `deploy.sh` now runs it with `zend.assertions=1` and **aborts** whenever the deploy set contains any `.php` |
| **N10a** no rate limiting | **Fixed** (speed bump, not a security control) | `rate_limit()` in `lib/config.php`, file-backed. availability 60/10min, create-order 10/10min, cancel-booking 5/10min. **Never** applied to `verify-payment.php` — N4's retry legitimately calls it six times |
| **N10b** `pending/` never expires | **Fixed** | `reconcile-pending.php` moves orders Razorpay confirms unpaid after 24h into `abandoned/`, and prunes stale rate-limit counters |
| **N18** zero conversion measurement | **Fixed** | Five GA4 ecommerce events: `view_item_list`, `add_to_cart`/`remove_from_cart`, `begin_checkout`, `add_payment_info`, `purchase`. `purchase` is deduped by reservation number and its `value` comes from `paidAmount()` — the same figure the guest sees as "Total paid". All wrapped in `track()`, which no-ops when gtag is blocked and swallows errors |
| **N17** no history or URL state | **Fixed** | `showStage(name, mode)` — `push` forward, `goBackTo()` unwinds backward, `none` under popstate. Dates go in the query string, and `restoreFromUrl()` auto-searches a deep link. Selection is cleared after a confirmed booking so Back can't re-enter the guest form |
| **B5** raw eZee errors echoed to client | **Fixed** | `json_error_upstream()` logs the real text, returns a fixed safe sentence |
| **B2** AddPayment failure not retried | **Fixed** | Retried once via `ezee_add_payment_once()`; a second failure logs `ACTION REQUIRED` with reservation, payment id and amount on one greppable line. Still non-fatal — the booking exists |
| **N14** status messages unannounced | **Fixed** | `showMsg()` sets `role=alert`/`assertive` for errors, `status`/`polite` otherwise; `showStage()` moves focus to the new stage heading |
| **N15** no reduced motion, false hover affordance | **Fixed** | `prefers-reduced-motion` block (keeps `.reveal` visible, since it is revealed *by* a transition); `.room-option` hover no longer lifts, as only its buttons act. Focus ring landed earlier with N13 |
| **N7** unknown availability looked sold out | **Fixed** | `availability.php` preserves `null` instead of coercing to `0`; widget renders three states — a count, "Sold out", or "Availability on request" with a WhatsApp link |
| **R4** quantity capped silently | **Fixed** | Says how many are left, on `#resultsMsg` (the stage the guest is actually on) |
| **N8** price drift charged silently | **Fixed** | Client sends an advisory `expected_total`; server still prices independently but returns `409 price_changed` with both figures, and the widget re-renders the summary and asks before continuing |
| **N16** one exception killed the widget | **Fixed** | `window.MOSAIC` destructuring guarded, decorative helpers degrade to no-ops, plus a `<noscript>` block pointing at WhatsApp |
| **N19** formatting and copy | **Fixed** | `Intl.NumberFormat('en-IN')` → ₹12,500 not ₹12500.00; `plural()` replaces "room(s)"; results and price summary now state dates and night count; four-step progress indicator added |
| **N20** dead CSS | **Fixed** | 693 bytes removed — `.widget-price small`, `.room-option-select`(+hover), `.guest-room-block`(+first-child), `.guest-room-label` |
| **G1** policy only behind a modal | **Fixed** | `.policy-brief` lists the four money-relevant terms inline above the T&C checkbox; the full modal remains |
| **S3** no security headers | **NOT A GAP — my error** | The root `.htaccess` already sets HSTS, `X-Frame-Options`, `nosniff`, Referrer-Policy, Permissions-Policy and a real CSP that allowlists Razorpay correctly. My original finding cited `api/.htaccess` and never checked the root file |
| **N21** rating mismatch | **Owner handling** | Visible "4.9/5 · 1500+ guests" vs JSON-LD `4.8` / `427`, on index/about/blog/book-now. Left unchanged at the owner's direction — it needs the real Tripadvisor figures, not a guess. Note a visible/`AggregateRating` mismatch is a Google structured-data policy violation |
| **B6** no modification endpoint | **Not attempted** | A feature, not a fix: needs an eZee modify API verified against a live account plus a new UI and re-pricing path |
| **B8** automated refunds | **Not attempted** | Moves real money; needs explicit authorisation and Razorpay refund scope. N9 already logs the work item |
| **B7** lookup by email only | **Declined on merit** | Requiring reservation number *and* email is what stops anyone who guesses a number cancelling a stranger's stay (`cancel-booking.php` docblock). Weakening it buys nothing while there is no email system to deliver a forgotten number |

Not verified by execution: no PHP runtime or Docker in the environment where these
were written, so `selftest.php` has **not been run** and no endpoint was exercised.
The N1 logic was reproduced and the fix confirmed against `mock.php`'s exact entry
shape via a faithful port; `parseISO` and the N4 retry classification were tested
directly. The PHP itself has only been read. **Run `php api/lib/selftest.php` before
deploying** — and from now on `deploy.sh` does that itself for any deploy containing
PHP, aborting if no `php` binary is present.

Cache-bust is at `?v=20260913` for `global.css` and `book-now.js` across all 24 HTML
files. `HEAD` still carries `20260819d` / `20260818f`, so `20260913` has never been
served — further edits today need no further bump, but any edit to those two files
*after* a deploy does.

---

## 0b. eZee compatibility check

Every eZee field this work sends or reads, checked against
`docs/eZee-Connectivity-API.md`. Doc lines are that file's.

### Supported — confirmed in the doc

| What we do | eZee says | Where |
|---|---|---|
| Send `number_adults` > 1 per `Room_N` on InsertBooking (N22) | **Mandatory** field; eZee's own example sends `"number_adults":"2"` | L7293, L7352 |
| Read `base_adult_occupancy` off a RoomList entry (N22) | Documented RoomList response field, "Base adult occupancy in room" | L2150, sample L2214 |
| Cap a stay at 30 nights (N5) | eZee caps it too: `NightsLimitExceeded` — "You can not request for more then 30 nights", and `num_nights` is "limited to the first 30 days" | L2119, L2337 |
| Reject past check-in dates (N5) | eZee rejects them too: `DateNotvalid` — "Requested date is past" | L2344 |
| Read `totalprice_inclusive_all` / `totalprice_room_only` (N1) | Both documented under `room_rates_info` | L2166-2167 |
| Read `available_rooms` / `min_ava_rooms` | Both documented; `available_rooms` is a date-keyed array, which the code already reduces with `min()` | L2157-2158 |
| `InsertBooking` → `ReservationNo`, `SubReservationNo[0]` | Response is `{"ReservationNo":"266","SubReservationNo":["266"],…}` — array for the sub-number, as the code assumes | L7360 |
| `CancelBooking` success via `status` containing "success" | Success response is `{"status":"Successful"}` | L5530 |
| Send `Country` as a full name ("India") | eZee's own samples use full names — "India", "Argentina", "Canada", "Germany" | L400, L807, L5854, L6263 |

### Fixed during this check

| Issue | Detail |
|---|---|
| **`Last_Name` sent empty to a Mandatory field** | InsertBooking marks `Last_Name` Mandatory (L7307), but `#gLastName` had no `required` attribute and `booking.php` sends `$unit['last_name'] ?? ''`. Added `required`. |
| **`CancelBooking` error shape read wrongly** | The doc gives `Errors.ErrorCode` / `Errors.ErrorMessage` as an **object** (L5531-5533), but `cancel-booking.php` indexed `Errors[0]`, which never matched. Harmless in practice — `ezee_curl()` rejects that shape upstream and the `status` check gated success — but it was dead code masquerading as a guard. Now reads the documented shape. |

Note the two families genuinely differ, so this is not a blanket rename:
`AddPayment` (kioskconnectivity) really does return `"Errors":[{…}]` as a
**list** (L6139-6144), so `booking.php`'s `Errors[0]['ErrorCode']` is correct
there and was left alone.

### Why the occupancy cap is `base_adult_occupancy`, not `max_adult_occupancy`

Above base occupancy eZee applies an extra-adult rate, and it validates rates it
is given — `114 Invalid extra adult rate`, `135 Invalid rate for any between
adult1 to adult7` (L1321, L1461). We pass `extradultrate` from
`extra_adult_rates_info.exclusive_tax`, but that figure is **per night and
exclusive of tax**, while the Razorpay amount is built from a **tax-inclusive
stay total**. Combining them correctly needs a live response to confirm the tax
treatment (**U1**), so until then guests may declare only up to the occupancy the
rate already covers, and anything larger is refused with a pointer to WhatsApp.
This keeps the charged amount and the eZee booking in agreement in every case.

Consistency check on that: `create-order.php` re-prices with
`number_adults => 1`. That is sound precisely *because* of the cap — within base
occupancy the rate does not vary with adult count, so pricing a 1-adult query and
booking 2 adults is the same money. It would stop being sound the moment the cap
was raised to `max_adult_occupancy`.

`MaxAdultLimitReach` (L2339) can't be triggered by us: every RoomList call we
make sends `number_adults=1`.

### Still unverified — needs a live call

- **U1** — whether the real response nests the stay totals under
  `room_rates_info` or puts them at the entry top level. `ezee_room_total()` now
  accepts both, so this no longer blocks anything; it only decides whether N1 was
  breaking production or only mock mode.
- **U3** — `Country` as a name is consistent with eZee's samples, but the
  authoritative list comes from the salutation/country-list endpoint (L549). Only
  `FetchSingleBooking` on a real booking proves what was stored.
- Whether this property's `base_adult_occupancy` is actually configured above 1
  for the private rooms. If eZee returns 1 for everything, the guest stepper
  never appears and N22 changes nothing visible — that is a property
  configuration question, not a code one.
---

## 1. Corrections to the existing report

| Existing ID | Claim | Status | Evidence |
|---|---|---|---|
| B11 | "`FetchSingleBooking` exists but unused" | **Wrong** — it is used | `api/cancel-booking.php:22` calls `ezee_fetch_booking()`; defined `api/lib/ezee.php:37` |
| G4 | "No detailed fare breakdown per room" | **Outdated** — a breakdown exists | `components/book-now.js:228-233` renders per-item rows + "Room rate" + "Tax"; `:212-216` does the same in the cart bar. The named function `renderPriceSummary()` does not exist |
| G6 | "No buttons on guest page" (Medium) | **Overstated** | `book-now.html:337` has `← Back to Rooms`. The real dead end is the confirmation stage (C1/C2), which is correct |
| B4 | "No past-date validation" | **Correct, and narrower than stated** | `availability.php:23` *does* reject past dates; `create-order.php:83-87` does not. The gap is the asymmetry, not the absence |
| S1–S6 | Security IDs | **Numbering collision** | `S1`–`S4` are also used for Stage 1 gaps in the same document |

---

## 2. New findings — correctness

### N1 — `create-order.php` reads price from a different place than `availability.php`, and fails closed (Critical)

`availability.php:85-89` falls back through **four** locations for the stay total:

```php
$total = $rates['totalprice_inclusive_all']
  ?? $rates['totalprice_room_only']
  ?? $entry['totalprice_inclusive_all']   // entry top level
  ?? $entry['totalprice_room_only'];      // entry top level
```

`create-order.php:131` reads only the **first two**:

```php
$perUnitTotal = ezee_price_scalar($rates['totalprice_inclusive_all'] ?? $rates['totalprice_room_only'] ?? 0);
```

If eZee returns the total at the entry's top level (not nested under
`room_rates_info`), search shows a price and checkout dies with
`502 "Could not determine a price for one of the selected rooms"`
(`create-order.php:132-134`).

This is not hypothetical — **it is exactly what mock mode produces.**
`api/lib/mock.php:33` puts `totalprice_inclusive_all` at the entry top level, and
`:36` gives `room_rates_info` only an `exclusive_tax` key. So with
`EZEE_MOCK_ROOMLIST` set, every booking attempt fails at checkout while the search
stage looks healthy. The mock path — the only way to test the flow without touching
the live hotel account — is broken end to end.

> **Update, 2026-09-14.** `api/lib/mock.php` and the `EZEE_MOCK_ROOMLIST` branches
> have since been removed at the owner's direction, so there is no mock path at
> all: `api/` talks only to real eZee and real Razorpay. The N1 fix itself stands
> and is guarded by `selftest.php` assertion 4, which now carries the two response
> shapes as inline fixtures rather than reading them from the mock.
> `scripts/e2e-booking-test.php` is consequently an integration suite requiring
> live credentials.

**Fix:** give `create-order.php:131` the same four-step fallback, or better, extract the
price-resolution into one function both endpoints call. One source of truth, since
a divergence here is silent on one side and fatal on the other.

### N2 — Pending-order write is unchecked; a failure means money taken with no record (High)

`create-order.php:192`:

```php
file_put_contents(PENDING_ORDERS_DIR . '/pending/' . $order['id'] . '.json', json_encode($pendingRecord, JSON_PRETTY_PRINT));
```

The return value is discarded, and `ensure_pending_dirs()` (`lib/config.php:27-32`)
doesn't check `mkdir()` either. The Razorpay order already exists at this point
(`:167`). If the write fails — permissions, full disk, `PENDING_ORDERS_DIR`
mis-resolved after a deploy — the endpoint still returns `200` with a valid
`order_id`, the guest pays, and then:

- `confirm_paid_order()` (`lib/booking.php:17`) finds no pending file → `rename()` fails
- no `done/`, no `failed/` → returns `['status' => 'unknown']` (`:23`)
- `verify-payment.php:41` returns `409 "already being processed"`
- `book-now.js:342-347` shows the "Payment Received, we couldn't auto-confirm" screen
- `reconcile-pending.php:21` globs `pending/*.json` — the file isn't there, so the
  cron backstop never sees it either

Money captured, no reservation, no record anywhere except Razorpay, and no alert.
The one path with no backstop.

**Fix:** check the write; on failure, `bookings_log()` it and return a 503 *before*
handing the guest an `order_id`. Cheaper still: write the pending file **before**
creating the Razorpay order and delete it if order creation fails.

### N3 — Confirmation badge contradicts the failure copy (Medium)

`book-now.html:342` hard-codes the badge:

```html
<div class="direct-badge"><div class="direct-badge-dot"></div>Booking Confirmed</div>
```

The failure path (`book-now.js:343-346`) rewrites `confirmTitle` to "Payment Received"
and the body to "we couldn't auto-confirm the reservation" — but never touches the
badge. A guest whose booking did not confirm reads a green **Booking Confirmed**
badge directly above text saying it wasn't confirmed.

### N4 — A confirmed booking can be reported to the guest as a failure (Medium)

`verify-payment.php:41` returns `409` when `confirm_paid_order()` reports `unknown` —
which includes the legitimate race where `razorpay-webhook.php:43` claimed the order
microseconds earlier and is still mid-`InsertBooking`. `book-now.js:337` treats any
non-2xx as a throw and lands on the "couldn't auto-confirm" screen. The booking is
fine; the guest is told it isn't and is pushed to WhatsApp.

**Fix:** on 409, poll `verify-payment.php` once or twice with a short delay before
falling through to the failure copy.

### N5 — Validation asymmetry between `availability.php` and `create-order.php` (Medium)

`create-order.php` is directly reachable and re-validates less than the search
endpoint that precedes it:

| Rule | `availability.php` | `create-order.php` |
|---|---|---|
| Check-in not in the past | `:23-25` | **absent** |
| Max 30 nights | `:30-32` | **absent** (`:88` computes `$nights` and never uses it) |
| Adults / children bounds | `:33-38` | n/a (server-derived) |
| Max 8 rooms | `:39-41` | `:60-62` ✓ |

A crafted POST can create a Razorpay order for a stay starting in 2020, or for 5,000
nights. eZee re-prices it, so the amount is "real" — but the reservation is garbage
and the order is live.

### N6 — Lenient date parsing accepts impossible dates (Low)

`DateTime::createFromFormat('Y-m-d', ...)` at `availability.php:17-18` and
`create-order.php:83-84` is used without the `!` format prefix (so unspecified time
components default to *now*, not midnight) and without a `getLastErrors()` check.
`2026-02-30` silently becomes `2026-03-02`. Cosmetically confusing; combined with N5
it widens what reaches eZee.

### N7 — Rooms with unknown availability silently become unbookable (Low)

`availability.php:111` coerces a missing availability count to `0`:

```php
'available' => (int)($available ?? 0),
```

`book-now.js:178` then clamps quantity to `Math.min(room.available, qty)` → `0`. The
room renders, shows "0 left at this rate", and the `+` button does nothing with no
explanation. Unknown availability and sold out are indistinguishable to the guest,
and the `+` button is a dead control rather than a disabled one.

### N8 — Price drift between search and payment is charged silently (Low/Medium)

`create-order.php` correctly re-fetches the authoritative price (`:97-106`, the
price-integrity boundary) and never trusts the client — right call. But it never
compares the fresh total to what the guest was shown, so if eZee's rate moved between
Stage 2 and Stage 3, the guest sees the new amount for the first time inside the
Razorpay modal. Nothing is wrong with the charge; the guest just wasn't told.

**Fix:** send the displayed total as an advisory field, and on mismatch return a
`409` the UI renders as "the rate for these dates changed to ₹X — continue?".

---

## 3. New findings — reliability & operations

### N9 — Cancellation initiates no refund and enforces no policy (High)

`cancel-booking.php` calls eZee `CancelBooking` (`:38`) and returns
`"Reservation #X has been cancelled"` (`book-now.js:496`). It never:

- checks the 72-hour window the policy states (`book-now.html:447`)
- calls Razorpay's refund API (no refund code exists anywhere in `api/`)
- surfaces `razorpay_payment_id`, which **is** on file at `lib/booking.php:112` in the
  `done/` record, so the data needed to refund exists and is simply not used

Net effect: a guest cancelling 2 hours before check-in gets an unqualified success
message, keeps 100% of their money pending a manual process nobody is notified about,
and the room is released. The two failure modes — guest not refunded when due, guest
refunded when not due — both land on staff with no queue and no alert.

**Minimum fix:** compute hours-to-check-in from the fetched reservation, state the
refund outcome in the response copy, and `bookings_log()` a refund line carrying
`reservation_no` + `razorpay_payment_id` + amount so there is a work queue.

### N10 — No rate limiting on any endpoint; each anonymous call costs real resources (Medium)

Confirmed absent (existing doc S1 — restating because the cost is concrete here, not
generic). Each unauthenticated `POST /api/create-order.php` creates a **real Razorpay
order** and a file in `PENDING_ORDERS_DIR/pending/`. Nothing expires or cleans up
`pending/` — `reconcile-pending.php:35` explicitly leaves unpaid orders in place
forever (`continue; // still unpaid or abandoned — leave pending`). An unbounded
directory that `reconcile-pending.php:21` globs on every cron tick is a slow-motion
resource problem independent of any attacker.

`cancel-booking.php` has the same exposure for reservation-number guessing. The error
copy is correctly uniform (`:25`, `:30` are byte-identical, so no enumeration oracle) —
only the throughput is unbounded.

### N11 — Repeated payment failures orphan Razorpay orders (Low)

`book-now.js:289-292` re-enables the submit button in the `finally` block, which runs
as soon as `rzp.open()` returns — while the modal is still open. After `ondismiss`
(`:313`) or `payment.failed` (`:318`), a second submit runs the whole handler again
and creates a **new** Razorpay order and a **new** pending file. Three retries leave
two dead orders. Not a double-charge (each order is independent), but it inflates
`pending/` and the Razorpay dashboard.

### N12 — `selftest.php` cannot run in CI and covers none of the flow (Medium)

`api/lib/selftest.php` asserts three things: HMAC verification, `rename()` semantics,
and paise rounding. It covers no endpoint, no eZee parsing, and — critically — not
N1's price-resolution path, which is precisely the kind of silent divergence a test
catches. There is no runner: no PHP in this environment, no CI config, nothing in
`deploy.sh` invoking it despite the file's own header saying "run before every deploy".

The cheapest high-value test is a pure-function one over `extract_room_options()` and
`create-order.php`'s price lookup, fed the `mock.php` fixture — it fails today, which
is the point.

---

## 4. New findings — frontend, accessibility, measurement

### N13 — Dates cannot be entered without a mouse (High, accessibility)

`book-now.html:242,246` declare both date fields `readonly`, delegating entry entirely
to the custom calendar in `book-now.js:358-458`. That calendar:

- builds day cells as bare `<div>`s (`:401-403`) — not focusable, no `role`, no
  `aria-selected`, no `tabindex`
- responds only to `click` (`:407`)
- has no arrow-key navigation, no focus trap, and no `Escape` handler (only
  `mousedown` outside closes it, `:445`)
- is appended to `document.body` (`:441`), so it is not even in the tab order near
  the field that opened it

A keyboard-only or screen-reader user can open the popup (`:455-457`) and then cannot
select a date by any means. The first step of the booking flow is unusable for them.
`readonly` also blocks typing a date directly, which would otherwise be the fallback.

**Lazy fix:** drop `readonly` and keep the custom popup as an enhancement — a typed
`YYYY-MM-DD` already parses correctly via `parseISO` (`:370-374`), and the existing
server validation covers bad input. Native `<input type="date">` would cover this
outright at the cost of the styling the popup exists to provide.

### N14 — Status messages are invisible to screen readers (Medium, accessibility)

Every `.form-msg` (`searchMsg`, `guestMsg`, `cancelMsg`) is written via `textContent`
+ `style.display` (`book-now.js:113-117`) with no `role="alert"` or `aria-live`. Errors
("Email addresses do not match", "Payment failed"), the "Confirming your booking..."
state (`:325`), and the entire confirmation screen announce nothing. Stage transitions
(`:85-89`) also move no focus, so after `showStage('confirm')` focus is still on a
button inside a now-hidden `display:none` stage.

### N15 — Quality-floor gaps in the stylesheet (Medium)

- **No `prefers-reduced-motion` block anywhere** in `styles/global.css` (0 matches).
  The page runs `.reveal` scroll transitions, `.cal-pop` transitions, a progress bar,
  and per-card 3D tilt (`book-now.js:58-70`) with no opt-out.
- **No visible keyboard focus** beyond form fields. The only `:focus` rule in the file
  is `.field input:focus, .field select:focus, .field textarea:focus`. Every
  `.qty-btn`, `.cal-day`, `.widget-back`, `.form-submit`, `.policy-modal-close` and nav
  link has `cursor:none` (the site's custom-cursor design) and **no focus ring** —
  tabbing through the booking widget gives no visual position at all.
- **Hover affordance on a non-interactive element:** `.room-option:hover` lifts and
  gold-borders the whole card, but only the `+`/`−` buttons inside it do anything.

### N16 — The whole booking engine is one uncaught exception from dead (Medium)

`book-now.js:3` destructures at IIFE top level:

```js
const { LOGO_COLORS, PAL, pick, fillById, fillStrip, fillGrid } = window.MOSAIC;
```

If `site.js` fails to load or renames an export, this throws before `init()` and the
booking widget silently never initialises — the search form renders (it is
`.active` in static HTML) but the date fields are `readonly` with no calendar, the
country dropdowns are empty (`:21-30` populates them), and the submit handler is
unbound, so the form does nothing. There is no `<noscript>` and no error boundary; the
guest sees a functional-looking form that cannot be used and no route to WhatsApp
from within the widget.

### N17 — The flow has no browser history and no persistence (Medium)

`showStage()` (`:85-89`) toggles classes only. No `history.pushState`, no URL params,
no `sessionStorage`. Consequences:

- Browser **Back** from Stage 3 leaves the site entirely, losing the whole selection
- A refresh at any stage returns to an empty search form
- Dates aren't in the URL, so a search can't be shared, bookmarked, linked from an ad,
  or recovered
- Returning from the Razorpay flow in any way other than the JS callback = total loss

This is also the largest measurement gap: no stage ever produces a distinct URL.

### N18 — Zero conversion measurement on a revenue flow (Medium)

GA4 (`book-now.html:24-30`) and Clarity (`:33-39`) are loaded, but nothing in
`book-now.js` fires an event. No `view_item_list` on results, no `add_to_cart` on
quantity change, no `begin_checkout`, and — most significantly — **no `purchase`
event on `verifyPayment()` success** (`:338-341`). There is no Google Ads conversion
tag either. The funnel is entirely unmeasured: drop-off between stages, payment
failure rate, and revenue per channel are all currently unknowable. The competitor's
eZee engine fires `add_payment` with `pg_success` on its status page
(`competitor-booking-flow-livefreehostels.md`, GA4 note) — we fire nothing.

### N19 — Copy and formatting details

- `fmtPrice()` (`:351-353`) is `toFixed(2)` with no thousands separator → **₹12500.00**
  where the rest of the site writes ₹2,599. `Intl.NumberFormat('en-IN')` is one line.
- `book-now.js:305` builds the Razorpay description as `"2 room(s) · ..."` — "room(s)"
  is placeholder grammar in the highest-trust moment of the flow. `updateCartBar()`
  (`:215`) already pluralises properly two lines away.
- Stage 2 ("Select Your Rooms") shows a stay **total** with a `/night` figure beneath,
  but never states the dates or the night count — the numbers can't be checked. The
  dates are in scope at `:221-222`.
- Stage 4 shows a reservation number and nothing else: no dates, no room, no amount.
- No progress indicator across the four stages; the guest never knows how many remain.

### N20 — Dead CSS

No HTML or JS references these rules — `#widgetPrice` is an id, and the guest form was
never per-room:

| Rule | Note |
|---|---|
| `.widget-price small` | element is `id="widgetPrice"` with no class (`book-now.html:270`); the live rule is `.price-header small` |
| `.room-option-select` | full button style, incl. `:hover`; superseded by the qty stepper |
| `.guest-room-block`, `.guest-room-block:first-child` | left from a per-room guest-form design |
| `.guest-room-label` | same |

### N21 — Visible ratings contradict the page's own structured data (Low)

`book-now.html:333` renders "★ 4.9/5 on Tripadvisor — 1500+ happy guests" inside the
guest form; the JSON-LD at `:104-107` on the same page declares
`ratingValue: 4.8, ratingCount: 427`. Both numbers also appear site-wide
(`index.html:69-72` vs `:193-194`, `about.html:87-90` vs `:246`). Given the recent
`fix(content): correct fabricated founding claims` pass, this pair is worth settling
against the actual Tripadvisor/Google figures — a mismatch between visible ratings and
`AggregateRating` markup is also a Google structured-data policy violation.

---

## 5. Confirmed from the existing report

Re-verified against current code, no change to the finding:

| ID | Finding | Evidence re-checked |
|---|---|---|
| C1, C2 | Confirmation stage is a dead end — no buttons at all | `book-now.html:341-344` |
| P1 | No retry affordance after payment failure | `book-now.js:318-320` |
| R4 | Quantity silently capped at availability, no message | `book-now.js:178` |
| G1 | Policy text only behind a modal | `book-now.html:331`, `:430-476` |
| S1 (stage) | No occupancy selector — see N22 below | `book-now.html:238-252` |
| B2 | `AddPayment` failure is logged, not retried | `lib/booking.php:105-107` |
| B5 | Raw eZee error text returned to the client | `create-order.php:109`, `:173` |
| B6 | No booking-modification endpoint | absent from `api/` |
| B7 | Cancellation requires reservation number **and** email | `cancel-booking.php:18` |
| S3 (sec) | No CSP / `X-Frame-Options` / security headers | `api/.htaccess` sets cache headers only |

### N22 — Sharpening the occupancy gap (re-rated: High for private rooms)

The existing report rates "no occupancy selector" Medium. For dorm beds that is right.
For private rooms it is not. `create-order.php:63`:

```php
$adults = $totalUnits; // 1 adult per room booked
```

So a couple booking the Double Room is sent to eZee as **one adult**, and
`extradultrate` (`:149`) is computed but always multiplied by zero extra adults. That
means: the second guest's extra-adult rate is never charged, the hotel's arrival list
under-counts, and eZee occupancy reporting is wrong for every private-room booking. A
plain "Guests" number on Stage 3, applied only to room types whose capacity exceeds 1,
closes it without adding a search-stage field.

---

## 6. Unknowns — cannot be settled without a live run

| # | Question | Why it matters | How to settle |
|---|---|---|---|
| U1 | Where does the real eZee `RoomList` put `totalprice_inclusive_all` — nested under `room_rates_info`, at the entry top level, or both? | Decides whether **N1 is already breaking production** or only mock mode. `availability.php`'s comment (`:67-70`) says nested was verified live on 2026-08-10; `create-order.php` assumes nested exclusively | One live `RoomList` call with real credentials, response dumped |
| U2 | Is the account's "No Data found" `RoomList` issue resolved? | If not, the live flow never reaches any of the checkout findings — `docs/ezee-roomlist-issue.md` | Same live call |
| U3 | Does eZee's `Country` field accept a country **name**? `create-order.php:42` passes the dropdown's display name (`book-now.js:28`) straight through to `lib/booking.php:69` | Silent data corruption on every booking if it wants an ISO code | One `InsertBooking` against sandbox, then `FetchSingleBooking` to read back |
| U4 | Is `RAZORPAY_WEBHOOK_SECRET` actually configured and the webhook registered? | `razorpay-webhook.php:24` exits `400` silently when unset — the backstop would look healthy while being inert | Razorpay dashboard, plus one test webhook delivery |
| U5 | Is `reconcile-pending.php` on a cron at all? | It is the last line of defence for N2/N4 | Server crontab |

I have not attempted any of these — say the word if you want to supply credentials and
I'll run U1–U3.

---

## 7. Suggested order

Ordered by (money or trust at risk) ÷ effort, not by severity label.

**First — these break bookings or lose money silently**

1. **N1** — unify price resolution across the two endpoints. Unblocks mock testing too.
2. **N2** — check the pending-file write before returning an `order_id`.
3. **N9** — cancellation: state the refund outcome, log a refund work queue.
4. **N13** — drop `readonly` on the date fields.

**Second — guests are currently told the wrong thing**

5. **N3** — badge must follow the outcome.
6. **N4** — retry once on 409 before showing failure.
7. **C1/C2** — give the confirmation screen a way out, and the booking summary (N19).
8. **P1** — a retry button on payment failure.

**Third — correctness and hardening**

9. **N5, N6** — mirror the date/nights validation into `create-order.php`.
10. **N22** — guest count for private rooms.
11. **N12** — one test over the N1 path, fed `mock.php`, wired into `deploy.sh`.
12. **N10** — rate limit `create-order.php` and `cancel-booking.php`; expire `pending/`.
13. **B5** — stop echoing raw eZee errors.

**Fourth — measurement and polish**

14. **N18** — GA4 ecommerce events; a `purchase` event is one line at `book-now.js:341`.
15. **N17** — stage in the URL; dates in query params.
16. **N14, N15** — `aria-live` on messages, focus rings, `prefers-reduced-motion`.
17. **N7, N8, N11, N16, N19, N20, N21**.

Nothing here needs eZee credentials except U1–U3.
