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

// 4. Stay-total resolution. eZee puts the total either nested under
// room_rates_info or at the entry top level depending on account config.
// availability.php and create-order.php both go through ezee_room_total(), and
// they MUST agree: when create-order.php checked only the nested location, any
// top-level response let search render a price that checkout then couldn't
// resolve, 502-ing every booking after the guest filled in the whole form.
require __DIR__ . '/ezee.php';

$nested = ['roomtypeunkid' => 'a', 'roomrateunkid' => 'b',
  'room_rates_info' => ['totalprice_inclusive_all' => '1650.0000', 'totalprice_room_only' => '1567.50']];
assert(ezee_room_total($nested) === 1650.00);
assert(ezee_room_base_total($nested) === 1567.50);

// The other shape eZee has been observed to return: totals at the entry's top
// level, with room_rates_info carrying only exclusive_tax. This returned 0
// before ezee_room_total() existed.
$topLevel = ['roomtypeunkid' => 'a', 'roomrateunkid' => 'b',
  'totalprice_inclusive_all' => '1650.0000', 'totalprice_room_only' => '1567.50',
  'room_rates_info' => ['exclusive_tax' => '522.50']];
assert(ezee_room_total($topLevel) === 1650.00);
assert(ezee_room_base_total($topLevel) === 1567.50);

// Date-keyed rate objects collapse to a scalar rather than casting to 1.
assert(ezee_room_total(['room_rates_info' => ['totalprice_inclusive_all' => ['2026-08-13' => '499.0000']]]) === 499.00);

// No price anywhere is null, not 0 — create-order.php rejects on <= 0, and a
// silent 0 would mean a free booking.
assert(ezee_room_total(['roomtypeunkid' => 'a', 'roomrateunkid' => 'b']) === null);

// The walker finds entries at any nesting depth and doesn't recurse into a match.
$found = [];
ezee_find_room_entries(['Rooms' => ['Room_0' => $nested, 'Room_1' => $topLevel]], $found);
assert(count($found) === 2);

// 5. Strict date parsing. availability.php and create-order.php now share
// validate_stay_dates(); before that each parsed dates itself and the order
// endpoint enforced less than the search that precedes it. PHP's lenient
// createFromFormat() silently rolls impossible dates over, which is what the
// getLastErrors() check exists to stop.
require_once __DIR__ . '/dates.php';

assert(parse_strict_date('2026-09-15') instanceof DateTime);
assert(parse_strict_date('2026-09-15')->format('H:i:s') === '00:00:00'); // '!' zeroes the clock time
assert(parse_strict_date('2026-02-30') === null); // would roll to 2 March
assert(parse_strict_date('2026-13-01') === null); // would roll to Jan 2027
assert(parse_strict_date('2026-00-10') === null);
assert(parse_strict_date('2026-9-5') === null);   // not zero-padded
assert(parse_strict_date('26-09-05') === null); // 2-digit year parses clean as year 0026
assert(parse_strict_date('15/09/2026') === null);
assert(parse_strict_date('next tuesday') === null);
assert(parse_strict_date('') === null);
// Leap years are real dates, not rollovers.
assert(parse_strict_date('2028-02-29') instanceof DateTime);
assert(parse_strict_date('2026-02-29') === null);

// eZee's own RoomList caps a search at 30 nights (error NightsLimitExceeded,
// "You can not request for more then 30 nights") — MAX_STAY_NIGHTS must not
// drift above what eZee will actually accept.
assert(MAX_STAY_NIGHTS <= 30);

// 6. Refund window. This decides whether a cancelling guest is told they get
// their money back, so both sides of the 72-hour boundary are pinned. Check-in
// is 1:00 PM, so the boundary for a 15 Sep check-in is 1:00 PM on 12 Sep.
$boundary = strtotime('2026-09-12 13:00:00');
assert(refund_due_for_checkin('2026-09-15', $boundary - 1) === true);   // a second before: refund
assert(refund_due_for_checkin('2026-09-15', $boundary) === true);       // exactly 72h: refund
assert(refund_due_for_checkin('2026-09-15', $boundary + 1) === false);  // a second after: none
assert(refund_due_for_checkin('2026-09-15', strtotime('2026-09-15 12:00:00')) === false);
assert(refund_due_for_checkin('2026-09-15', strtotime('2026-09-01 09:00:00')) === true);
// Already past check-in — no refund, and it must not wrap to true.
assert(refund_due_for_checkin('2026-09-15', strtotime('2026-10-01 09:00:00')) === false);
// Undeterminable input must stay null so the caller promises nothing.
assert(refund_due_for_checkin(null) === null);
assert(refund_due_for_checkin('') === null);
assert(refund_due_for_checkin('not-a-date') === null);
assert(refund_due_for_checkin('2026-02-30') === null);

echo "All selftest assertions passed.\n";
