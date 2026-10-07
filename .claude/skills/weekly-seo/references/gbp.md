# Google Business Profile (GBP)

> Added 2026-10-07. Facts about the world: overwrite when re-verified. Dated numbers are a snapshot; the newest report in seo-reports/ has current values.

## Extractor

`.claude/seo/gbp-extract.py [days]` (run by `extract-all.sh`, step (b)) pulls the profile, attributes, Voice of Merchant, place action links, all reviews, daily performance (8 metrics, 3-day lag) and monthly keywords with GET requests only, then prints a gap analysis. Bundle: `seo-reports/gbp/<date>.json`; `normalize.py` writes `seo-reports/data/<date>/gbp.metrics.json` (impressions by surface, website clicks, calls, direction requests, bookings, rating, review count, unanswered reviews), so `deltas.py` and the coverage ledger include it. It authenticates with the authorized-user OAuth file in `GBP_CREDENTIALS_FILE` (default `~/.config/gcloud/application_default_credentials.json`) and does **not** need the MCP, so an MCP outage does not block it. The `mosaic-gbp` MCP is still the tool for writes and ad-hoc reads below.

## Access

- MCP `mosaic-gbp` (Node, `~/.local/share/mosaic-seo/gbp-mcp/index.ts`, launched by `~/.config/mosaic-seo/mcp/gbp.sh` with the gcloud ADC file). It is outside the repo and is not git-tracked.
- Account `115700488226449879148` ("Mosaic Hostels", type PERSONAL, shows UNVERIFIED but the location has `hasVoiceOfMerchant: true`, so the profile is live on Google).
- Location `188127158281998203` "Mosaic Hostel Varanasi". Place id `ChIJkZttFu8xjjkRO8yKCXATQZY`, Maps CID `10826956351092739131`.

## Read calls that work

`list_accounts`, `list_locations` (needs `read_mask`), `get_location` (needs `read_mask`, e.g. `name,title,profile,websiteUri,phoneNumbers,regularHours,serviceItems,openInfo,latlng,storefrontAddress`), `get_location_attributes` (parameter is `location_name`), `list_reviews` (v4; `page_size` up to 100 but pages come back at about 50; follow `next_page_token`; `order_by` `updateTime desc`), `get_multi_daily_metrics`, `search_keyword_impressions` (monthly counts), `list_place_action_links`, `get_voice_of_merchant_state`.

- `get_multi_daily_metrics` over ~90 days is too large for the transcript; it is auto-saved to a file. Total it with a short Bash `python3` script (the `ctx_execute_file` tool refuses paths outside the project).
- Review responses over ~50 are also saved to a file; parse them with Python.

## Snapshot 2026-10-07

- Profile: categories Backpacker Hostel (primary) plus Inn, Cafe, Youth Hostel; open 24 h every day; website `https://www.mosaichostels.com/`; phone 091254 92225; address matches the site; no special hours.
- Reviews: **4.5 average, 71 reviews** (the site markup says 4.8 / 427, an owner-confirmed cross-platform figure, see `fix.md`). Of the 71, 64 already had owner replies and the 7 newest-unanswered ones were answered on 2026-10-07.
- Performance 9 Jul to 5 Oct: about 20.8k impressions (mobile search 12.7k, mobile Maps 6.7k, desktop 1.5k), 376 direction requests, 144 call clicks, 26 website clicks, 0 bookings. GBP is the largest local discovery surface; calls and directions far outnumber website clicks.
- Top keywords Jul to Sep: "hostels in varanasi" 1,450, "hotels" 1,444, "hostel in varanasi" 916, "mosaic" 603, "hostel" 444, "hostel in banaras" 305.
- Attributes set: welcomes_lgbtq, url_instagram, url_whatsapp. No amenity, language or check-in attributes. No place action link (no Book button).

## Issues found

- `serviceItems` carry prices (4 dorm items at INR 549, Private Room INR 2599). This conflicts with the owner's no-price rule of 2026-10-07 (see `fix.md`). Not changed: waiting for the owner.
- WhatsApp attribute pointed at `wa.me/9125492225` (no country code, wrong number). **Fixed 2026-10-07** to `https://wa.me/919125492225`.
- Business description is empty and **cannot be set through the API**: `update_location` with `profile` returns 400 `LODGING_CANNOT_EDIT_PROFILE_DESCRIPTION` (lodging listings lock it). A 489-character draft from site facts exists in the 2026-10-07 session; the owner can try the dashboard.

## Write calls and pitfalls

Writes run only when the owner asks for that exact action (see the MCP rule in SKILL.md).

- `reply_to_review`: **fixed 2026-10-07**. The MCP used `PATCH .../reviews/{id}:updateReply`, which Google answers with 404 for every review; it now uses `PUT .../reviews/{id}/reply` (and `DELETE .../reply` for removal). The MCP process must be reconnected (`/mcp`) to load the patch.
- Review ids are long and case-sensitive. Copy them from the saved data; never retype. A single dropped letter gives 404 `Requested entity was not found`.
- `update_location_attributes` takes `attribute_mask` (names) plus `attributes` with `uriValues` for URL attributes.
- `update_location` needs an `update_mask` matching the body.

## Owner's reply voice (use for any future reply)

Thank the guest by name; echo one specific thing they said; keep replies short for short reviews; for 3 stars or less apologise sincerely and invite them to contact the hostel directly; end with a hope to welcome them back. No emoji, no prices, no claims the reviewer did not make. Seven replies in this voice were posted on 2026-10-07 (Rajat, Satabdi, Dishant, Sonu, "The Dramatic Things", Shashikant, "shukla sir5").

## Lodging data: amenities, languages, hours (2026-10-07)

For this lodging listing Google allows only 10 normal attributes (LGBTQ+ friendly, Facebook/Instagram/LinkedIn/Pinterest/X/YouTube/WhatsApp links, texting number, preferred chat app). Amenities, languages spoken and check-in times live in the **My Business Lodging API** (`mybusinesslodging.googleapis.com/v1/locations/<id>/lodging`), which the `mosaic-gbp` MCP does not wrap, so it is called directly with the same OAuth login (it must be enabled in the Google Cloud project; the owner enabled it on 2026-10-07).

- Read needs `readMask` (`*` works). Update is `PATCH ...?updateMask=<field paths>` and the body **must include `metadata.updateTime`** (any current UTC timestamp) plus `name`. `allUnits` and `someUnits` are output-only (derived from `guestUnits`); set room features through `guestUnits` instead. Repeated fields such as `languagesSpoken` are replaced whole.
- Set on 2026-10-07 from site facts: `connectivity.wifiAvailable` and `freeWifi`, `services.twentyFourHourFrontDesk` and `frontDesk`, `services.languagesSpoken` = English and Hindi, `commonLivingArea.eating.kitchenAvailable`, `policies.checkinTime` 13:00 and `checkoutTime` 10:30. The record was empty before. Not set (not clearly stated on the site or needs `guestUnits`): air conditioning, in-room showers, baggage storage, rooftop.
- There is no "Book a room" place action type (types are appointment, food ordering/delivery/takeout, dining reservation, shop online), so a Book button is not available through the profile API; booking buttons come through Google's hotel programme.

