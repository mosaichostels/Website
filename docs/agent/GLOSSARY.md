Read when: a term in code, alerts or the owner's messages is unclear.
Verified: 2026-10-29 @ fd29588
Covers: -

# Glossary

| Term | Meaning |
|---|---|
| eZee / YCS / IPMS247 | The hotel property-management system and its Connectivity API; source of truth for rooms, rates, reservations |
| RoomList / InsertBooking / AddPayment / CancelBooking / FetchSingleBooking | eZee request types used by `api/lib/ezee.php` |
| `roomtypeunkid`, `ratetypeunkid`, `roomrateunkid` | eZee ids for room type, rate type, rate plan (the booking picks by `roomrateunkid`) |
| Reservation No / sub-reservation | eZee booking number the guest quotes to cancel; one sub-number per room |
| Order | Razorpay order (`order_...`) plus our JSON record in the order store |
| Claim | The atomic `rename()` of an order file into `processing/`; whoever wins books it |
| Confirm paths A/B/C | browser verify-payment, Razorpay webhook, cron reconcile |
| Pending / abandoned / failed / done | order folders (DATA.md) |
| Ambiguous failure | InsertBooking outcome unknown (timeout); never auto-retried |
| Paise | Razorpay amounts in 1/100 rupee, integer math only |
| Sucuri | WAF in front of eZee's account; why InsertBooking is POSTed |
| LSCache | Hostinger LiteSpeed cache module configured in `.htaccess` |
| `?v=` | Cache-bust query on shared JS/CSS |
| F-00xx | SEO finding id in `seo-reports/data/findings-ledger.json` |
| IndexNow | Protocol to push changed URLs to Bing/Yandex/Seznam |
| GEO / LLMO / `llms.txt` | Optimising for AI answer engines; the file that describes the site to them |
| Assi Ghat | Varanasi riverfront, 100 m from the hostel (owner-confirmed) |
| Dorm types | 8-bed mixed, 6-bed mixed, 4-bed mixed, 6-bed female-only; plus Private room |
| OpenMontage | Vendored video tool in `OpenMontage/`; not the site |
