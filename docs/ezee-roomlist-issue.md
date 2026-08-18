# eZee RoomList API — "No Data found" issue

**Status:** Resolved (2026-08-10). eZee-side fix — rooms/rates are now published and RoomList returns live data.
**Last tested:** 2026-08-10

## Endpoint

```
GET https://live.ipms247.com/booking/reservation_api/listing.php
```

## Auth (from `api/secrets.php`)

```
request_type = RoomList
HotelCode    = 57677
APIKey       = 5137190432e4acb9a0-9306-11f1-8
```

## Test 1 — near-future dates, full filter set

Request:
```
https://live.ipms247.com/booking/reservation_api/listing.php?request_type=RoomList&HotelCode=57677&APIKey=5137190432e4acb9a0-9306-11f1-8&check_in_date=2026-08-13&check_out_date=2026-08-14&number_adults=1&number_children=0&num_rooms=1&show_only_available_rooms=1&showtax=1
```

Response (HTTP 200):
```json
{"0":{"Error Details":{"Error_Code":-1,"Error_Message":"No Data found."}},"_ok":true}
```

## Test 2 — no params (auth sanity check)

Request:
```
https://live.ipms247.com/booking/reservation_api/listing.php?request_type=RoomList&HotelCode=57677&APIKey=5137190432e4acb9a0-9306-11f1-8
```

Response:
```json
{"0":{"Error Details":{"Error_Code":"EmptyParameter","Error_Message":"Parameters are empty."}},"_ok":true}
```

Different error code than Test 1 (`EmptyParameter` vs `No Data found`) confirms HotelCode + APIKey are accepted — auth layer passes.

## Test 3 — far-future date (+30 days), relaxed filters

Request:
```
https://live.ipms247.com/booking/reservation_api/listing.php?request_type=RoomList&HotelCode=57677&APIKey=5137190432e4acb9a0-9306-11f1-8&check_in_date=2026-09-09&num_nights=2&number_adults=1&number_children=0&num_rooms=1&property_configuration_info=0&show_only_available_rooms=0&showtax=0
```

Response:
```json
{"0":{"Error Details":{"Error_Code":-1,"Error_Message":"No Data found."}},"_ok":true}
```

## Param name check

`api/availability.php` params cross-checked against eZee's own spec (`docs/eZee-Connectivity-API.md`, lines ~2113-2130):

| Param sent | Matches spec |
|---|---|
| `check_in_date` | yes |
| `check_out_date` | yes |
| `number_adults` | yes |
| `number_children` | yes |
| `num_rooms` | yes |
| `show_only_available_rooms` | yes |
| `showtax` | yes |

No naming mismatch found.

## Conclusion

- HotelCode + APIKey are valid — proven by `EmptyParameter` (bad request shape) vs `No Data found` (valid request, no data) being distinct error codes.
- Param names/format match eZee's documented spec exactly.
- Every date range tested (3 days out, 30 days out) with both strict and relaxed filters returns `Error_Code: -1, "No Data found."`
- Root cause is on eZee's side: room types/rate plans not published to the booking-engine channel, and/or BE-API Lite plan not activated for HotelCode 57677.

## Resolution (2026-08-10)

Re-tested with identical request — same params, same HotelCode/APIKey. eZee now returns live room data instead of "No Data found":

```
Double Room: room_only=1999 tax_incl=2098.95 rack=5000.0000
4 - Bed Mixed Dorm: room_only=649 tax_incl=681.45 rack=3000.0000
6 - Bed Female Dorm: room_only=599 tax_incl=628.95 rack=3500.0000
8 - Bed Mixed Dorm: room_only=499 tax_incl=523.95 rack=300.0000
6 - Bed Mixed Dorm: room_only=549 tax_incl=576.45 rack=4000.0000
```

Nothing changed in this repo's request shape — confirms the earlier root-cause diagnosis (eZee back-office publishing/plan activation) was correct.

## Follow-up bug found once live data arrived

`extract_room_options()` in `api/availability.php` was written defensively before live data existed, and its price-extraction logic didn't match eZee's actual response shape:

- `per_night` read `entry['room_rates_info']['inclusive_tax_adjustment']`, which is a **date-keyed array** (e.g. `{"2026-08-13": 5250}`), not a scalar. Casting an array to `(float)` in PHP produces `1` — every room silently priced at ₹1.
- `total` looked for `totalprice_inclusive_all` / `totalprice_room_only` at the entry's top level, but those keys only exist nested under `room_rates_info`. Always resolved to `null`.

Fixed in `api/availability.php`: `per_night` now reads `room_rates_info.avg_per_night_after_discount` (a true scalar), and `total` reads `room_rates_info.totalprice_inclusive_all`/`totalprice_room_only`, with `reset()` fallback if either is ever date-keyed. Verified against live response — correct prices now returned (e.g. Double Room ₹2099/night, dorms ₹524–681/night).
