# eZee Charge Posting Integration — Analysis

Date: 2026-08-11
Status: analysis only, not implemented

## Goal

Automatically post cafe order charges to the guest's eZee folio instead of staff manually adding a Room Charge and typing the item list into Remarks in the eZee UI.

## Constraint

Subscription covers eZee Absolute and Centrix only — no eZee Optimus. This rules out the F&B module (`/v1/service/menu`, `/v1/service/orders`, etc.) which requires Optimus. All API references below were checked against `docs/eZee-Connectivity-API.md` to confirm they sit outside the Optimus-gated F&B section (only lines 10944–11733 of that doc mention Optimus).

## eZee API options evaluated

| API | Category | Optimus required | Fit |
|---|---|---|---|
| `chargepost` (Post Charge To Room) | POS Connectivity | No | **Chosen.** Built for exactly this case: restaurant charge billed to room, freeform `charge` + `remark` fields, tax-inclusive/exclusive amounts. |
| `voidcharge` | POS Connectivity | No | Reversal path for a bad `chargepost` call (uses `requestid` from the post response). |
| `roomlist` / `roomquery` | POS Connectivity | No | Look up in-house room/folio (`room`, `masterfolio`, `guestname`, `resno`) before posting. |
| `AddExtraCharge` | Kiosk Connectivity | No | Works but needs a pre-defined `ChargeId` (fixed price/qty extra) — worse fit for a variable-price, variable-item cafe order than `chargepost`. |
| F&B `/orders`, `/menu` | eZee Optimus | Yes | Not usable — read-only pull APIs, and gated behind Optimus which we don't have. |

`chargepost` endpoint: `https://live.ipms247.com/index.php/page/service.pos2pms`, XML, `oprn=chargepost`. Response is async — returns `status=ok` + `requestid`, not an instant confirmation. Needs the outlet ("Cafe") pre-registered on eZee's side (POS2PMS setup), or the call fails with "POS2PMS account is not setup at PMS end."

## Current app architecture (relevant to this integration)

Three clients share one Spring Boot backend (`mosaichostels-cafe_backend`) over a JWT-authenticated REST API:

- Guest website (`mosaichostels-cafe_frontend/js/user.js`) — order placement
- Android app (`mosaichostels-cafe_android`) — order placement + staff delivery flow
- Admin web (`mosaichostels-cafe_frontend/js/admin.js`) — staff order management

Order lifecycle (`Order.status`, backend `OrderService.java`):

```
ORDERED → DELIVERED → CHECKED
   ↓
CANCELLED (any point before CHECKED)
```

- `ORDERED`: guest places order via website or Android app → `POST /orders` → `OrderService.createOrder()` reprices server-side from DB (client-sent prices are never trusted) → FCM push to staff.
- `DELIVERED`: staff marks delivered from the Android app (`OrdersFragment`).
- `CHECKED`: staff marks checked from the admin web (`AdminApp.markAsChecked`). This is the existing manual-billing checkpoint — status is `locked:false` in `mongodb-init.js`, the one custom status layered on top of the core ORDERED/DELIVERED/CANCELLED set, added specifically as the "billed to guest" step.

Both the Android "mark delivered" action and the admin web "mark checked" action call the same backend endpoint: `PUT /orders/{id}/status` → `OrderService.updateOrderStatus()` (`OrderService.java:117`).

## Integration point

Add the `chargepost` call inside `OrderService.updateOrderStatus()`, gated on the new status being `CHECKED`. Single change point in the backend — no duplication needed across Android app or admin web, since both already route through this one method.

## Field mapping (order → chargepost)

| Order field | eZee `chargepost` field |
|---|---|
| `order.bookingName` | `guestname` — match against `roomlist` response to resolve `room`/`masterfolio` |
| `order.dormitory` | `room` / `folio` (`masterfolio`) — **see gap below** |
| `order.items` (name × qty × subtotal) | `remark` — same item-list string staff types manually today |
| `order.totalAmount` | `amount` (excl. tax) / `tax` / `gross_amount` (incl. tax) |
| `order.id` | `voucherno` |
| today's date | `postingdate`, `trandate` |
| staff username from `updatedBy` | `posuser` |

## Open gap

`order.dormitory` is a free-text display string from the app's own config (e.g. `"101 - Private Room"`, `"8 - Bed Mixed Dorm"`) — there's no existing mapping to eZee's actual room name/number. Two options:

1. Add a config table: app dormitory name → eZee room id/name. Reliable, one-time setup, needs maintenance when rooms change.
2. At CHECKED-time, call `roomlist` and fuzzy-match on `guestname` instead of relying on `dormitory` at all. No extra data entry, but ambiguous if two in-house guests share a similar name.

Recommend option 1 (explicit mapping table) for correctness — posting a charge to the wrong guest's folio is the failure mode to avoid.

## Not yet decided / needed before implementation

- Confirm exact `charge` category string eZee expects for the existing "Room Charge" postings (may not literally be `"Restaurant Charge"` — check what's selected in the eZee UI dropdown when done manually).
- Get sandbox hotel code + auth token from eZee to test `roomlist` against real in-house data before wiring `chargepost`.
- Confirm POS2PMS module is enabled on the account (separate toggle from Optimus).
- Decide handling for async failure: `chargepost` queues the post, doesn't confirm immediately — need a way to detect and alert staff if the queued post ultimately fails (folio not found, credit limit, tax mapping mismatch, etc.), since order status is already CHECKED in our own DB by then.
