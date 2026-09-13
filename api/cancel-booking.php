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

// Tightest of the three: without a ceiling this is a free oracle for guessing
// reservation numbers. Nobody legitimately cancels five times in ten minutes.
rate_limit('cancel-booking', 5, 600);

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
// CancelBooking returns Errors as an OBJECT ({"ErrorCode":..,"ErrorMessage":..}),
// documented at docs/eZee-Connectivity-API.md ~L5531 — not the array that the
// AddPayment endpoint returns. The list indexing here read Errors[0], which
// never matched, so this relied entirely on the status check below. Success is
// {"status":"Successful"}.
$ok = $cancelResponse['_ok']
  && empty($cancelResponse['Errors']['ErrorCode'])
  && stripos((string)($cancelResponse['status'] ?? ''), 'success') !== false;
if (!$ok) {
  bookings_log("CANCEL FAILED reservation=$reservationNo response=" . json_encode($cancelResponse));
  json_error(502, "We couldn't cancel that automatically. Please WhatsApp us and we'll cancel it for you right away.");
}

// Refund is NOT automatic — no code moves money back. What this does is decide
// whether one is owed, tell the guest the truth instead of an unqualified
// "cancelled", and leave staff a work item naming the exact Razorpay payment to
// refund. Cancelling is never blocked: inside the window the guest still frees
// the room, they just aren't refunded for it.
$record = find_done_record($reservationNo);
$refundDue = refund_due_for_checkin($record['check_in'] ?? null); // null = undetermined

bookings_log(sprintf(
  'CANCELLED reservation=%s email=%s payment=%s amount=%s refund_due=%s',
  $reservationNo,
  $email,
  $record['razorpay_payment_id'] ?? 'unknown',
  $record['total'] ?? 'unknown',
  $refundDue === null ? 'unknown' : ($refundDue ? 'YES' : 'no')
));

if ($refundDue === true) {
  $refundNote = 'Your refund will be processed within 7–10 business days.';
} elseif ($refundDue === false) {
  $refundNote = 'This is within 72 hours of check-in, so under our cancellation policy the booking amount is not refundable.';
} else {
  $refundNote = 'We\'ll confirm any refund due with you shortly.';
}

json_ok(['success' => true, 'reservation_no' => $reservationNo, 'refund_note' => $refundNote]);

/**
 * Our own done/ record, looked up by reservation number. Preferred over eZee's
 * FetchSingleBooking for the check-in date because this shape is one we write
 * ourselves (create-order.php) and is the only place the Razorpay payment id
 * lives — eZee's date field names for a reservation aren't pinned down.
 * ponytail: linear scan over done/, fine at hostel volume; index by
 * reservation number if the directory ever gets large.
 */
function find_done_record(string $reservationNo): ?array {
  foreach (glob(PENDING_ORDERS_DIR . '/done/*.json') ?: [] as $file) {
    $record = json_decode((string)file_get_contents($file), true);
    if (is_array($record) && (string)($record['reservation_no'] ?? '') === $reservationNo) return $record;
  }
  return null;
}
