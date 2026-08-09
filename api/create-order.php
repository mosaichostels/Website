<?php
/**
 * POST /api/create-order.php
 * Body: { check_in, check_out, adults, children, child_ages, rooms:
 *         [{roomtypeunkid, ratetypeunkid, roomrateunkid, qty}, ...],
 *         first_name, last_name, email, phone, special_request }
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

$required = ['check_in', 'check_out', 'adults', 'children', 'rooms', 'first_name', 'email', 'phone'];
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
$adults = (int)$body['adults'];
$children = (int)$body['children'];
if ($totalUnits > $adults) {
  json_error(400, 'Each room needs at least one adult — please increase adults or select fewer rooms.');
}
$childAges = array_values(array_filter(array_map('trim', explode(',', $body['child_ages'] ?? '')), fn($a) => $a !== ''));
if ($children > 0 && count($childAges) < $children) {
  json_error(400, "Please provide each child's age.");
}

// One guest identity (title/name/gender) per physical room — eZee's
// InsertBooking captures this per Room_N, not just once per booking.
$guests = is_array($body['guests'] ?? null) ? $body['guests'] : [];
if (count($guests) !== $totalUnits) {
  json_error(400, 'Please provide a guest name for each room.');
}
foreach ($guests as $g) {
  if (empty($g['first_name'])) json_error(400, 'Please provide a first name for each room guest.');
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
  $perUnitTotal = (float)($matched['totalprice_inclusive_all'] ?? $matched['totalprice_room_only'] ?? 0);
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
      // NOTE: baserate/extradultrate/extrachildrate field names below are best-
      // effort mappings from the RoomList response — not yet verified against a
      // live eZee sandbox call. Confirm these match InsertBooking's expected
      // values before going live; adjust the fallbacks if they don't.
      'baserate' => (float)($matched['exclusive_tax'] ?? $matched['before_discount_inclusive_tax_adjustment'] ?? 0),
      'extradultrate' => (float)($matched['extradultrate'] ?? 0),
      'extrachildrate' => (float)($matched['extrachildrate'] ?? 0),
      'adults' => max(1, $unitAdults),
      'children' => $unitChildren,
      'child_ages' => implode(',', $unitChildAges),
      'title' => $guests[$unitIndex]['title'] ?? '',
      'first_name' => $guests[$unitIndex]['first_name'],
      'last_name' => $guests[$unitIndex]['last_name'] ?? '',
      'gender' => $guests[$unitIndex]['gender'] ?? '',
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
