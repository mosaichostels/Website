<?php
/**
 * Thin wrappers around eZee's YCS Connectivity API. Two call shapes:
 * GET-style (RoomList, InsertBooking) authenticate via HotelCode+APIKey
 * querystring params. POST-style (AddPayment) authenticate via a
 * HotelCode+AuthCode pair inside a JSON "Authentication" block.
 */

/**
 * eZee's date-keyed rate fields (e.g. {"2026-08-13": "500.0000"}) collapse to a
 * single scalar for single-night-rate lookups; already-scalar values pass through.
 */
function ezee_price_scalar($val): float {
  if (is_array($val)) return (float)(reset($val) ?: 0);
  return (float)$val;
}

/**
 * Stay total (tax-inclusive where eZee gives it) for one room entry.
 *
 * eZee puts this EITHER nested under room_rates_info OR at the entry's top
 * level, depending on account configuration. Both are checked here, in one
 * place, because availability.php and create-order.php must agree: when they
 * disagreed, search rendered a price from the top level that checkout then
 * couldn't resolve, and every booking died on a 502 after the guest had filled
 * in the whole form. Add a location here, never in a caller.
 */
function ezee_room_total(array $entry): ?float {
  $rates = $entry['room_rates_info'] ?? [];
  $total = $rates['totalprice_inclusive_all']
    ?? $rates['totalprice_room_only']
    ?? $entry['totalprice_inclusive_all']
    ?? $entry['totalprice_room_only']
    ?? null;
  return $total === null ? null : round(ezee_price_scalar($total), 2);
}

/** Room-only (pre-tax) stay total — same dual-location lookup as ezee_room_total(). */
function ezee_room_base_total(array $entry): ?float {
  $rates = $entry['room_rates_info'] ?? [];
  $base = $rates['totalprice_room_only'] ?? $entry['totalprice_room_only'] ?? null;
  return $base === null ? null : round(ezee_price_scalar($base), 2);
}

/**
 * Walk a decoded eZee response and collect every associative array that looks
 * like a room-rate entry (has roomtypeunkid + roomrateunkid). The nesting
 * varies by account configuration, so this doesn't assume one exact shape.
 */
function ezee_find_room_entries(array $data, array &$found) {
  if (isset($data['roomtypeunkid']) && isset($data['roomrateunkid'])) {
    $found[] = $data;
    return; // don't recurse further into a matched entry
  }
  foreach ($data as $value) {
    if (is_array($value)) ezee_find_room_entries($value, $found);
  }
}

/** Nights between two valid YYYY-MM-DD dates (check-out day not counted). */
function ezee_nights(string $checkIn, string $checkOut): int {
  return (int)(new DateTime($checkIn))->diff(new DateTime($checkOut))->days;
}

/**
 * eZee's InsertBooking refuses ANY multi-night stay unless baserate, extradultrate and extrachildrate each hold one
 * comma-separated value per night, in date order ("2099,2099,2099,2099,3500"). Verified live 2026-10-27: a single number,
 * the stay total, a dated map, or a list for baserate only were all refused with InvalidData, which left every multi-night
 * guest paid but without a reservation. RoomList gives these rates date-keyed. A flat scalar repeats for each night.
 * Returns null when the rates cannot be matched to the nights; the caller refuses the order rather than guess a price.
 */
function ezee_daywise_rates($rate, int $nights): ?string {
  if (is_array($rate)) {
    ksort($rate);
    $values = array_values($rate);
  } elseif (is_numeric($rate)) {
    $values = array_fill(0, max(0, $nights), $rate);
  } else {
    return null;
  }
  if ($nights < 1 || count($values) !== $nights) return null;
  foreach ($values as $v) if (!is_numeric($v)) return null;
  return implode(',', array_map(fn ($v) => (string)(float)$v, $values));
}

function ezee_get(string $requestType, array $params): array {
  $query = array_merge([
    'request_type' => $requestType,
    'HotelCode' => EZEE_HOTEL_CODE,
    'APIKey' => EZEE_API_KEY,
  ], $params);
  $url = EZEE_BASE_URL . 'booking/reservation_api/listing.php';
  // InsertBooking's BookingData JSON pushes the GET query string past a
  // length this account's WAF (Sucuri) silently rejects — every GET attempt
  // returned a generic ParametersMissing regardless of payload content, even
  // with BookingData omitted entirely. POST form body to the same endpoint
  // works (verified live 2026-08-10). Docs say GET; this account needs POST.
  if ($requestType === 'InsertBooking') {
    return ezee_curl($url, null, $query);
  }
  return ezee_curl($url . '?' . http_build_query($query), null);
}

/**
 * FetchSingleBooking — different endpoint + auth shape (HotelCode+AuthCode
 * in a JSON Authentication block) than RoomList/InsertBooking/CancelBooking,
 * which all share the querystring HotelCode+APIKey endpoint via ezee_get().
 */
function ezee_fetch_booking(string $bookingId): array {
  $requestBody = [
    'RES_Request' => [
      'Request_Type' => 'FetchSingleBooking',
      'BookingId' => $bookingId,
      'Authentication' => ['HotelCode' => EZEE_HOTEL_CODE, 'AuthCode' => EZEE_AUTH_CODE],
    ],
  ];
  $url = EZEE_BASE_URL . 'pmsinterface/pms_connectivity.php';
  return ezee_curl($url, json_encode($requestBody));
}

function ezee_post_json(array $requestBody): array {
  $url = EZEE_BASE_URL . 'index.php/page/service.kioskconnectivity';
  return ezee_curl($url, json_encode($requestBody));
}

function ezee_curl(string $url, ?string $jsonBody, ?array $formFields = null): array {
  $ch = curl_init($url);
  curl_setopt_array($ch, [
    CURLOPT_RETURNTRANSFER => true,
    CURLOPT_TIMEOUT => 15,
    CURLOPT_CONNECTTIMEOUT => 5,
  ]);
  if ($jsonBody !== null) {
    curl_setopt($ch, CURLOPT_POST, true);
    curl_setopt($ch, CURLOPT_POSTFIELDS, $jsonBody);
    curl_setopt($ch, CURLOPT_HTTPHEADER, ['Content-Type: application/json']);
  } elseif ($formFields !== null) {
    curl_setopt($ch, CURLOPT_POST, true);
    curl_setopt($ch, CURLOPT_POSTFIELDS, http_build_query($formFields));
  }
  $response = curl_exec($ch);
  $curlErrno = curl_errno($ch);
  $curlError = curl_error($ch);
  $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);

  // _transport marks failures where we cannot know whether eZee acted on the
  // request (timeout, dropped connection, garbage reply). InsertBooking
  // callers must NOT blindly retry those — the reservation may already exist.
  if ($curlErrno !== 0) {
    return ['_ok' => false, '_transport' => true, '_error' => "eZee request failed: $curlError"];
  }
  return ezee_interpret_response($httpCode, $response);
}

/**
 * The message when a decoded eZee reply is a rejection, else null. eZee reports one in several
 * shapes, and only the first used to be recognised — the others came back "_ok", so a refused
 * InsertBooking was filed as ambiguous (no retry, no reason). Seen live:
 *   {"Errors":{"ErrorMessage":"..."}}                                       RoomList and friends
 *   {"ErrorCode":"InsertBookingFailed","ErrorDescription":"..."}            2026-08-29
 *   {"0":{"Error Details":{"Error_Code":"InvalidData","Error_Message":"..."}}}   2026-09-27, 2026-10-26
 * AddPayment's own Errors LIST (ErrorCode "0" = success) is deliberately not touched here:
 * ezee_add_payment_once() reads it.
 */
function ezee_decoded_error(array $decoded): ?string {
  if (isset($decoded['Errors']['ErrorMessage'])) {
    return 'eZee error: ' . $decoded['Errors']['ErrorMessage'];
  }
  if (!empty($decoded['ErrorCode']) && $decoded['ErrorCode'] !== '0') {
    return 'eZee error: ' . $decoded['ErrorCode'] . ' - ' . ($decoded['ErrorDescription'] ?? '');
  }
  $details = $decoded['0']['Error Details'] ?? null;
  if (is_array($details)) {
    return 'eZee error: ' . ($details['Error_Code'] ?? '') . ' - ' . ($details['Error_Message'] ?? '');
  }
  return null;
}

/** HTTP status + body of an eZee reply -> the array every caller reads (_ok, _transport, _error). Pure, so selftest.php can feed it real replies. */
function ezee_interpret_response(int $httpCode, $response): array {
  if ($httpCode === 429) {
    return ['_ok' => false, '_error' => 'eZee rate limit hit, please try again shortly.', '_rateLimited' => true];
  }
  // A 5xx means the gateway or eZee itself failed; whatever JSON came back says
  // nothing about whether the request was acted on.
  if ($httpCode >= 500) {
    return ['_ok' => false, '_transport' => true, '_error' => "eZee returned HTTP $httpCode."];
  }
  $decoded = json_decode((string)$response, true);
  if (!is_array($decoded)) {
    return ['_ok' => false, '_transport' => true, '_error' => "eZee returned an unexpected response (HTTP $httpCode)."];
  }
  $error = ezee_decoded_error($decoded);
  if ($error !== null) {
    // A coded rejection (InvalidData, past ArrivalDate...) repeats identically on every retry, so confirm_paid_order()
    // parks it at once. The plain Errors.ErrorMessage reply may be transient and keeps the normal retries.
    return ['_ok' => false, '_error' => $error, '_permanent' => !isset($decoded['Errors']['ErrorMessage'])];
  }
  $decoded['_ok'] = true;
  return $decoded;
}
