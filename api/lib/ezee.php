<?php
/**
 * Thin wrappers around eZee's YCS Connectivity API. Two call shapes:
 * GET-style (RoomList, InsertBooking) authenticate via HotelCode+APIKey
 * querystring params. POST-style (AddPayment) authenticate via a
 * HotelCode+AuthCode pair inside a JSON "Authentication" block.
 */

function ezee_get(string $requestType, array $params): array {
  if (getenv('EZEE_MOCK_ROOMLIST') && in_array($requestType, ['RoomList', 'InsertBooking'], true)) {
    require_once __DIR__ . '/mock.php';
    if ($requestType === 'RoomList') return ezee_mock_roomlist($params);
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
  $decoded['_ok'] = true;
  return $decoded;
}
