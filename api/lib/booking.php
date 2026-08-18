<?php
/**
 * Shared "turn a paid Razorpay order into an eZee reservation" logic — used
 * by both the client-triggered verify-payment.php and the server-to-server
 * razorpay-webhook.php backstop. Same atomic rename() claim either way, so
 * whichever caller gets there first wins and the other sees done/failed.
 */
require_once __DIR__ . '/ezee.php';

function confirm_paid_order(string $orderId, string $paymentId): array {
  ensure_pending_dirs();
  $pendingPath = PENDING_ORDERS_DIR . '/pending/' . $orderId . '.json';
  $processingPath = PENDING_ORDERS_DIR . '/processing/' . $orderId . '.json';
  $donePath = PENDING_ORDERS_DIR . '/done/' . $orderId . '.json';
  $failedPath = PENDING_ORDERS_DIR . '/failed/' . $orderId . '.json';

  if (!@rename($pendingPath, $processingPath)) {
    if (file_exists($donePath)) {
      $record = json_decode(file_get_contents($donePath), true);
      return ['status' => 'done', 'reservation_no' => $record['reservation_no'] ?? null, 'sub_reservation_no' => $record['sub_reservation_no'] ?? null];
    }
    if (file_exists($failedPath)) return ['status' => 'failed'];
    return ['status' => 'unknown'];
  }

  $record = json_decode(file_get_contents($processingPath), true);

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
    @rename($processingPath, $failedPath);
    bookings_log("FAILED InsertBooking order=$orderId payment=$paymentId response=" . json_encode($insertResponse));
    return ['status' => 'failed'];
  }

  $reservationNo = $insertResponse['ReservationNo'];
  $subReservationNo = $insertResponse['SubReservationNo'][0] ?? $reservationNo;

  // Reconciliation only — doesn't move money, payment is already captured by
  // Razorpay. A failure here doesn't fail the caller.
  if (EZEE_PAYMENT_ID !== '' && EZEE_CURRENCY_ID !== '') {
    $paymentResponse = ezee_post_json([
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
    ]);
    if (!$paymentResponse['_ok'] || !empty($paymentResponse['Errors'][0]['ErrorCode'])) {
      bookings_log("WARN AddPayment failed reservation=$reservationNo response=" . json_encode($paymentResponse));
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
