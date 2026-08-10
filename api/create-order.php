<?php
/**
 * POST /api/create-order.php
 * Body: { check_in, check_out, rooms:
 *         [{roomtypeunkid, ratetypeunkid, roomrateunkid, qty}, ...],
 *         guest: {title, first_name, last_name, gender},
 *         first_name, last_name, email, phone, special_request }
 *
 * No client-supplied occupancy: adults is fixed at 1 per room booked,
 * children at 0 — matches eZee's own hosted booking engine, which has no
 * upfront guest-count fields either.
 *
 * PRICE-INTEGRITY BOUNDARY: the client never sends a price. This
 * re-fetches eZee's RoomList server-side for the same query and takes the
 * authoritative total from that fresh response — never from the client —
 * before creating the Razorpay order. Otherwise a tampered client request
 * could pay ₹1 for a real booking.
 */
require __DIR__ . '/lib/config.php';
require __DIR__ . '/lib/ezee.php';
require __DIR__ . '/lib/razorpay.php';

if (RAZORPAY_KEY_ID === '' || RAZORPAY_KEY_SECRET === '') {
  json_error(503, 'Online payment isn\'t set up yet — please book via WhatsApp for now.');
}

$body = read_json_body();

$required = ['check_in', 'check_out', 'rooms', 'first_name', 'email', 'phone'];
foreach ($required as $field) {
  $val = $body[$field] ?? '';
  if ($val === '' || $val === null) json_error(400, "Missing required field: $field");
}
if (!filter_var($body['email'], FILTER_VALIDATE_EMAIL)) {
  json_error(400, 'Please provide a valid email address.');
}
$phoneDigits = preg_replace('/\D/', '', $body['phone']);
if (strlen($phoneDigits) < 8 || strlen($phoneDigits) > 15) {
  json_error(400, 'Please provide a valid phone number.');
}
if (!is_array($body['rooms']) || count($body['rooms']) === 0) {
  json_error(400, 'Please select at least one room.');
}
$cart = [];
$totalUnits = 0;
foreach ($body['rooms'] as $item) {
  $qty = (int)($item['qty'] ?? 0);
  if ($qty < 1) continue;
  if (empty($item['roomtypeunkid']) || empty($item['ratetypeunkid']) || empty($item['roomrateunkid'])) {
    json_error(400, 'Invalid room selection.');
  }
  $cart[] = ['roomtypeunkid' => $item['roomtypeunkid'], 'ratetypeunkid' => $item['ratetypeunkid'], 'roomrateunkid' => $item['roomrateunkid'], 'qty' => $qty];
  $totalUnits += $qty;
}
if ($totalUnits === 0) {
  json_error(400, 'Please select at least one room.');
}
if ($totalUnits > 8) {
  json_error(400, 'This quick booking covers up to 8 rooms — for larger groups, please WhatsApp us.');
}
$adults = $totalUnits; // 1 adult per room booked — no client-supplied occupancy
$children = 0;
$childAges = [];

// One guest contact for the whole booking — matches eZee's own hosted
// engine, which collects a single guest identity, not one per room
// (confirmed live on both our engine and a competitor's eZee engine).
$guest = is_array($body['guest'] ?? null) ? $body['guest'] : [];
if (empty($guest['first_name'])) {
  json_error(400, "Please provide the guest's first name.");
}

$specialRequest = trim($body['special_request'] ?? '');
$arrivalTime = trim($body['arrival_time'] ?? '');
if ($arrivalTime !== '') {
  $specialRequest = 'Estimated arrival: ' . $arrivalTime . '. ' . $specialRequest;
}

$checkIn = $body['check_in'];
$checkOut = $body['check_out'];
$dCheckIn = DateTime::createFromFormat('Y-m-d', $checkIn);
$dCheckOut = DateTime::createFromFormat('Y-m-d', $checkOut);
if (!$dCheckIn || !$dCheckOut || $dCheckOut <= $dCheckIn) {
  json_error(400, 'Invalid dates.');
}
$nights = $dCheckIn->diff($dCheckOut)->days;

// Re-fetch fresh availability/pricing — the only source of truth for amount.
$ezeeResponse = ezee_get('RoomList', [
  'check_in_date' => $checkIn,
  'check_out_date' => $checkOut,
  // eZee rejects requests that pass both check_out_date and num_nights.
  'number_adults' => $adults,
  'number_children' => $children,
  'num_rooms' => $totalUnits,
  'show_only_available_rooms' => 1,
  'showtax' => 1,
]);
if (!$ezeeResponse['_ok']) {
  if (!empty($ezeeResponse['_rateLimited'])) json_error(429, $ezeeResponse['_error']);
  json_error(502, $ezeeResponse['_error']);
}

// Build the flat list of room units (one entry per physical room), splitting
// total adults/children as evenly as possible across units, paired with the
// guest identity submitted for that same unit (same cart order the client
// used to render the per-room guest blocks).
$roomUnits = [];
$total = 0.0;
$childAgeCursor = 0;
$unitIndex = 0;
foreach ($cart as $item) {
  $matched = find_matching_room($ezeeResponse, $item['roomrateunkid']);
  if (!$matched) {
    json_error(409, 'One of the selected rooms is no longer available for these dates. Please search again.');
  }
  $available = $matched['available_rooms'] ?? $matched['min_ava_rooms'] ?? null;
  if (is_array($available)) $available = min($available) ?: 0;
  if ($available !== null && $item['qty'] > (int)$available) {
    json_error(409, 'Only ' . (int)$available . ' left of "' . ($matched['Roomtype_Name'] ?? 'this room') . '" — please adjust quantity.');
  }
  $rates = $matched['room_rates_info'] ?? [];
  $perUnitTotal = ezee_price_scalar($rates['totalprice_inclusive_all'] ?? $rates['totalprice_room_only'] ?? 0);
  if ($perUnitTotal <= 0) {
    json_error(502, 'Could not determine a price for one of the selected rooms. Please try again or WhatsApp us.');
  }
  for ($i = 0; $i < $item['qty']; $i++) {
    $unitAdults = intdiv($adults, $totalUnits) + ($unitIndex < ($adults % $totalUnits) ? 1 : 0);
    $unitChildren = $children > 0 ? intdiv($children, $totalUnits) + ($unitIndex < ($children % $totalUnits) ? 1 : 0) : 0;
    $unitChildAges = $unitChildren > 0 ? array_slice($childAges, $childAgeCursor, $unitChildren) : [];
    $childAgeCursor += $unitChildren;
    $roomUnits[] = [
      'roomtypeunkid' => $item['roomtypeunkid'],
      'ratetypeunkid' => $item['ratetypeunkid'],
      'roomrateunkid' => $item['roomrateunkid'],
      // Per eZee's documented RoomList shape (docs/eZee-Connectivity-API.md
      // ~L2158-2290): these rates live nested under room_rates_info /
      // extra_adult_rates_info / extra_child_rates_info as date-keyed
      // objects, not flat keys on the entry — ezee_price_scalar() unwraps them.
      'baserate' => ezee_price_scalar($matched['room_rates_info']['exclusive_tax'] ?? 0),
      'extradultrate' => ezee_price_scalar($matched['extra_adult_rates_info']['exclusive_tax'] ?? 0),
      'extrachildrate' => ezee_price_scalar($matched['extra_child_rates_info']['exclusive_tax'] ?? 0),
      'adults' => max(1, $unitAdults),
      'children' => $unitChildren,
      'child_ages' => implode(',', $unitChildAges),
      'title' => $guest['title'] ?? '',
      'first_name' => $guest['first_name'],
      'last_name' => $guest['last_name'] ?? '',
      'gender' => $guest['gender'] ?? '',
      'special_request' => $specialRequest,
    ];
    $unitIndex++;
    $total += $perUnitTotal;
  }
}
$amountPaise = (int)round($total * 100); // integer math — avoids float rounding drift on paise conversion

$orderReceipt = 'mosaic-' . date('Ymd-His') . '-' . substr(md5(uniqid('', true)), 0, 6);
$order = razorpay_create_order($amountPaise, $orderReceipt, [
  'email' => $body['email'],
  'check_in' => $checkIn,
  'check_out' => $checkOut,
]);
if (!$order['_ok']) {
  json_error(502, 'Could not start payment: ' . $order['_error']);
}

ensure_pending_dirs();
$pendingRecord = [
  'order_id' => $order['id'],
  'amount' => $amountPaise,
  'total' => $total,
  'check_in' => $checkIn,
  'check_out' => $checkOut,
  'room_units' => $roomUnits,
  'first_name' => $body['first_name'],
  'last_name' => $body['last_name'] ?? '',
  'email' => $body['email'],
  'phone' => $body['phone'],
  'special_request' => $specialRequest,
  'created_at' => date('c'),
];
file_put_contents(PENDING_ORDERS_DIR . '/pending/' . $order['id'] . '.json', json_encode($pendingRecord, JSON_PRETTY_PRINT));

json_ok([
  'order_id' => $order['id'],
  'amount' => $amountPaise,
  'currency' => 'INR',
  'key_id' => RAZORPAY_KEY_ID,
]);

// eZee's date-keyed rate fields (e.g. {"2026-08-13": "500.0000"}) collapse to
// a single scalar for single-night-rate lookups; already-scalar values pass through.
function ezee_price_scalar($val): float {
  if (is_array($val)) return (float)(reset($val) ?: 0);
  return (float)$val;
}

function find_matching_room(array $data, string $roomrateunkid): ?array {
  $found = [];
  find_room_entries_local($data, $found);
  foreach ($found as $entry) {
    if ((string)($entry['roomrateunkid'] ?? '') === $roomrateunkid) return $entry;
  }
  return null;
}

function find_room_entries_local(array $data, array &$found) {
  if (isset($data['roomtypeunkid']) && isset($data['roomrateunkid'])) {
    $found[] = $data;
    return;
  }
  foreach ($data as $value) {
    if (is_array($value)) find_room_entries_local($value, $found);
  }
}
