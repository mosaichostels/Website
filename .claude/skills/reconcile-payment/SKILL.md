---
name: reconcile-payment
description: Diagnose and resolve a stuck/pending Razorpay-to-eZee booking reconciliation issue
disable-model-invocation: true
---

## Payment Reconciliation Flow

The booking system has **three paths** to turn a paid Razorpay order into an eZee reservation:

1. **Fast path** (client-triggered): Browser's Razorpay Checkout callback → `api/verify-payment.php` → signature validation → `confirm_paid_order()`
2. **Webhook backstop** (server-to-server): Razorpay `payment.captured` event → `api/razorpay-webhook.php` → `confirm_paid_order()`
3. **Cron sweep backstop** (polling): `api/reconcile-pending.php` polls Razorpay directly for captured payments on stuck orders

All three paths share the same `confirm_paid_order()` function in `api/lib/booking.php`, which atomically renames pending orders through state directories (`pending/` → `processing/` → `done/` or `failed/`). Whichever path gets there first wins; others see the result idempotently.

## Stuck Order Diagnosis Checklist

**Before making ANY changes:** this touches production money and booking state. Confirm the resolution against the actual stuck order before writing anything back to eZee or marking it settled.

### 1. Verify `api/lib/config.php` is included in the failing code path

A past incident: missing `require` of `config.php` silently broke payment resolution.

```bash
# Check if the failing endpoint actually requires config.php
grep -n "require.*config\.php" api/verify-payment.php api/razorpay-webhook.php api/reconcile-pending.php

# config.php defines:
# - PENDING_ORDERS_DIR: path to pending order JSON storage
# - EZEE_BASE_URL, EZEE_HOTEL_CODE, EZEE_AUTH_CODE, EZEE_CURRENCY_ID: eZee credentials
# - Helper functions: ensure_pending_dirs(), bookings_log(), json_error(), json_ok(), read_json_body()
```

If the error path doesn't require it, that's the root cause — add the include.

### 2. Check pending orders directory path exists and matches config

```bash
# From api/lib/config.php line 25:
# PENDING_ORDERS_DIR = dirname(__DIR__, 3) . '/ezee-pending-orders'
# That's: api/lib -> api -> docroot -> parent of docroot

# Verify the directory structure:
cd /Users/naveen/Projects/hostel/Website
ls -la ../ezee-pending-orders/
ls -la ../ezee-pending-orders/pending/
ls -la ../ezee-pending-orders/processing/
ls -la ../ezee-pending-orders/done/
ls -la ../ezee-pending-orders/failed/

# If directories don't exist, the ensure_pending_dirs() function should create them
# (api/lib/config.php lines 27-32), but check if the parent directory is writable:
test -w ../ && echo "Parent writable" || echo "Parent NOT writable — permission issue"
```

If the directory doesn't exist or isn't writable, that's the root cause.

### 3. Check eZee API for date-based rejection errors

A past incident: eZee rejected booking dates that were in the past or near midnight.

```bash
# Look at the last failed order in the logs:
tail -50 ../ezee-pending-orders/bookings.log | grep "FAILED\|WARN"

# Check a specific failed order's JSON to see the response:
# (replace ORDER_ID with the stuck order)
cat ../ezee-pending-orders/failed/ORDER_ID.json | jq '.response' 2>/dev/null || \
  cat ../ezee-pending-orders/failed/ORDER_ID.json

# The booking dates are in $record['check_in'] and $record['check_out']
# (from api/lib/booking.php line 57-58)
# Confirm they're in future date format eZee expects:
# - Format: YYYY-MM-DD
# - Must be in the future (eZee rejects past dates)
# - Avoid near-midnight times if submitting via API
```

If the response shows date rejection, recalculate dates or contact eZee support.

### 4. Manually run reconciliation logic against the stuck order

```bash
# Find the stuck order:
ls ../ezee-pending-orders/pending/*.json

# Read its details:
cat ../ezee-pending-orders/pending/ORDER_ID.json | jq '.'

# The order has these fields:
# - razorpay_order_id: order ID from Razorpay
# - room_units: array of room bookings with guest details
# - check_in, check_out: booking dates
# - total: total amount paid
# - email, phone, nationality: guest info
```

**Test Razorpay payment status directly:**
```bash
# Use Razorpay API (you need RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET from secrets.php)
# Call: GET https://api.razorpay.com/v1/orders/ORDER_ID/payments
# (implemented in api/lib/razorpay.php, razorpay_fetch_order_payments())

# If you have PHP available:
php << 'EOF'
$orderId = 'YOUR_ORDER_ID_HERE';
$keyId = getenv('RAZORPAY_KEY_ID');      // from secrets.php
$keySecret = getenv('RAZORPAY_KEY_SECRET');

$ch = curl_init("https://api.razorpay.com/v1/orders/$orderId/payments");
curl_setopt_array($ch, [
  CURLOPT_RETURNTRANSFER => true,
  CURLOPT_USERPWD => "$keyId:$keySecret",
]);
$response = curl_exec($ch);
echo json_encode(json_decode($response, true), JSON_PRETTY_PRINT);
EOF
```

Look for a payment with `status: "captured"`. If it exists, the payment is confirmed on Razorpay's side and should be safe to reconcile.

### 5. Verify signature/webhook validity before trusting any resolution

A payment can only be confirmed if **one of these is true:**

1. **Client callback**: Browser sent `razorpay_order_id`, `razorpay_payment_id`, `razorpay_signature` to `api/verify-payment.php`
   - Must call `razorpay_verify_signature()` (api/lib/razorpay.php line 39-42)
   - Expected signature: `hash_hmac('sha256', $orderId . '|' . $paymentId, RAZORPAY_KEY_SECRET)`
   - Only trust if signature matches

2. **Webhook event**: Razorpay sent `X-Razorpay-Signature` header with `payment.captured` event
   - Must verify header against the raw body (api/razorpay-webhook.php line 24)
   - Expected header: `hash_hmac('sha256', $raw_body, RAZORPAY_WEBHOOK_SECRET)`
   - Webhook secret is **different** from the API key secret — both must be in `secrets.php`

3. **Cron polling**: `api/reconcile-pending.php` fetches the order from Razorpay's API directly
   - Uses `razorpay_fetch_order_payments()` (api/lib/razorpay.php line 47-68)
   - Only trusts payments marked as `status: "captured"` (reconcile-pending.php line 33)
   - Safe because it's server-to-server with API key auth

**DO NOT manually move an order from `pending/` to `done/` or skip verification.** Always confirm the payment actually exists on Razorpay's side before reconciling.

## After Diagnosis

Once you've confirmed the root cause:

- **Missing include?** Add `require_once __DIR__ . '/lib/config.php';` to the failing endpoint
- **Missing directory?** Run `ensure_pending_dirs()` or create the directories manually
- **Failed date?** Recalculate the dates and manually retry `confirm_paid_order($orderId, $paymentId)` via PHP
- **Unverified payment?** Run the cron sweep manually to let Razorpay API confirm payment status

Log your findings in `../ezee-pending-orders/bookings.log` before and after the fix.

## Related Files

- `api/verify-payment.php` — Client verification endpoint
- `api/razorpay-webhook.php` — Razorpay event listener
- `api/reconcile-pending.php` — Cron sweep (CLI-only, not HTTP-reachable)
- `api/lib/booking.php` — `confirm_paid_order()` state machine
- `api/lib/razorpay.php` — Razorpay API helpers
- `api/lib/config.php` — Bootstrap, paths, and helper functions
- `api/lib/ezee.php` — eZee API integration
