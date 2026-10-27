<?php
/**
 * Local stand-in for eZee (/ezee/...) and Razorpay (/razorpay/...), plus /ctl/... for the test driver.
 * Test use only. Modelled on replies seen live (docs/eZee-Connectivity-API.md and the server order files).
 */
$H = getenv('MOCK_STATE_DIR') ?: __DIR__ . '/state';
@mkdir($H, 0777, true);
function st(string $n, $d = []) { global $H; $f = "$H/$n.json"; return is_file($f) ? json_decode(file_get_contents($f), true) : $d; }
function put(string $n, $v) { global $H; file_put_contents("$H/$n.json", json_encode($v), LOCK_EX); }
function logcall(array $c) { global $H; file_put_contents("$H/calls.log", json_encode($c) . "\n", FILE_APPEND | LOCK_EX); }
function out($v, int $code = 200) { http_response_code($code); header('Content-Type: application/json'); echo json_encode($v); exit; }
function cfg(string $k, $d = null) { return st('config', [])[$k] ?? $d; }

$path = parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH);
$raw = file_get_contents('php://input');
$json = json_decode($raw, true);

// ---- control ----
if ($path === '/ctl/reset') { foreach (glob("$H/*") as $f) @unlink($f); out(['ok' => true]); }
if ($path === '/ctl/set') { $c = st('config', []); foreach ($_GET as $k => $v) $c[$k] = $v; put('config', $c); out($c); }
if ($path === '/ctl/calls') { $l = is_file("$H/calls.log") ? array_filter(explode("\n", file_get_contents("$H/calls.log"))) : []; out(array_map(fn ($x) => json_decode($x, true), array_values($l))); }
if ($path === '/ctl/bookings') out(st('bookings', []));
if ($path === '/ctl/pay') { // simulate the guest paying (or failing to pay) a Razorpay order
  $orders = st('orders', []); $o = $orders[$_GET['order'] ?? ''] ?? null;
  if (!$o) out(['error' => 'no such order'], 404);
  $pays = st('payments', []);
  $p = ['id' => 'pay_MOCK' . (count($pays) + 1) . 'x' . substr(md5((string)microtime(true)), 0, 6), 'entity' => 'payment', 'order_id' => $o['id'],
    'amount' => (int)($_GET['amount'] ?? $o['amount']), 'currency' => $_GET['currency'] ?? 'INR', 'status' => $_GET['status'] ?? 'captured',
    'method' => 'upi', 'captured' => ($_GET['status'] ?? 'captured') === 'captured', 'notes' => $o['notes'] ?? []];
  $pays[] = $p; put('payments', $pays);
  $p['signature'] = hash_hmac('sha256', $o['id'] . '|' . $p['id'], 'mocksecret'); // what Razorpay Checkout would hand the browser
  out($p);
}

// ---- Razorpay ----
if (str_starts_with($path, '/razorpay/')) {
  $auth = ($_SERVER['PHP_AUTH_USER'] ?? '') . ':' . ($_SERVER['PHP_AUTH_PW'] ?? '');
  if ($auth !== 'rzp_test_mock:mocksecret') out(['error' => ['description' => 'Authentication failed']], 401);
  if (cfg('rzp_down')) out(['error' => ['description' => 'Razorpay is down']], 503);
  if ($path === '/razorpay/v1/orders' && $_SERVER['REQUEST_METHOD'] === 'POST') {
    $orders = st('orders', []);
    $o = ['id' => 'order_MOCK' . (count($orders) + 1) . substr(md5((string)microtime(true)), 0, 6), 'entity' => 'order', 'amount' => $json['amount'],
      'currency' => $json['currency'], 'receipt' => $json['receipt'], 'status' => 'created', 'notes' => $json['notes'] ?? []];
    $orders[$o['id']] = $o; put('orders', $orders); logcall(['rzp' => 'create_order', 'amount' => $o['amount'], 'id' => $o['id']]); out($o);
  }
  if (preg_match('#^/razorpay/v1/orders/([^/]+)/payments$#', $path, $m)) {
    if (cfg('rzp_429')) out(['error' => ['description' => 'Too many requests']], 429);
    out(['entity' => 'collection', 'items' => array_values(array_filter(st('payments', []), fn ($p) => $p['order_id'] === $m[1]))]);
  }
  if (preg_match('#^/razorpay/v1/payments/([^/]+)/refund$#', $path, $m)) {
    $key = $_SERVER['HTTP_X_REFUND_IDEMPOTENCY'] ?? '';
    logcall(['rzp' => 'refund', 'payment' => urldecode($m[1]), 'key' => $key, 'body' => $json]);
    if (cfg('refund_mode') === 'fail') out(['error' => ['description' => 'The payment has been fully refunded already']], 400);
    $r = st('refunds', []);
    if (!isset($r[$key])) $r[$key] = ['id' => 'rfnd_MOCK' . (count($r) + 1), 'status' => 'processed', 'payment_id' => urldecode($m[1])];
    put('refunds', $r); out($r[$key]);
  }
  out(['error' => ['description' => 'not found']], 404);
}

// ---- eZee ----
$today = date('Y-m-d');
function days(string $in, string $out): array { $d = []; for ($t = strtotime($in); $t < strtotime($out); $t += 86400) $d[] = date('Y-m-d', $t); return $d; }

if (str_starts_with($path, '/ezee/booking/reservation_api/listing.php')) {
  $type = $_GET['request_type'] ?? $_POST['request_type'] ?? '';
  if (cfg('ezee_429') && $type === 'RoomList') out(['Errors' => ['ErrorMessage' => 'rate']], 429);
  if ($type === 'RoomList') {
    if (cfg('roomlist_down')) { http_response_code(503); exit; }
    $ds = days($_GET['check_in_date'], $_GET['check_out_date']); $n = count($ds);
    $mk = function (string $type, string $name, string $rt, string $rr, array $perNight, int $avail) use ($ds) {
      $ex = array_combine($ds, array_map(fn ($v) => number_format($v, 4, '.', ''), $perNight));
      $tax = array_combine($ds, array_map(fn ($v) => round($v * .05, 2), $perNight));
      $roomOnly = array_sum($perNight); $incl = round($roomOnly * 1.05, 2);
      return ['Room_Name' => "$name - EP", 'Roomtype_Name' => $name, 'roomtypeunkid' => $rt, 'ratetypeunkid' => '5767700000000000001', 'roomrateunkid' => $rr,
        'base_adult_occupancy' => 1, 'max_adult_occupancy' => 2, 'available_rooms' => array_combine($ds, array_fill(0, count($ds), (string)$avail)), 'min_ava_rooms' => $avail,
        'room_rates_info' => ['exclusive_tax' => $ex, 'totalprice_room_only' => $roomOnly, 'totalprice_inclusive_all' => $incl, 'avg_per_night_after_discount' => round($incl / count($ds), 2)],
        'extra_adult_rates_info' => ['exclusive_tax' => array_combine($ds, array_fill(0, count($ds), '300.0000'))],
        'extra_child_rates_info' => ['exclusive_tax' => array_combine($ds, array_fill(0, count($ds), '0.0000'))]];
    };
    $double = array_fill(0, $n, 2099); if ($n >= 2) $double[$n - 1] = 3500;       // rate changes on the last night (seen live 16-21 Nov)
    $dorm8 = array_fill(0, $n, 699); if ($n >= 2) $dorm8[$n - 1] = 899;           // and on 21-23 Nov
    out(['SearchCriteria' => ['check_in_date' => $_GET['check_in_date']], 'RoomList' => ['RoomType' => [
      $mk('dorm', '4 - Bed Mixed Dorm', '5767700000000000006', '5767700000000000004', array_fill(0, $n, 499), (int)cfg('dorm4_avail', 5)),
      $mk('dorm', '8 - Bed Mixed Dorm', '5767700000000000001', '5767700000000000001', $dorm8, 4),
      $mk('priv', 'Double Room', '5767700000000000007', '5767700000000000005', $double, 3)]]]);
  }
  if ($type === 'InsertBooking') {
    $bd = json_decode($_POST['BookingData'] ?? $_GET['BookingData'] ?? '', true);
    logcall(['ezee' => 'InsertBooking', 'via' => $_SERVER['REQUEST_METHOD'], 'data' => $bd]);
    $mode = cfg('insert_mode', 'ok');
    if ($mode === 'http500') { http_response_code(500); exit; }
    if ($mode === 'garbage') { echo '<html>Sucuri blocked</html>'; exit; }
    if ($mode === 'timeout') { sleep(18); out(['ReservationNo' => '999']); }
    if ($mode === 'busy') out(['Errors' => ['ErrorMessage' => 'Server busy, please try again']]);
    if ($mode === 'noresno') out(['Info' => 'accepted']);
    if ($mode === 'invaliddata') out(['0' => ['Error Details' => ['Error_Code' => 'InvalidData', 'Error_Message' => 'Please check data passed.']]]);
    if (!is_array($bd) || empty($bd['Room_Details'])) out(['0' => ['Error Details' => ['Error_Code' => 'InvalidData', 'Error_Message' => 'Please check data passed.']]]);
    if (($bd['check_in_date'] ?? '') < $today) out(['ErrorCode' => 'InsertBookingFailed', 'ErrorDescription' => 'ArrivalDate is Past date.']);
    // What live eZee enforces (verified 2026-10-27 by creating and cancelling test reservations): any title/gender/country/last name is
    // accepted; a stay of more than one night needs baserate, extradultrate AND extrachildrate as one comma-separated value per night,
    // otherwise InvalidData. One night takes a single value.
    $nights = max(1, (strtotime($bd['check_out_date']) - strtotime($bd['check_in_date'])) / 86400);
    foreach ($bd['Room_Details'] as $r) {
      foreach (['baserate', 'extradultrate', 'extrachildrate'] as $f) {
        $parts = explode(',', (string)($r[$f] ?? ''));
        $bad = count($parts) !== (int)$nights || count(array_filter($parts, 'is_numeric')) !== count($parts);
        if ($bad) out(['0' => ['Error Details' => ['Error_Code' => 'InvalidData', 'Error_Message' => 'Please check data passed.']]]);
      }
    }
    $b = st('bookings', []); $no = (string)(1800 + count($b) + 1);
    $b[$no] = ['ReservationNo' => $no, 'Email' => $bd['Email_Address'], 'CurrentStatus' => 'Confirmed', 'check_in' => $bd['check_in_date'], 'rooms' => count($bd['Room_Details'])];
    put('bookings', $b); out(['ReservationNo' => $no, 'SubReservationNo' => [$no]]);
  }
  if ($type === 'CancelBooking') {
    $b = st('bookings', []); $no = $_GET['ResNo'] ?? '';
    logcall(['ezee' => 'CancelBooking', 'res' => $no]);
    if (cfg('cancel_mode') === 'fail' || !isset($b[$no])) out(['Errors' => ['ErrorCode' => '9', 'ErrorMessage' => 'cannot cancel']]);
    $b[$no]['CurrentStatus'] = 'Cancel'; put('bookings', $b); out(['status' => 'Successful']);
  }
  out(['Errors' => ['ErrorMessage' => "unknown request_type $type"]]);
}
if (str_starts_with($path, '/ezee/pmsinterface/pms_connectivity.php')) {
  $no = $json['RES_Request']['BookingId'] ?? ''; $b = st('bookings', [])[$no] ?? null;
  if (!$b) out(['Errors' => ['ErrorCode' => '1', 'ErrorMessage' => 'No booking found']]);
  out(['Reservations' => ['Reservation' => [['Email' => $b['Email'], 'BookingTran' => [['CurrentStatus' => $b['CurrentStatus']]]]]]]);
}
if (str_starts_with($path, '/ezee/index.php/page/service.kioskconnectivity')) {
  logcall(['ezee' => 'AddPayment', 'req' => $json['RES_Request']['Reservation'][0] ?? null]);
  if (cfg('addpayment_mode') === 'slow') sleep(18);
  $code = cfg('addpayment_mode') === 'fail' ? '5' : '0';
  out(['Errors' => [['ErrorCode' => $code, 'ErrorMessage' => $code === '0' ? 'Success' : 'failed']]]);
}
out(['error' => 'mock: no route ' . $path], 404);
