# Competitor booking flow — Live Free Hostels (Varanasi)

Explored 2026-08-08 via Orca browser automation, for reference while building
`/book-now.html`'s custom eZee + Razorpay engine (see
`~/.claude/plans/dreamy-dazzling-kazoo.md`). Live Free runs on **eZee's own
hosted booking-engine widget** (not a custom build) — same PMS platform we're
integrating against, different product (their site: "Powered by Yanolja Cloud
Solution" = eZee's parent).

## Entry point

Main site (`livefreehostels.com`) has a search widget: Destination dropdown
(Varanasi/Rishikesh/Dehradun), Check In / Check Out date fields, "BOOK NOW"
button. That button is a plain `target="_blank"` link to eZee's hosted
widget — **not** an API call from their own site. Confirmed via:

```
document.querySelector('form').action
→ https://book.livefreehostels.com/booking/book-rooms-livefreehostelvaranasi
```

`book.livefreehostels.com` is the eZee booking-engine subdomain for this
property.

## Screen 1 — Room list (on `book.livefreehostels.com`)

Search auto-runs for the dates passed in the query string. Per room type:
name, rate-plan/package name (e.g. "Special Discount - 10-Bed Mixed Dorm"),
capacity, price/night, live availability count ("3 Rooms Left" / "Not
Available"), Room Info / Enquire / Availability Calendar links. "Add Room"
button adds it to a running booking-summary sidebar (dates, nights, per-room
price, total). "Book" button continues.

Confirms eZee's `RoomList`-equivalent data (availability + pricing) renders
correctly for a live, correctly-configured property — useful baseline while
debugging our own account's "No Data found" issue (separate account/plan,
not a platform-wide problem).

## Screen 2 — Guest info + billing (same page, no separate step)

One page combining:
- **Booking summary**: hotel address/contact, dates, room + rate + package,
  Room Charges / Taxes & Fees / Adjustment / Total / **Total Payable Now** /
  amount due at check-in.
- **Guest form**: title, first/last name, gender, special requests, mobile
  (country-code dropdown + number), email + confirm email, country dropdown,
  estimated arrival time dropdown.
- "Online Payment" note: *"You will be redirected to our secure online
  payment site."* — payment is a redirect/embed, not built into this page.
- Hotel Policy + Cancellation Policy text, T&C checkbox, "Book Now" button.

## Screen 3 — Payment (Razorpay Checkout)

"Book Now" submits the guest form, which redirects into eZee's own
Razorpay bridge:

```
https://book.livefreehostels.com/commonpg/ezeepayrazorpay/request.php
```

This is eZee's built-in Razorpay integration endpoint pattern — confirms
eZee has an off-the-shelf Razorpay bridge (we're not using it, building our
own `create-order.php` / `verify-payment.php` instead, but the URL shape is
a useful reference if we ever need to cross-check behavior).

Loads standard **Razorpay Checkout**, running in **Test Mode** on their
live site at the time of this exploration. Payment options offered: UPI,
Cards, EMI, Netbanking, Wallet.

### Card automation still blocked — completed manually instead

As previously found, Razorpay's card-number field rejects all forms of
scripted input (`fill`, `type`, per-digit `keypress`) — deliberate PCI-DSS
anti-automation on Razorpay's iframe. On 2026-08-08, the user drove two full
manual passes (one successful payment, one failed payment) while Claude
observed via `orca snapshot`/`screenshot`/`eval` at each step, no scripted
field input used. Findings below are from those two real runs.

### Network trace on the Razorpay payment page

`checkout.razorpay.com/v1/checkout.js` loads client-side as normal, then:

```
api.razorpay.com/v1/checkout/public?key_id=...&rzp_device_id=...&session_id=...   (iframe)
cdn.razorpay.com/.../razorpay-risk-detection/bundle.js
lumberjack.razorpay.com/v1/track                                                   (analytics)
```

`key_id` observed: `rzp_live_oauth_T2ctwBqANQO22D` — a **live** OAuth-style
key (not a `rzp_test_...` key), yet the Checkout UI showed a "Test Mode"
banner. This means eZee's Razorpay integration is set up via **Razorpay
Partner/OAuth connect** (the property's own Razorpay account linked to
eZee), and "Test Mode" here is the merchant account's own toggle, not a
separate test key. Our own setup (raw `key_id`/`key_secret` pair,
`RAZORPAY_KEY_ID` returned to the client) is the simpler, standard
integration — still the right call for a single-property custom build.

The actual Razorpay **order-creation** call happens server-side before this
page ever loads (not visible in browser network) — same price-integrity
boundary as our own `create-order.php`.

### Screen 4 — Payment result (full-page redirect, not a JS callback)

This is the one real architectural difference from our build. eZee does
**not** rely on Razorpay's client-side `handler` callback. Instead, on both
success and failure, Razorpay redirects the top-level page (not just an
iframe) to eZee's own PHP:

```
book.livefreehostels.com/booking/bookingstatus.php?bst=<long opaque signed token>[&ErrorTxt=...]
```

Same page template renders both outcomes, only the banner color/copy and
`bst`/`ErrorTxt` differ:

- **Success**: green banner, "Thank You! YOUR BOOKING HAS BEEN CONFIRMED."
  **No reservation/booking number shown on-page at all** — text says "use
  the Booking ID provided in your email." Buttons: Make another booking /
  Return to Website.
- **Failure** (triggered here by closing the Razorpay checkout modal via the
  X button): red/pink banner, "SORRY! YOUR BOOKING HAS FAILED. Error
  Occurred: Guest or Payer has closed the window or Cancel the payment
  process." Same two buttons, no diagnostic detail beyond that one line.
- Before reaching the failure redirect, a **card decline did not close
  checkout** — Razorpay auto-fell back to a "Retry payment of ₹567 with"
  screen (UPI QR + other methods, countdown timer), staying open until the
  checkout was explicitly dismissed. Only that explicit dismissal produced
  the `ErrorTxt=Guest or Payer has closed the window...` redirect.
- "Return to Website" does not land on any receipt/summary page — it just
  drops back to a fresh room-search page (dates reset), on both success and
  failure.

GA4 (`google-analytics.com/g/collect`) fires an `add_payment` event on the
status page with `pg_success=1`, `pg_amount=...`, `hotelCode` — pure
analytics, not part of the booking contract.

## Takeaways for our build

1. Their flow is 3 screens: Search → Room list+summary → Guest details+pay
   (redirect into Razorpay). Our planned Search → Results → Guest
   details+pay (Razorpay modal, not full-page redirect) is a reasonable,
   slightly more modern variant of the same shape.
2. If we ever want to browser-test full Razorpay payment completion
   end-to-end (our own or a competitor's), don't rely on scripted field
   fill — Razorpay actively resists it. A real manual pass (as done here) is
   the only reliable way; Razorpay's server-side test webhooks/API would be
   the alternative to driving the Checkout UI at all.
3. Confirms `RoomList`-equivalent data works fine on a correctly configured
   eZee property — supports the theory that our own "No Data found" issue is
   account/plan-scoped (BE-API Lite permissions or inventory-channel gap),
   not a platform-wide eZee fault.
4. **Their success/failure handling is a real server-side page redirect
   (Razorpay `callback_url`), ours is a client-side JS `handler` callback
   that never navigates away.** Redirect survives a JS crash/tab-interrupt
   better than a pure client callback does. Doesn't invalidate our approach,
   but reinforces that the Phase 6 webhook backstop (flagged as deferred in
   the plan) is a real gap worth closing before going live, not a
   theoretical one — even the simpler competitor flow doesn't lean on
   client JS alone for the final confirmation step.
5. **Guest form has a "Confirm Email" field** (retype-to-verify) — ours
   (`book-now.js`) only has a single email input. Worth adding: cheap typo
   guard on the one field a guest can't self-correct after paying.
6. **Guest name/gender is captured per-room**, not once per booking — not
   relevant to us directly since we cap bookings at 1 room, but explains why
   their form is longer than ours.
7. Real hotel/cancellation policy text is visible on their billing page
   (their policy, not ours, but gives the template shape to drop Mosaic's
   actual policy into once the user supplies it): check-in/out times,
   prepayment-at-property-mandatory line, accepted ID types, group-size cap,
   under-5s-free, non-smoking, 48hr free-cancellation window, early-check-in
   caveat. Their T&C checkbox copy ("I acknowledge and accept the Terms of
   Cancellation Policy & Hotel Policy") is functionally identical to ours —
   confirms our placeholder checkbox is the right shape, just needs real
   policy text swapped in.
8. Their post-payment success screen shows **no reservation number inline**
   (email-only). Our flow (`components/book-now.js` `verifyPayment()`) shows
   `Reservation #{id}` immediately on confirmation — keep this, it's better
   UX than the competitor's.
