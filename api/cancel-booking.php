<?php
/**
 * POST /api/cancel-booking.php
 * Body: { reservation_no, email }
 *
 * Self-service cancellation. eZee's CancelBooking API only needs a
 * reservation number — no guest verification built in — so anyone who
 * guessed/saw a reservation number could cancel someone else's stay.
 * We close that gap ourselves: fetch the booking first, require the
 * submitted email to match the one on file before cancelling.
 */
require __DIR__ . '/lib/config.php';
require __DIR__ . '/lib/ezee.php';

$body = read_json_body();
$reservationNo = trim($body['reservation_no'] ?? '');
$email = trim($body['email'] ?? '');
if ($reservationNo === '' || $email === '') {
  json_error(400, 'Please provide your reservation number and email.');
}

$booking = ezee_fetch_booking($reservationNo);
$reservation = $booking['Reservations']['Reservation'][0] ?? null;
if (!$booking['_ok'] || !$reservation) {
  json_error(404, 'Reservation not found or email does not match. Please check the details or WhatsApp us.');
}

$onFileEmail = strtolower(trim($reservation['Email'] ?? ''));
if ($onFileEmail === '' || $onFileEmail !== strtolower($email)) {
  json_error(404, 'Reservation not found or email does not match. Please check the details or WhatsApp us.');
}

$status = $reservation['BookingTran'][0]['CurrentStatus'] ?? '';
if (in_array($status, ['Cancel', 'Void', 'Checked Out'], true)) {
  json_error(409, "This reservation is already $status — nothing to cancel.");
}

$cancelResponse = ezee_get('CancelBooking', ['ResNo' => $reservationNo]);
$ok = $cancelResponse['_ok'] && empty($cancelResponse['Errors'][0]['ErrorCode']) && stripos((string)($cancelResponse['status'] ?? ''), 'success') !== false;
if (!$ok) {
  $msg = $cancelResponse['Errors'][0]['ErrorMessage'] ?? ($cancelResponse['_error'] ?? 'Cancellation failed.');
  bookings_log("CANCEL FAILED reservation=$reservationNo response=" . json_encode($cancelResponse));
  json_error(502, "Could not cancel automatically ($msg). Please WhatsApp us and we'll cancel it manually.");
}

bookings_log("CANCELLED reservation=$reservationNo email=$email");
json_ok(['success' => true, 'reservation_no' => $reservationNo]);
