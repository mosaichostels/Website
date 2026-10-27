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
// their money back, so both sides of the 72-hour boundary are pinned. The window
// is measured from the START of the check-in date (00:00), matching the policy wording, so the
// boundary for a 15 Sep check-in is midnight at the start of 12 Sep.
$boundary = strtotime('2026-09-12 00:00:00');
assert(refund_due_for_checkin('2026-09-15', $boundary - 1) === true);   // a second before: refund
assert(refund_due_for_checkin('2026-09-15', $boundary) === true);       // exactly 72h: refund
assert(refund_due_for_checkin('2026-09-15', $boundary + 1) === false);  // a second after: none
assert(refund_due_for_checkin('2026-09-15', strtotime('2026-09-12 12:00:00')) === false); // was refundable under the old 13:00 cutoff
assert(refund_due_for_checkin('2026-09-15', strtotime('2026-09-15 12:00:00')) === false);
assert(refund_due_for_checkin('2026-09-15', strtotime('2026-09-01 09:00:00')) === true);
// Already past check-in — no refund, and it must not wrap to true.
assert(refund_due_for_checkin('2026-09-15', strtotime('2026-10-01 09:00:00')) === false);
// Undeterminable input must stay null so the caller promises nothing.
assert(refund_due_for_checkin(null) === null);
assert(refund_due_for_checkin('') === null);
assert(refund_due_for_checkin('not-a-date') === null);
assert(refund_due_for_checkin('2026-02-30') === null);

// 5. Automatic refund on an eligible cancellation. The request is a FULL refund (no amount, so the
// total can never be mis-converted), normal speed, and carries the reservation as the idempotency key
// so a retried cancel can never refund twice.
$req = razorpay_refund_request('pay_AbC123', 'mosaic-cancel-RES-1', ['reservation_no' => 'RES-1']);
assert($req['path'] === '/v1/payments/pay_AbC123/refund');
assert(!array_key_exists('amount', $req['body']));
assert($req['body']['speed'] === 'normal');
assert($req['body']['notes']['reservation_no'] === 'RES-1');
assert(in_array('X-Refund-Idempotency: mosaic-cancel-RES-1', $req['headers'], true));
assert(razorpay_refund_request('pay_a/b?x', 'k', [])['path'] === '/v1/payments/pay_a%2Fb%3Fx/refund'); // never injects path

$calls = [];
$ok = function (string $pid, string $key, array $notes) use (&$calls): array {
  $calls[] = [$pid, $key]; return ['_ok' => true, 'id' => 'rfnd_X1', 'status' => 'pending'];
};
$refusing = function (string $pid, string $key, array $notes) use (&$calls): array {
  $calls[] = [$pid, $key]; return ['_ok' => false, '_error' => 'The payment has been fully refunded already'];
};
$throwing = function (string $pid, string $key, array $notes): array { throw new RuntimeException('network down'); };
$failedStatus = function (string $pid, string $key, array $notes): array { return ['_ok' => true, 'id' => 'rfnd_X2', 'status' => 'failed']; };
$noId = function (string $pid, string $key, array $notes): array { return ['_ok' => true]; };

// Inside the 72h window: never refund, never even call Razorpay.
$calls = []; $r = cancellation_refund_outcome(false, 'pay_1', 'RES-1', $ok);
assert($r['action'] === 'none' && $calls === [] && str_contains($r['note'], 'not refundable'));
// Date unreadable: promise nothing, leave it to a person.
$calls = []; $r = cancellation_refund_outcome(null, 'pay_1', 'RES-1', $ok);
assert($r['action'] === 'manual' && $calls === [] && str_contains($r['note'], 'confirm'));
// Eligible but no payment id on record: a person must look.
foreach ([null, ''] as $noPay) {
  $calls = []; $r = cancellation_refund_outcome(true, $noPay, 'RES-1', $ok);
  assert($r['action'] === 'manual' && $calls === []);
}
// Eligible and Razorpay accepts: one call, right payment, reservation-keyed idempotency.
$calls = []; $r = cancellation_refund_outcome(true, 'pay_1', 'RES-1', $ok);
assert($r['action'] === 'refunded' && $r['refund_id'] === 'rfnd_X1' && $calls === [['pay_1', 'mosaic-cancel-RES-1']]);
assert(str_contains($r['note'], 'initiated') && str_contains($r['note'], '7–10 business days'));
// Eligible but Razorpay refuses: fall back to the manual path and keep the reason; the guest is not told it was sent.
$calls = []; $r = cancellation_refund_outcome(true, 'pay_1', 'RES-1', $refusing);
assert($r['action'] === 'manual' && str_contains($r['reason'], 'fully refunded already') && !str_contains($r['note'], 'initiated'));
// A crash or a reply without a refund id is also a failure, never a success.
$r = cancellation_refund_outcome(true, 'pay_1', 'RES-1', $throwing);
assert($r['action'] === 'manual' && str_contains($r['reason'], 'network down'));
$r = cancellation_refund_outcome(true, 'pay_1', 'RES-1', $noId);
assert($r['action'] === 'manual');
// A refund object with status 'failed' has an id but no money moves: manual, never "initiated".
$r = cancellation_refund_outcome(true, 'pay_1', 'RES-1', $failedStatus);
assert($r['action'] === 'manual' && !str_contains($r['note'], 'initiated') && str_contains($r['reason'], 'failed'));
// Razorpay needs an idempotency key of at least 10 characters; even a 1-character reservation number must get one.
$calls = []; cancellation_refund_outcome(true, 'pay_1', 'A', $ok);
assert(strlen($calls[0][1]) >= 10);

// 6b. Day-wise rates. Verified live 2026-10-27: eZee refuses ANY multi-night InsertBooking unless baserate, extradultrate
// AND extrachildrate each carry one comma-separated value per night ("599,599"); a single number, a total, a dated map or
// "599,599" with a single extradultrate are all refused (InvalidData). One night takes a single value.
$night5 = ['2026-11-16' => '2099.0000', '2026-11-17' => '2099.0000', '2026-11-18' => '2099.0000', '2026-11-19' => '2099.0000', '2026-11-20' => '3500.0000'];
assert(ezee_daywise_rates($night5, 5) === '2099,2099,2099,2099,3500'); // the 26 Oct order's rates
assert(ezee_daywise_rates(['2026-11-21' => '699.0000', '2026-11-22' => '899.0000'], 2) === '699,899');   // the 27 Sep order's rates
assert(ezee_daywise_rates(['2027-02-10' => '599.0000'], 1) === '599');
assert(ezee_daywise_rates(['2026-11-17' => '2099.5', '2026-11-16' => '1000'], 2) === '1000,2099.5');       // date order, decimals kept
assert(ezee_daywise_rates('599.0000', 2) === '599,599');                                                    // a flat scalar repeats
assert(ezee_daywise_rates(['a' => '1000'], 2) === null);                                                    // fewer rates than nights: refuse, never guess
assert(ezee_daywise_rates($night5, 4) === null);
assert(ezee_daywise_rates(null, 1) === null && ezee_daywise_rates([], 1) === null && ezee_daywise_rates('abc', 1) === null);
assert(ezee_daywise_rates('0.0000', 3) === '0,0,0'); // the child rate is 0 and must still be one value per night
assert(ezee_nights('2026-11-16', '2026-11-21') === 5 && ezee_nights('2026-02-27', '2026-03-01') === 2 && ezee_nights('2026-12-30', '2027-01-02') === 3);

// 7. Guest field values. Live eZee accepts other text (verified 2026-10-27), but a translated page used to submit "Mâle",
// "M." and "12h00 – 15h00" (the <option>s had no value=, so .value was the visible, translated text) and that ended up in
// the guest record. They are refused before payment instead.
require_once __DIR__ . '/guest.php';

assert(guest_values_error(['title' => 'Mr.', 'gender' => 'Male'], 'India', '12:00 PM – 3:00 PM') === null);
assert(guest_values_error(['title' => 'Ms.', 'gender' => 'Female'], 'France', 'After 9:00 PM') === null);
assert(guest_values_error([], '', '') === null); // all four are optional on the form
assert(guest_values_error(['title' => '', 'gender' => ''], '', '') === null);
assert(str_contains((string)guest_values_error(['gender' => 'Mâle'], '', ''), 'gender'));
assert(str_contains((string)guest_values_error(['title' => 'M.'], '', ''), 'title'));
assert(str_contains((string)guest_values_error([], 'Allemagne', ''), 'nationality'));
assert(str_contains((string)guest_values_error([], '', '12h00 – 15h00'), 'arrival'));
assert(guest_values_error(['gender' => 'male'], '', '') !== null); // exact match only, no case folding

// The server lists and the form must not drift apart: every <option> the page offers has an
// explicit value= (so translation cannot change what is sent) and is on the server's list.
$page = file_get_contents(__DIR__ . '/../../book-now.html');
foreach (['gTitle' => GUEST_TITLES, 'gGender' => GUEST_GENDERS, 'gArrival' => GUEST_ARRIVAL_TIMES] as $id => $allowed) {
  preg_match('/<select id="' . $id . '"[^>]*>(.*?)<\/select>/s', $page, $m);
  assert(isset($m[1]), "select #$id not found");
  preg_match_all('/<option([^>]*)>/', $m[1], $opts);
  $values = [];
  foreach ($opts[1] as $attrs) {
    assert(preg_match('/\bvalue="([^"]*)"/', $attrs, $v) === 1, "an <option> in #$id has no value=");
    $values[] = $v[1];
  }
  assert(array_values(array_diff($values, [''])) === $allowed, "#$id options differ from the server list");
}
// The nationality list lives in book-now.js (COUNTRIES, "name|dial-code,...").
preg_match("/COUNTRIES = \\((.*?)\\)\\s*\\.split/s", file_get_contents(__DIR__ . '/../../components/book-now.js'), $m);
preg_match_all("/'([^']*)'/", $m[1], $chunks);
$jsNames = array_map(fn ($s) => explode('|', $s)[0], explode(',', implode('', $chunks[1])));
assert($jsNames === GUEST_COUNTRIES, 'COUNTRIES in book-now.js differs from GUEST_COUNTRIES');
// ...and the nationality <option>s are generated with an explicit value= as well.
assert(str_contains(file_get_contents(__DIR__ . '/../../components/book-now.js'), '<option value="${escapeHtml(c.name)}">'));

// 7b. Free-text guest fields: a blank first name or oversized text is refused before payment.
assert(guest_text_error('Rahul', 'Sharma', '', 'a@b.co') === null);
assert(guest_text_error('राहुल', "O'Brien-Smith", 'late arrival, vegetarian', 'a+b@example.com') === null);
assert(guest_chars('राहुल') === 5 && guest_chars('é') === 1 && guest_chars('') === 0); // characters, not bytes
assert(preg_match_all('/./su', 'राहुल') === 5); // the fallback used when mbstring is missing counts the same
assert(str_contains((string)guest_text_error('', 'Sharma', '', 'a@b.co'), 'first name'));
assert(str_contains((string)guest_text_error('   ', 'Sharma', '', 'a@b.co'), 'first name'));
assert(guest_text_error('Rahul', '', '', 'a@b.co') === null);        // live eZee accepts a blank last name
assert(guest_text_error('Rahul', " \t ", '', 'a@b.co') === null);
assert(str_contains((string)guest_text_error(str_repeat('a', 61), 'Sharma', '', 'a@b.co'), 'first name'));
assert(guest_text_error(str_repeat('a', 60), str_repeat('é', 60), '', 'a@b.co') === null); // 60 characters, not 60 bytes
assert(str_contains((string)guest_text_error('Rahul', 'Sha' . "\n" . 'rma', '', 'a@b.co'), 'last name')); // no control characters in a name
assert(guest_text_error('Rahul', 'Sharma', str_repeat('x', 500), 'a@b.co') === null);
assert(str_contains((string)guest_text_error('Rahul', 'Sharma', str_repeat('x', 501), 'a@b.co'), 'request'));
assert(guest_text_error('Rahul', 'Sharma', "line1\nline2", 'a@b.co') === null); // a request may span lines
assert(str_contains((string)guest_text_error('Rahul', 'Sharma', '', str_repeat('a', 250) . '@b.co'), 'email'));

// 8. eZee reports a rejection in several shapes; only one used to be recognised, so the others
// came back "_ok" and an InsertBooking refusal was filed as ambiguous (no retry, no reason).
// The first three payloads are the real replies from the 2026-08-29, 2026-09-27 and 2026-10-26 orders.
$pastDate = ['ErrorCode' => 'InsertBookingFailed', 'ErrorDescription' => 'ArrivalDate is Past date.'];
$invalidData = ['0' => ['Error Details' => ['Error_Code' => 'InvalidData', 'Error_Message' => 'Please check data passed.']]];
$classic = ['Errors' => ['ErrorMessage' => 'Invalid hotel code']];
assert(str_contains((string)ezee_decoded_error($pastDate), 'ArrivalDate is Past date.'));
assert(str_contains((string)ezee_decoded_error($invalidData), 'Please check data passed.'));
assert(str_contains((string)ezee_decoded_error($invalidData), 'InvalidData'));
assert(str_contains((string)ezee_decoded_error($classic), 'Invalid hotel code'));
// Successful replies are not errors: InsertBooking, a RoomList-like body, and AddPayment's
// Errors LIST whose ErrorCode "0" means success (booking.php reads that one itself).
assert(ezee_decoded_error(['ReservationNo' => '1615', 'SubReservationNo' => ['1615']]) === null);
assert(ezee_decoded_error(['RoomList' => ['RoomType' => [['roomtypeunkid' => '1']]], 'SearchCriteria' => []]) === null);
assert(ezee_decoded_error(['Errors' => [['ErrorCode' => '0', 'ErrorMessage' => 'Success']]]) === null);
assert(ezee_decoded_error([]) === null);

// The whole reply classification, minus the network: a definite rejection is _ok=false WITHOUT
// _transport (confirm_paid_order retries those and calls them non-ambiguous); a timeout/5xx/garbage
// reply is _transport (never retried: the reservation may exist); 429 is refused-before-processing.
$r = ezee_interpret_response(200, json_encode($invalidData));
assert($r['_ok'] === false && empty($r['_transport']) && str_contains($r['_error'], 'Please check data passed.'));
$r = ezee_interpret_response(200, json_encode($pastDate));
assert($r['_ok'] === false && empty($r['_transport']));
$r = ezee_interpret_response(200, json_encode(['ReservationNo' => '1615']));
assert($r['_ok'] === true && $r['ReservationNo'] === '1615');
$r = ezee_interpret_response(503, '{"ReservationNo":"9"}');
assert($r['_ok'] === false && $r['_transport'] === true && !isset($r['ReservationNo']));
$r = ezee_interpret_response(200, '<html>blocked</html>');
assert($r['_ok'] === false && $r['_transport'] === true);
$r = ezee_interpret_response(429, '');
assert($r['_ok'] === false && $r['_rateLimited'] === true && empty($r['_transport']));
// A coded rejection (bad data, past arrival) can never succeed on a retry: it is marked permanent so the order is parked and
// the alert goes out at once. The plain Errors.ErrorMessage reply keeps the old behaviour (retried, it may be transient).
$r = ezee_interpret_response(200, json_encode($invalidData)); assert($r['_permanent'] === true);
$r = ezee_interpret_response(200, json_encode($pastDate)); assert($r['_permanent'] === true);
$r = ezee_interpret_response(200, json_encode($classic)); assert($r['_ok'] === false && empty($r['_permanent']));
// A reply the account's WAF dresses up as success must not become a reservation.
$r = ezee_interpret_response(200, '[]');
assert($r['_ok'] === true && empty($r['ReservationNo']));

echo "All selftest assertions passed.\n";
