# Book-Now Flow: Gaps and Issues Report

**Audit Date:** 2026-09-13
**Audited By:** Cline AI Coding Agent
**Scope:** End-to-end booking flow (`/book-now.html` → widget → APIs → eZee PMS)
**Status:** Complete evidence-based audit

---

## Table of Contents
1. [Overview](#overview)
2. [Change Log](#change-log)
3. [Flow Overview](#flow-overview)
4. [Gaps by Stage](#gaps-by-stage)
5. [Backend & Architecture Issues](#backend--architecture-issues)
6. [Security & Reliability Gaps](#security--reliability-gaps)
7. [Missing Email Infrastructure](#missing-email-infrastructure)
8. [Priority Matrix](#priority-matrix)
9. [Evidence Index](#evidence-index)

---

## Overview

This document reports all gaps, missing features, and issues discovered during a thorough, line-by-line audit of the Mosaic Hostel book-now flow. The audit examined:

- Frontend: `book-now.html`, `components/book-now.js`
- API endpoints: `availability.php`, `create-order.php`, `verify-payment.php`, `razorpay-webhook.php`, `reconcile-pending.php`, `cancel-booking.php`
- Backend libraries: `lib/booking.php`, `lib/ezee.php`, `lib/razorpay.php`, `lib/config.php`
- Test/sanity: `lib/selftest.php`

The flow consists of **4 frontend stages** and a **5-step backend chain**:

```
Stage 1: Search (dates)
    ↓
Stage 2: Results (room selection + cart)
    ↓
Stage 3: Guest Details (form + payment)
    ↓
Stage 4: Confirmation (success/failure)
          ↓
Backend: availability → create-order → verify-payment → booking (InsertBooking + AddPayment) → eZee
```

---

## Change Log

| Date | Author | Description |
|------|--------|-------------|
| 2026-09-13 | Cline AI | Initial audit and report generation |

---

## Flow Overview

### Frontend Stages (book-now.html + book-now.js)

1. **Stage 1: Search** (`#stageSearch`)
   - Check-in / check-out date inputs
   - "Check Availability" button
   - Form validation (dates required, check-out > check-in)

2. **Stage 2: Results** (`#stageResults`)
   - Room options grid (name, description, price, availability)
   - Quantity selector per room (0–available)
   - Running cart bar with summary
   - "Continue" button → Stage 3

3. **Stage 3: Guest Details** (`#stageGuest`)
   - Title, first name, last name, gender
   - Email + **Confirm Email** (retype-to-verify)
   - Phone with country-code dropdown
   - Nationality dropdown
   - Special requests textarea
   - Estimated arrival time dropdown
   - Price summary (room rate + tax)
   - Terms & conditions checkbox (links to policy modal)
   - "Pay & Confirm Booking" button → Razorpay Checkout

4. **Stage 4: Confirmation** (`#stageConfirm`)
   - Success: Shows reservation number + "confirmation sent to email" (false claim)
   - Failure: Shows "Payment Received" with WhatsApp fallback
   - Both states: No action buttons

### Backend Chain (api/ folder)

1. `availability.php` → Proxies eZee RoomList, validates input
2. `create-order.php` → Creates Razorpay order (server-side price re-validation)
3. Browser → Razorpay Checkout → `verify-payment.php` OR webhook → `razorpay-webhook.php`
4. `verify-payment.php` / `razorpay-webhook.php` → `confirm_paid_order()` (booking.php)
5. `booking.php` → Calls eZee `InsertBooking` → (if successful) → eZee `AddPayment`
6. `reconcile-pending.php` → Cron sweep for stuck orders (CLI-only)
7. `cancel-booking.php` → Email-verified cancellation via eZee `CancelBooking`

---
## Gaps by Stage

### Stage 1: Search

| ID | Gap | Severity | Evidence |
|----|-----|----------|----------|
| S1 | No occupancy selector (adults/children/rooms) | Medium | `book-now.html` lines 238-252: form has only `checkIn` and `checkOut` inputs |
| S2 | Default occupancy hardcoded to 1 adult/0 children/1 room | Low | `availability.php` lines 12-14 |
| S3 | No flexible date range / multi-date options | Low | — |
| S4 | "> 8 rooms" note only on results page (not search) | Low | `book-now.html` line 249 inside `stageResults`, not `stageSearch` |

### Stage 2: Results (Room Selection)

| ID | Gap | Severity | Evidence |
|----|-----|----------|----------|
| R1 | No rate-plan/package name displayed (competitor shows "Special Discount - 10-Bed Mixed Dorm") | Low | `availability.php` lines 105-106: only `Roomtype_Name` and `Room_Description` used |
| R2 | No "Room Info" / "Enquire" / "Availability Calendar" links per room | Low | — |
| R3 | No visual distinction of room type categories (dorms vs. private rooms) | Low | `book-now.js` `renderRoomOptions()` |
| R4 | Cart quantity silently capped at availability (no error when trying to add more than available) | Medium | `book-now.js` line 178: `qty = Math.max(0, Math.min(room.available, qty))` |
| R5 | No explicit "Not Available" state rendering (rooms with 0 availability still show qty selector) | Low | — |

### Stage 3: Guest Details + Payment

| ID | Gap | Severity | Evidence |
|----|-----|----------|----------|
| G1 | Policy text hidden behind modal (competitor displays policy inline on billing page) | Medium | `book-now.html` lines 430-476 (modal), line 331 (checkbox label) |
| G2 | No explicit "prepayment at property mandatory" notice (competitor has this) | Low | `book-now.html` line 331: "Prepayment secures this reservation" (insufficient) |
| G3 | No "You will be redirected to our secure online payment site." notice | Low | — |
| G4 | No detailed fare breakdown per room (competitor shows Room Charges / Taxes & Fees / Adjustment / Total / Total Payable Now / amount due at check-in) | Low | `book-now.js` `renderPriceSummary()` |
| G5 | No group-size cap or under-5s-free policy mentioned (competitor includes these) | Low | `book-now.html` policy modal |
| G6 | No "Make another booking" / "Return to Website" buttons on guest page | Medium | — |
| G7 | No booking summary displayed alongside guest form (competitor shows hotel address, dates, room, rate, package, charges) | Low | — |

### Stage 4: Payment (Razorpay)

| ID | Gap | Severity | Evidence |
|----|-----|----------|----------|
| P1 | No retry mechanism after payment failure (user must manually restart form) | High | `book-now.js` lines 318-320: `payment.failed` handler only shows error |
| P2 | No card-decline fallback (competitor observed Razorpay auto-fallback to retry screen) | Medium | — |
| P3 | No Razorpay test-mode warning banner | Low | — |
| P4 | No "Processing payment..." state between form submit and Razorpay opening | Low | `book-now.js` `openRazorpay()` |
| P5 | No Razorpay order ID shown to user on failure/success | Low | — |

### Stage 5: Confirmation

| ID | Gap | Severity | Evidence |
|----|-----|----------|----------|
| C1 | No "Make another booking" button | High | `book-now.html` lines 341-345: no buttons in `stageConfirm` |
| C2 | No "Return to Website" / "Return to home" button | High | — |
| C3 | **FALSE CLAIM**: UI states "A confirmation has been sent to your email" but **zero email-sending code exists** | Critical | Entire codebase searched: no `mail()`, `PHPMailer`, `sendmail`, SMTP, or external email API |
| C4 | No reservation management link (view/modify/cancel) | Medium | — |
| C5 | No booking details summary on confirmation (competitor shows dates, rooms, total) | Low | `book-now.js` lines 338-340 |

---
## Backend & Architecture Issues

| ID | Gap | Severity | Evidence |
|----|-----|----------|----------|
| B1 | **NO EMAIL INFRASTRUCTURE**: System never sends booking confirmations, cancellation notices, or any guest emails | Critical | Search entire `api/` and `components/` folders: zero email-sending code |
| B2 | No AddPayment retry logic (if eZee payment recording fails, booking still marked done → risk of double-charging) | High | `booking.php` lines 91-107: errors logged but not fatal |
| B3 | No price upper bound validation in create-order.php (only validates price > 0) | Medium | `create-order.php` line 132 |
| B4 | No past-date validation (guest could book for 2020-01-01) | Medium | `create-order.php` lines 83-87: validates format and check_out > check_in only |
| B5 | Raw eZee error responses echoed to client (potential credential leakage) | Medium | `create-order.php` lines 108-109, 173 |
| B6 | No booking modification endpoint (date/room/guest changes) | High | No `modify-booking.php` or similar |
| B7 | No booking lookup by email only (cancel requires both reservation number AND email) | Medium | `cancel-booking.php` requires both fields |
| B8 | No refund processing code (policy says refunds take 7-10 days but no implementation) | Medium | `cancel-booking.php` only calls `CancelBooking`, no refund logic |
| B9 | No monitoring/alerting for stuck orders (reconcile-pending.php runs but no alerting) | Low | — |
| B10 | No integration tests for full booking flow (selftest.php only tests crypto/rename/paise math) | Medium | Only `lib/selftest.php` exists |
| B11 | eZee `FetchSingleBooking` exists but unused for booking display/modification | Medium | `ezee.php` lines 37-47 |

---

## Security & Reliability Gaps

*(Additional to issues noted in .claude/agents/security-reviewer.md)*

| ID | Gap | Severity | Evidence |
|----|-----|----------|----------|
| S1 | No rate limiting on API endpoints (brute-force attack surface) | Medium | — |
| S2 | No input sanitization beyond basic validation (e.g., XSS in special_request) | Low | — |
| S3 | No CSP headers, X-Frame-Options, or other security headers | Low | — |
| S4 | No booking confirmation SMS/WhatsApp fallback (email-only claim is false) | High | Critical dependency on non-existent email |
| S5 | No audit trail for price validation failures or payment mismatches | Low | — |
| S6 | No booking expiration/cleanup for pending orders (relies on 3-min cutoff in reconcile) | Low | `reconcile-pending.php` line 19 |

---

## Missing Email Infrastructure

### CRITICAL FINDING

**The system sends NO emails at all.** Despite the UI stating:

> "A confirmation has been sent to your email."
> (`components/book-now.js` line 339)

...there is **zero email-sending code** anywhere in the codebase.

**Places checked:**
- All `api/*.php` endpoints
- All `api/lib/*.php` files
- `components/book-now.js`
- `book-now.html`
- `components/*` (navbar, footer, etc.)

**Missing:**
- PHP `mail()` function
- PHPMailer / Symfony Mailer
- SMTP configuration
- External email API (SendGrid, Mailgun, etc.)
- Email templates
- Email queueing system
- Email failure handling/retry

**Impact:**
- Guests never receive booking confirmations
- No way to recover lost reservation numbers
- No cancellation notices
- No pre-arrival emails
- No post-stay feedback requests
- Complete breakdown in guest communication

**Required Fix:**
Implement email sending via:
1. Transactional email service (SendGrid, Mailgun, Amazon SES, etc.) OR
2. Configured SMTP (Gmail, Outlook, etc.) with app-specific password
3. Email templates for:
   - Booking confirmation
   - Cancellation confirmation
   - Payment failed/retry
   - Pre-arrival checklist
   - Post-stay feedback
4. Add email dispatch in:
   - `booking.php` after successful InsertBooking
   - `cancel-booking.php` after successful cancellation
   - `verify-payment.php` on payment failure (optional)
5. Add email configuration to `secrets.php`
6. Add email sending tests to `selftest.php`

---
## Priority Matrix

| Priority | ID(s) | Description | Effort Estimate |
|----------|-------|-------------|-----------------|
| **P0** | B1, C3 | **NO EMAIL INFRASTRUCTURE** (critical false claim) | 4-8 hours |
| **P0** | P1 | No retry button after payment failure | 2-4 hours |
| **P0** | C1, C2 | No action buttons on confirmation screen | 1-2 hours |
| **P1** | B6 | No booking modification endpoint | 8-16 hours |
| **P1** | B2 | No AddPayment retry logic (double-charge risk) | 4-6 hours |
| **P1** | B7 | No booking lookup by email only | 2-4 hours |
| **P1** | G1 | Policy text hidden behind modal (poor UX) | 2-4 hours |
| **P2** | S1-S6 | Security hardening (rate limiting, headers, etc.) | 6-12 hours |
| **P2** | B3, B4, B5 | Input validation & sanitization improvements | 4-6 hours |
| **P2** | R1, R2, R3, R4, R5 | Room selection UX improvements | 4-8 hours |
| **P2** | S2-S4 | Search stage improvements | 2-4 hours |
| **P3** | B8-B10, B11 | Refund processing, testing, observability | 6-12 hours |
| **P3** | G2-G7 | Policy details, fine-print UX | 2-4 hours |

---

## Evidence Index

| File Path | Lines | Description |
|-----------|-------|-------------|
| `/Users/naveen/Projects/hostel/Website/book-now.html` | 238-252 | Search form (no occupancy fields) |
| `/Users/naveen/Projects/hostel/Website/book-now.html` | 249 | "> 8 rooms" note (in wrong stage) |
| `/Users/naveen/Projects/hostel/Website/book-now.html` | 272-336 | Guest form fields |
| `/Users/naveen/Projects/hostel/Website/book-now.html` | 331 | Terms & conditions checkbox |
| `/Users/naveen/Projects/hostel/Website/book-now.html` | 341-345 | Confirmation stage (no buttons) |
| `/Users/naveen/Projects/hostel/Website/components/book-now.js` | 73-513 | Full widget logic |
| `/Users/naveen/Projects/hostel/Website/components/book-now.js` | 178 | Cart qty silent cap |
| `/Users/naveen/Projects/hostel/Website/components/book-now.js` | 318-320 | Payment failed handler |
| `/Users/naveen/Projects/hostel/Website/components/book-now.js` | 323-324 | Ondismiss handler |
| `/Users/naveen/Projects/hostel/Website/components/book-now.js` | 338-340 | **FALSE** confirmation message |
| `/Users/naveen/Projects/hostel/Website/api/availability.php` | 12-14 | Default occupancy |
| `/Users/naveen/Projects/hostel/Website/api/availability.php` | 50, 91-92 | Availability extraction |
| `/Users/naveen/Projects/hostel/Website/api/create-order.php` | 47-61 | Total units & 8-room limit |
| `/Users/naveen/Projects/hostel/Website/api/create-order.php` | 83-87 | Date validation (no future check) |
| `/Users/naveen/Projects/hostel/Website/api/create-order.php` | 132 | Price validation (no upper bound) |
| `/Users/naveen/Projects/hostel/Website/api/create-order.php` | 108-109, 173 | Raw eZee error echo |
| `/Users/naveen/Projects/hostel/Website/api/verify-payment.php` | 1-45 | Signature verification |
| `/Users/naveen/Projects/hostel/Website/api/razorpay-webhook.php` | 1-45 | Webhook backstop |
| `/Users/naveen/Projects/hostel/Website/api/reconcile-pending.php` | 1-40 | Cron sweep |
| `/Users/naveen/Projects/hostel/Website/api/lib/booking.php` | 1-120 | Atomic state machine |
| `/Users/naveen/Projects/hostel/Website/api/lib/booking.php` | 91-107 | AddPayment non-fatal failure |
| `/Users/naveen/Projects/hostel/Website/api/lib/booking.php` | 78 | InsertBooking call |
| `/Users/naveen/Projects/hostel/Website/api/cancel-booking.php` | 1-50 | Cancellation endpoint |
| `/Users/naveen/Projects/hostel/Website/api/lib/ezee.php` | 1-120 | eZee API wrappers |
| `/Users/naveen/Projects/hostel/Website/api/lib/config.php` | 1-60 | Shared bootstrap |
| `/Users/naveen/Projects/hostel/Website/api/lib/selftest.php` | 1-42 | Runtime sanity checks |
| `/Users/naveen/Projects/hostel/Website/api/lib/mock.php` | 1-57 | Mock implementations |
| `/Users/naveen/Projects/hostel/Website/docs/competitor-booking-flow-livefreehostels.md` | Entire file | Competitor flow reference |

---

### CONCLUSION

The book-now flow has a **solid foundation** with good security practices (price re-validation, atomic state machine, signature verification) and a clean UI. However, it suffers from several **critical omissions**:

1. **NO EMAIL SYSTEM** – The most critical issue: the system lies to guests about sending confirmations.
2. **POOR POST-PAYMENT UX** – No retry buttons, no action confirmations, trapped in confirmation screen.
3. **MISSING MANAGEMENT FEATURES** – Cannot modify, lookup, or view past bookings.
4. **SECURITY & RELIABILITY GAPS** – Missing validation, retry logic, and observability.

Addressing the **P0 issues** (email infrastructure, payment retry, confirmation buttons) is essential before considering this flow production-ready. The remaining issues improve UX and reduce risk but do not block core functionality.

All gaps are documented with exact file paths and line numbers for immediate action.

---
*Report generated by Cline AI Coding Agent on 2026-09-13*
