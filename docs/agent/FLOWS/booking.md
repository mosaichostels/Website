Read when: changing or debugging search, price, payment or reservation creation (guest books a bed/room).
Verified: 2026-10-29 @ fd29588
Covers: components/book-now.js,book-now.html,api/availability.php,api/create-order.php,api/verify-payment.php,api/razorpay-webhook.php,api/lib/booking.php,api/lib/ezee.php,api/lib/razorpay.php,api/lib/guest.php,api/lib/dates.php

# Flow: guest books and pays

Success = eZee reservation exists AND the Razorpay payment is posted to it (AddPayment). Guest actor: book-now page `/book-now`.

## Chain
```
1 search   book-now.js:300  GET /api/availability.php?check_in&check_out&adults&children&rooms
           -> rate_limit('availability',60/600s) -> validate_stay_dates (Y-m-d, MAX_STAY_NIGHTS=30) -> rooms 1-8
           -> ezee_get RoomList (showtax=1, show_only_available_rooms=1) -> extract_room_options -> {rooms:[{roomtypeunkid,ratetypeunkid,roomrateunkid,name,description,base_adults,per_night,total,base_total,tax_total,available}]}
2 order    book-now.js:534  POST /api/create-order.php {check_in,check_out,rooms[{roomtypeunkid,ratetypeunkid,roomrateunkid,qty,adults}],guest{title,first_name,last_name,gender},first_name,last_name,email,phone,phone_code,nationality,special_request,arrival_time,expected_total}
           -> rate_limit('create-order',10/600s) + ('create-order-all',60/600s global)
           -> validate strings, email, phone 8-15 digits, guest_values_error/guest_text_error (api/lib/guest.php)
           -> RE-FETCH eZee RoomList, find room by roomrateunkid, total = ezee_room_total() (client never sends a price)
           -> expected_total differs from fresh total -> HTTP 409 {price_changed,old_total,new_total}; widget re-asks the guest
           -> razorpay_create_order(amount paise) -> write pending/<order_id>.json (fail 503 if unwritable) -> {order_id,amount,currency:'INR',key_id}
3 pay      book-now.js:582  Razorpay Checkout (browser popup, CSP allows checkout.razorpay.com)
4 confirm  A book-now.js:732 POST /api/verify-payment.php {razorpay_order_id,razorpay_payment_id,razorpay_signature}
             -> HMAC check (razorpay_verify_signature) -> confirm_paid_order()
           B Razorpay -> POST /api/razorpay-webhook.php (event payment.captured, header X-Razorpay-Signature) -> confirm_paid_order($order,$pay,$payment)
           C cron php api/reconcile-pending.php -> FLOWS/payment-recovery.md
5 book     confirm_paid_order (api/lib/booking.php:42): atomic rename pending|abandoned -> processing/<order>@<unixtime>.json
           -> ezee InsertBooking (POSTed form body, one Room_N per physical room, per-night comma rate lists) -> record.reservation_no saved
           -> ezee AddPayment (skipped when `EZEE_PAYMENT_ID`/`EZEE_CURRENCY_ID` are empty; else once, retried once) -> done/<order>.json -> {status:'done',reservation_no,sub_reservation_no}
6 show     verify-payment replies {success,reservation_no,sub_reservation_no}; widget shows the confirmation screen
```
- `verify-payment` is NEVER rate limited: one guest legitimately calls it up to 6 times (`VERIFY_RETRY_DELAYS=[1000,2000,3000,5000,5000]`, `book-now.js:708`, ~16 s total, then "Payment Received - confirmation pending").
- Search always sends adults=1 (`book-now.js:292`). Each cart line carries `adults` (stepper capped at the room's `base_adults` from availability, default 1); create-order re-checks it against eZee `base_adult_occupancy` and answers 409 above it, because the extra-adult rate is not added to the Razorpay amount. Children are always 0.
- Amounts are integer paise: `(int)round($total*100)`.

## Failure paths
| Where | Result | Guest sees |
|---|---|---|
| availability: bad dates/adults/rooms | 400 | message |
| availability or create-order: eZee rate limited | 429 | "booking system is busy" |
| availability/create-order: eZee error | 502, real text only in `bookings.log` | fixed sentence + WhatsApp |
| create-order: room gone | 409 "no longer available" | search again |
| create-order: qty above eZee count / adults above base occupancy | 409 "Only N left" / "covers up to N guests" | adjust |
| create-order: no usable price, or rates do not match the night count | 502, detail in `bookings.log` | retry or WhatsApp |
| create-order: price moved | 409 `price_changed` | old vs new total, must confirm |
| create-order: secrets empty | 503 | "book via WhatsApp" |
| create-order: pending file unwritable | 503, Razorpay order unused | retry or WhatsApp |
| verify: bad signature | 400 | error |
| confirm: `processing/` claim lost | other path won; result `done`/`failed`/`unknown` | verify 409 "already being processed" |
| confirm: payment amount/currency/status != order | `mismatch` + alert, no booking | (webhook/cron only) |
| InsertBooking coded rejection (`_permanent`) | parked in `failed/` at once, alert `ambiguous=no` | 502 "confirmation pending" |
| InsertBooking plain `Errors.ErrorMessage` | retry (max 3, `CONFIRM_RETRY_GAP_SECONDS=120` apart) then `failed/` | pending message |
| InsertBooking transport error or no ReservationNo | ambiguous: parked, NEVER retried, alert | pending message |
| unreadable order record at claim time | parked in `failed/`, alert "PAID but order record unreadable", eZee not called | pending message |
| AddPayment fails twice | alert "ACTION REQUIRED AddPayment failed twice"; reservation stays, order -> `done/` | success (guest not told) |
| `done/` write fails | claim file kept, alert | success |

## Do not
- Add price logic outside `ezee_room_total()` (`api/lib/ezee.php:28`). Do not trust any client number.
- Rate limit `verify-payment.php`. Do not make the webhook return 5xx for `failed` (Razorpay disables the endpoint after ~24 h of 5xx).
- Change JSON keys: `book-now.js` and `selftest.php`/`scripts/flow-test` read them.
