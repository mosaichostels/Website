<?php
/**
 * Razorpay Orders API + payment-signature verification.
 * https://razorpay.com/docs/api/orders/ · https://razorpay.com/docs/payments/server-integration/php/payment-gateway/build-integration/#3-verify-payment-signature
 */

// Overridable only so tests can point at a local mock; production leaves it unset.
function razorpay_api_base(): string {
  return defined('RAZORPAY_API_BASE') ? RAZORPAY_API_BASE : 'https://api.razorpay.com';
}

function razorpay_create_order(int $amountPaise, string $receipt, array $notes): array {
  $ch = curl_init(razorpay_api_base() . '/v1/orders');
  curl_setopt_array($ch, [
    CURLOPT_RETURNTRANSFER => true,
    CURLOPT_TIMEOUT => 15,
    CURLOPT_CONNECTTIMEOUT => 5,
    CURLOPT_USERPWD => RAZORPAY_KEY_ID . ':' . RAZORPAY_KEY_SECRET,
    CURLOPT_POST => true,
    CURLOPT_HTTPHEADER => ['Content-Type: application/json'],
    CURLOPT_POSTFIELDS => json_encode([
      'amount' => $amountPaise,
      'currency' => 'INR',
      'receipt' => $receipt,
      'payment_capture' => 1,
      'notes' => $notes,
    ]),
  ]);
  $response = curl_exec($ch);
  $curlErrno = curl_errno($ch);
  $curlError = curl_error($ch);
  $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);

  if ($curlErrno !== 0) return ['_ok' => false, '_error' => "Razorpay request failed: $curlError"];
  $decoded = json_decode($response, true);
  if (!is_array($decoded) || $httpCode >= 300) {
    $msg = $decoded['error']['description'] ?? "Razorpay returned HTTP $httpCode";
    return ['_ok' => false, '_error' => $msg];
  }
  $decoded['_ok'] = true;
  return $decoded;
}

function razorpay_verify_signature(string $orderId, string $paymentId, string $signature): bool {
  $expected = hash_hmac('sha256', $orderId . '|' . $paymentId, RAZORPAY_KEY_SECRET);
  return hash_equals($expected, $signature);
}

// Used by reconcile-pending.php to poll for captured payments directly —
// doesn't depend on the client callback firing or the webhook being
// registered/reachable, both of which have been observed to fail silently.
function razorpay_fetch_order_payments(string $orderId): array {
  $ch = curl_init(razorpay_api_base() . '/v1/orders/' . urlencode($orderId) . '/payments');
  curl_setopt_array($ch, [
    CURLOPT_RETURNTRANSFER => true,
    CURLOPT_TIMEOUT => 15,
    CURLOPT_CONNECTTIMEOUT => 5,
    CURLOPT_USERPWD => RAZORPAY_KEY_ID . ':' . RAZORPAY_KEY_SECRET,
  ]);
  $response = curl_exec($ch);
  $curlErrno = curl_errno($ch);
  $curlError = curl_error($ch);
  $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);

  if ($curlErrno !== 0) return ['_ok' => false, '_error' => "Razorpay request failed: $curlError"];
  $decoded = json_decode($response, true);
  if (!is_array($decoded) || $httpCode >= 300) {
    $msg = $decoded['error']['description'] ?? "Razorpay returned HTTP $httpCode";
    return ['_ok' => false, '_error' => $msg];
  }
  $decoded['_ok'] = true;
  return $decoded;
}

/**
 * Full refund of one captured payment. No "amount": Razorpay refunds the whole payment, so the booking
 * total is never converted to paise here. $idempotencyKey makes a repeated call return the same refund
 * instead of paying twice. Pure, so selftest.php can check exactly what would be sent.
 */
function razorpay_refund_request(string $paymentId, string $idempotencyKey, array $notes): array {
  return [
    'path' => '/v1/payments/' . rawurlencode($paymentId) . '/refund',
    'body' => ['speed' => 'normal', 'notes' => $notes],
    'headers' => ['Content-Type: application/json', 'X-Refund-Idempotency: ' . $idempotencyKey],
  ];
}

function razorpay_refund_payment(string $paymentId, string $idempotencyKey, array $notes): array {
  $req = razorpay_refund_request($paymentId, $idempotencyKey, $notes);
  $ch = curl_init(razorpay_api_base() . $req['path']);
  curl_setopt_array($ch, [
    CURLOPT_RETURNTRANSFER => true,
    CURLOPT_TIMEOUT => 20,
    CURLOPT_CONNECTTIMEOUT => 5,
    CURLOPT_USERPWD => RAZORPAY_KEY_ID . ':' . RAZORPAY_KEY_SECRET,
    CURLOPT_POST => true,
    CURLOPT_HTTPHEADER => $req['headers'],
    CURLOPT_POSTFIELDS => json_encode($req['body']),
  ]);
  $response = curl_exec($ch);
  $curlErrno = curl_errno($ch);
  $curlError = curl_error($ch);
  $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);

  if ($curlErrno !== 0) return ['_ok' => false, '_error' => "Razorpay request failed: $curlError"];
  $decoded = json_decode($response, true);
  if (!is_array($decoded) || $httpCode >= 300) {
    $msg = $decoded['error']['description'] ?? "Razorpay returned HTTP $httpCode";
    return ['_ok' => false, '_error' => $msg];
  }
  $decoded['_ok'] = true;
  return $decoded;
}

/**
 * What a cancellation does about money, and what the guest is told. $refundDue comes from
 * refund_due_for_checkin() (true = 72h or more before check-in, false = inside the window, null = unknown).
 * Inside the window or when unknown Razorpay is never called. When a refund is due it is issued
 * automatically; ANY failure (error reply, crash, reply without a refund id, missing payment id) falls back to
 * 'manual' so staff are alerted as before. $refund is injected so selftest.php needs no network.
 * Returns ['action' => 'none'|'manual'|'refunded', 'note' => guest-facing text, 'reason' => ?, 'refund_id' => ?].
 */
function cancellation_refund_outcome(?bool $refundDue, ?string $paymentId, string $reservationNo, callable $refund): array {
  if ($refundDue === false) {
    return ['action' => 'none', 'note' => 'This is within 72 hours of check-in, so under our cancellation policy the booking amount is not refundable.'];
  }
  if ($refundDue === null) {
    return ['action' => 'manual', 'note' => 'We\'ll confirm any refund due with you shortly.', 'reason' => 'check-in date unreadable'];
  }
  $manual = 'Your refund will be processed within 7–10 business days.';
  if ($paymentId === null || $paymentId === '') {
    return ['action' => 'manual', 'note' => $manual, 'reason' => 'no Razorpay payment id on record'];
  }
  try {
    $res = $refund($paymentId, 'mosaic-cancel-' . $reservationNo /* key must be 10+ chars */, [
      'reservation_no' => $reservationNo,
      'reason' => 'guest cancellation more than 72 hours before check-in',
    ]);
  } catch (Throwable $e) {
    return ['action' => 'manual', 'note' => $manual, 'reason' => substr('refund call crashed: ' . $e->getMessage(), 0, 200)];
  }
  $refundId = $res['id'] ?? '';
  $refundStatus = $res['status'] ?? '';
  if (($res['_ok'] ?? false) === true && is_string($refundId) && $refundId !== '') {
    // A refund object can exist with status 'failed'; only pending/processed mean money is on its way.
    if (!in_array($refundStatus, ['pending', 'processed'], true)) {
      return ['action' => 'manual', 'note' => $manual, 'reason' => 'refund status ' . substr((string)$refundStatus, 0, 40) . ' (' . $refundId . ')'];
    }
    return ['action' => 'refunded', 'refund_id' => $refundId,
      'note' => 'Your refund has been initiated and will reach your original payment method within 7–10 business days.'];
  }
  return ['action' => 'manual', 'note' => $manual, 'reason' => substr((string)($res['_error'] ?? 'refund reply had no refund id'), 0, 200)];
}
