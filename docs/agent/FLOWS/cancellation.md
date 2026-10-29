Read when: changing or debugging guest cancellation or refunds.
Verified: 2026-10-29 @ fd29588
Covers: api/cancel-booking.php,api/lib/razorpay.php,api/lib/dates.php,components/book-now.js

# Flow: guest cancels a booking

Actor: guest with reservation number + email (cancel form on `/book-now`, `book-now.js:1085 initCancelForm`, POST at `:1102`).

## Chain
```
POST /api/cancel-booking.php {reservation_no, email}
 -> rate_limit('cancel-booking',5/600s per IP) + ('cancel-all',60/600s) + ('cancel-reservation',5/3600s keyed by reservation number)
 -> ezee_fetch_booking (FetchSingleBooking, pms_connectivity.php, HotelCode+AuthCode)
 -> reservation found AND Email on file == email (case-insensitive) else 404 (same text for both: no oracle)
 -> BookingTran[0].CurrentStatus in Cancel|Void|Checked Out -> 409 "already <status>"
 -> write refunds/<reservation_no>.json {status:'cancelling'}   (recoverable trace)
 -> ezee_get CancelBooking {ResNo}   fail -> delete trace, 502 "WhatsApp us"
 -> refund_due_for_checkin(record.check_in) (>= FREE_CANCELLATION_HOURS=72 h before check-in, IST)
 -> cancellation_refund_outcome(...) -> razorpay_refund_payment (idempotency key, full refund)
 -> refunds/<reservation_no>.json = refunded | manual ; booking_alert mail either way
 -> {success:true, reservation_no, refund_note}
```
- Cancelling is never blocked by the policy: inside 72 h the room is freed, no refund.
- `record` (payment id, total, check_in) is read from `done/<order>.json` by reservation number.
- Eligible refund that Razorpay does not confirm -> `status:'manual'` + alert "REFUND to review after cancellation".
- Undetermined check-in date (`null`) -> no automatic refund, manual.

## Known gap
Owner-confirmed 2026-10-29: never tested end to end. End to end NOT verified live: eZee FetchSingleBooking returns "No Reservation Found" for a reservation without a posted payment (60 s tested), so a real test needs AddPayment first (leaves a payment line in eZee). `scripts/flow-test` covers it against the mock only.

## Do not
Return different errors for "not found" and "email mismatch". Skip the `refunds/` trace before CancelBooking.
