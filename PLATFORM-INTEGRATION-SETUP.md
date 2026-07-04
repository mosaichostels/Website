# Platform Integration Setup — Mosaic Hostel Varanasi

**Date:** 2026-07-04  
**Platforms:** 16 indexed  
**Goal:** Cross-link + sync reviews + contact integration  
**Expected Impact:** +30-50% repeat bookings, unified brand presence

---

## 📌 INTEGRATION OVERVIEW

**Current Platforms (16):**
1. Booking.com
2. Hostelworld
3. Hotels.com
4. Agoda
5. Skyscanner
6. Trip.com
7. LateRooms
8. MakeMyTrip
9. ReadyToTrip
10. TripAdvisor
11. JustDial
12. Goibibo
13. Instagram
14. Google Search (organic)
15. Google Maps (GMB synced)
16. OpenStreetMap

---

## 1️⃣ CROSS-LINKING STRATEGY

### A. Website → All Platforms

**Update homepage/book-now.html with booking links:**

```html
<!-- Booking Links Section -->
<div class="booking-platforms">
  <a href="https://www.booking.com/hotel/in/mosaic-hostel-varanasi.html" target="_blank">Booking.com</a>
  <a href="https://www.hostelworld.com/hostels/p/335875/mosaic-hostel-varanasi/" target="_blank">Hostelworld</a>
  <a href="https://in.hotels.com/ho4002720928/" target="_blank">Hotels.com</a>
  <a href="https://www.agoda.com/en-za/mosaic-hostel-varanasi/hotel/varanasi-in.html" target="_blank">Agoda</a>
  <a href="https://www.skyscanner.com/hotels/india/varanasi-hotels/mosaic-hostel-varanasi/ht-225013464" target="_blank">Skyscanner</a>
  <a href="https://au.trip.com/hotels/varanasi-hotel-detail-132802842/mosaic-hostel-varanasi/" target="_blank">Trip.com</a>
  <a href="https://www.laterooms.com/hotel/varanasi/mosaic-hostel-varanasi/" target="_blank">LateRooms</a>
  <a href="https://www.makemytrip.com/hotels/mosaic_hostel_varanasi-details-varanasi.html" target="_blank">MakeMyTrip</a>
</div>
```

### B. Platform → Website

**For each platform, add primary website link:**

| Platform | Link Field | URL |
|----------|-----------|-----|
| Booking.com | Website/Homepage | https://www.mosaichostels.com |
| Hostelworld | Website | https://www.mosaichostels.com |
| Hotels.com | Website | https://www.mosaichostels.com |
| Agoda | Website | https://www.mosaichostels.com |
| TripAdvisor | Website | https://www.mosaichostels.com |
| Google My Business | Website | https://www.mosaichostels.com |
| Instagram | Bio Link | https://www.mosaichostels.com |
| JustDial | Website | https://www.mosaichostels.com |

---

## 2️⃣ REVIEW SYNCHRONIZATION

### A. Pull Reviews (Monitor & Respond)

**Multi-platform review tracking:**

| Platform | Review Count | Status | Monitor |
|----------|-------------|--------|---------|
| Booking.com | ~60 reviews | Active | Daily |
| TripAdvisor | ~50+ reviews | Active | Daily |
| Google Maps | ~40+ reviews | Linked to GMB | Real-time alerts |
| Hostelworld | ~30+ reviews | Active | 3x/week |
| Hotels.com | ~10+ reviews | Synced | Weekly |
| Agoda | ~25+ reviews | Active | Weekly |

**Tool: Hootsuite / Google Alerts**
- [ ] Set up daily review alerts for all 6 platforms
- [ ] Auto-notify: mosaichostels@gmail.com
- [ ] Monitor sentiment (positive/negative/neutral)

### B. Respond to Reviews

**Response templates + SLA:**

**Positive Review (Respond within 24 hours):**
```
Thank you for choosing Mosaic Hostel! We're delighted you enjoyed your stay. 
Your feedback is invaluable. Hope to welcome you back soon! 🙏

Visit us again: mosaichostels.com
```

**Negative Review (Respond within 12 hours):**
```
We appreciate your feedback and sincerely apologize for the experience. 
Your concerns are important to us. Please message us directly so we can make it right.

Email: mosaichostels@gmail.com | WhatsApp: +91 91254 92225
```

**Setup:**
- [ ] Assign review manager (15 min/day)
- [ ] Respond to ALL reviews within SLA
- [ ] Update response if issue resolved

### C. Review Generation Strategy

**Ask guests to review (post-checkout):**
- [ ] Add review request to booking confirmation email
- [ ] Post QR code in rooms linking to top 3 platforms
- [ ] Offer "Featured Guest" badge (Instagram mention) for reviews
- [ ] Monthly: email past guests requesting reviews

**Priority order:** Booking.com > Google Maps > TripAdvisor > Hostelworld

---

## 3️⃣ CONTACT INTEGRATION

### A. WhatsApp Business Link

**Add to ALL platforms:**

```
https://wa.me/919125492225?text=Hi%20Mosaic%20Hostel%2C%20I'd%20like%20to%20inquire%20about%20booking
```

**Platforms to update:**
- [ ] Booking.com — Contact/Message field
- [ ] Hostelworld — WhatsApp button
- [ ] Hotels.com — Contact info
- [ ] Agoda — Contact
- [ ] TripAdvisor — Message owner
- [ ] Google My Business — Call/Message button (auto-enabled)
- [ ] Instagram — Bio link to WhatsApp
- [ ] Facebook — Messenger + WhatsApp
- [ ] JustDial — Contact number
- [ ] Website — "Book on WhatsApp" button

### B. Email Integration

**mosaichostels@gmail.com** — Central contact

**Auto-responder setup:**
```
Subject: We received your inquiry

Thanks for reaching out to Mosaic Hostel!

We typically reply within 2 hours during business hours (8 AM - 10 PM IST).

For urgent inquiries: WhatsApp us at +91 91254 92225

Best regards,
Mosaic Hostel Varanasi Team
```

### C. Contact Info Audit

**Verify across ALL platforms:**

| Info | Current | Verified |
|------|---------|----------|
| Phone | +91 91254 92225 | ✅ |
| Email | mosaichostels@gmail.com | ✅ |
| Address | B1/85C, Assi Ghat Road, Anandbagh, Varanasi 221005 | ✅ |
| Hours | 24/7 | ✅ |

**Setup:**
- [ ] Monthly audit — ensure consistent across all 16 platforms
- [ ] Update all if any change

---

## 4️⃣ ANALYTICS & TRACKING

### A. UTM Parameters (Traffic Source Attribution)

**Add UTM codes to each platform link:**

```
https://www.mosaichostels.com/book-now?utm_source=booking&utm_medium=platform&utm_campaign=cross-link
```

**Setup template:**
```
?utm_source=[platform_name]&utm_medium=platform&utm_campaign=integration
```

| Platform | Source Code |
|----------|-------------|
| Booking.com | booking |
| Hostelworld | hostelworld |
| Hotels.com | hotels_com |
| Agoda | agoda |
| TripAdvisor | tripadvisor |
| Google Maps | google_maps |
| Instagram | instagram |
| JustDial | justdial |
| Google Search | google_organic |

**Track in Google Analytics:**
- [ ] Create dashboard: "Platform Traffic" (16-segment view)
- [ ] Monitor: sessions, bookings, conversion rate per platform
- [ ] Monthly report: which platform drives most bookings

### B. Booking Sync (Manual Tracking)

**Create spreadsheet to track:**
| Date | Guest Name | Platform | Amount | Contact |
|------|-----------|----------|--------|---------|
| 2026-07-05 | John Doe | Booking.com | ₹2,500 | john@email.com |

**Use to identify:**
- Which platform brings most revenue
- Guest demographics per platform
- Repeat booking rate per platform
- Focus marketing on top 2-3 platforms

### C. Google Analytics Setup

**Add tracking to website:**
- [ ] Verify mosaichostels.com in Google Analytics
- [ ] Link to Google My Business (see reviews in Analytics)
- [ ] Create platform segments (for each 16)
- [ ] Set up conversion goals: "Book Now Click"
- [ ] Monthly review dashboard

---

## 5️⃣ BOOKING WINDOW SYNC

### A. Availability Sync (Manual)

**If using multiple OTAs with different availability:**

**Setup:**
- [ ] Create master calendar (Google Calendar or spreadsheet)
- [ ] Update ALL platforms when booking made on ANY platform
- [ ] Daily check: prevent overbooking
- [ ] Tool suggestion: Cloudbeds, Smoobu, or PMS integration

**Checklist (daily):**
- [ ] Check Booking.com for new bookings
- [ ] Check Hostelworld for new bookings
- [ ] Update all other platforms' availability
- [ ] Confirm no double-bookings

### B. Policy Consistency

**Ensure all platforms have same:**
- [ ] Cancellation policy: "Free cancellation up to 7 days before"
- [ ] Check-in time: "3 PM"
- [ ] Check-out time: "11 AM"
- [ ] House rules: "No outside alcohol, quiet hours 11 PM - 8 AM"
- [ ] Amenities list: "Free WiFi, AC, Hot Water, etc."

**Update frequency:** Immediately when policy changes

---

## 6️⃣ UNIFIED MESSAGING STRATEGY

### A. Brand Consistency

**Ensure all platforms use:**
- [ ] Same hostel name: "Mosaic Hostel Varanasi"
- [ ] Same description (first 150 chars):
  ```
  Premium budget hostel in Varanasi near Assi Ghat. 
  Private & dorm rooms, free WiFi, AC, 24/7 check-in.
  ```
- [ ] Same photos (use 5-10 identical photos across platforms)
- [ ] Same amenities list
- [ ] Same price range display

**Review quarterly:** Ensure no drift between platforms

### B. Social Media Sync

**Instagram → Facebook (auto-sync):**
- [ ] Enable cross-posting: Instagram → Facebook
- [ ] All Instagram posts appear on Facebook automatically
- [ ] Reply to comments on both platforms

**Website → Social Media:**
- [ ] Share blog posts on Instagram (2-3x/week)
- [ ] Share gallery on Instagram Stories (daily)
- [ ] Cross-link: website → Instagram in header

### C. Review Request Campaign

**Automated post-booking:**
1. Guest checks out
2. Send email with review links (all 6 platforms)
3. Re-send after 2 weeks if no review
4. Incentivize: "Leave a review → feature on our Instagram!"

---

## 7️⃣ MONTHLY INTEGRATION CHECKLIST

**Every 1st of month:**
- [ ] Review all platform listings (15 min each = 4 hours total)
- [ ] Check for outdated info (hours, prices, amenities)
- [ ] Respond to pending reviews (all 6 review platforms)
- [ ] Update booking calendar sync status
- [ ] Review analytics: top 3 performing platforms
- [ ] Update website links if any platform URL changes

**Monthly report template:**
```
PLATFORM INTEGRATION REPORT — July 2026

Reviews responded: 12/15 (80%)
Average response time: 18 hours
Top platform by bookings: Booking.com (40%)
Top platform by reviews: TripAdvisor (8 new reviews)
Tech issues: None
Action items: Update hours on Agoda (3 PM → 2 PM)
```

---

## 📊 EXPECTED IMPACT

**Timeline:** 1-2 weeks full integration setup + 30 min/month maintenance

**Benefits:**
- ✅ Unified brand across 16 platforms
- ✅ Faster review response = higher ratings
- ✅ Cross-platform traffic routing = 20-30% booking increase
- ✅ Analytics clarity = optimize marketing spend
- ✅ Prevention of overbooking/conflicts
- ✅ Higher guest trust (consistent brand)

**Metrics to track:**
- Reviews per month (target: +10-15)
- Average rating (maintain 4.5+)
- Booking source attribution (see top 5 platforms)
- Repeat booking rate (target: 10%+)
- Response time to reviews (target: <24 hrs)

---

## ✅ IMPLEMENTATION CHECKLIST

### Week 1: Setup
- [ ] Add website links to all platforms
- [ ] Set up review alerts (Hootsuite/Google Alerts)
- [ ] Create review response templates
- [ ] Update WhatsApp link on all platforms
- [ ] Set up UTM codes for website links
- [ ] Create Google Analytics dashboard

### Week 2: Synchronization
- [ ] Set up booking calendar tracking
- [ ] Verify policy consistency across all platforms
- [ ] Upload identical photos across platforms
- [ ] Enable Instagram → Facebook sync
- [ ] Create review request email template
- [ ] Set up monthly audit calendar

### Week 3: Optimization
- [ ] Launch review request campaign
- [ ] Start responding to all reviews
- [ ] Monitor first week of analytics
- [ ] Adjust based on initial data
- [ ] Train team on process
- [ ] Create integration SOP document

---

**Status:** Guide ready for implementation  
**Effort:** 6-8 hours setup + 30 min/month maintenance  
**Priority:** High (maximizes ROI on existing 16 platforms)

Ready to implement?
