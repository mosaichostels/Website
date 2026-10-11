# Impeccable Findings Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task by task.

**Goal:** Resolve the six approved findings without changing booking rules or adding unverified room claims.

**Architecture:** Reuse the gallery's dialog behavior for the home lightbox. Keep room and gallery copy in their existing static pages; keep booking payload fields and server validation intact while simplifying their presentation.

**Tech Stack:** Static HTML, CSS, JavaScript, PHP booking API.

**Spec:** Approved six-item change list in the conversation; product constraints in `PRODUCT.md` and visual rules in `DESIGN.md`.

## Global Constraints

- Preserve the five owner-confirmed bookable room types and treat the common room as shared space.
- Do not invent photos, prices, amenities, or claims.
- Preserve the eZee and Razorpay booking payload and validation.
- Keep booking and WhatsApp paths clear on mobile and desktop.

## Review Focus

- Keyboard users must open, navigate, and close the home lightbox, then return to the trigger.
- A room card must lead toward booking without implying a fixed price or availability.
- The female dorm image must not be represented as a verified photo of that room.
- The mobile menu must announce open and closed state after every close path.
- Optional guest details must remain sendable when entered and skippable when empty.

## Tasks

### 1. Home room lightbox and mobile menu

**Files:** `components/home.js`, `index.html`, `components/navbar.js`, browser interaction checks.

- [x] Reproduce the missing keyboard and menu-state behavior.
- [x] Reuse the gallery's dialog pattern on the home lightbox and synchronize `aria-expanded` in every menu transition.
- [x] Verify keyboard open, navigation, Escape, focus return, and mobile menu state.

### 2. Accurate room comparison and gallery labels

**Files:** `index.html`, `gallery.html`, `styles/global.css`, browser layout checks.

- [x] Check the current desktop and mobile room/gallery presentation.
- [x] Separate the common room visually, link each bookable room toward booking, label the female dorm image as representative, and use room-specific gallery labels supported by the images.
- [x] Verify links, captions, image descriptions, and layouts at desktop and mobile widths.

### 3. Booking details hierarchy

**Files:** `book-now.html`, `components/book-now.js` only if necessary, browser booking-form checks.

- [x] Confirm optional fields against `api/create-order.php` and current JavaScript payload.
- [x] Keep required guest/contact inputs prominent and move optional details into a clearly labeled secondary group without altering payloads.
- [x] Verify field requirements, optional value retention, keyboard access, and responsive layout; live payment submission requires configured eZee and Razorpay services.

### 4. Final verification

- [x] Run relevant syntax or static checks and one desktop/mobile browser inspection batch.
- [x] Run the Impeccable detector once over changed web targets, triage genuine findings, and inspect the final diff.
