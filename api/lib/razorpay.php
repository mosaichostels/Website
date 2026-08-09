<?php
/**
 * Razorpay Orders API + payment-signature verification.
 * https://razorpay.com/docs/api/orders/ · https://razorpay.com/docs/payments/server-integration/php/payment-gateway/build-integration/#3-verify-payment-signature
 */

function razorpay_create_order(int $amountPaise, string $receipt, array $notes): array {
  $ch = curl_init('https://api.razorpay.com/v1/orders');
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
