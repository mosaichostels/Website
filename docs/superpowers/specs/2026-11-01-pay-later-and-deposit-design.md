# 50% deposit option at checkout: design

Status: DRAFT, waiting for the owner's approval. Nothing is built.
Date: 2026-11-01. Revised the same day: "pay at hotel" was considered and removed by the owner.

## Intent
At the payment step the guest picks one of two options:
1. **Pay in full** (today's behaviour, unchanged).
2. **Pay a 50% deposit** now through Razorpay; the rest is collected at the hotel.

Why: fewer abandoned checkouts from guests who will not prepay a whole stay, while money stays at risk for every booking (there is always a payment, so no free bed holds).

## Goals
- The guest sees, before paying, exactly what is charged now and what is due at check-in.
- The reservation in eZee is Confirmed with the room assigned, and eZee's folio shows the right paid and due amounts (the deposit is posted with `AddPayment`).
- All amounts are computed on the server from a fresh eZee RoomList, never from the browser.
- The existing full-payment path, refund, webhook, recovery cron and alert behaviour keep working.

## Added at the owner's request (same day): guest booking lookup
Extends the existing "Manage / cancel a booking" card on the book-now page. The guest enters reservation number and email (the same two keys the cancel form already needs; email alone is NOT enough, so nobody can list a guest's bookings by guessing an email). The page then shows status, dates, room names, and, for bookings made on this site, "Paid" and "Due at check-in", with the existing cancel button below. Read-only apart from cancel. My calls: new endpoint `api/lookup-booking.php` with the same rate limits and the same generic "not found or email does not match" reply as cancel-booking.php; room, dates and status come from eZee (`FetchSingleBooking`), money from our own `done/` record (eZee's lookup does not return paid and due); no email, phone or full name is returned.

## Non-goals
- Pay at hotel (removed by the owner), changing booking dates from the page, paying the balance online, reminder or confirmation emails, auto-cancelling no-shows, changing booking dates, changing the 72-hour rule or the 48 versus 72 hour mismatch with eZee.

## Anti-goals
- Never undercharge or accept a client-supplied amount.
- Never lose a paid deposit without a reservation (same safeguards as today).

## Decided by the owner
- Two options, guest chooses: full or deposit.
- Deposit is a fixed **50% of the total**.
- No pay-at-hotel option.

## Verified live on eZee (2026-11-01, fake ZZTEST reservations, all cancelled)
- `AddPayment` with a partial amount works: Rs 1 of 4200 gave due 4199, deposit 1.
- `InsertBooking` creates a Confirmed reservation with the full amount due; `ProcessBooking` `ConfirmBooking` assigns the room (already in the booking flow as of today).
- `CancelBooking` works with a payment on the reservation.

## How it works
**Order data.** The order record gains `pay_option` (full or deposit), `total`, `pay_now` and `due_at_hotel`. `amount` (paise) stays "what Razorpay charges", so the webhook and cron amount checks need no change.

**create-order.php.** Accepts `pay_option` (default full, anything else is a 400). Recomputes the total as today. `pay_now` is the total for full, and `round(total * 0.5, 2)` (at least Rs 1) for deposit; the Razorpay order is for `pay_now`. The price-changed check still compares the full total.

**booking.php.** `AddPayment` posts `pay_now` instead of `total`. Everything else (claim, InsertBooking, ConfirmBooking, retries, alerts) is unchanged. `Booking_Payment_Mode` stays "Online Payment (Razorpay)".

**cancel-booking.php and razorpay.php.** The existing full refund of the one captured payment is the deposit when the option was deposit. The "not refundable" note says "deposit" in that case.

**book-now page.** A two-way choice in the guest step; the price summary shows "Pay now" and "Due at check-in"; the pay button text follows the choice; the confirmation screen shows paid and due. Policy modal, FAQ and JSON-LD copy are updated.

## Policy: my calls, for the owner to confirm
- Keep the 72-hour rule. A deposit is refunded in full if the guest cancels 72 hours or more before check-in; inside 72 hours the deposit is not refunded.
- The balance (the other 50%) is collected at check-in. If a guest cancels late or does not turn up, only the deposit is kept; the balance cannot be charged.
- `PRODUCT.md` currently says "charged in full inside 72 hours". That sentence becomes untrue for deposit bookings and must be reworded.

## Constraints
- Server timezone, rate-limit and file-claim rules in `docs/agent/GOTCHAS.md` apply.
- No secrets in the repo. Live eZee tests only on fake ZZTEST reservations, cancelled at once.
- Tests first: extend `scripts/flow-test/` (mock eZee and Razorpay) for both options and the failure paths, and keep all existing checks green.

## Left to the builder
- Exact UI layout and wording, within the site's existing styles.
- Whether `pay_now` is stored in rupees or paise (it must match how `total` and `amount` are stored today).

## Risks
- A deposit guest's balance relies on the front desk collecting it; eZee shows the due amount.
- The Rs 1 test payment 664 stays on cancelled test reservation 1831 in eZee's records.
