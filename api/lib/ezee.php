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

function ezee_get(string $requestType, array $params): array {
  if (getenv('EZEE_MOCK_ROOMLIST') && in_array($requestType, ['RoomList', 'InsertBooking', 'CancelBooking'], true)) {
    require_once __DIR__ . '/mock.php';
    if ($requestType === 'RoomList') return ezee_mock_roomlist($params);
    if ($requestType === 'CancelBooking') return ezee_mock_cancelbooking($params['ResNo'] ?? '');
    return ezee_mock_insertbooking($params);
  }
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
  if (getenv('EZEE_MOCK_ROOMLIST')) {
    require_once __DIR__ . '/mock.php';
    return ezee_mock_fetchsinglebooking($bookingId);
  }
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
  if (getenv('EZEE_MOCK_ROOMLIST') && ($requestBody['RES_Request']['Request_Type'] ?? '') === 'AddPayment') {
    require_once __DIR__ . '/mock.php';
    return ezee_mock_addpayment($requestBody);
  }
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

  if ($curlErrno !== 0) {
    return ['_ok' => false, '_error' => "eZee request failed: $curlError"];
  }
  if ($httpCode === 429) {
    return ['_ok' => false, '_error' => 'eZee rate limit hit, please try again shortly.', '_rateLimited' => true];
  }
  $decoded = json_decode($response, true);
  if (!is_array($decoded)) {
    return ['_ok' => false, '_error' => "eZee returned an unexpected response (HTTP $httpCode)."];
  }
  if (isset($decoded['Errors']['ErrorMessage'])) {
    return ['_ok' => false, '_error' => 'eZee error: ' . $decoded['Errors']['ErrorMessage']];
  }
  $decoded['_ok'] = true;
  return $decoded;
}
