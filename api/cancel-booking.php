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
require_once __DIR__ . '/lib/razorpay.php';

// Tightest of the three: without a ceiling this is a free oracle for guessing
// reservation numbers. Nobody legitimately cancels five times in ten minutes.
require_method('POST');
rate_limit('cancel-booking', 5, 600);
// The per-client limit above is keyed on a header a caller can rotate, so the
// guessing ceiling also lives where it cannot be: per reservation, and site-wide.
rate_limit('cancel-all', 60, 600, 'all');

$body = read_json_body();
$reservationNo = str_field($body, 'reservation_no');
$email = str_field($body, 'email');
if ($reservationNo === '' || $email === '') {
  json_error(400, 'Please provide your reservation number and email.');
}
if (!preg_match('/^[A-Za-z0-9-]{1,32}$/', $reservationNo)) {
  json_error(404, 'Reservation not found or email does not match. Please check the details or WhatsApp us.');
}
rate_limit('cancel-reservation', 5, 3600, $reservationNo);

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

// Leave a recoverable trace BEFORE the irreversible eZee call: if this process dies between eZee
// cancelling and the refund steps below, a person can still find the reservation and finish the refund.
$intentFile = PENDING_ORDERS_DIR . '/refunds/' . $reservationNo . '.json';
@file_put_contents($intentFile, json_encode(['reservation_no' => $reservationNo, 'status' => 'cancelling',
  'started_at' => date('c')], JSON_PRETTY_PRINT), LOCK_EX);

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
  @unlink($intentFile); // nothing was cancelled, so nothing to recover
  bookings_log("CANCEL FAILED reservation=$reservationNo response=" . json_encode($cancelResponse));
  json_error(502, "We couldn't cancel that automatically. Please WhatsApp us and we'll cancel it for you right away.");
}

// The cancellation policy decides the money: 72h or more before check-in the guest gets a full refund,
// inside the window nothing. cancellation_refund_outcome() (lib/razorpay.php) issues an eligible refund
// automatically and returns the guest-facing note. Anything unusual (Razorpay refuses, network error, no
// payment id, unreadable date) falls back to a work item + alert for staff, and the guest is never told a
// refund was sent unless Razorpay confirmed one. Cancelling is never blocked: inside the window the guest
// still frees the room, they just aren't refunded for it.
$record = find_done_record($reservationNo);
$refundDue = refund_due_for_checkin($record['check_in'] ?? null); // null = undetermined
$outcome = cancellation_refund_outcome($refundDue, $record['razorpay_payment_id'] ?? null, $reservationNo, 'razorpay_refund_payment');

bookings_log(sprintf(
  'CANCELLED reservation=%s email=%s payment=%s amount=%s refund_due=%s action=%s refund_id=%s',
  $reservationNo,
  $email,
  $record['razorpay_payment_id'] ?? 'unknown',
  $record['total'] ?? 'unknown',
  $refundDue === null ? 'unknown' : ($refundDue ? 'YES' : 'no'),
  $outcome['action'],
  $outcome['refund_id'] ?? '-'
));

// Leave a trace a person can find: refunded automatically (for the record) or needs a manual refund.
if ($outcome['action'] === 'none') {
  @unlink($intentFile);
} else {
  $refund = ['reservation_no' => $reservationNo, 'razorpay_payment_id' => $record['razorpay_payment_id'] ?? null,
    'amount' => $record['total'] ?? null, 'refund_due' => $refundDue === null ? 'unknown' : 'yes',
    'status' => $outcome['action'] === 'refunded' ? 'refunded' : 'manual',
    'razorpay_refund_id' => $outcome['refund_id'] ?? null, 'reason' => $outcome['reason'] ?? null,
    'cancelled_at' => date('c')];
  @file_put_contents($intentFile, json_encode($refund, JSON_PRETTY_PRINT), LOCK_EX);
  booking_alert($outcome['action'] === 'refunded' ? 'REFUND issued automatically' : 'REFUND to review after cancellation', json_encode($refund));
}

json_ok(['success' => true, 'reservation_no' => $reservationNo, 'refund_note' => $outcome['note']]);

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
