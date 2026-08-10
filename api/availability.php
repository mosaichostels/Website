<?php
/**
 * GET /api/availability.php?check_in=&check_out=&adults=&children=&rooms=
 * Proxies eZee's RoomList endpoint, validates input before calling eZee,
 * and maps the response down to only what the booking widget needs.
 */
require __DIR__ . '/lib/config.php';
require __DIR__ . '/lib/ezee.php';

$checkIn = $_GET['check_in'] ?? '';
$checkOut = $_GET['check_out'] ?? '';
$adults = (int)($_GET['adults'] ?? 1);
$children = (int)($_GET['children'] ?? 0);
$rooms = (int)($_GET['rooms'] ?? 1);

$today = new DateTime('today');
$dCheckIn = DateTime::createFromFormat('Y-m-d', $checkIn);
$dCheckOut = DateTime::createFromFormat('Y-m-d', $checkOut);

if (!$dCheckIn || !$dCheckOut) {
  json_error(400, 'Please provide valid check-in and check-out dates.');
}
if ($dCheckIn < $today) {
  json_error(400, 'Check-in date cannot be in the past.');
}
if ($dCheckOut <= $dCheckIn) {
  json_error(400, 'Check-out date must be after check-in date.');
}
$nights = $dCheckIn->diff($dCheckOut)->days;
if ($nights > 30) {
  json_error(400, 'Stays longer than 30 nights cannot be searched here — please WhatsApp us directly.');
}
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
  if (!empty($ezeeResponse['_rateLimited'])) json_error(429, $ezeeResponse['_error']);
  json_error(502, $ezeeResponse['_error']);
}

json_ok(['rooms' => extract_room_options($ezeeResponse)]);

/**
 * eZee's RoomList response nests room/rate entries under a structure that
 * varies by account configuration. Rather than assume one exact shape,
 * walk the decoded response and collect every associative array that looks
 * like a room-rate entry (has roomtypeunkid + roomrateunkid).
 *
 * Verified against a live response (2026-08-10): per-night and total prices
 * live as scalars under entry['room_rates_info'], not at the entry's top
 * level — inclusive_tax_adjustment/exclusive_tax there are date-keyed
 * arrays, not scalars, so they're only usable as a last-resort fallback.
 */
function extract_room_options(array $data): array {
  $found = [];
  find_room_entries($data, $found);

  $options = [];
  foreach ($found as $entry) {
    $rates = $entry['room_rates_info'] ?? [];
    $perNight = $rates['avg_per_night_after_discount']
      ?? $rates['inclusive_tax_adjustment']
      ?? $entry['inclusive_tax_adjustment']
      ?? $entry['exclusive_tax']
      ?? null;
    if (is_array($perNight)) $perNight = reset($perNight);
    $total = $rates['totalprice_inclusive_all']
      ?? $rates['totalprice_room_only']
      ?? $entry['totalprice_inclusive_all']
      ?? $entry['totalprice_room_only']
      ?? null;
    if (is_array($total)) $total = reset($total);
    $available = $entry['available_rooms'] ?? $entry['min_ava_rooms'] ?? null;
    if (is_array($available)) $available = min($available) ?: 0;

    $options[] = [
      'roomtypeunkid' => (string)($entry['roomtypeunkid'] ?? ''),
      'ratetypeunkid' => (string)($entry['ratetypeunkid'] ?? ''),
      'roomrateunkid' => (string)($entry['roomrateunkid'] ?? ''),
      'name' => $entry['Roomtype_Name'] ?? $entry['Room_Name'] ?? 'Room',
      'description' => $entry['Room_Description'] ?? $entry['Package_Description'] ?? '',
      'per_night' => $perNight !== null ? round((float)$perNight, 2) : null,
      'total' => $total !== null ? round((float)$total, 2) : null,
      'available' => (int)($available ?? 0),
    ];
  }
  return $options;
}

function find_room_entries(array $data, array &$found) {
  $isRoomEntry = isset($data['roomtypeunkid']) && isset($data['roomrateunkid']);
  if ($isRoomEntry) {
    $found[] = $data;
    return; // don't recurse further into a matched entry
  }
  foreach ($data as $value) {
    if (is_array($value)) find_room_entries($value, $found);
  }
}
