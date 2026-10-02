<?php
/**
 * Shared "turn a paid Razorpay order into an eZee reservation" logic — used
 * by both the client-triggered verify-payment.php and the server-to-server
 * razorpay-webhook.php backstop. Same atomic rename() claim either way, so
 * whichever caller gets there first wins and the other sees done/failed.
 */
require_once __DIR__ . '/ezee.php';

/**
 * One AddPayment attempt, normalised to a plain _ok. eZee reports failure two
 * different ways here — a transport/`_ok` failure, or a non-zero ErrorCode in
 * an Errors LIST (this endpoint returns a list; the reservation_api endpoints
 * return an object — see docs/eZee-Connectivity-API.md ~L6139). ErrorCode "0"
 * means success.
 */
function ezee_add_payment_once(array $request): array {
  $response = ezee_post_json($request);
  if (!$response['_ok'] || !empty($response['Errors'][0]['ErrorCode'])) {
    $response['_ok'] = false;
  }
  return $response;
}

// How many times a definite eZee rejection of InsertBooking is retried.
// Ambiguous failures (timeouts) are never retried.
const MAX_CONFIRM_ATTEMPTS = 3;
// Minimum gap between attempts. Razorpay redelivers a webhook that got a 5xx
// within seconds, which used all the attempts at once and gave eZee no time to
// recover. A delivery inside the gap is handed back untouched and not counted.
const CONFIRM_RETRY_GAP_SECONDS = 120;

/**
 * $payment is Razorpay's payment entity when the caller has one (webhook,
 * cron): its amount/currency/status are checked against what we created the
 * order for before any reservation is made. verify-payment.php only has the
 * signed ids, and Razorpay orders are amount-locked, so it passes null.
 *
 * Statuses: done | failed (needs a human) | retry (will be retried) |
 * unknown | mismatch.
 */
function confirm_paid_order(string $orderId, string $paymentId, ?array $payment = null): array {
  // Ids end up in file paths. The signature gate makes traversal impractical
  // for verify-payment, but the webhook and cron take ids from other sources,
  // so the shape is enforced once, here, where every caller passes through.
  if (!preg_match('/^order_[A-Za-z0-9]{6,40}$/', $orderId) || !preg_match('/^pay_[A-Za-z0-9]{6,40}$/', $paymentId)) {
    bookings_log('REJECTED malformed order/payment id');
    return ['status' => 'unknown'];
  }
  ensure_pending_dirs();
  $pendingPath = PENDING_ORDERS_DIR . '/pending/' . $orderId . '.json';
  $abandonedPath = PENDING_ORDERS_DIR . '/abandoned/' . $orderId . '.json';
  // The claim time is part of the NAME, set by the same rename() that claims the
  // order, so "how long has this been processing" never depends on a file's mtime
  // (which rename() keeps from the old pending/ file) and no window exists in which
  // a live claim looks stale to reconcile-pending.php's sweep.
  $processingPath = PENDING_ORDERS_DIR . '/processing/' . $orderId . '@' . time() . '.json';
  $donePath = PENDING_ORDERS_DIR . '/done/' . $orderId . '.json';
  $failedPath = PENDING_ORDERS_DIR . '/failed/' . $orderId . '.json';

  if ($payment !== null) {
    $source = file_exists($pendingPath) ? $pendingPath : (file_exists($abandonedPath) ? $abandonedPath : null);
    $expected = $source ? json_decode((string)@file_get_contents($source), true) : null;
    if (is_array($expected) && (
      ($payment['status'] ?? '') !== 'captured'
      || (int)($payment['amount'] ?? -1) !== (int)($expected['amount'] ?? -2)
      || ($payment['currency'] ?? '') !== 'INR'
    )) {
      booking_alert('payment does not match order', "order=$orderId payment=$paymentId status=" . ($payment['status'] ?? '?')
        . ' amount=' . ($payment['amount'] ?? '?') . ' expected=' . ($expected['amount'] ?? '?'));
      return ['status' => 'mismatch'];
    }
  }

  // A Razorpay order stays payable forever and cron moves unpaid ones to
  // abandoned/ after a day, so a late payment must still find its record.
  $claimed = @rename($pendingPath, $processingPath) || @rename($abandonedPath, $processingPath);
  if (!$claimed) {
    if (file_exists($donePath)) {
      $record = json_decode(file_get_contents($donePath), true);
      return ['status' => 'done', 'reservation_no' => $record['reservation_no'] ?? null, 'sub_reservation_no' => $record['sub_reservation_no'] ?? null];
    }
    if (file_exists($failedPath)) return ['status' => 'failed'];
    return ['status' => 'unknown'];
  }

  $record = json_decode(file_get_contents($processingPath), true);

  if (!empty($record['last_attempt_at']) && time() - (int)$record['last_attempt_at'] < CONFIRM_RETRY_GAP_SECONDS) {
    @rename($processingPath, $pendingPath);
    return ['status' => 'retry'];
  }

  // One Room_N entry per physical room — occupancy and guest identity
  // (title/name/gender) already split per unit by create-order.php.
  $roomDetailsList = [];
  foreach ($record['room_units'] as $unit) {
    $roomDetailsList[] = [
      'Rateplan_Id' => $unit['roomrateunkid'],
      'Ratetype_Id' => $unit['ratetypeunkid'],
      'Roomtype_Id' => $unit['roomtypeunkid'],
      'baserate' => (string)$unit['baserate'],
      'extradultrate' => (string)$unit['extradultrate'],
      'extrachildrate' => (string)$unit['extrachildrate'],
      'number_adults' => (string)$unit['adults'],
      'number_children' => (string)$unit['children'],
      'ExtraChild_Age' => $unit['child_ages'] ?? '',
      'Title' => $unit['title'] ?? '',
      'First_Name' => $unit['first_name'],
      'Last_Name' => $unit['last_name'] ?? '',
      'Gender' => $unit['gender'] ?? '',
      'SpecialRequest' => $unit['special_request'] ?? '',
    ];
  }

  $roomDetails = [];
  foreach ($roomDetailsList as $i => $details) {
    $roomDetails['Room_' . ($i + 1)] = $details;
  }

  $bookingData = [
    'Room_Details' => $roomDetails,
    'check_in_date' => $record['check_in'],
    'check_out_date' => $record['check_out'],
    // Blank here creates the reservation in "Void" status (verified live
    // 2026-08-10) — this account has no eZee-native payment gateway
    // configured (ConfiguredPGList is empty), so any non-blank label works;
    // guest has already paid via Razorpay before this call runs.
    'Booking_Payment_Mode' => 'Online Payment (Razorpay)',
    'Email_Address' => $record['email'],
    'Source_Id' => '',
    'MobileNo' => $record['phone'],
    'Address' => '',
    'State' => '',
    'Country' => $record['nationality'] ?? '',
    'City' => '',
    'Zipcode' => '',
    'Fax' => '',
    'Device' => '',
    'Languagekey' => '',
    'paymenttypeunkid' => '',
  ];

  $insertResponse = ezee_get('InsertBooking', ['BookingData' => json_encode($bookingData)]);

  if (!$insertResponse['_ok'] || empty($insertResponse['ReservationNo'])) {
    $record['attempts'] = ($record['attempts'] ?? 0) + 1;
    $record['last_attempt_at'] = time();
    $record['last_failure'] = json_encode($insertResponse);
    // Retry only when eZee EXPLICITLY rejected the request: an error reply
    // (_ok=false) that is not a transport/5xx failure, or a 429 that was
    // refused before processing. Everything else is ambiguous — a timeout, an
    // unreadable or 5xx reply, or a well-formed reply that simply lacks a
    // ReservationNo (it may have been created) — and retrying risks a double
    // booking, so it goes to a human with the evidence.
    $ambiguous = !empty($insertResponse['_transport']) || !empty($insertResponse['_ok']);
    file_put_contents($processingPath, json_encode($record, JSON_PRETTY_PRINT));
    if (!$ambiguous && $record['attempts'] < MAX_CONFIRM_ATTEMPTS) {
      // Back to pending/: reconcile-pending.php re-polls it, and the fresh
      // mtime gives eZee a few minutes before the next attempt.
      @rename($processingPath, $pendingPath);
      bookings_log("RETRY InsertBooking order=$orderId payment=$paymentId attempt={$record['attempts']} response=" . json_encode($insertResponse));
      return ['status' => 'retry'];
    }
    // Parked for a human: drop the timestamp so a manual re-queue (move the file
    // back to pending/) is attempted immediately instead of waiting out the gap.
    unset($record['last_attempt_at']);
    file_put_contents($processingPath, json_encode($record, JSON_PRETTY_PRINT));
    @rename($processingPath, $failedPath);
    booking_alert('PAID but booking NOT created', "order=$orderId payment=$paymentId amount={$record['total']} email={$record['email']}"
      . ' ambiguous=' . ($ambiguous ? 'yes (check eZee for an existing reservation BEFORE re-queueing)' : 'no')
      . ' response=' . json_encode($insertResponse));
    return ['status' => 'failed'];
  }

  $reservationNo = $insertResponse['ReservationNo'];
  $subReservationNo = $insertResponse['SubReservationNo'][0] ?? $reservationNo;

  // Reconciliation only — doesn't move money, payment is already captured by
  // Razorpay. A failure here doesn't fail the caller.
  if (EZEE_PAYMENT_ID !== '' && EZEE_CURRENCY_ID !== '') {
    $request = [
      'RES_Request' => [
        'Request_Type' => 'AddPayment',
        'Authentication' => ['HotelCode' => EZEE_HOTEL_CODE, 'AuthCode' => EZEE_AUTH_CODE],
        'Reservation' => [[
          'BookingId' => $reservationNo,
          'PaymentId' => EZEE_PAYMENT_ID,
          'CurrencyId' => EZEE_CURRENCY_ID,
          'Payment' => (string)$record['total'],
          'Comment' => 'Razorpay payment ' . $paymentId,
        ]],
      ],
    ];
    // Retried once, because the common failure here is a transient timeout and
    // the consequence of losing it is a reservation eZee believes is UNPAID for
    // money we have already taken — which is how a guest gets asked to pay
    // twice at the front desk. Still non-fatal: the booking itself exists and
    // the guest must not be told it failed.
    // ponytail: one retry, not a queue. If these start failing in pairs, the
    // fix is a proper outbox, not a third attempt.
    $paymentResponse = ezee_add_payment_once($request);
    if (!$paymentResponse['_ok']) {
      sleep(1);
      $paymentResponse = ezee_add_payment_once($request);
    }
    if (!$paymentResponse['_ok']) {
      // Deliberately loud and greppable: this is a manual reconciliation item.
      // Everything needed to post the payment by hand is on this one line.
      booking_alert('ACTION REQUIRED AddPayment failed twice', "reservation=$reservationNo"
        . " payment=$paymentId amount={$record['total']} response=" . json_encode($paymentResponse));
    }
  }

  $record['reservation_no'] = $reservationNo;
  $record['sub_reservation_no'] = $subReservationNo;
  $record['razorpay_payment_id'] = $paymentId;
  $record['confirmed_at'] = date('c');
  file_put_contents($donePath, json_encode($record, JSON_PRETTY_PRINT));
  @unlink($processingPath);
  bookings_log("CONFIRMED order=$orderId reservation=$reservationNo payment=$paymentId total={$record['total']}");

  return ['status' => 'done', 'reservation_no' => $reservationNo, 'sub_reservation_no' => $subReservationNo];
}
