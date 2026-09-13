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
// Unpaid orders used to sit in pending/ forever, so this glob grew without
// bound and every tick re-polled Razorpay for orders nobody ever paid. After a
// day they're abandoned carts. They're MOVED, not deleted: a Razorpay order
// stays payable indefinitely, so on the remote chance one is paid later the
// record it needs still exists — just not somewhere that costs a poll a minute.
$abandonCutoff = time() - 86400;

foreach (glob(PENDING_ORDERS_DIR . '/pending/*.json') ?: [] as $file) {
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
  if (!$captured) {
    // Confirmed unpaid by Razorpay itself, not merely quiet.
    if (filemtime($file) < $abandonCutoff) {
      @rename($file, PENDING_ORDERS_DIR . '/abandoned/' . $orderId . '.json');
      bookings_log("ABANDONED order=$orderId (unpaid for over 24h)");
    }
    continue;
  }

  $result = confirm_paid_order($orderId, $captured['id']);
  bookings_log("RECONCILE order=$orderId payment={$captured['id']} status={$result['status']}");
}

// Rate-limit counters are disposable: each is a fixed window of at most a few
// minutes, so anything untouched for an hour is dead weight. Pruned here
// because this is the only thing already running on a schedule.
foreach (glob(PENDING_ORDERS_DIR . '/ratelimit/*.json') ?: [] as $file) {
  if (filemtime($file) < time() - 3600) @unlink($file);
}
