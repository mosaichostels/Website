<?php
/**
 * Mock eZee RoomList response — used only when the EZEE_MOCK_ROOMLIST env
 * var is set, to unblock building/testing the rest of the booking flow
 * while the real RoomList "No Data found" issue (BE-API Lite account scope)
 * is unresolved. Room type names match Mosaic's real RoomTypeList response.
 * Remove this + its call site in ezee_get() once RoomList works for real.
 */
function ezee_mock_roomlist(array $params): array {
  $checkIn = new DateTime($params['check_in_date']);
  $checkOut = new DateTime($params['check_out_date']);
  $nights = max(1, $checkIn->diff($checkOut)->days);

  $roomTypes = [
    ['id' => '187270000000000101', 'name' => '4-Bed Mixed Dorm', 'desc' => 'Shared dorm bed, lockers, AC.', 'rate' => 550, 'avail' => 4],
    ['id' => '187270000000000102', 'name' => '6-Bed Mixed Dorm', 'desc' => 'Shared dorm bed, lockers, AC.', 'rate' => 499, 'avail' => 6],
    ['id' => '187270000000000103', 'name' => '6-Bed Female Dorm', 'desc' => 'Female-only dorm bed, lockers, AC.', 'rate' => 520, 'avail' => 3],
    ['id' => '187270000000000104', 'name' => '8-Bed Mixed Dorm', 'desc' => 'Shared dorm bed, lockers, AC.', 'rate' => 450, 'avail' => 8],
    ['id' => '187270000000000105', 'name' => 'Double Room', 'desc' => 'Private double room, ensuite bathroom, AC.', 'rate' => 1500, 'avail' => 2],
  ];

  $rooms = [];
  foreach ($roomTypes as $i => $rt) {
    $total = $rt['rate'] * $nights;
    $rooms['Room_' . $i] = [
      'roomtypeunkid' => $rt['id'],
      'ratetypeunkid' => $rt['id'] . '1',
      'roomrateunkid' => $rt['id'] . '2',
      'Roomtype_Name' => $rt['name'],
      'Room_Description' => $rt['desc'],
      'inclusive_tax_adjustment' => (string)$rt['rate'],
      'exclusive_tax' => (string)round($rt['rate'] * 0.95, 2),
      'totalprice_inclusive_all' => (string)$total,
      'totalprice_room_only' => (string)round($total * 0.95, 2),
      'available_rooms' => $rt['avail'],
      'room_rates_info' => ['exclusive_tax' => (string)round($rt['rate'] * 0.95, 2)],
      'extra_adult_rates_info' => ['exclusive_tax' => '0'],
      'extra_child_rates_info' => ['exclusive_tax' => '0'],
    ];
  }

  return array_merge(['_ok' => true, '_mock' => true], $rooms);
}

/**
 * Mock InsertBooking — critical that this never hits the real eZee API in
 * mock mode, since real InsertBooking creates a live reservation on the
 * production hotel account even with fake guest data.
 */
function ezee_mock_insertbooking(array $params): array {
  $resNo = 'MOCK' . substr((string)time(), -6);
  return ['_ok' => true, '_mock' => true, 'ReservationNo' => $resNo, 'SubReservationNo' => [$resNo], 'Inventory_Mode' => 'ALLOCATED'];
}

function ezee_mock_addpayment(array $requestBody): array {
  return ['_ok' => true, '_mock' => true, 'Success' => ['SuccessMsg' => 'Mock payment recorded'], 'Errors' => [['ErrorCode' => '0', 'ErrorMessage' => 'Success']]];
}
