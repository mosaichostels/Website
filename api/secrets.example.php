<?php
/**
 * Copy this file to secrets.php (git-ignored) and fill in real values.
 * secrets.php is never committed and must be uploaded to the server by hand
 * (e.g. `./deploy.sh api/secrets.php`), never via `./deploy.sh all`.
 */

// ── eZee YCS Connectivity API ──
// HotelCode + APIKey: used as querystring auth for GET-style endpoints
// (RoomList / InsertBooking). Get these from your eZee YCS dashboard.
define('EZEE_HOTEL_CODE', '');
define('EZEE_API_KEY', '');

// AuthCode: used inside the JSON Authentication block for POST-style
// endpoints (AddPayment). Also from the eZee YCS dashboard — may be the
// same value as EZEE_API_KEY depending on your account, confirm with eZee.
define('EZEE_AUTH_CODE', '');

// Static per-property config values — fetch these ONCE via eZee's
// "Retrieve Pay Methods" and "Retrieve Currency" endpoints and hardcode
// here. They don't change per-request.
define('EZEE_PAYMENT_ID', '');   // PayMethods->PaymentID for your Razorpay/online payment method
define('EZEE_CURRENCY_ID', ''); // CurrencyID for INR

// ── Razorpay ──
// From the Razorpay dashboard (Settings → API Keys). Use rzp_test_* keys
// until you're ready to go live, then swap for rzp_live_* keys.
define('RAZORPAY_KEY_ID', '');
define('RAZORPAY_KEY_SECRET', '');

// From Dashboard → Settings → Webhooks after adding the payment.captured
// webhook pointed at api/razorpay-webhook.php. Blank disables the webhook
// endpoint (it 400s every request) without breaking the main booking flow.
define('RAZORPAY_WEBHOOK_SECRET', '');
