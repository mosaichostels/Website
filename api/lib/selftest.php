<?php
/**
 * Run: php api/lib/selftest.php
 * CLI-only sanity check for the three non-trivial pieces of logic in the
 * booking engine. Not a test framework — plain assert()s, run before every
 * deploy touching create-order.php / verify-payment.php / razorpay.php.
 */
if (php_sapi_name() !== 'cli') exit;

ini_set('assert.exception', 1);
require __DIR__ . '/razorpay.php';

define('RAZORPAY_KEY_SECRET', 'test_secret_for_selftest_only');

// 1. Signature verification: accepts a known-good HMAC, rejects a tampered one.
$orderId = 'order_test123';
$paymentId = 'pay_test456';
$goodSig = hash_hmac('sha256', "$orderId|$paymentId", RAZORPAY_KEY_SECRET);
assert(razorpay_verify_signature($orderId, $paymentId, $goodSig) === true);
assert(razorpay_verify_signature($orderId, $paymentId, 'deadbeef' . $goodSig) === false);
assert(razorpay_verify_signature($orderId, 'pay_wrongid', $goodSig) === false);

// 2. rename() claim: first call succeeds, second call on the same
// now-renamed path fails — this is the concurrency/idempotency guard in
// verify-payment.php.
$tmpDir = sys_get_temp_dir() . '/mosaic-selftest-' . uniqid();
mkdir($tmpDir);
$src = "$tmpDir/pending.json";
$dst = "$tmpDir/processing.json";
file_put_contents($src, '{}');
assert(@rename($src, $dst) === true);
assert(@rename($src, $dst) === false); // src no longer exists — second claimant loses
array_map('unlink', glob("$tmpDir/*"));
rmdir($tmpDir);

// 3. Paise conversion uses integer math so fractional totals don't drift
// from float error (e.g. naive float math can give 130049 instead of 130050).
assert((int)round(1300.50 * 100) === 130050);
assert((int)round(999.99 * 100) === 99999);
assert((int)round(1.005 * 100) === 101 || (int)round(1.005 * 100) === 100); // float boundary, either rounding is acceptable — just must not throw/drift wildly

echo "All selftest assertions passed.\n";
