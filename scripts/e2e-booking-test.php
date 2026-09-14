<?php
/**
 * End-to-end driver for the book-now API flow against the local dev server in
 * mock mode. Nothing here bypasses a check: the Razorpay signature is computed
 * with the same secret the server holds, so verify-payment.php verifies it for
 * real. The "payment status" switch flips the MOCK order's stored status
 * (captured / failed / never paid), which is what a real Razorpay would report.
 */
error_reporting(E_ALL & ~E_DEPRECATED);

// Usage, from the repo root:
//   EZEE_MOCK_ROOMLIST=1 php -S 127.0.0.1:8899 -t . &
//   php scripts/e2e-booking-test.php
//
// Requires api/secrets.php with mock values whose RAZORPAY_KEY_SECRET matches
// SECRET below; the key id must NOT be a live key (razorpay_mock_enabled()
// refuses to mock one). Never run this against production credentials.
const BASE = 'http://127.0.0.1:8899';
const SECRET = 'mockseceretlocaltestonly';
// Mirrors PENDING_ORDERS_DIR in api/lib/config.php: one level above the docroot.
define('PENDING', dirname(__DIR__, 2) . '/ezee-pending-orders');

$pass = 0; $fail = 0; $failures = [];

function req(string $method, string $path, ?array $body = null): array {
  $ch = curl_init(BASE . $path);
  curl_setopt_array($ch, [
    CURLOPT_RETURNTRANSFER => true, CURLOPT_TIMEOUT => 30,
    CURLOPT_CUSTOMREQUEST => $method,
    CURLOPT_HTTPHEADER => ['Content-Type: application/json'],
  ]);
  if ($body !== null) curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($body));
  $raw = curl_exec($ch);
  $code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
  return ['code' => $code, 'json' => json_decode((string)$raw, true), 'raw' => (string)$raw];
}

function check(string $name, bool $ok, string $detail = '') {
  global $pass, $fail, $failures;
  if ($ok) { $pass++; echo "  PASS  $name\n"; }
  else { $fail++; $failures[] = $name; echo "  FAIL  $name" . ($detail ? "  -> $detail" : '') . "\n"; }
}

/**
 * Clear rate-limit counters. The driver hammers these endpoints far harder than
 * any guest ever would, so without this the limiter (correctly) blocks the rest
 * of the suite. Section 12 deliberately does NOT call this — that is where the
 * limiter itself is under test.
 */
function reset_limits() {
  foreach (glob(PENDING . '/ratelimit/*.json') ?: [] as $f) @unlink($f);
}

function section(string $t) { reset_limits(); echo "\n== $t ==\n"; }

function d(int $daysFromNow): string { return date('Y-m-d', strtotime("+$daysFromNow days")); }

/** Flip the mock Razorpay order's payment status, as Razorpay would report it. */
function set_payment(string $orderId, ?string $status, string $paymentId = 'pay_MOCK123456') {
  $f = PENDING . '/mock-rzp/' . $orderId . '.json';
  $o = json_decode((string)file_get_contents($f), true);
  if ($status === null) { unset($o['_payment_status'], $o['_payment_id']); }
  else { $o['_payment_status'] = $status; $o['_payment_id'] = $paymentId; }
  file_put_contents($f, json_encode($o));
}

function sign(string $orderId, string $paymentId): string {
  return hash_hmac('sha256', $orderId . '|' . $paymentId, SECRET);
}

function base_order(array $over = []): array {
  return array_merge([
    'check_in' => d(20), 'check_out' => d(22),
    'rooms' => [['roomtypeunkid' => '187270000000000104', 'ratetypeunkid' => '1872700000000001041',
                 'roomrateunkid' => '1872700000000001042', 'qty' => 1, 'adults' => 1]],
    'guest' => ['title' => 'Mr', 'first_name' => 'Test', 'last_name' => 'Guest', 'gender' => 'Male'],
    'first_name' => 'Test', 'last_name' => 'Guest', 'email' => 'test@example.com',
    'phone' => '9876543210', 'phone_code' => '+91', 'nationality' => 'India',
  ], $over);
}

// ─────────────────────────────────────────────────────────────────────────────
section('1. Availability (N7 unknown availability, N1 pricing, N22 base_adults)');

$r = req('GET', '/api/availability.php?check_in=' . d(20) . '&check_out=' . d(22) . '&adults=1');
check('availability 200', $r['code'] === 200, "got {$r['code']} {$r['raw']}");
$rooms = $r['json']['rooms'] ?? [];
check('returns 5 mock room types', count($rooms) === 5, 'got ' . count($rooms));
$dorm = null; $double = null;
foreach ($rooms as $room) {
  if ($room['roomtypeunkid'] === '187270000000000104') $dorm = $room;
  if ($room['roomtypeunkid'] === '187270000000000105') $double = $room;
}
check('8-bed dorm total = 450*2 nights = 900', $dorm && (float)$dorm['total'] === 900.0, 'got ' . json_encode($dorm['total'] ?? null));
check('double room total = 1500*2 = 3000', $double && (float)$double['total'] === 3000.0, 'got ' . json_encode($double['total'] ?? null));
check('N22: dorm base_adults = 1', $dorm && (int)$dorm['base_adults'] === 1, 'got ' . json_encode($dorm['base_adults'] ?? null));
check('N22: double base_adults = 2', $double && (int)$double['base_adults'] === 2, 'got ' . json_encode($double['base_adults'] ?? null));
check('N7: available count preserved (8)', $dorm && $dorm['available'] === 8, 'got ' . json_encode($dorm['available'] ?? null));

section('2. Date validation (N5 shared rules, N6 strict parsing)');

$cases = [
  ['past check-in',        ['check_in' => d(-5),  'check_out' => d(-3)]],
  ['checkout before checkin', ['check_in' => d(20), 'check_out' => d(19)]],
  ['same-day checkout',    ['check_in' => d(20), 'check_out' => d(20)]],
  ['31 nights > cap',      ['check_in' => d(10), 'check_out' => d(41)]],
  ['rollover 2026-02-30',  ['check_in' => '2027-02-30', 'check_out' => '2027-03-05']],
  ['month 13',             ['check_in' => '2027-13-01', 'check_out' => '2027-13-03']],
  ['not zero-padded',      ['check_in' => '2027-9-5', 'check_out' => '2027-09-07']],
  ['2-digit year',         ['check_in' => '27-09-05', 'check_out' => '2027-09-07']],
  ['slashes',              ['check_in' => '05/09/2027', 'check_out' => '07/09/2027']],
  ['garbage',              ['check_in' => 'next tuesday', 'check_out' => 'whenever']],
];
foreach ($cases as [$label, $over]) {
  reset_limits();
  $r = req('POST', '/api/create-order.php', base_order($over));
  check("create-order rejects $label", $r['code'] === 400, "got {$r['code']} {$r['raw']}");
}
// Same rules must hold on the search endpoint.
$r = req('GET', '/api/availability.php?check_in=2027-9-5&check_out=2027-09-07&adults=1');
check('availability rejects non-padded too (N5 symmetry)', $r['code'] === 400, "got {$r['code']}");
$r = req('GET', '/api/availability.php?check_in=' . d(10) . '&check_out=' . d(41) . '&adults=1');
check('availability rejects 31 nights', $r['code'] === 400, "got {$r['code']}");
// 30 nights exactly must be allowed on both.
$r = req('POST', '/api/create-order.php', base_order(['check_in' => d(10), 'check_out' => d(40)]));
check('30 nights exactly is allowed', $r['code'] === 200, "got {$r['code']} {$r['raw']}");

section('3. Field validation');

foreach ([
  ['bad email',   ['email' => 'not-an-email']],
  ['short phone', ['phone' => '123']],
  ['long phone',  ['phone' => '1234567890123456789']],
  ['no rooms',    ['rooms' => []]],
  ['qty 0',       ['rooms' => [['roomtypeunkid' => 'x', 'ratetypeunkid' => 'y', 'roomrateunkid' => 'z', 'qty' => 0]]]],
  ['missing ids', ['rooms' => [['qty' => 1]]]],
] as [$label, $over]) {
  reset_limits();
  $r = req('POST', '/api/create-order.php', base_order($over));
  check("create-order rejects $label", $r['code'] === 400, "got {$r['code']} {$r['raw']}");
}

section('4. N22 occupancy cap enforced server-side');

$r = req('POST', '/api/create-order.php', base_order([
  'rooms' => [['roomtypeunkid' => '187270000000000104', 'ratetypeunkid' => '1872700000000001041',
               'roomrateunkid' => '1872700000000001042', 'qty' => 1, 'adults' => 2]],
]));
// 409, not 400: the cap comes from eZee's live response, so it is a conflict
// with current inventory/rates rather than a malformed request.
check('2 adults in a 1-base dorm bed is refused', $r['code'] === 409, "got {$r['code']} {$r['raw']}");
check('refusal names the cap and points at WhatsApp',
  stripos($r['raw'], 'covers up to 1 guest') !== false && stripos($r['raw'], 'WhatsApp') !== false, $r['raw']);

reset_limits();
$r = req('POST', '/api/create-order.php', base_order([
  'rooms' => [['roomtypeunkid' => '187270000000000105', 'ratetypeunkid' => '1872700000000001051',
               'roomrateunkid' => '1872700000000001052', 'qty' => 1, 'adults' => 2]],
]));
check('2 adults in a 2-base double is allowed', $r['code'] === 200, "got {$r['code']} {$r['raw']}");
check('double priced at 3000 not 1500 (server-priced)',
  ($r['json']['amount'] ?? 0) === 300000, 'got ' . json_encode($r['json']['amount'] ?? null));

section('5. N8 price drift → 409 price_changed');

$r = req('POST', '/api/create-order.php', base_order(['expected_total' => 100]));
check('wrong expected_total → 409', $r['code'] === 409, "got {$r['code']} {$r['raw']}");
check('409 body flags price_changed', ($r['json']['price_changed'] ?? false) === true, $r['raw']);
check('409 returns both figures, and they are the ones book-now.js reads',
  (float)($r['json']['old_total'] ?? -1) === 100.0 && (float)($r['json']['new_total'] ?? -1) === 900.0, $r['raw']);
reset_limits();
$r = req('POST', '/api/create-order.php', base_order(['expected_total' => 900]));
check('matching expected_total → 200', $r['code'] === 200, "got {$r['code']} {$r['raw']}");

section('6. Happy path — SUCCESSFUL payment');

$r = req('POST', '/api/create-order.php', base_order());
check('create-order 200', $r['code'] === 200, "got {$r['code']} {$r['raw']}");
$order = $r['json'];
check('amount is 90000 paise (900.00)', ($order['amount'] ?? 0) === 90000, json_encode($order['amount'] ?? null));
check('key_id returned to client', !empty($order['key_id']));
check('key SECRET never returned', strpos($r['raw'], SECRET) === false);
$orderId = $order['order_id'] ?? '';
check('pending file written', $orderId && file_exists(PENDING . '/pending/' . $orderId . '.json'));

set_payment($orderId, 'captured', 'pay_SUCCESS001');
$r = req('POST', '/api/verify-payment.php', [
  'razorpay_order_id' => $orderId, 'razorpay_payment_id' => 'pay_SUCCESS001',
  'razorpay_signature' => sign($orderId, 'pay_SUCCESS001'),
]);
check('verify-payment 200', $r['code'] === 200, "got {$r['code']} {$r['raw']}");
check('reservation number returned', !empty($r['json']['reservation_no']), $r['raw']);
$reservationNo = $r['json']['reservation_no'] ?? '';
check('moved pending -> done', !file_exists(PENDING . '/pending/' . $orderId . '.json')
  && file_exists(PENDING . '/done/' . $orderId . '.json'));
$done = json_decode((string)file_get_contents(PENDING . '/done/' . $orderId . '.json'), true);
check('done record keeps the charged total', (float)$done['total'] === 900.0, json_encode($done['total'] ?? null));
check('done record links the razorpay payment', ($done['razorpay_payment_id'] ?? '') === 'pay_SUCCESS001');

section('7. Idempotency — replay and concurrent claim');

$r2 = req('POST', '/api/verify-payment.php', [
  'razorpay_order_id' => $orderId, 'razorpay_payment_id' => 'pay_SUCCESS001',
  'razorpay_signature' => sign($orderId, 'pay_SUCCESS001'),
]);
check('replay returns 200, same reservation (no double booking)',
  $r2['code'] === 200 && ($r2['json']['reservation_no'] ?? '') === $reservationNo, "got {$r2['code']} {$r2['raw']}");
$doneCount = count(glob(PENDING . '/done/*.json'));
check('still exactly one done record for this order', file_exists(PENDING . '/done/' . $orderId . '.json'));

section('8. FAILED signature — the security boundary');

$r = req('POST', '/api/create-order.php', base_order());
check('create-order for forged-signature test', $r['code'] === 200, "got {$r['code']} {$r['raw']}");
$badOrder = $r['json']['order_id'] ?? '';
set_payment($badOrder, 'captured', 'pay_FORGED');
$r = req('POST', '/api/verify-payment.php', [
  'razorpay_order_id' => $badOrder, 'razorpay_payment_id' => 'pay_FORGED',
  'razorpay_signature' => str_repeat('0', 64),
]);
check('forged signature rejected 400', $r['code'] === 400, "got {$r['code']} {$r['raw']}");
check('no reservation created from a forged signature',
  !file_exists(PENDING . '/done/' . $badOrder . '.json'));
check('order stays in pending for the cron to pick up',
  file_exists(PENDING . '/pending/' . $badOrder . '.json'));
$r = req('POST', '/api/verify-payment.php', ['razorpay_order_id' => $badOrder]);
check('missing fields rejected 400', $r['code'] === 400, "got {$r['code']}");

section('9. Reconcile cron — captured, failed, and never-paid');

// (a) captured but client callback never fired -> cron must confirm it
$r = req('POST', '/api/create-order.php', base_order());
$cronOrder = $r['json']['order_id'] ?? '';
set_payment($cronOrder, 'captured', 'pay_CRON001');
touch(PENDING . '/pending/' . $cronOrder . '.json', time() - 600); // older than the 3-min grace
// (b) payment FAILED -> must stay pending, never become a booking
reset_limits();
$r = req('POST', '/api/create-order.php', base_order());
$failOrder = $r['json']['order_id'] ?? '';
set_payment($failOrder, 'failed', 'pay_FAILED001');
touch(PENDING . '/pending/' . $failOrder . '.json', time() - 600);
// (c) never paid, older than 24h -> abandoned
reset_limits();
$r = req('POST', '/api/create-order.php', base_order());
$abandonOrder = $r['json']['order_id'] ?? '';
set_payment($abandonOrder, null);
touch(PENDING . '/pending/' . $abandonOrder . '.json', time() - 90000);

exec('EZEE_MOCK_ROOMLIST=1 php '
  . escapeshellarg(dirname(__DIR__) . '/api/reconcile-pending.php') . ' 2>&1', $out, $rc);
check('reconcile ran cleanly', $rc === 0, implode("\n", $out));
check('(a) captured order confirmed by cron', file_exists(PENDING . '/done/' . $cronOrder . '.json'), 'still pending');
check('(b) FAILED payment did NOT create a booking', !file_exists(PENDING . '/done/' . $failOrder . '.json'));
check('(b) FAILED payment left in pending', file_exists(PENDING . '/pending/' . $failOrder . '.json'));
check('(c) N10b unpaid >24h moved to abandoned/',
  file_exists(PENDING . '/abandoned/' . $abandonOrder . '.json')
  && !file_exists(PENDING . '/pending/' . $abandonOrder . '.json'));
check('(c) abandoned order NOT deleted (still payable at Razorpay)',
  file_exists(PENDING . '/abandoned/' . $abandonOrder . '.json'));

section('10. Cancellation + N9 refund window');

// Ownership check
$r = req('POST', '/api/cancel-booking.php', ['reservation_no' => $reservationNo, 'email' => 'someone@else.com']);
check('wrong email cannot cancel (404, no leak)', $r['code'] === 404, "got {$r['code']} {$r['raw']}");
check('404 message does not confirm the reservation exists',
  stripos($r['raw'], 'not found or email does not match') !== false, $r['raw']);
reset_limits();
$r = req('POST', '/api/cancel-booking.php', ['reservation_no' => $reservationNo]);
check('missing email rejected 400', $r['code'] === 400, "got {$r['code']}");

// Outside 72h (check-in is 20 days away) -> refund due
reset_limits();
$r = req('POST', '/api/cancel-booking.php', ['reservation_no' => $reservationNo, 'email' => 'test@example.com']);
check('correct email cancels 200', $r['code'] === 200, "got {$r['code']} {$r['raw']}");
check('N9: refund_note promises a refund outside 72h',
  stripos($r['json']['refund_note'] ?? '', 'refund will be processed') !== false, $r['raw']);

// Inside 72h -> no refund. Rewrite the done record's check-in to tomorrow.
$doneFile = PENDING . '/done/' . $cronOrder . '.json';
$rec = json_decode((string)file_get_contents($doneFile), true);
$rec['check_in'] = d(1);
file_put_contents($doneFile, json_encode($rec));
reset_limits();
$r = req('POST', '/api/cancel-booking.php',
  ['reservation_no' => $rec['reservation_no'], 'email' => $rec['email']]);
check('N9: inside 72h -> told it is NOT refundable',
  $r['code'] === 200 && stripos($r['json']['refund_note'] ?? '', 'not refundable') !== false, "{$r['code']} {$r['raw']}");

section('11. B5 — upstream detail never reaches the client');

$r = req('POST', '/api/cancel-booking.php', ['reservation_no' => 'NOSUCH999', 'email' => 'test@example.com']);
check('unknown reservation 404', $r['code'] === 404, "got {$r['code']}");
foreach (['MOCKHOTEL', 'mock-api-key', 'mock-auth-code', SECRET, 'ipms247'] as $needle) {
  check("no '$needle' in any client response", stripos($r['raw'], $needle) === false, $r['raw']);
}

section('12. N10a rate limiting');

$codes = [];
for ($i = 0; $i < 8; $i++) {
  $codes[] = req('POST', '/api/cancel-booking.php', ['reservation_no' => 'X' . $i, 'email' => 'a@b.com'])['code'];
}
check('cancel-booking limited to 5/10min (429 appears)', in_array(429, $codes, true), implode(',', $codes));
check('first 5 were not rate-limited', count(array_filter(array_slice($codes, 0, 5), fn($c) => $c === 429)) === 0, implode(',', $codes));

// verify-payment must NEVER be limited: N4 retries call it up to 6 times.
$vCodes = [];
for ($i = 0; $i < 10; $i++) {
  $vCodes[] = req('POST', '/api/verify-payment.php', ['razorpay_order_id' => 'o', 'razorpay_payment_id' => 'p', 'razorpay_signature' => 'bad'])['code'];
}
check('verify-payment is NEVER rate-limited (N4 needs 6 calls)', !in_array(429, $vCodes, true), implode(',', $vCodes));

section('13. Webhook backstop');

$r = req('POST', '/api/create-order.php', base_order());
$whOrder = $r['json']['order_id'] ?? '';
set_payment($whOrder, 'captured', 'pay_WEBHOOK1');
$payload = json_encode(['event' => 'payment.captured', 'payload' => ['payment' => ['entity' => [
  'id' => 'pay_WEBHOOK1', 'order_id' => $whOrder, 'status' => 'captured']]]]);
$ch = curl_init(BASE . '/api/razorpay-webhook.php');
curl_setopt_array($ch, [CURLOPT_RETURNTRANSFER => true, CURLOPT_POST => true, CURLOPT_POSTFIELDS => $payload,
  CURLOPT_HTTPHEADER => ['Content-Type: application/json', 'X-Razorpay-Signature: ' . str_repeat('0', 64)]]);
curl_exec($ch);
$whBad = curl_getinfo($ch, CURLINFO_HTTP_CODE); curl_close($ch);
check('webhook rejects a bad signature', $whBad >= 400, "got $whBad");
check('bad-signature webhook created no booking', !file_exists(PENDING . '/done/' . $whOrder . '.json'));

$ch = curl_init(BASE . '/api/razorpay-webhook.php');
curl_setopt_array($ch, [CURLOPT_RETURNTRANSFER => true, CURLOPT_POST => true, CURLOPT_POSTFIELDS => $payload,
  CURLOPT_HTTPHEADER => ['Content-Type: application/json',
    'X-Razorpay-Signature: ' . hash_hmac('sha256', $payload, 'mockwebhooksecret')]]);
curl_exec($ch);
$whOk = curl_getinfo($ch, CURLINFO_HTTP_CODE); curl_close($ch);
check('webhook with a valid signature confirms the booking',
  $whOk === 200 && file_exists(PENDING . '/done/' . $whOrder . '.json'), "http $whOk");

section('14. CLI-only guard');

$r = req('GET', '/api/reconcile-pending.php');
check('reconcile-pending.php is not HTTP-reachable', $r['code'] === 404, "got {$r['code']}");

section('15. B2 — AddPayment recorded against the reservation');

$log = (string)@file_get_contents(PENDING . '/bookings.log');
check('CONFIRMED lines logged', substr_count($log, 'CONFIRMED order=') >= 3, 'count=' . substr_count($log, 'CONFIRMED order='));
check('no ACTION REQUIRED (AddPayment succeeded)', strpos($log, 'ACTION REQUIRED') === false);
check('CANCELLED lines record payment + amount + refund_due',
  preg_match('/CANCELLED reservation=\S+ email=\S+ payment=\S+ amount=\S+ refund_due=(YES|no)/', $log) === 1);
check('RATELIMIT events logged', strpos($log, 'RATELIMIT bucket=cancel-booking') !== false);

echo "\n" . str_repeat('─', 60) . "\n";
echo "PASS: $pass   FAIL: $fail\n";
if ($failures) { echo "\nFailed:\n"; foreach ($failures as $f) echo "  - $f\n"; }
exit($fail === 0 ? 0 : 1);
