---
name: Mosaic Hostel Varanasi
description: Warm parchment, gold and jewel-tone tiles for a hostel steps from Assi Ghat.
colors:
  gold: "#C8860A"
  gold-light: "#E8B84B"
  gold-pale: "#FBF0D8"
  ghat-teal: "#1A6B7A"
  burgundy: "#8B1A1A"
  cobalt: "#1A3A6B"
  brown: "#5C3A1E"
  sage: "#3D6B3A"
  ink: "#1A1208"
  cream: "#FAF4EA"
  parchment: "#F2E8D5"
  muted: "#7A6A50"
  whatsapp: "#25D366"
typography:
  display:
    fontFamily: "Cinzel, serif"
    fontSize: "48px"
    fontWeight: 400
    lineHeight: 1.05
    letterSpacing: "3px"
  headline:
    fontFamily: "'Cormorant Garamond', serif"
    fontWeight: 300
  body:
    fontFamily: "Jost, sans-serif"
    fontWeight: 300
  label:
    fontFamily: "Jost, sans-serif"
    fontSize: "10px"
    fontWeight: 400
    letterSpacing: "5px"
rounded:
  hairline: "1px"
  sm: "2px"
  md: "4px"
  lg: "8px"
  xl: "12px"
components:
  button-gold:
    backgroundColor: "{colors.gold}"
    textColor: "#ffffff"
    typography: "{typography.label}"
    rounded: "{rounded.hairline}"
    padding: "16px 56px"
  button-light:
    textColor: "#ffffff"
    typography: "{typography.label}"
    padding: "13px 40px"
---

# Design System: Mosaic Hostel Varanasi

## Overview

**Creative North Star: "The Ghat Tile Mosaic"**

The site reads as warm parchment laid with small tiles of gold and jewel colour, echoing the brand idea that each guest is a piece and each story a tile. Serif display type in wide-tracked capitals gives a ceremonial, temple-city tone; light-weight Jost keeps body copy calm and modern for backpackers.

Surfaces are flat and sharp. Corners are near-square, buttons are small wide-tracked uppercase labels, and depth appears as large, diffuse, warm-brown shadows on cards and hover states rather than hard edges.

**Key Characteristics:**
- Cream and parchment grounds with a single dominant gold accent.
- Jewel tones (teal, burgundy, cobalt, sage) used as tile colours, not as UI chrome.
- Cinzel capitals with generous letter-spacing; Cormorant Garamond italics for warmth.
- Large soft shadows, tiny corner radii.
- Custom cursor on desktop (`cursor:none`), disabled for touch via `(hover:none),(pointer:coarse)`.

## Colors

Warm, earthy and saturated only in the accents.

### Primary
- **Marigold Gold** (#C8860A): buttons, rules, accents. **Lamp Gold** (#E8B84B) is its lighter highlight; **Gold Haze** (#FBF0D8) is the pale tint behind highlights.

### Secondary (tile colours)
- **Ghat Teal** (#1A6B7A), **Temple Burgundy** (#8B1A1A), **Cobalt Blue** (#1A3A6B), **Sage Green** (#3D6B3A), **Sandstone Brown** (#5C3A1E): room tiles and decorative accents.

### Neutral
- **Ink** (#1A1208): text and dark bands (stats band, room cards). **Cream** (#FAF4EA): page background. **Parchment** (#F2E8D5): alternate sections. **Muted Umber** (#7A6A50): secondary text. **WhatsApp Green** (#25D366): WhatsApp actions only.

### Named Rules
**The One Gold Rule.** Gold is the only action colour; jewel tones decorate, never drive actions.

## Typography

**Display Font:** Cinzel (serif)
**Body Font:** Jost (sans-serif, weight 300)
**Accent Font:** Cormorant Garamond (serif, light and italic)

**Character:** Roman-inscription capitals paired with a quiet geometric sans and a soft literary italic.

### Hierarchy
- **Display** (400, 48px, 1.05, +3px tracking): section titles in Cinzel.
- **Headline** (300, Cormorant Garamond): intro lines and pull quotes.
- **Body** (300, Jost): paragraphs and FAQ.
- **Label** (400, 10px, +4 to +5px tracking, uppercase): buttons and eyebrows.

### Named Rules
**The Wide Caps Rule.** Uppercase text is always letter-spaced; tight capitals break the voice.

## Layout

Full-width bands alternating cream, parchment and ink, with centred content sections. Breakpoints cluster at 1024px and 768px, with smaller steps at 600, 480. A `prefers-reduced-motion` query is present. Easing is a single curve, `cubic-bezier(.25,.46,.45,.94)`.

## Elevation & Depth

Flat at rest; hybrid on hover. Cards lift with large, low-opacity warm shadows.

### Shadow Vocabulary
- **Soft card** (`0 16px 48px rgba(26,18,8,.1)`), **Lifted card** (`0 20px 60px rgba(26,18,8,.12)`), **Hero panel** (`0 32px 80px rgba(26,18,8,.12)`), **Gold glow** (`0 12px 40px rgba(200,134,10,.1)`), **Overlay** (`0 20px 60px rgba(26,18,8,.3)`).

## Shapes

Near-square: 1px on buttons and tiles, 2-4px on small controls, 8-12px only for a few cards and dialogs, 50% for dots and avatars.

## Components

### Buttons
- **Shape:** 1px radius.
- **Gold (primary):** Marigold Gold fill, white label, 16px 56px padding, Jost 10px, +5px tracking, uppercase.
- **Light (on dark):** transparent with a 50% white 1px border; border and text go solid white on hover.
- **Transition:** background .3s, slight lift (`translateY`) .2s.

### Room Cards
- Ink-backed, image-led tiles with overflow clipped; the category (Private, Mixed Dorm, Ladies Only) sits as a small label.

### Stats Band
- Ink background, flex row with gold figures.

## Do's and Don'ts

### Do:
- **Do** keep gold as the single call-to-action colour.
- **Do** letter-space every uppercase label.
- **Do** use large, soft, warm shadows for lift.

### Don't:
- **Don't** use rounded pill buttons or heavy 16px+ radii.
- **Don't** use cool grey neutrals; stay in cream, parchment and ink.
- **Don't** use jewel tones for buttons.
