<?php
/**
 * POST /api/razorpay-webhook.php
 *
 * Server-to-server backstop for the case verify-payment.php can't cover:
 * guest pays, then closes the tab/loses connection before the browser's
 * Checkout `handler` callback ever fires. Razorpay has the money, nothing
 * else creates the eZee reservation. This listens for "payment.captured"
 * and calls the same confirm_paid_order() claim used by verify-payment.php,
 * so whichever path gets there first wins — no double-booking either way.
 *
 * Setup: Razorpay Dashboard → Settings → Webhooks → add this URL, event
 * "payment.captured", then put the secret Razorpay generates for it into
 * RAZORPAY_WEBHOOK_SECRET in secrets.php (different from the API key
 * secret).
 */
require __DIR__ . '/lib/config.php';
require __DIR__ . '/lib/ezee.php';
require __DIR__ . '/lib/booking.php';

$raw = file_get_contents('php://input');
$signature = $_SERVER['HTTP_X_RAZORPAY_SIGNATURE'] ?? '';

if (RAZORPAY_WEBHOOK_SECRET === '' || !hash_equals(hash_hmac('sha256', $raw, RAZORPAY_WEBHOOK_SECRET), $signature)) {
  http_response_code(400);
  exit;
}

$event = json_decode($raw, true);
if (!is_array($event) || ($event['event'] ?? '') !== 'payment.captured') {
  http_response_code(200); // acknowledge so Razorpay stops retrying; nothing to do
  exit;
}

$payment = $event['payload']['payment']['entity'] ?? [];
$orderId = $payment['order_id'] ?? '';
$paymentId = $payment['id'] ?? '';
if ($orderId === '' || $paymentId === '') {
  http_response_code(400);
  exit;
}

confirm_paid_order($orderId, $paymentId);
http_response_code(200);
