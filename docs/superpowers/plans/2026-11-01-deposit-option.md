# 50% Deposit Option Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** At checkout the guest chooses to pay in full (today) or a 50% deposit now by Razorpay, with the balance due at check-in; and a guest can look up their booking (status, dates, rooms, paid, due) and cancel from it.

**Architecture:** `create-order.php` prices from a fresh eZee RoomList as today and derives what Razorpay charges from a new `pay_option`. The pending record carries `pay_option`, `pay_now` and `due_at_hotel`; `confirm_paid_order()` posts `pay_now` to eZee `AddPayment`. Refunds already refund the one captured payment, so only the wording changes. The booking page gets a two-way choice and shows "Pay now" and "Due at check-in".

**Tech Stack:** PHP 8.2 (production) endpoints, vanilla JS (`components/book-now.js`), local mock suite `scripts/flow-test/` (run with `sh scripts/flow-test/run.sh`, about 2 minutes, expects 0 failures) and `php api/lib/selftest.php`.

**Spec:** `docs/superpowers/specs/2026-11-01-pay-later-and-deposit-design.md` (owner approved 2026-11-01).

## Global Constraints
- Deposit is **50% of the total**; options are exactly `full` and `deposit`; no pay-at-hotel option.
- The client never sends an amount; `expected_total` stays the full total for the price-changed check.
- Keep the 72-hour rule. Wording: "Free cancellation up to 72 hours before check-in. Inside 72 hours the amount paid is not refunded." plus "Pay in full, or a 50% deposit now with the balance due at check-in."
- Amounts are integer paise; deposit paise = `max(100, ceil(totalPaise / 2))`, capped at `totalPaise`.
- Never read, print or edit `api/secrets.php`. No live eZee or Razorpay calls in this plan; tests use the local mock.
- Do not commit, push or deploy unless the owner asks. Deploy set when approved: `api/create-order.php`, `api/cancel-booking.php`, `api/lookup-booking.php`, `api/lib/razorpay.php`, `api/lib/booking.php`, `book-now.html`, `components/book-now.js`.
- Bump `book-now.js?v=` in `book-now.html` (its only referrer) when the JS changes.

## Review Focus
1. Odd paise: total ₹733.95 gives deposit ₹366.98 and due ₹366.97, which add up to the total.
2. An order saved before this deploy (no `pay_option`/`pay_now`) must still book and post the full total.
3. Tampered `pay_option` (`"Deposit"`, `"half"`, an array, `""`) gives 400 and no Razorpay order.
4. A deposit booking cancelled inside 72 hours makes no Razorpay refund call and tells the guest the deposit is not refundable.
5. A rate change with deposit chosen still returns 409 `price_changed` with the full new total.
6. Lookup with a wrong email and lookup of an unknown reservation return the identical 404 body (no way to tell which reservations exist), and the reply never contains the guest's email or phone.

---

### Task 1: Deposit amount helper

**Files:**
- Modify: `api/lib/razorpay.php` (add function)
- Test: `api/lib/selftest.php`

**Interfaces:**
- Produces: `pay_now_paise(int $totalPaise, string $option): ?int` returns paise to charge now for `'full'` or `'deposit'`, `null` for any other string.

- [ ] **Step 1: Write failing assertions in `api/lib/selftest.php`** (next to the existing paise checks): `pay_now_paise(73395,'full') === 73395`; `pay_now_paise(73395,'deposit') === 36698`; `pay_now_paise(73394,'deposit') === 36697`; `pay_now_paise(150,'deposit') === 100`; `pay_now_paise(100,'deposit') === 100`; `pay_now_paise(73395,'half') === null`; `pay_now_paise(73395,'Deposit') === null`.
- [ ] **Step 2: Run `php api/lib/selftest.php`.** Expected: fails (undefined function).
- [ ] **Step 3: Implement `pay_now_paise` in `api/lib/razorpay.php`**: deposit is `min($totalPaise, max(100, (int)ceil($totalPaise / 2)))`.
- [ ] **Step 4: Run `php api/lib/selftest.php`.** Expected: "All selftest assertions passed."

### Task 2: create-order takes `pay_option`

**Files:**
- Modify: `api/create-order.php` (validate near line 36-47; amount at line 211; order at 231; record 241-255)
- Test: `scripts/flow-test/flow-test.php` (new section after "Pay + verify")

**Interfaces:**
- Consumes: `pay_now_paise` from Task 1.
- Produces: pending record keys `pay_option` (`'full'|'deposit'`), `pay_now` (float rupees, `amount/100`), `due_at_hotel` (float, `round(total - pay_now, 2)`); `amount` is now the paise Razorpay charges; `total` stays the full rupees.

- [ ] **Step 1: Write failing flow-test checks** in a new section "Deposit option": (a) `new_order(['pay_option'=>'deposit'])` returns 200 with `amount === 36698` for the 733.95 room, and `rec()` has `pay_option='deposit'`, `pay_now=366.98`, `due_at_hotel=366.97`, `total=733.95`; (b) omitting `pay_option` gives `amount === 73395` and `pay_option='full'`; (c) for each of `'half'`, `'Deposit'`, `''`, `['deposit']` the reply is 400, and the mock's Razorpay order count does not change (`rzp_orders()`); (d) with `expected_total` 1.00 and `pay_option='deposit'` the reply is 409 with `price_changed` true and `new_total` 733.95.
- [ ] **Step 2: Run `sh scripts/flow-test/run.sh`.** Expected: the new checks fail, all earlier checks still pass.
- [ ] **Step 3: Implement in `api/create-order.php`**: reject a non-string `pay_option` with 400 together with the other scalar checks; default `'full'` when absent; unknown value gives `json_error(400, 'Please choose how to pay.')` before any Razorpay call; `$amountPaise = pay_now_paise($totalPaise, $option)` where `$totalPaise = (int)round($total * 100)`; Razorpay order and `amount` use the charged paise; store the three new record keys. The price-changed block is unchanged.
- [ ] **Step 4: Run `sh scripts/flow-test/run.sh`.** Expected: 0 failures.

### Task 3: AddPayment posts what was paid

**Files:**
- Modify: `api/lib/booking.php` (the `'Payment' => (string)$record['total']` line in the AddPayment request)
- Test: `scripts/flow-test/flow-test.php` (Deposit section)

**Interfaces:**
- Consumes: record key `pay_now` from Task 2.

- [ ] **Step 1: Write failing flow-test checks:** (a) deposit order paid via `confirmed(['pay_option'=>'deposit'])` and `calls('ezee','AddPayment')` last request has `Payment === '366.98'`, record in `done/`; (b) the same through the webhook path (the existing helper used in the webhook section) books once and posts `'366.98'`; (c) a pending record from before the deploy: create a full order, remove `pay_now`, `pay_option` and `due_at_hotel` from its `pending/<order>.json`, pay and verify; `Payment === '733.95'` and the booking is `done`.
- [ ] **Step 2: Run `sh scripts/flow-test/run.sh`.** Expected: (a) and (b) fail, (c) passes.
- [ ] **Step 3: Implement:** `'Payment' => (string)($record['pay_now'] ?? $record['total'])`.
- [ ] **Step 4: Run `sh scripts/flow-test/run.sh`.** Expected: 0 failures.

### Task 4: Refund wording for deposits

**Files:**
- Modify: `api/lib/razorpay.php` (`cancellation_refund_outcome`, add optional 5th parameter), `api/cancel-booking.php` (the call at line 80)
- Test: `api/lib/selftest.php`, `scripts/flow-test/flow-test.php`

**Interfaces:**
- Produces: `cancellation_refund_outcome(?bool $refundDue, ?string $paymentId, string $reservationNo, callable $refund, string $payOption = 'full'): array`; with `'deposit'` and `$refundDue === false` the note is "This is within 72 hours of check-in, so under our cancellation policy your deposit is not refundable."; every other result is unchanged.

- [ ] **Step 1: Write failing tests:** selftest: deposit inside the window returns `action 'none'`, a note containing "deposit", and the injected refund callable is never called; deposit outside the window still returns `'refunded'`. flow-test: a deposit booking 20 days out, cancelled, calls Razorpay refund once with the deposit's payment id; a deposit booking whose `done/` record check-in is rewritten to tomorrow (the existing pattern at the "Inside 72h" check) makes no refund call and the reply `refund_note` contains "deposit".
- [ ] **Step 2: Run both suites.** Expected: the new checks fail.
- [ ] **Step 3: Implement** the parameter and pass `$record['pay_option'] ?? 'full'` from `cancel-booking.php`.
- [ ] **Step 4: Run `php api/lib/selftest.php` and `sh scripts/flow-test/run.sh`.** Expected: 0 failures.

### Task 5: Booking page choice, summary and confirmation

**Files:**
- Modify: `book-now.html` (new radio group before the terms checkbox near line 368; pay button at line 371; script tag at line 675), `components/book-now.js` (`guestForm` submit at line 481, `renderPriceSummary` at 817, `summaryRows` at 658, button text resets at 555 and 692)
- Test: `api/lib/selftest.php` (page-drift check)

**Interfaces:**
- Consumes: reply `amount` (paise) from create-order, request key `pay_option`.
- Produces: radios `input[name="pay_option"]` with values `full` (checked by default) and `deposit`; `payload.pay_option`.

- [ ] **Step 1: Write the failing drift check in `api/lib/selftest.php`:** `book-now.html` contains `name="pay_option"` with values `full` and `deposit` and no other value (same style as the existing guest-list drift check).
- [ ] **Step 2: Run `php api/lib/selftest.php`.** Expected: fails.
- [ ] **Step 3: Implement the markup:** a fieldset "How would you like to pay?" with two labelled radios: "Pay in full" and "Pay 50% now, the rest at check-in". Keep the site's existing form classes.
- [ ] **Step 4: Implement the JS:** add `pay_option` from the checked radio to `payload` (this also changes `payloadKey`, so switching option creates a new order instead of reusing the old one); `renderPriceSummary()` adds "Pay now" and "Due at check-in" rows when deposit is selected, using the same rounding as `pay_now_paise` (`Math.min(t, Math.max(100, Math.ceil(t / 2))) / 100` on paise `t = Math.round(total*100)`); redraw on radio change; pay button text is "Pay & Confirm Booking" for full and "Pay ₹X now & Confirm Booking" for deposit, and the two resets at lines 555 and 692 must restore the text for the current option; `summaryRows()` shows "Paid now" (from `paidAmount()`) and, when `paid < selection.total`, a "Due at check-in" row for the difference; the Razorpay `description` stays as is. Bump `book-now.js?v=` to `20261101a`.
- [ ] **Step 5: Run `php api/lib/selftest.php`.** Expected: passes.
- [ ] **Step 6: Browser check** with the headless Playwright MCP against a local copy served the way `scripts/flow-test/run.sh` does (mock eZee and Razorpay on 127.0.0.1:8900, site on 8899; start them by hand because `run.sh` shuts them down): search two dates, pick a room, choose deposit, confirm the summary shows pay now ₹366.98 and due ₹366.97, the button text matches, switching back to full restores it, and the Razorpay order amount requested from the mock is 36698. Report what was seen; stop the servers after.

### Task 6: Guest booking lookup

**Files:**
- Create: `api/lookup-booking.php`
- Modify: `book-now.html` (the "Manage / cancel a booking" card near line 462), `components/book-now.js` (`initCancelForm` at line 1085), `scripts/flow-test/mock.php` (`FetchSingleBooking` reply must carry `RoomTypeName`, `Start`, `End` per `BookingTran` entry, taken from the InsertBooking it saw), `api/lib/selftest.php` (only if a pure helper is added)
- Test: `scripts/flow-test/flow-test.php` (new section "Booking lookup")

**Interfaces:**
- Consumes: record keys `pay_now`, `total`, `due_at_hotel` and `find_done_record()` from `api/cancel-booking.php` (move `find_done_record` into `api/lib/booking.php` so both endpoints share it); `ezee_fetch_booking()`.
- Produces: `POST /api/lookup-booking.php` body `{reservation_no, email}`; 200 reply `{success:true, reservation_no, status, check_in, check_out, rooms:[string room type names], total?, paid?, due?}` (money keys only when our `done/` record exists); every miss, including a wrong email, is the same 404 body as cancel-booking.php uses ("Reservation not found or email does not match. Please check the details or WhatsApp us."). The reply never contains email, phone or surname.

- [ ] **Step 1: Write failing flow-test checks:** (a) a deposit booking looked up with its email returns 200, `status` is the mock's status, `check_in`/`check_out` match, `rooms` has the room type name, `paid === 366.98`, `due === 366.97`, `total === 733.95`; (b) wrong email and an unknown reservation number give 404 with identical bodies; (c) a reservation that exists only in the mock's eZee list (no `done/` record, like a staff booking) returns 200 with no `paid`/`due`/`total` keys; (d) the raw reply does not contain the booking email or phone; (e) the sixth lookup from one client inside the window returns 429; (f) a full-payment booking shows `paid === total` and `due === 0`.
- [ ] **Step 2: Run `sh scripts/flow-test/run.sh`.** Expected: the new checks fail (endpoint missing), earlier checks pass.
- [ ] **Step 3: Implement `api/lookup-booking.php`** modelled on `api/cancel-booking.php` lines 12-44: same method, rate limits (`lookup-booking` 5 per 600 s, `lookup-all` 60 per 600 s site-wide, per-reservation 5 per 3600 s) and email check; status from `BookingTran[0].CurrentStatus`; dates and room names from every `BookingTran` entry; money from the `done/` record (`due` is `due_at_hotel`, `paid` is `pay_now`; for records without those keys `paid = total`, `due = 0`).
- [ ] **Step 4: Update the mock and re-run `sh scripts/flow-test/run.sh`.** Expected: 0 failures.
- [ ] **Step 5: Implement the page:** the manage card gets a first step "Look up booking" (reservation number and email, same field validation as cancel) that calls the endpoint and shows status, dates, rooms, and "Paid / Due at check-in" when present; the existing "Cancel Booking" button appears under the details (hidden when status is Cancel, Void or Checked Out) and still posts to `api/cancel-booking.php`; errors reuse the card's message area. Bump `book-now.js?v=` again if Task 5 has not already.
- [ ] **Step 6: Browser check** the same way as Task 5: look up a booking made on the local mock, see its details, see a wrong-email message, cancel it from the details view and see the refund note. Report what was seen.

### Task 7: Policy copy and docs

**Files:**
- Modify: `book-now.html` lines 156, 361, 456 and 504 (cancellation copy: the JSON-LD FAQ text, the terms list item, the FAQ answer, the policy modal), `PRODUCT.md` line 23, `docs/agent/OVERVIEW.md` line 13, `docs/agent/CONVENTIONS.md` line 14, `docs/agent/FLOWS/booking.md`, `docs/agent/DATA.md` (new record keys), `docs/agent/API.md` (new `lookup-booking.php` endpoint and limits), `docs/agent/FLOWS/cancellation.md` (lookup step and deposit wording), `docs/agent/STATUS.md`

- [ ] **Step 1: Search the old wording:** `rg -n "charged in full" book-now.html PRODUCT.md docs/agent llms.txt`; every hit is replaced with the Global Constraints wording or confirmed historical.
- [ ] **Step 2: Replace the copy** in the files above; keep the site's tone and the "72 hours" figures unchanged.
- [ ] **Step 3: Update the docs:** `FLOWS/booking.md` chain (step 2 order and step 5 AddPayment posts `pay_now`), `DATA.md` keys `pay_option`, `pay_now`, `due_at_hotel`, STATUS entry with the deploy set from Global Constraints and "not deployed".
- [ ] **Step 4: Run `python3 /Users/naveen/.agents/hooks/project_context_index.py docs/agent`, then `sh scripts/flow-test/run.sh` and `php api/lib/selftest.php`.** Expected: 0 failures, and the final `rg` from Step 1 shows no stale "charged in full" in site copy.

---

## Self-review notes
- Spec coverage: options and 50% (Tasks 1-2), AddPayment (3), refund wording (4), UI and "Pay now / Due" (5), guest lookup (6), policy and docs (7). Non-goals (pay at hotel, changing dates, emails, 48 vs 72) are untouched.
- Names used across tasks: `pay_now_paise`, `pay_option`, `pay_now`, `due_at_hotel`, `cancellation_refund_outcome(..., $payOption)`, `find_done_record()` (moved to `api/lib/booking.php` in Task 6), `api/lookup-booking.php`.
- Task 5's spec of "Pay now / Due" and Task 6's lookup both depend on Task 2's record keys, so run tasks in order 1 to 7.
