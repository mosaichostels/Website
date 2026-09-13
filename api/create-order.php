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

// Each call creates a REAL Razorpay order and a pending file. A genuine guest
// needs one or two; the order-reuse path in book-now.js means retries mostly
// don't come back here at all.
rate_limit('create-order', 10, 600);

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
$phoneCode = preg_replace('/[^0-9+]/', '', $body['phone_code'] ?? '+91') ?: '+91';
$nationality = trim($body['nationality'] ?? '');
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
  // Adults staying in each room of this line. Re-validated below against
  // eZee's own base_adult_occupancy — the client's figure is never trusted.
  $cart[] = [
    'roomtypeunkid' => $item['roomtypeunkid'],
    'ratetypeunkid' => $item['ratetypeunkid'],
    'roomrateunkid' => $item['roomrateunkid'],
    'qty' => $qty,
    'adults' => max(1, (int)($item['adults'] ?? 1)),
  ];
  $totalUnits += $qty;
}
if ($totalUnits === 0) {
  json_error(400, 'Please select at least one room.');
}
if ($totalUnits > 8) {
  json_error(400, 'This quick booking covers up to 8 rooms — for larger groups, please WhatsApp us.');
}
$children = 0; // children aren't collected anywhere in the flow yet

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
// Same rules the search enforces — past dates and over-long stays used to get
// through here, because this endpoint validated dates independently and less.
validate_stay_dates($checkIn, $checkOut);

// Re-fetch fresh availability/pricing — the only source of truth for amount.
// number_adults/num_rooms mirror availability.php's search query (1/1), not
// the guest's actual totals — verified live (2026-08-11) that eZee's RoomList
// silently drops a room type from the response entirely when num_rooms > 1
// (e.g. booking 2 beds of the same dorm), even though real inventory is
// available. Per-room-type availability count is unaffected by these params
// at num_rooms=1, and quantity is validated separately per cart line below.
$ezeeResponse = ezee_get('RoomList', [
  'check_in_date' => $checkIn,
  'check_out_date' => $checkOut,
  // eZee rejects requests that pass both check_out_date and num_nights.
  'number_adults' => 1,
  'number_children' => 0,
  'num_rooms' => 1,
  'show_only_available_rooms' => 1,
  'showtax' => 1,
]);
if (!$ezeeResponse['_ok']) {
  if (!empty($ezeeResponse['_rateLimited'])) json_error(429, 'Our booking system is busy — please try again in a moment.');
  json_error_upstream(502, 'We couldn\'t confirm live pricing just now. Please try again shortly, or WhatsApp us.', $ezeeResponse['_error']);
}

// Build the flat list of room units (one entry per physical room), each
// carrying the adult count declared for its cart line. This used to hardcode
// one adult per room, so a couple booking a private double was sent to eZee as
// a single guest — wrong on the arrival list and in occupancy reporting.
$roomUnits = [];
$total = 0.0;
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
  // Same resolver availability.php used to render the price the guest saw —
  // when these two disagreed, search worked and checkout 502'd every time.
  $perUnitTotal = ezee_room_total($matched) ?? 0.0;
  if ($perUnitTotal <= 0) {
    json_error(502, 'Could not determine a price for one of the selected rooms. Please try again or WhatsApp us.');
  }
  // eZee is the authority on how many adults this rate covers. Above its base
  // occupancy an extra-adult rate applies that we do NOT add to the Razorpay
  // amount, so accepting one here would confirm a booking we undercharged.
  $baseAdults = max(1, (int)($matched['base_adult_occupancy'] ?? 1));
  if ($item['adults'] > $baseAdults) {
    json_error(409, 'The rate for "' . ($matched['Roomtype_Name'] ?? 'this room') . '" covers up to '
      . $baseAdults . ' guest' . ($baseAdults > 1 ? 's' : '') . ' per room. For a larger group, please WhatsApp us.');
  }
  for ($i = 0; $i < $item['qty']; $i++) {
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
      'adults' => $item['adults'],
      'children' => $children,
      'child_ages' => '',
      'title' => $guest['title'] ?? '',
      'first_name' => $guest['first_name'],
      'last_name' => $guest['last_name'] ?? '',
      'gender' => $guest['gender'] ?? '',
      'special_request' => $specialRequest,
    ];
    $total += $perUnitTotal;
  }
}
$amountPaise = (int)round($total * 100); // integer math — avoids float rounding drift on paise conversion

// The price above is authoritative and always has been — the client never sets
// it. What was missing is TELLING the guest when it moved. eZee rates can
// change between the search and the payment, and the first the guest knew about
// it was a different number inside the Razorpay window. This is advisory only:
// a mismatch never changes what we charge, it just stops and asks first.
$expectedTotal = isset($body['expected_total']) ? (float)$body['expected_total'] : null;
if ($expectedTotal !== null && abs($expectedTotal - $total) >= 0.01) {
  http_response_code(409);
  echo json_encode([
    'error' => 'The rate for these dates has changed since you searched.',
    'price_changed' => true,
    'old_total' => round($expectedTotal, 2),
    'new_total' => round($total, 2),
  ]);
  exit;
}

$orderReceipt = 'mosaic-' . date('Ymd-His') . '-' . substr(md5(uniqid('', true)), 0, 6);
$order = razorpay_create_order($amountPaise, $orderReceipt, [
  'email' => $body['email'],
  'check_in' => $checkIn,
  'check_out' => $checkOut,
]);
if (!$order['_ok']) {
  json_error_upstream(502, 'We couldn\'t start the payment just now. Please try again, or WhatsApp us.', $order['_error']);
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
  'phone' => $phoneCode . ' ' . $phoneDigits,
  'nationality' => $nationality,
  'special_request' => $specialRequest,
  'created_at' => date('c'),
];
// This file is the ONLY record linking a Razorpay order to its booking —
// confirm_paid_order() claims it, and reconcile-pending.php sweeps it. If the
// write fails and we still hand back an order_id, the guest pays into a void:
// no reservation, no failed/ record, and nothing for the cron to find. So fail
// here instead. The Razorpay order is already created at this point but is
// unpaid and its id never reaches the browser, so it simply expires unused.
$pendingFile = PENDING_ORDERS_DIR . '/pending/' . $order['id'] . '.json';
if (file_put_contents($pendingFile, json_encode($pendingRecord, JSON_PRETTY_PRINT), LOCK_EX) === false) {
  bookings_log("FATAL pending write failed order={$order['id']} path=$pendingFile");
  error_log("mosaic booking: pending write failed for order {$order['id']} at $pendingFile");
  json_error(503, 'We could not start your booking just now. Please try again in a moment, or WhatsApp us and we\'ll book it for you.');
}

json_ok([
  'order_id' => $order['id'],
  'amount' => $amountPaise,
  'currency' => 'INR',
  'key_id' => RAZORPAY_KEY_ID,
]);

function find_matching_room(array $data, string $roomrateunkid): ?array {
  $found = [];
  ezee_find_room_entries($data, $found);
  foreach ($found as $entry) {
    if ((string)($entry['roomrateunkid'] ?? '') === $roomrateunkid) return $entry;
  }
  return null;
}
