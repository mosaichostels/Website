<?php
/**
 * POST /api/verify-payment.php
 * Body: { razorpay_order_id, razorpay_payment_id, razorpay_signature }
 *
 * Only path that ever creates an eZee reservation. The client-side Razorpay
 * "payment succeeded" callback is never trusted alone — signature is
 * verified server-side first, unconditionally.
 */
require __DIR__ . '/lib/config.php';
require __DIR__ . '/lib/ezee.php';
require __DIR__ . '/lib/razorpay.php';
require __DIR__ . '/lib/booking.php';

$body = read_json_body();
$orderId = $body['razorpay_order_id'] ?? '';
$paymentId = $body['razorpay_payment_id'] ?? '';
$signature = $body['razorpay_signature'] ?? '';
if ($orderId === '' || $paymentId === '' || $signature === '') {
  json_error(400, 'Missing payment verification fields.');
}
if (!razorpay_verify_signature($orderId, $paymentId, $signature)) {
  json_error(400, 'Payment signature could not be verified.');
}

// Shared with razorpay-webhook.php's server-to-server backstop — same
// atomic rename() claim either way, so whichever caller gets here first
// wins and the other sees the done/failed result idempotently.
$result = confirm_paid_order($orderId, $paymentId);

if ($result['status'] === 'done') {
  json_ok([
    'success' => true,
    'reservation_no' => $result['reservation_no'],
    'sub_reservation_no' => $result['sub_reservation_no'],
  ]);
}
if ($result['status'] === 'failed') {
  json_error(502, 'Payment received but booking confirmation is still pending — our team will follow up shortly.');
}
json_error(409, 'This booking is already being processed. Please wait a moment and refresh.');
