<?php
/**
 * GET /api/availability.php?check_in=&check_out=&adults=&children=&rooms=
 * Proxies eZee's RoomList endpoint, validates input before calling eZee,
 * and maps the response down to only what the booking widget needs.
 */
require __DIR__ . '/lib/config.php';
require __DIR__ . '/lib/ezee.php';

// Searching is cheap but each call is a live eZee query; generous enough that
// a guest comparing dates never notices it.
rate_limit('availability', 60, 600);

$checkIn = $_GET['check_in'] ?? '';
$checkOut = $_GET['check_out'] ?? '';
$adults = (int)($_GET['adults'] ?? 1);
$children = (int)($_GET['children'] ?? 0);
$rooms = (int)($_GET['rooms'] ?? 1);

validate_stay_dates($checkIn, $checkOut);

if ($adults < 1 || $adults > 20) {
  json_error(400, 'Please enter a valid number of adults.');
}
if ($children < 0 || $children > 10) {
  json_error(400, 'Please enter a valid number of children.');
}
if ($rooms < 1 || $rooms > 8) {
  json_error(400, 'Please enter a valid number of rooms (1–8). For larger groups, please WhatsApp us.');
}

$ezeeResponse = ezee_get('RoomList', [
  'check_in_date' => $checkIn,
  'check_out_date' => $checkOut,
  // eZee rejects requests that pass both check_out_date and num_nights.
  'number_adults' => $adults,
  'number_children' => $children,
  'num_rooms' => $rooms,
  'show_only_available_rooms' => 1,
  'showtax' => 1,
]);

if (!$ezeeResponse['_ok']) {
  if (!empty($ezeeResponse['_rateLimited'])) json_error(429, 'Our booking system is busy — please try again in a moment.');
  json_error_upstream(502, 'We couldn\'t load live availability just now. Please try again shortly, or WhatsApp us.', $ezeeResponse['_error']);
}

json_ok(['rooms' => extract_room_options($ezeeResponse)]);

/**
 * Maps eZee's RoomList response down to what the widget needs.
 *
 * Verified against a live response (2026-08-10): per-night and total prices
 * live as scalars under entry['room_rates_info'], not at the entry's top
 * level — inclusive_tax_adjustment/exclusive_tax there are date-keyed
 * arrays, not scalars, so they're only usable as a last-resort fallback.
 * Stay totals come from ezee_room_total() so create-order.php resolves the
 * identical number from the identical response — see its docblock.
 */
function extract_room_options(array $data): array {
  $found = [];
  ezee_find_room_entries($data, $found);

  $options = [];
  foreach ($found as $entry) {
    $rates = $entry['room_rates_info'] ?? [];
    $perNight = $rates['avg_per_night_after_discount']
      ?? $rates['inclusive_tax_adjustment']
      ?? $entry['inclusive_tax_adjustment']
      ?? $entry['exclusive_tax']
      ?? null;
    if (is_array($perNight)) $perNight = reset($perNight);
    $total = ezee_room_total($entry);
    $available = $entry['available_rooms'] ?? $entry['min_ava_rooms'] ?? null;
    if (is_array($available)) $available = min($available) ?: 0;

    // Base (room-only, pre-tax) vs tax split — eZee gives both the room-only
    // and tax-inclusive stay totals; tax is the difference between them.
    $baseTotal = ezee_room_base_total($entry);
    $taxTotal = ($total !== null && $baseTotal !== null) ? round($total - $baseTotal, 2) : null;

    $options[] = [
      'roomtypeunkid' => (string)($entry['roomtypeunkid'] ?? ''),
      'ratetypeunkid' => (string)($entry['ratetypeunkid'] ?? ''),
      'roomrateunkid' => (string)($entry['roomrateunkid'] ?? ''),
      'name' => $entry['Roomtype_Name'] ?? $entry['Room_Name'] ?? 'Room',
      'description' => $entry['Room_Description'] ?? $entry['Package_Description'] ?? '',
      // How many adults the rate already covers. Guests may declare up to this
      // many; beyond it eZee charges an extra-adult rate we don't yet compute
      // into the Razorpay amount, so those bookings go via WhatsApp instead.
      'base_adults' => max(1, (int)($entry['base_adult_occupancy'] ?? 1)),
      'per_night' => $perNight !== null ? round((float)$perNight, 2) : null,
      'total' => $total,
      'base_total' => $baseTotal,
      'tax_total' => $taxTotal,
      // null is preserved rather than collapsed to 0: eZee omitting a count
      // means "unknown", which is not the same as "sold out", and the widget
      // renders them differently. Coercing both to 0 made every room with an
      // unreported count look sold out with a dead + button.
      'available' => $available === null ? null : (int)$available,
    ];
  }
  return $options;
}
