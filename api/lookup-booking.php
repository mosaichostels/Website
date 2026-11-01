<?php
/**
 * POST /api/lookup-booking.php
 * Body: { reservation_no, email }
 *
 * Read-only guest lookup for the "manage a booking" card. Same gate as
 * cancel-booking.php (reservation number AND matching email, same limits, same
 * generic 404 for every miss so reservations cannot be enumerated). Status,
 * dates and rooms come from eZee; money from our own done/ record.
 * Never returns email, phone or name.
 */
require __DIR__ . '/lib/config.php';
require __DIR__ . '/lib/ezee.php';
require_once __DIR__ . '/lib/booking.php';

require_method('POST');
rate_limit('lookup-booking', 5, 600);
rate_limit('lookup-all', 60, 600, 'all');

$body = read_json_body();
$reservationNo = str_field($body, 'reservation_no');
$email = str_field($body, 'email');
if ($reservationNo === '' || $email === '') {
  json_error(400, 'Please provide your reservation number and email.');
}
const LOOKUP_NOT_FOUND = 'Reservation not found or email does not match. Please check the details or WhatsApp us.';
if (!preg_match('/^[A-Za-z0-9-]{1,32}$/', $reservationNo)) json_error(404, LOOKUP_NOT_FOUND);
rate_limit('lookup-reservation', 5, 3600, $reservationNo);

$booking = ezee_fetch_booking($reservationNo);
$reservation = $booking['Reservations']['Reservation'][0] ?? null;
if (!$booking['_ok'] || !$reservation) json_error(404, LOOKUP_NOT_FOUND);

if (!is_array($reservation) || !is_string($reservation['Email'] ?? '')) json_error(404, LOOKUP_NOT_FOUND);
$onFileEmail = strtolower(trim($reservation['Email'] ?? ''));
if ($onFileEmail === '' || $onFileEmail !== strtolower($email)) json_error(404, LOOKUP_NOT_FOUND);

$trans = $reservation['BookingTran'] ?? [];
// One transaction can arrive as a bare object; anything that is not a list of objects counts as none.
if (is_array($trans) && $trans && array_keys($trans) !== range(0, count($trans) - 1)) $trans = [$trans];
$trans = is_array($trans) ? array_values(array_filter($trans, 'is_array')) : [];
if (!$trans) json_error(404, LOOKUP_NOT_FOUND);
$starts = array_filter(array_column($trans, 'Start'), 'is_string');
$ends = array_filter(array_column($trans, 'End'), 'is_string');
$reply = [
  'success' => true,
  'reservation_no' => $reservationNo,
  'status' => (string)($trans[0]['CurrentStatus'] ?? ''),
  'check_in' => $starts ? min($starts) : null,
  'check_out' => $ends ? max($ends) : null,
  'rooms' => array_values(array_filter(array_column($trans, 'RoomTypeName'))),
];
$record = find_done_record($reservationNo);
// No dates from eZee: use what we stored when the booking was made.
if ($record && !$starts) $reply['check_in'] = $record['check_in'] ?? null;
if ($record && !$ends) $reply['check_out'] = $record['check_out'] ?? null;
if ($record && isset($record['total'])) {
  // Records from before the deposit option have no pay_now: everything was paid up front.
  $reply['total'] = $record['total'];
  $reply['paid'] = $record['pay_now'] ?? $record['total'];
  $reply['due'] = $record['due_at_hotel'] ?? 0;
}
json_ok($reply);
