<?php
/**
 * Cron sweep — backstop for when BOTH verify-payment.php (client callback)
 * and razorpay-webhook.php (server webhook) fail to fire, e.g. guest closes
 * the tab AND the webhook is unregistered/misconfigured/unreachable. Polls
 * Razorpay directly for each stuck pending order instead of waiting for
 * Razorpay to call us — confirm_paid_order()'s atomic rename() claim makes
 * this safe to run even if another path confirms the same order first.
 * CLI-only (cron), never HTTP-reachable.
 */
if (php_sapi_name() !== 'cli') { http_response_code(404); exit; }

require __DIR__ . '/lib/config.php';
require __DIR__ . '/lib/ezee.php';
require __DIR__ . '/lib/razorpay.php';
require __DIR__ . '/lib/booking.php';

ensure_pending_dirs();
$cutoff = time() - 180; // give the fast paths 3 minutes before we intervene

foreach (glob(PENDING_ORDERS_DIR . '/pending/*.json') as $file) {
  $orderId = basename($file, '.json');
  if (filemtime($file) > $cutoff) continue;

  $payments = razorpay_fetch_order_payments($orderId);
  if (!$payments['_ok']) {
    bookings_log("RECONCILE fetch failed order=$orderId error={$payments['_error']}");
    continue;
  }

  $captured = null;
  foreach ($payments['items'] ?? [] as $payment) {
    if ($payment['status'] === 'captured') { $captured = $payment; break; }
  }
  if (!$captured) continue; // still unpaid or abandoned — leave pending

  $result = confirm_paid_order($orderId, $captured['id']);
  bookings_log("RECONCILE order=$orderId payment={$captured['id']} status={$result['status']}");
}
