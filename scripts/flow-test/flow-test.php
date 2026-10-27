<?php
/**
 * Drives the REAL api/*.php (a throwaway copy built by run.sh) against a local eZee + Razorpay mock (mock.php).
 * Nothing here can reach live eZee or Razorpay: the copy's secrets.php points at 127.0.0.1.
 * Run it with scripts/flow-test/run.sh (it builds the copy, starts both servers, runs this, stops them).
 */
error_reporting(E_ALL & ~E_DEPRECATED);
const APP = 'http://127.0.0.1:8899';
const MOCK = 'http://127.0.0.1:8900';
const SECRET = 'mocksecret';
const WHSECRET = 'mockwebhooksecret';
$H = getenv('FLOW_TEST_DIR') ?: sys_get_temp_dir() . '/mosaic-flow-test';
$PEND = "$H/ezee-pending-orders";
$pass = 0; $fail = 0; $failures = [];
$only = [];
$sec = 0; $run = true; // every section runs: later ones depend on the state earlier ones leave

function http(string $method, string $url, $body = null, array $headers = ['Content-Type: application/json'], int $timeout = 40): array {
  $ch = curl_init($url);
  curl_setopt_array($ch, [CURLOPT_RETURNTRANSFER => true, CURLOPT_TIMEOUT => $timeout, CURLOPT_CUSTOMREQUEST => $method, CURLOPT_HTTPHEADER => $headers]);
  if ($body !== null) curl_setopt($ch, CURLOPT_POSTFIELDS, is_string($body) ? $body : json_encode($body));
  $raw = curl_exec($ch);
  return ['code' => curl_getinfo($ch, CURLINFO_HTTP_CODE), 'json' => json_decode((string)$raw, true), 'raw' => (string)$raw];
}
$keep_limits = false;
function app(string $m, string $p, $b = null) { global $keep_limits, $PEND; if (!$keep_limits) foreach (glob("$PEND/ratelimit/*.json") ?: [] as $f) @unlink($f); return http($m, APP . $p, $b); }
function ctl(string $p) {
  global $PEND;
  if ($p === '/ctl/reset') { // a mid-section reset restarts reservation numbers, so old order records must go too
    foreach (['pending', 'processing', 'done', 'failed', 'abandoned', 'refunds'] as $dir) foreach (glob("$PEND/$dir/*") ?: [] as $f) @unlink($f);
    @file_put_contents("$PEND/bookings.log", '');
  }
  return http('GET', MOCK . $p)['json'];
}
function check(string $name, bool $ok, string $detail = '') {
  global $pass, $fail, $failures, $run;
  if (!$run) return;
  if ($ok) { $pass++; echo "  PASS  $name\n"; } else { $fail++; $failures[] = $name; echo "  FAIL  $name" . ($detail ? "  -> $detail" : '') . "\n"; }
}
function section(string $title) {
  global $sec, $run, $only, $PEND;
  $sec++;
  echo "\n== $sec. $title ==\n";
  // Clean slate: mock config + state, and the order folders (reservation numbers restart at 1801 after a reset).
  foreach (['ratelimit', 'pending', 'processing', 'done', 'failed', 'abandoned', 'refunds'] as $dir) foreach (glob("$PEND/$dir/*") ?: [] as $f) @unlink($f);
  @file_put_contents("$PEND/bookings.log", '');
  @chmod("$PEND/pending", 0700);
  ctl('/ctl/reset');
}
function d(int $n): string { return date('Y-m-d', strtotime("+$n days")); }
function sig(string $o, string $p): string { return hash_hmac('sha256', "$o|$p", SECRET); }
function ROOM_8() { return ['roomtypeunkid' => '5767700000000000001', 'ratetypeunkid' => '5767700000000000001', 'roomrateunkid' => '5767700000000000001', 'qty' => 1, 'adults' => 1]; }
function ROOM_DOUBLE() { return ['roomtypeunkid' => '5767700000000000007', 'ratetypeunkid' => '5767700000000000001', 'roomrateunkid' => '5767700000000000005', 'qty' => 1, 'adults' => 1]; }
function ROOM_4() { return ['roomtypeunkid' => '5767700000000000006', 'ratetypeunkid' => '5767700000000000001', 'roomrateunkid' => '5767700000000000004', 'qty' => 1, 'adults' => 1]; }
function order_body(array $over = []): array {
  $b = ['check_in' => d(30), 'check_out' => d(31), 'rooms' => [ROOM_8()],
    'guest' => ['title' => 'Mr.', 'first_name' => 'Test', 'last_name' => 'Guest', 'gender' => 'Male'],
    'first_name' => 'Test', 'last_name' => 'Guest', 'email' => 'test@example.com', 'phone' => '9876543210', 'phone_code' => '+91',
    'nationality' => 'India', 'arrival_time' => '12:00 PM – 3:00 PM', 'special_request' => ''];
  foreach ($over as $k => $v) $b[$k] = is_array($v) && isset($b[$k]) && is_array($b[$k]) && $k !== 'rooms' ? array_merge($b[$k], $v) : $v;
  return $b;
}
function new_order(array $over = []): array { return app('POST', '/api/create-order.php', order_body($over)); }
function pay(string $orderId, string $status = 'captured', array $q = []): array { return ctl('/ctl/pay?' . http_build_query(['order' => $orderId, 'status' => $status] + $q)); }
function verify(string $o, string $p, ?string $s = null): array { return app('POST', '/api/verify-payment.php', ['razorpay_order_id' => $o, 'razorpay_payment_id' => $p, 'razorpay_signature' => $s ?? sig($o, $p)]); }
function where_is(string $orderId): string {
  global $PEND;
  foreach (['pending', 'processing', 'done', 'failed', 'abandoned'] as $s) if (glob("$PEND/$s/$orderId*.json")) return $s;
  return 'nowhere';
}
function rec(string $orderId): array { global $PEND; foreach (['pending', 'processing', 'done', 'failed', 'abandoned'] as $s) foreach (glob("$PEND/$s/$orderId*.json") as $f) return json_decode(file_get_contents($f), true); return []; }
function patch_rec(string $orderId, array $set, array $unset = []) { global $PEND; foreach (glob("$PEND/*/$orderId*.json") as $f) { $r = json_decode(file_get_contents($f), true); foreach ($set as $k => $v) $r[$k] = $v; foreach ($unset as $k) unset($r[$k]); file_put_contents($f, json_encode($r)); } }
function log_text(): string { global $PEND; return @file_get_contents("$PEND/bookings.log") ?: ''; }
function calls(string $key, string $val): array { return array_values(array_filter(ctl('/ctl/calls') ?: [], fn ($c) => ($c[$key] ?? null) === $val)); }
function inserts(): array { return calls('ezee', 'InsertBooking'); }
function rzp_orders(): int { return count(calls('rzp', 'create_order')); }
function files_in(string $dir): int { global $PEND; return count(glob("$PEND/$dir/*.json") ?: []); }
function cron(): string { global $H; return (string)shell_exec('php ' . escapeshellarg("$H/site/api/reconcile-pending.php") . ' 2>&1'); }
function age(string $orderId, int $seconds) { global $PEND; foreach (glob("$PEND/pending/$orderId.json") as $f) touch($f, time() - $seconds); }
function webhook(array $payment, ?string $event = 'payment.captured', ?string $badSig = null): array {
  $raw = json_encode(['event' => $event, 'payload' => ['payment' => ['entity' => $payment]]]);
  return http('POST', APP . '/api/razorpay-webhook.php', $raw, ['Content-Type: application/json', 'X-Razorpay-Signature: ' . ($badSig ?? hash_hmac('sha256', $raw, WHSECRET))]);
}
/** Full happy path to a confirmed booking; returns [orderId, paymentId, verifyResponse]. */
function confirmed(array $over = []): array {
  $o = new_order($over)['json']['order_id']; $p = pay($o)['id']; return [$o, $p, verify($o, $p)];
}

// ============================================================================
section('Search: availability');
$r = app('GET', '/api/availability.php?check_in=' . d(30) . '&check_out=' . d(31) . '&adults=1&rooms=1');
check('200 with three room options', $r['code'] === 200 && count($r['json']['rooms'] ?? []) === 3, $r['raw']);
$by = []; foreach ($r['json']['rooms'] ?? [] as $x) $by[$x['name']] = $x;
check('8-bed dorm 1 night = 699 + 5% = 733.95', ($by['8 - Bed Mixed Dorm']['total'] ?? 0) === 733.95);
check('available counts come through', ($by['4 - Bed Mixed Dorm']['available'] ?? 0) === 5);
$r5 = app('GET', '/api/availability.php?check_in=' . d(40) . '&check_out=' . d(45) . '&adults=1&rooms=1');
$dbl = array_values(array_filter($r5['json']['rooms'] ?? [], fn ($x) => $x['name'] === 'Double Room'))[0] ?? [];
check('Double Room 5 nights, rate changes on last night = 12490.80 (matches the 26 Oct order)', ($dbl['total'] ?? 0) === 12490.8, json_encode($dbl));
check('past date rejected', app('GET', '/api/availability.php?check_in=2020-01-01&check_out=2020-01-02')['code'] === 400);
check('check-out before check-in rejected', app('GET', '/api/availability.php?check_in=' . d(5) . '&check_out=' . d(3))['code'] === 400);
check('stay over 30 nights rejected', app('GET', '/api/availability.php?check_in=' . d(5) . '&check_out=' . d(40))['code'] === 400);
check('array-typed check_in does not 500', app('GET', '/api/availability.php?check_in[]=1&check_out=' . d(3))['code'] === 400);
check('rooms=9 rejected', app('GET', '/api/availability.php?check_in=' . d(5) . '&check_out=' . d(6) . '&rooms=9')['code'] === 400);
check('wrong method rejected', app('POST', '/api/availability.php')['code'] === 405);
ctl('/ctl/set?roomlist_down=1');
check('eZee down -> 502, no internal detail leaked', ($x = app('GET', '/api/availability.php?check_in=' . d(5) . '&check_out=' . d(6)))['code'] === 502 && !str_contains($x['raw'], '503'), $x['raw']);
ctl('/ctl/reset'); ctl('/ctl/set?ezee_429=1');
check('eZee rate limit -> 429 to the guest', app('GET', '/api/availability.php?check_in=' . d(5) . '&check_out=' . d(6))['code'] === 429);

// ============================================================================
section('Order creation: happy path and what is stored');
$before = rzp_orders();
$r = new_order();
check('200 with order_id, amount, key_id', $r['code'] === 200 && !empty($r['json']['order_id']) && ($r['json']['amount'] ?? 0) === 73395 && ($r['json']['key_id'] ?? '') === 'rzp_test_mock', $r['raw']);
$oid = $r['json']['order_id'] ?? 'x';
check('exactly one Razorpay order created', rzp_orders() === $before + 1);
check('pending record written', where_is($oid) === 'pending');
$rc = rec($oid);
check('record holds eZee ids, rates and English guest values', ($rc['room_units'][0]['gender'] ?? '') === 'Male' && ($rc['room_units'][0]['title'] ?? '') === 'Mr.' && ($rc['room_units'][0]['baserate'] ?? 0) == 699 && $rc['check_in'] === d(30), json_encode($rc['room_units'][0] ?? []));
check('special request carries the arrival time', str_contains($rc['special_request'] ?? '', 'Estimated arrival: 12:00 PM – 3:00 PM'));
check('price is taken from eZee, never the client (client "total" ignored)', ($x = new_order(['total' => 1, 'amount' => 100]))['json']['amount'] === 73395);
$tamper = new_order(['expected_total' => 100]);
check('stale/tampered expected_total -> 409 price_changed with new total', $tamper['code'] === 409 && ($tamper['json']['price_changed'] ?? false) && $tamper['json']['new_total'] === 733.95, $tamper['raw']);
check('correct expected_total passes', new_order(['expected_total' => 733.95])['code'] === 200);

// ============================================================================
section('Order creation: values from a TRANSLATED page are refused BEFORE payment (the 27 Sep bug)');
$before = rzp_orders(); $files = files_in('pending');
foreach ([
  'French gender (Mâle)' => ['guest' => ['gender' => 'Mâle']],
  'French title (M.)' => ['guest' => ['title' => 'M.']],
  'French arrival (12h00 – 15h00)' => ['arrival_time' => '12h00 – 15h00'],
  'translated nationality (Allemagne)' => ['nationality' => 'Allemagne'],
  'lower-case gender' => ['guest' => ['gender' => 'male']],
  'Hindi gender' => ['guest' => ['gender' => 'पुरुष']],
  'title with trailing space' => ['guest' => ['title' => 'Mr. ']],
] as $name => $over) {
  $r = new_order($over);
  check("$name -> 400 with a clear message", $r['code'] === 400 && str_contains($r['json']['error'] ?? '', 'valid'), $r['raw']);
}
check('none of them created a Razorpay order', rzp_orders() === $before);
check('none of them wrote a pending record', files_in('pending') === $files);
foreach (['guest' => ['title' => '', 'gender' => ''], 'nationality' => '', 'arrival_time' => ''] as $k => $v) {
  check("optional field empty is still accepted: $k", new_order([$k => $v])['code'] === 200);
}
check('French guest with the form\'s real (English) values works: France', new_order(['nationality' => 'France', 'guest' => ['title' => 'Mr.', 'gender' => 'Male']])['code'] === 200);
check('every country on the form is accepted', (function () { $bad = 0; foreach (['India', 'UAE', 'United States', 'New Zealand', 'Hong Kong', 'South Korea'] as $c) if (new_order(['nationality' => $c])['code'] !== 200) $bad++; return $bad === 0; })());

// ============================================================================
section('Order creation: input validation');
foreach ([
  'missing email' => ['email' => ''],
  'invalid email' => ['email' => 'not-an-email'],
  'short phone' => ['phone' => '123'],
  'empty first name' => ['guest' => ['first_name' => ''], 'first_name' => ''],
  'past check-in' => ['check_in' => '2020-01-01', 'check_out' => '2020-01-02'],
  'impossible date 2026-02-30' => ['check_in' => '2026-02-30', 'check_out' => '2026-03-02'],
  'stay over 30 nights' => ['check_in' => d(5), 'check_out' => d(45)],
  'no rooms' => ['rooms' => []],
  'qty 0' => ['rooms' => [array_merge(ROOM_8(), ['qty' => 0])]],
  'array first_name' => ['first_name' => ['x']],
  'array guest.title' => ['guest' => ['title' => ['Mr.']]],
  'more than 8 rooms' => ['rooms' => [array_merge(ROOM_8(), ['qty' => 9])]],
] as $name => $over) { $r = new_order($over); check("$name -> 400", $r['code'] === 400, $r['code'] . ' ' . $r['raw']); }
check('invalid JSON body -> 400', http('POST', APP . '/api/create-order.php', '{bad')['code'] === 400);
check('wrong method -> 405', app('GET', '/api/create-order.php')['code'] === 405);
$r = new_order(['rooms' => [array_merge(ROOM_8(), ['roomrateunkid' => '999'])]]);
check('unknown room id -> 409, not 500', $r['code'] === 409, $r['raw']);
$r = new_order(['rooms' => [array_merge(ROOM_4(), ['qty' => 6])]]);
check('more beds than available (6 > 5) -> 409', $r['code'] === 409, $r['raw']);
$r = new_order(['rooms' => [array_merge(ROOM_8(), ['adults' => 2])]]);
check('more adults than the rate covers -> 409 (we would undercharge)', $r['code'] === 409, $r['raw']);
$r = new_order(['rooms' => [array_merge(ROOM_4(), ['qty' => 2]), array_merge(ROOM_8(), ['qty' => 1])]]);
check('multi-line cart: 2 x 4-bed + 1 x 8-bed = 2*523.95 + 733.95', $r['code'] === 200 && $r['json']['amount'] === 178185, $r['raw']);
check('3 room units stored', count(rec($r['json']['order_id'] ?? 'x')['room_units'] ?? []) === 3);
ctl('/ctl/set?rzp_down=1'); $b = rzp_orders(); $f = files_in('pending');
$r = new_order(); check('Razorpay down -> 502 and NO pending record left behind', $r['code'] === 502 && files_in('pending') === $f, $r['raw']);
ctl('/ctl/reset'); ctl('/ctl/set?roomlist_down=1');
check('eZee down at checkout -> 502, no Razorpay order', new_order()['code'] === 502 && rzp_orders() === 0);

// ============================================================================
section('Pay + verify: the browser path creates the eZee booking');
$o = new_order()['json']['order_id']; $p = pay($o)['id'];
check('bad signature -> 400, nothing booked', verify($o, $p, 'deadbeef')['code'] === 400 && count(inserts()) === 0 && where_is($o) === 'pending');
$v = verify($o, $p);
check('good signature -> 200 success with reservation number', $v['code'] === 200 && ($v['json']['success'] ?? false) && !empty($v['json']['reservation_no']), $v['raw']);
check('record moved to done/ with reservation + payment ids', where_is($o) === 'done' && (rec($o)['razorpay_payment_id'] ?? '') === $p && (rec($o)['reservation_no'] ?? '') === ($v['json']['reservation_no'] ?? 'x'));
$ins = inserts()[0]['data'] ?? [];
$r1 = $ins['Room_Details']['Room_1'] ?? [];
check('InsertBooking sent via POST (the WAF rejects long GET query strings)', (inserts()[0]['via'] ?? '') === 'POST');
check('InsertBooking carries dates, guest, English values, Razorpay payment mode', ($ins['check_in_date'] ?? '') === d(30) && ($ins['check_out_date'] ?? '') === d(31) && ($r1['Gender'] ?? '') === 'Male' && ($r1['Title'] ?? '') === 'Mr.' && ($ins['Email_Address'] ?? '') === 'test@example.com' && ($ins['Booking_Payment_Mode'] ?? '') === 'Online Payment (Razorpay)' && ($ins['Country'] ?? '') === 'India', json_encode($ins));
$ap = calls('ezee', 'AddPayment')[0]['req'] ?? [];
check('AddPayment posts the exact total against the reservation', ($ap['Payment'] ?? '') === '733.95' && ($ap['BookingId'] ?? '') === ($v['json']['reservation_no'] ?? 'x'), json_encode($ap));
$v2 = verify($o, $p);
check('verify again (guest double-clicks / reloads) -> same reservation, NO second booking', $v2['code'] === 200 && $v2['json']['reservation_no'] === $v['json']['reservation_no'] && count(inserts()) === 1, $v2['raw']);
check('log has CONFIRMED line', str_contains(log_text(), "CONFIRMED order=$o"));
check('verify-payment for an unknown order -> 409, nothing booked', verify('order_UNKNOWN12345', 'pay_UNKNOWN12345')['code'] === 409);
check('malformed ids rejected (path traversal attempt)', verify('order_../../etc/passwd', 'pay_x', sig('order_../../etc/passwd', 'pay_x'))['code'] === 409);
check('missing fields -> 400', app('POST', '/api/verify-payment.php', ['razorpay_order_id' => 'x'])['code'] === 400);
// AddPayment failing must not fail the booking
ctl('/ctl/set?addpayment_mode=fail');
[$o2, $p2, $v3] = confirmed();
check('AddPayment failing twice still confirms the booking, and alerts', $v3['code'] === 200 && where_is($o2) === 'done' && str_contains(log_text(), 'ACTION REQUIRED AddPayment failed twice'), $v3['raw']);

// ============================================================================
section('Multi-night stays: eZee needs one rate per night (the cause of the 27 Sep and 26 Oct failures)');
[$o, $p, $v] = confirmed(['check_in' => d(40), 'check_out' => d(45), 'rooms' => [ROOM_DOUBLE()], 'guest' => ['title' => 'Ms.', 'gender' => 'Female'], 'nationality' => '']);
check('Double Room, 5 nights, rate changing on the last night, empty nationality (the 26 Oct order) now confirms', $v['code'] === 200 && rec($o)['amount'] === 1249080, $v['raw']);
$r1 = (inserts()[0]['data']['Room_Details']['Room_1'] ?? []);
check('baserate sent to eZee is one value per night: 2099,2099,2099,2099,3500', ($r1['baserate'] ?? '') === '2099,2099,2099,2099,3500', json_encode($r1));
check('extradultrate and extrachildrate are per-night lists too (eZee refuses the booking otherwise)', ($r1['extradultrate'] ?? '') === '300,300,300,300,300' || ($r1['extradultrate'] ?? '') === '500,500,500,500,500', json_encode($r1));
ctl('/ctl/reset');
[$o, $p, $v] = confirmed(['check_in' => d(40), 'check_out' => d(42), 'rooms' => [ROOM_8()]]);
check('8-bed dorm, 2 nights, 699 then 899 (the 27 Sep order) confirms; list is 699,899', $v['code'] === 200 && (inserts()[0]['data']['Room_Details']['Room_1']['baserate'] ?? '') === '699,899', $v['raw']);
ctl('/ctl/reset');
[$o, $p, $v] = confirmed(['check_in' => d(40), 'check_out' => d(41), 'rooms' => [ROOM_8()]]);
check('1 night still sends a single value (no trailing comma)', $v['code'] === 200 && (inserts()[0]['data']['Room_Details']['Room_1']['baserate'] ?? '') === '699', $v['raw']);
ctl('/ctl/reset');
[$o, $p, $v] = confirmed(['check_in' => d(40), 'check_out' => d(70), 'rooms' => [ROOM_4()]]);
check('30 nights confirms with 30 rates', $v['code'] === 200 && count(explode(',', inserts()[0]['data']['Room_Details']['Room_1']['baserate'] ?? '')) === 30, $v['raw']);
ctl('/ctl/reset');
[$o, $p, $v] = confirmed(['check_in' => d(40), 'check_out' => d(43), 'rooms' => [array_merge(ROOM_4(), ['qty' => 2]), ROOM_8()]]);
$rd = inserts()[0]['data']['Room_Details'] ?? [];
check('3 rooms, 3 nights in one booking: every room carries 3 rates', $v['code'] === 200 && count($rd) === 3 && count(array_filter($rd, fn ($r) => count(explode(',', $r['baserate'])) === 3 && count(explode(',', $r['extradultrate'])) === 3 && count(explode(',', $r['extrachildrate'])) === 3)) === 3, json_encode(array_column($rd, 'baserate')));
ctl('/ctl/reset');
$o = new_order(['check_in' => d(40), 'check_out' => d(42), 'rooms' => [ROOM_8()]])['json']['order_id']; $p = pay($o)['id'];
patch_rec($o, ['room_units' => array_map(fn ($u) => array_merge($u, ['baserate' => 699, 'extradultrate' => 300, 'extrachildrate' => 0]), rec($o)['room_units'])]);
$v = verify($o, $p);
check('control: the OLD single-number payload is refused by the mock exactly as live eZee refused it (so the checks above mean something)', $v['code'] === 502 && where_is($o) === 'failed', $v['raw']);

// ============================================================================
section('eZee rejects or fails InsertBooking after payment');
ctl('/ctl/set?insert_mode=invaliddata');
$o = new_order()['json']['order_id']; $p = pay($o)['id'];
$v = verify($o, $p);
check('coded rejection (InvalidData): parked at ONCE, one eZee call, guest told "our team will follow up"', $v['code'] === 502 && where_is($o) === 'failed' && count(inserts()) === 1, $v['raw'] . ' ' . where_is($o));
check('ALERT is precise: PAID but booking NOT created, ambiguous=no, real eZee message', preg_match('/ALERT PAID but booking NOT created order=' . $o . '.*ambiguous=no.*InvalidData - Please check data passed\\./', log_text()) === 1);
check('the failed record keeps the eZee reply for diagnosis', str_contains(rec($o)['last_failure'] ?? '', 'InvalidData'));
check('webhook redelivery for a parked order is acknowledged (200) and not re-attempted', webhook(['id' => $p, 'order_id' => $o, 'status' => 'captured', 'amount' => 73395, 'currency' => 'INR'])['code'] === 200 && count(inserts()) === 1);
ctl('/ctl/reset'); ctl('/ctl/set?insert_mode=busy');
$o = new_order()['json']['order_id']; $p = pay($o)['id'];
$v = verify($o, $p);
check('transient rejection ("server busy"): attempt 1 -> 502 pending, order back in pending/ with attempts=1', $v['code'] === 502 && where_is($o) === 'pending' && (rec($o)['attempts'] ?? 0) === 1, $v['raw']);
check('log shows RETRY with eZee\'s real message', str_contains(log_text(), 'RETRY InsertBooking') && str_contains(log_text(), 'Server busy'));
verify($o, $p);
check('immediate redelivery inside the 120 s gap does not call eZee again or count as an attempt', count(inserts()) === 1 && (rec($o)['attempts'] ?? 0) === 1);
patch_rec($o, ['last_attempt_at' => time() - 200]); verify($o, $p);
check('attempt 2 after the gap', count(inserts()) === 2 && (rec($o)['attempts'] ?? 0) === 2 && where_is($o) === 'pending');
patch_rec($o, ['last_attempt_at' => time() - 200]); $v = verify($o, $p);
check('attempt 3 -> parked in failed/ with ambiguous=no', where_is($o) === 'failed' && $v['code'] === 502 && count(inserts()) === 3 && preg_match('/PAID but booking NOT created order=' . $o . '.*ambiguous=no/', log_text()) === 1, $v['raw']);
// manual recovery: owner fixes the cause and moves the file back
ctl('/ctl/set?insert_mode=ok');
global $PEND; rename("$PEND/failed/$o.json", "$PEND/pending/$o.json");
$v = verify($o, $p);
check('after the cause is fixed, moving failed/ -> pending/ by hand books it immediately', $v['code'] === 200 && where_is($o) === 'done', $v['raw']);

foreach ([
  'http500' => 'eZee 500 (gateway down)',
  'garbage' => 'HTML from the WAF instead of JSON',
  'noresno' => 'well-formed reply with no ReservationNo',
] as $mode => $label) {
  ctl("/ctl/reset"); ctl("/ctl/set?insert_mode=$mode");
  $o = new_order()['json']['order_id']; $p = pay($o)['id']; $v = verify($o, $p);
  check("$label -> parked at once (ambiguous: a reservation may exist), never retried", where_is($o) === 'failed' && count(inserts()) === 1 && preg_match('/ambiguous=yes/', log_text()) === 1, $v['raw'] . ' ' . where_is($o));
}
ctl('/ctl/reset'); ctl('/ctl/set?insert_mode=timeout');
$o = new_order()['json']['order_id']; $p = pay($o)['id']; $t = microtime(true); $v = verify($o, $p);
check('eZee timeout (15 s) -> parked as ambiguous, no retry', where_is($o) === 'failed' && preg_match('/ambiguous=yes/', log_text()) === 1 && microtime(true) - $t < 40, sprintf('%.1fs %s', microtime(true) - $t, where_is($o)));
ctl('/ctl/reset'); ctl('/ctl/set?insert_mode=pastdate');
// past-arrival shape (the 27 Aug order): eZee says ArrivalDate is Past date
$o = new_order()['json']['order_id']; $p = pay($o)['id'];
patch_rec($o, ['check_in' => d(-2), 'check_out' => d(-1)]); ctl('/ctl/set?insert_mode=ok');
verify($o, $p);
check('arrival already in the past (27 Aug order) -> parked at once with the real reason', where_is($o) === 'failed' && count(inserts()) === 1 && str_contains(log_text(), 'ArrivalDate is Past date.'), where_is($o));

// ============================================================================
section('Webhook path (guest closed the tab)');
$o = new_order()['json']['order_id']; $pay = pay($o);
check('bad webhook signature -> 400, nothing booked', webhook($pay, 'payment.captured', 'deadbeef')['code'] === 400 && where_is($o) === 'pending');
check('other events are acknowledged and ignored', webhook($pay, 'payment.failed')['code'] === 200 && where_is($o) === 'pending');
$w = webhook($pay);
check('payment.captured books it', $w['code'] === 200 && where_is($o) === 'done' && count(inserts()) === 1, $w['raw']);
check('redelivered webhook is idempotent (no second booking)', webhook($pay)['code'] === 200 && count(inserts()) === 1);
check('then the browser callback arriving late is also idempotent', verify($o, $pay['id'])['code'] === 200 && count(inserts()) === 1);
$o = new_order()['json']['order_id']; $pay = pay($o, 'captured', ['amount' => 100]);
$w = webhook($pay);
check('amount mismatch (paid 1.00 for a 733.95 order) -> NOT booked, alerted', where_is($o) === 'pending' && str_contains(log_text(), 'payment does not match order'), $w['raw']);
$o = new_order()['json']['order_id']; $pay = pay($o, 'authorized');
webhook($pay); check('payment not yet captured -> NOT booked', where_is($o) === 'pending');
check('webhook for an unknown order is acknowledged, not booked', webhook(['id' => 'pay_UNKNOWNX1234', 'order_id' => 'order_UNKNOWNX1234', 'status' => 'captured', 'amount' => 1, 'currency' => 'INR'])['code'] === 200);
check('webhook with an empty JSON object is acknowledged and ignored', http('POST', APP . '/api/razorpay-webhook.php', '{}', ['X-Razorpay-Signature: ' . hash_hmac('sha256', '{}', WHSECRET)])['code'] === 200);
ctl('/ctl/set?insert_mode=busy');
$o = new_order()['json']['order_id']; $pay = pay($o); $w = webhook($pay);
check('transient eZee trouble during a webhook -> 500 so Razorpay redelivers', $w['code'] === 500 && where_is($o) === 'pending', (string)$w['code']);
ctl('/ctl/set?insert_mode=invaliddata');
$o = new_order()['json']['order_id']; $pay = pay($o); $w = webhook($pay);
check('a coded rejection during a webhook is parked and acknowledged (200): redelivery cannot help', $w['code'] === 200 && where_is($o) === 'failed', (string)$w['code']);

// ============================================================================
section('Cron sweep (reconcile-pending.php): neither browser nor webhook arrived');
$o = new_order()['json']['order_id']; pay($o);
cron(); check('paid but still fresh (< 3 min): left alone', where_is($o) === 'pending');
age($o, 600); $out = cron();
check('paid and 10 min old: booked by the cron', where_is($o) === 'done' && str_contains(log_text(), "RECONCILE order=$o") && count(inserts()) === 1, $out);
$u = new_order()['json']['order_id']; age($u, 600); cron();
check('unpaid order older than 3 min is left pending (guest may still be paying)', where_is($u) === 'pending');
age($u, 2 * 86400); cron();
check('unpaid for over 24 h -> moved to abandoned/ (never deleted)', where_is($u) === 'abandoned' && str_contains(log_text(), "ABANDONED order=$u"));
$late = pay($u); $v = verify($u, $late['id']);
check('a payment arriving for an abandoned order still books it', $v['code'] === 200 && where_is($u) === 'done', $v['raw']);
$o = new_order()['json']['order_id']; pay($o); age($o, 600); ctl('/ctl/set?rzp_429=1'); cron();
check('Razorpay "too many requests" is logged and the order stays for the next tick', where_is($o) === 'pending' && str_contains(log_text(), "RECONCILE fetch failed order=$o"));
ctl('/ctl/set?rzp_429=0'); ctl('/ctl/set?rzp_429='); cron(); check('...and is booked once Razorpay answers', where_is($o) === 'done');
// stuck in processing: PHP died mid-claim
@mkdir("$PEND/processing", 0700, true);
$stuck = 'order_STUCKXXXXXX1'; file_put_contents("$PEND/processing/$stuck@" . (time() - 1000) . '.json', json_encode(['order_id' => $stuck]));
cron();
check('claim stuck in processing/ for >10 min -> parked in failed/ with an alert (not re-queued: could double-book)', is_file("$PEND/failed/$stuck.json") && str_contains(log_text(), "order stuck in processing order=$stuck"));
$fresh = 'order_FRESHXXXXXX2'; file_put_contents("$PEND/processing/$fresh@" . time() . '.json', '{}'); cron();
check('a live claim (seconds old) is never touched', glob("$PEND/processing/$fresh@*.json") !== []);
check('reconcile-pending.php is CLI-only: over HTTP it 404s', app('GET', '/api/reconcile-pending.php')['code'] === 404);

// ============================================================================
section('Concurrency: browser callback and webhook at the same instant');
$o = new_order()['json']['order_id']; $pay = pay($o); $p = $pay['id'];
$mh = curl_multi_init(); $hs = [];
$wraw = json_encode(['event' => 'payment.captured', 'payload' => ['payment' => ['entity' => $pay]]]);
for ($i = 0; $i < 6; $i++) {
  $ch = curl_init($i % 2 ? APP . '/api/verify-payment.php' : APP . '/api/razorpay-webhook.php');
  curl_setopt_array($ch, [CURLOPT_RETURNTRANSFER => true, CURLOPT_POST => true, CURLOPT_TIMEOUT => 40,
    CURLOPT_POSTFIELDS => $i % 2 ? json_encode(['razorpay_order_id' => $o, 'razorpay_payment_id' => $p, 'razorpay_signature' => sig($o, $p)]) : $wraw,
    CURLOPT_HTTPHEADER => $i % 2 ? ['Content-Type: application/json'] : ['Content-Type: application/json', 'X-Razorpay-Signature: ' . hash_hmac('sha256', $wraw, WHSECRET)]]);
  curl_multi_add_handle($mh, $ch); $hs[] = $ch;
}
do { curl_multi_exec($mh, $run2); curl_multi_select($mh, 0.2); } while ($run2 > 0);
check('six simultaneous confirmations -> exactly ONE eZee reservation', count(inserts()) === 1 && where_is($o) === 'done', 'inserts=' . count(inserts()));
check('only one booking exists in eZee', count(ctl('/ctl/bookings')) === 1);

// ============================================================================
section('Cancellation and refund');
[$o, $p, $v] = confirmed(['check_in' => d(30), 'check_out' => d(31)]); $no = $v['json']['reservation_no'];
check('wrong email -> 404 (reservation not leaked)', app('POST', '/api/cancel-booking.php', ['reservation_no' => $no, 'email' => 'other@example.com'])['code'] === 404);
check('unknown reservation -> 404', app('POST', '/api/cancel-booking.php', ['reservation_no' => '99999', 'email' => 'test@example.com'])['code'] === 404);
check('injection-shaped reservation number -> 404', app('POST', '/api/cancel-booking.php', ['reservation_no' => '1; DROP', 'email' => 'test@example.com'])['code'] === 404);
$c = app('POST', '/api/cancel-booking.php', ['reservation_no' => $no, 'email' => 'TEST@example.com ']);
check('right email (case/space tolerant), 30 days out -> cancelled and refund initiated', $c['code'] === 200 && str_contains($c['json']['refund_note'] ?? '', 'initiated'), $c['raw']);
$rf = calls('rzp', 'refund');
check('exactly one refund call, for the right payment, keyed by reservation (idempotent)', count($rf) === 1 && $rf[0]['payment'] === $p && $rf[0]['key'] === "mosaic-cancel-$no" && !isset($rf[0]['body']['amount']), 'p=' . $p . ' ' . json_encode($rf));
check('refunds/ record says refunded', (json_decode(@file_get_contents("$PEND/refunds/$no.json"), true)['status'] ?? '') === 'refunded');
check('cancel again -> 409 already cancelled, no second refund', app('POST', '/api/cancel-booking.php', ['reservation_no' => $no, 'email' => 'test@example.com'])['code'] === 409 && count(calls('rzp', 'refund')) === 1);
ctl('/ctl/reset');
[$o, $p, $v] = confirmed(['check_in' => d(1), 'check_out' => d(2)]); $no = $v['json']['reservation_no'];
$c = app('POST', '/api/cancel-booking.php', ['reservation_no' => $no, 'email' => 'test@example.com']);
check('inside 72 h: cancelled, told it is not refundable, Razorpay never called', $c['code'] === 200 && str_contains($c['json']['refund_note'] ?? '', 'not refundable') && count(calls('rzp', 'refund')) === 0, $c['raw']);
ctl('/ctl/reset'); ctl('/ctl/set?refund_mode=fail');
[$o, $p, $v] = confirmed(); $no = $v['json']['reservation_no'];
$c = app('POST', '/api/cancel-booking.php', ['reservation_no' => $no, 'email' => 'test@example.com']);
check('Razorpay refuses the refund -> still cancelled, guest not told it was sent, staff alerted', $c['code'] === 200 && !str_contains($c['json']['refund_note'] ?? '', 'initiated') && str_contains(log_text(), 'REFUND to review after cancellation'), $c['raw']);
ctl('/ctl/reset'); [$o, $p, $v] = confirmed(); ctl('/ctl/set?cancel_mode=fail');
$c = app('POST', '/api/cancel-booking.php', ['reservation_no' => $v['json']['reservation_no'], 'email' => 'test@example.com']);
check('eZee cannot cancel -> 502 with WhatsApp fallback, no refund', $c['code'] === 502 && count(calls('rzp', 'refund')) === 0, $c['raw']);
ctl('/ctl/reset'); [$o, $p, $v] = confirmed(); $no = $v['json']['reservation_no'];
$keep_limits = true;
for ($i = 0; $i < 6; $i++) $last = app('POST', '/api/cancel-booking.php', ['reservation_no' => $no, 'email' => "x$i@example.com"]);
check('guessing: more than 5 tries in 10 minutes -> 429', $last['code'] === 429, (string)$last['code']);
$keep_limits = false;

// ============================================================================
section('Rate limiting and abuse');
ctl('/ctl/reset'); $keep_limits = true; foreach (glob("$PEND/ratelimit/*.json") as $f) @unlink($f); $codes = [];
for ($i = 0; $i < 12; $i++) $codes[] = new_order()['code'];
check('create-order: 10 per 10 minutes per client, then 429', $codes[9] === 200 && $codes[10] === 429, implode(',', $codes));
foreach (glob("$PEND/ratelimit/*.json") as $f) @unlink($f);
$c = [];
for ($i = 0; $i < 62; $i++) $c[] = app('GET', '/api/availability.php?check_in=' . d(5) . '&check_out=' . d(6))['code'];
check('availability: 60 per 10 minutes, then 429', $c[59] === 200 && $c[60] === 429);
$keep_limits = false;
check('pending dir is not reachable over HTTP', !str_contains(app('GET', '/ezee-pending-orders/bookings.log')['raw'], 'CONFIRMED'));

// ============================================================================
section('Guest names and free text: what can reach eZee after payment');
$b = fn (array $o) => new_order($o);
check('whitespace-only first name -> 400', ($x = $b(['guest' => ['first_name' => '   ']]))['code'] === 400, $x['raw']);
check('empty last name is accepted (live eZee books it; the form still asks for one)', ($x = $b(['guest' => ['last_name' => ''], 'last_name' => '']))['code'] === 200, $x['raw']);
check('whitespace-only last name is accepted and stored empty', ($x = $b(['guest' => ['last_name' => '  ']]))['code'] === 200 && (rec($x['json']['order_id'])['room_units'][0]['last_name'] ?? 'x') === '', $x['raw']);
check('over-long name (1000 chars) -> 400', ($x = $b(['guest' => ['first_name' => str_repeat('a', 1000)]]))['code'] === 400, $x['raw']);
check('over-long special request (20 000 chars) -> 400', ($x = $b(['special_request' => str_repeat('x', 20000)]))['code'] === 400, $x['raw']);
check('over-long email -> 400', ($x = $b(['email' => str_repeat('a', 300) . '@example.com']))['code'] === 400, $x['raw']);
[$o, $p, $v] = confirmed(['guest' => ['first_name' => '  Rahul ', 'last_name' => " O'Brien "]]);
$r1 = inserts()[0]['data']['Room_Details']['Room_1'] ?? [];
check('names are trimmed before they reach eZee', ($r1['First_Name'] ?? '') === 'Rahul' && ($r1['Last_Name'] ?? '') === "O'Brien", json_encode([$r1['First_Name'] ?? null, $r1['Last_Name'] ?? null]));
ctl('/ctl/reset'); [$o, $p, $v] = confirmed(['guest' => ['first_name' => 'राहुल', 'last_name' => 'शर्मा ✈'], 'special_request' => "line1\nline2 \"quoted\" & <b>"]);
$r1 = inserts()[0]['data']['Room_Details']['Room_1'] ?? [];
check('Hindi/emoji names and quotes survive to eZee intact', $v['code'] === 200 && ($r1['First_Name'] ?? '') === 'राहुल' && str_contains($r1['SpecialRequest'] ?? '', '"quoted" & <b>'), json_encode($r1));
check('email with + and capitals accepted', new_order(['email' => 'Guest+Test@Example.COM'])['code'] === 200);
check('phone with spaces/dashes accepted', new_order(['phone' => '98765-43210', 'phone_code' => '+91'])['code'] === 200);
check('phone with 20 digits -> 400', new_order(['phone' => str_repeat('9', 20)])['code'] === 400);
check('check-in TODAY is bookable (same-day arrivals are normal for a hostel)', ($x = new_order(['check_in' => d(0), 'check_out' => d(1)]))['code'] === 200, $x['raw']);
check('1-night stay at the 30-night limit boundary: exactly 30 nights ok', ($x = new_order(['check_in' => d(5), 'check_out' => d(35)]))['code'] === 200, $x['raw']);
check('31 nights -> 400', new_order(['check_in' => d(5), 'check_out' => d(36)])['code'] === 400);

// ============================================================================
section('Payment oddities');
$o = new_order()['json']['order_id']; $bad = pay($o, 'failed'); $good = pay($o, 'captured');
check('webhook for a FAILED payment is ignored', webhook($bad, 'payment.failed')['code'] === 200 && where_is($o) === 'pending');
age($o, 600); cron();
check('guest failed once then paid: cron books with the CAPTURED payment, once', where_is($o) === 'done' && rec($o)['razorpay_payment_id'] === $good['id'] && count(inserts()) === 1);
$o = new_order()['json']['order_id']; pay($o, 'failed'); age($o, 600); cron();
check('only failed payments: nothing booked, order waits', where_is($o) === 'pending' && count(inserts()) === 1);
$o = new_order()['json']['order_id']; $usd = pay($o, 'captured', ['currency' => 'USD']); webhook($usd);
check('captured in the wrong currency -> NOT booked, alerted', where_is($o) === 'pending' && str_contains(log_text(), 'payment does not match order'));
$o = new_order()['json']['order_id']; $p = pay($o)['id'];
check('signature for a different payment id than the one sent -> 400', verify($o, $p, sig($o, 'pay_SOMEONEELSE1'))['code'] === 400 && where_is($o) === 'pending');

// ============================================================================
section('Webhook behaviour once an order is parked for a human (Razorpay disables endpoints that keep failing)');
ctl('/ctl/set?insert_mode=http500');
$o = new_order()['json']['order_id']; $pay = pay($o); $w1 = webhook($pay);
check('first delivery while eZee is broken -> parked as failed/', where_is($o) === 'failed', $w1['raw']);
$w2 = webhook($pay);
check('REDELIVERY for an order already parked in failed/ must be acknowledged (200); a 500 here repeats for 24 h and gets the webhook switched off', $w2['code'] === 200, 'got ' . $w2['code']);
ctl('/ctl/reset'); ctl('/ctl/set?insert_mode=busy');
$o = new_order()['json']['order_id']; $pay = pay($o); $w = webhook($pay);
check('a retryable rejection (attempt 1 of 3) still returns 500 so Razorpay redelivers', where_is($o) === 'pending' && $w['code'] === 500);

// ============================================================================
section('Corrupt or missing data on the server');
$o = new_order()['json']['order_id']; $p = pay($o)['id'];
file_put_contents("$PEND/pending/$o.json", '{not json');
$v = verify($o, $p);
check('corrupt pending record + payment: no crash (not a bare 500), record not lost, alert raised', $v['code'] !== 500 && where_is($o) !== 'nowhere' && str_contains(log_text(), 'ALERT'), $v['code'] . ' ' . where_is($o) . ' ' . substr($v['raw'], 0, 120));
ctl('/ctl/reset'); $o = new_order()['json']['order_id']; $p = pay($o)['id'];
file_put_contents("$PEND/pending/$o.json", '{}'); $v = verify($o, $p);
check('empty pending record ({}) + payment: nothing sent to eZee, record kept, human alerted', count(inserts()) === 0 && where_is($o) !== 'nowhere' && str_contains(log_text(), 'ALERT'), $v['code'] . ' ' . where_is($o) . ' inserts=' . count(inserts()));
ctl('/ctl/reset'); chmod("$PEND/pending", 0500);
$b0 = rzp_orders(); $r = new_order();
check('pending dir not writable -> 503 and the guest is NOT sent to pay', $r['code'] === 503 && empty($r['json']['order_id']), $r['code'] . ' ' . $r['raw']);
chmod("$PEND/pending", 0700);
ctl('/ctl/reset'); $o = new_order()['json']['order_id']; $p = pay($o)['id']; chmod("$PEND/done", 0500);
$v = verify($o, $p); chmod("$PEND/done", 0700);
$rec = 'order_RECOVERXXX1'; file_put_contents("$PEND/processing/$rec@" . (time() - 1000) . '.json', json_encode(['order_id' => $rec, 'total' => 1, 'reservation_no' => '1888', 'razorpay_payment_id' => 'pay_X']));
cron(); check('claim interrupted AFTER eZee returned a reservation number: the cron completes it into done/ (no alert, no double booking)', is_file("$PEND/done/$rec.json") && !glob("$PEND/processing/$rec*") && str_contains(log_text(), "RECOVERED order=$rec"));
check('booking made but done/ not writable: guest still told success AND the record is not lost', $v['code'] === 200 && where_is($o) !== 'nowhere', $v['code'] . ' record in: ' . where_is($o));

// ============================================================================
section('eZee slow after the booking exists (PHP limit on the host is typically 30 s)');
ctl('/ctl/set?addpayment_mode=slow');
$o = new_order()['json']['order_id']; $p = pay($o)['id']; $t = microtime(true); $v = verify($o, $p);
$el = microtime(true) - $t;
check('slow AddPayment (2 x 18 s): reservation exists, so the guest must get success and the record must be in done/', $v['code'] === 200 && where_is($o) === 'done', sprintf('%.0fs http=%d record in %s bookings=%d', $el, $v['code'], where_is($o), count(ctl('/ctl/bookings'))));

// ============================================================================
section('Cancellation edge cases');
[$o, $p, $v] = confirmed(); $no = $v['json']['reservation_no']; unlink("$PEND/done/$o.json");
$c = app('POST', '/api/cancel-booking.php', ['reservation_no' => $no, 'email' => 'test@example.com']);
check('booking with no done/ record (made by hand in eZee): cancelled, no auto-refund, staff alerted', $c['code'] === 200 && count(calls('rzp', 'refund')) === 0 && str_contains(log_text(), 'REFUND to review'), $c['raw']);
ctl('/ctl/reset'); [$o, $p, $v] = confirmed(); $no = $v['json']['reservation_no']; patch_rec($o, ['check_in' => d(-1)]);
$c = app('POST', '/api/cancel-booking.php', ['reservation_no' => $no, 'email' => 'test@example.com']);
check('cancel after check-in date: no refund, Razorpay never called', $c['code'] === 200 && count(calls('rzp', 'refund')) === 0, $c['raw']);
ctl('/ctl/reset'); [$o, $p, $v] = confirmed(); $no = $v['json']['reservation_no'];
$mh = curl_multi_init(); $hs = [];
for ($i = 0; $i < 2; $i++) { $ch = curl_init(APP . '/api/cancel-booking.php'); curl_setopt_array($ch, [CURLOPT_RETURNTRANSFER => true, CURLOPT_POST => true, CURLOPT_POSTFIELDS => json_encode(['reservation_no' => $no, 'email' => 'test@example.com']), CURLOPT_HTTPHEADER => ['Content-Type: application/json', "X-Forwarded-For: 10.0.0.$i"]]); curl_multi_add_handle($mh, $ch); $hs[] = $ch; }
do { curl_multi_exec($mh, $run2); curl_multi_select($mh, 0.2); } while ($run2 > 0);
$rf = calls('rzp', 'refund'); $keys = array_unique(array_column($rf, 'key'));
check('two simultaneous cancels: every refund call carries the SAME idempotency key (Razorpay pays once)', count($keys) === 1 && $keys[0] === "mosaic-cancel-$no", json_encode($keys));

// ============================================================================
echo "\n----------------------------------------\n";
echo "PASS $pass   FAIL $fail\n";
if ($failures) { echo "Failures:\n"; foreach ($failures as $f) echo " - $f\n"; }
exit($fail ? 1 : 0);
