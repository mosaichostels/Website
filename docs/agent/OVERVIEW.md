Read when: you need the product goal, audience, room lineup or repo basics before touching anything.
Verified: 2026-10-29 @ c019c06
Covers: PRODUCT.md,sitemap.xml,.htaccess

# Overview

| Item | Fact | Source |
|---|---|---|
| Product | Mosaic Hostel Varanasi direct-booking site, "Premium budget hostel near Assi Ghat", est. 2025 | `PRODUCT.md` |
| Success | A completed direct booking (eZee availability + Razorpay payment) or a WhatsApp enquiry, no OTA | `PRODUCT.md` |
| Audience | International backpackers and solo travellers (incl. solo women) and domestic Indian travellers, equal weight, mostly mobile, arriving via Google and the blog | `PRODUCT.md` |
| Rooms (owner-confirmed) | Private room; 8-bed mixed; 6-bed mixed; 4-bed mixed; 6-bed female-only dorm. Common room is NOT a room type | `PRODUCT.md` |
| Policies | Check-in from 1:00 PM, check-out by 10:30 AM, 24-hour reception, free cancellation up to 72 h before check-in (charged in full inside), valid govt photo ID per guest | `PRODUCT.md` |
| Contact channel | WhatsApp is first-class (number in `PRODUCT.md`) | `PRODUCT.md` |
| Live site | https://www.mosaichostels.com (apex and http redirect 301 to https www) | `.htaccess` |
| Remote | github.com/mosaichostels/Website, `main`; local `main` level with `origin/main` at c019c06 (2026-10-29) | `git status -sb` |
| Hosting | Hostinger, FTP deploy (manual) | `scripts/deploy.sh` |

## Pages (24 URLs in `sitemap.xml`)
- Core: `/`, `/dorms/`, `/gallery`, `/about`, `/contact`, `/book-now`, `/privacy`, plus `404.html` (noindex).
- Blog: `/blog/` listing + 16 posts under `/blog/<slug>/` (all in `sitemap.xml`).
- `/dorms/` added 2026-10-23 (F-0058) for "dormitory near Assi Ghat" queries; linked from `index.html` and `llms.txt`, not from `components/navbar.js`.

## Brand
Name and tile idea ("Each guest is a piece. Each story is a tile.") are in use; palette and type are in `DESIGN.md` (incumbent, not declared binding).

## Product principles (from `PRODUCT.md`)
1. Direct booking is the primary conversion. 2. Serve international and domestic guests equally. 3. State trust/safety plainly. 4. Only owner-backed proof. 5. Preserve SEO-established positioning/copy structure.

## Open product questions
WCAG AA as a formal requirement: undecided. FTP/Hostinger stack "assumed to continue", not declared binding.
