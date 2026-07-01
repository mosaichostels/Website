# HERO SECTION — Design Plan vs Implementation AUDIT

**Issue:** Hero video and text not correctly aligned according to original design spec.

---

## ORIGINAL DESIGN SPEC (from decisions.md 2026-06-30)

### Hero Section Requirements
```
**Hero Section:** 600px desktop/400px mobile, video background + gradient overlay + parallax scroll depth
- Full-height video background (autoplay, looped, with gradient + mosaic overlay)
- Hero content: Main heading (H1) + subtitle + description
- Gradient overlay for readability
- Parallax scroll depth effects
- Animated text reveals
- Call-to-action buttons
```

### Success Criteria
✅ Hero video as central focal point
✅ 600px desktop / 400px mobile height
✅ Video background + gradient overlay
✅ Parallax depth + animation
✅ Hero text properly centered and readable
✅ WCAG AA contrast maintained

---

## CURRENT IMPLEMENTATION (index.html)

### Hero HTML Structure
```html
<section class="hero" role="banner" aria-label="Welcome to Mosaic Hostel">
    <video class="hero-video" autoplay muted loop playsinline aria-hidden="true">
        <source src="images/hero-video.webm" type="video/webm">
        <source src="images/hero-video.mp4" type="video/mp4">
    </video>
    <img class="hero-bg" src="images/IMG_4450.JPG" alt="..." fetchpriority="high">
    <div class="hero-stripe" id="heroStripe"></div>
    <div class="hero-overlay" aria-hidden="true"></div>
    
    <div class="hero-content">
        <div class="hero-subtitle">Where Culture Meets Comfort</div>
        <h1>Each Guest a Piece.<br>Each Story a Tile.</h1>
        <p>Together, we make something beautiful...</p>
    </div>
    
    <div class="scroll-indicator" aria-hidden="true">
        <p>Scroll</p>
    </div>
</section>
```

### Hero CSS Status
❌ **CRITICAL: NO HERO CSS IN global.css**
- `.hero` — not defined
- `.hero-video` — not defined
- `.hero-content` — not defined
- `.hero-subtitle` — not defined
- `.hero-overlay` — not defined
- `.scroll-indicator` — not defined
- `.hero-stripe` — not defined

---

## ISSUES FOUND

### 1. **Missing Hero CSS** ❌ CRITICAL
**Impact:** Hero section renders with browser defaults, NOT per design spec

**Missing styles:**
- No height definition (should be 600px desktop, 400px mobile)
- No positioning for video background
- No overlay gradient
- No text alignment/centering
- No parallax effects
- No animation on text reveals
- No scroll indicator styling

### 2. **Text Alignment Issues** ❌
**Current:** Hero content has NO CSS, renders at top-left with default styling
**Expected (per spec):**
- Content centered vertically & horizontally
- Subtitle small (14px), muted color
- H1 large (56px), high contrast
- Description text (16px), readable on video
- Proper spacing between elements (8px grid)

### 3. **Video Not Properly Displayed** ❌
**Current:** No CSS to position/size video
- Video might not cover full section
- No aspect ratio maintenance
- No object-fit property
- Fallback image (IMG_4450.JPG) might not show

**Expected:**
```css
.hero-video {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    object-fit: cover;
    z-index: 1;
}
```

### 4. **Overlay Gradient Missing** ❌
**Current:** `.hero-overlay` exists in HTML but NO CSS
**Expected (per design):**
```css
.hero-overlay {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: linear-gradient(to bottom, rgba(26, 18, 8, 0.3), rgba(26, 18, 8, 0.6));
    z-index: 2;
}
```

**Why:** Ensures text readable on video background (WCAG AA contrast)

### 5. **Scroll Indicator Not Hidden** ❌
**Rule:** `.scroll-indicator { display: none; }` (from rules.md)
**Current:** No CSS, text "Scroll" likely visible
**Issue:** Violates design — scroll indicator should be decorative/hidden

### 6. **No Parallax Scroll Effect** ❌
**Design spec:** "parallax scroll depth" required
**Current:** No CSS/JS parallax implementation
**Missing:**
- JavaScript scroll listener
- CSS transform: translateY() on hero-content
- Parallax speed calculations

### 7. **Text Spacing Off-Grid** ❌
**Rule:** All spacing must use 8px grid
**Current:** HTML has no margin/padding classes
**Missing:**
- margin-bottom on subtitle
- margin-bottom on H1
- margin-bottom on description
- Padding around hero-content

---

## VISUAL COMPARISON

### Expected (Per Design Spec)
```
┌─────────────────────────────────────────┐
│ [NAVBAR - 80px fixed]                    │
├─────────────────────────────────────────┤
│                                          │
│  [VIDEO BACKGROUND with gradient]       │
│                                          │
│         [Hero Content - CENTERED]        │
│                                          │
│      Where Culture Meets Comfort         │
│      Each Guest a Piece                  │
│      Each Story a Tile                   │
│                                          │
│   Together we make something beautiful   │
│                                          │
│        [CTA Buttons - if present]       │
│                                          │
│  ↓ Scroll ↓ [decorative indicator]      │
│                                          │
│ [600px desktop / 400px mobile height]    │
└─────────────────────────────────────────┘
```

### Current (No CSS)
```
┌─────────────────────────────────────────┐
│ [NAVBAR - 80px fixed]                    │
├─────────────────────────────────────────┤
│ MOSAIC HOSTEL entrance photo            │
│ [fallback image, no video overlay]       │
│                                          │
│ Where Culture Meets Comfort              │
│ Each Guest a Piece.                      │
│ Each Story a Tile.                       │
│                                          │
│ Together, we make...                     │
│                                          │
│ Scroll [text visible - should be hidden] │
│                                          │
│ [unknown height, no alignment]           │
└─────────────────────────────────────────┘
```

---

## MISSING CSS (Complete)

Add to `styles/global.css`:

```css
/* ─── HERO SECTION ─── */
.hero {
    position: relative;
    height: 600px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    overflow: hidden;
    margin-top: 80px; /* navbar height */
}

@media (max-width: 768px) {
    .hero {
        height: 400px;
    }
}

/* Video background */
.hero-video {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    object-fit: cover;
    z-index: 1;
}

/* Fallback image if video fails */
.hero-bg {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    object-fit: cover;
    z-index: 1;
}

/* Gradient overlay for text readability */
.hero-overlay {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: linear-gradient(
        to bottom,
        rgba(26, 18, 8, 0.3),
        rgba(26, 18, 8, 0.6)
    );
    z-index: 2;
}

/* Decorative stripe (if used) */
.hero-stripe {
    position: absolute;
    height: 8px;
    width: 100%;
    background: var(--gold);
    z-index: 3;
    bottom: 0;
}

/* Hero content container */
.hero-content {
    position: relative;
    z-index: 4;
    text-align: center;
    color: white;
    max-width: 600px;
    padding: 0 24px;
    animation: fadeInUp 0.8s ease-out;
}

/* Hero subtitle */
.hero-subtitle {
    font-size: 14px;
    font-weight: 500;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: rgba(255, 255, 255, 0.9);
    margin-bottom: 16px;
}

/* Hero heading */
.hero h1 {
    font-size: 56px;
    font-weight: 700;
    line-height: 1.2;
    margin-bottom: 24px;
    letter-spacing: 1px;
    color: white;
    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

/* Hero description */
.hero-content p {
    font-size: 18px;
    line-height: 1.6;
    color: rgba(255, 255, 255, 0.95);
    margin-bottom: 32px;
    text-shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
}

/* Scroll indicator */
.scroll-indicator {
    position: absolute;
    bottom: 32px;
    z-index: 4;
    animation: pulse 2s infinite;
}

.scroll-indicator p {
    font-size: 12px;
    font-weight: 600;
    letter-spacing: 1px;
    color: rgba(255, 255, 255, 0.6);
}

/* Animations */
@keyframes fadeInUp {
    from {
        opacity: 0;
        transform: translateY(20px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

@keyframes pulse {
    0%, 100% {
        opacity: 1;
    }
    50% {
        opacity: 0.5;
    }
}

/* Parallax effect (JavaScript handled) */
.hero-content.scrolled {
    transform: translateY(var(--parallax-offset, 0px));
}

/* Mobile adjustments */
@media (max-width: 768px) {
    .hero-content {
        padding: 0 16px;
    }
    
    .hero h1 {
        font-size: 42px;
    }
    
    .hero-content p {
        font-size: 16px;
    }
    
    .scroll-indicator {
        display: none; /* Hide on mobile per design */
    }
}
```

---

## ADDITIONAL ISSUES

### Parallax Not Implemented
**Design spec:** "parallax scroll depth" required
**Current:** No JavaScript parallax logic
**Missing:** Scroll listener + transform calculations

### CTA Buttons
**Design mentions:** "Call-to-action buttons" in hero
**Current HTML:** No buttons visible in hero
**Check:** Should there be "Explore Rooms" / "Book Now" buttons in hero?

### Text Shadow
**Current:** No text shadow
**Needed:** Drop shadow on text for contrast against video
**Example:** `text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);`

---

## SUMMARY OF ALIGNMENT ISSUES

| Issue | Status | Severity | Impact |
|-------|--------|----------|--------|
| **Hero CSS completely missing** | ❌ | CRITICAL | Hero renders unstyled |
| **No height definition** | ❌ | CRITICAL | Layout broken |
| **Text not centered** | ❌ | CRITICAL | Poor UX |
| **Video not positioned** | ❌ | HIGH | Fallback image shows instead |
| **Overlay gradient missing** | ❌ | HIGH | Text not readable on video |
| **Scroll indicator visible** | ❌ | MEDIUM | Design violation |
| **No parallax animation** | ❌ | MEDIUM | Missing premium feel |
| **Text spacing off-grid** | ❌ | MEDIUM | Inconsistent with design |
| **No text shadow** | ❌ | LOW | Reduced contrast |

---

## FIX PRIORITY

1. **IMMEDIATE:** Add missing hero CSS (height, positioning, overlay)
2. **IMMEDIATE:** Center hero-content properly
3. **IMMEDIATE:** Hide scroll indicator
4. **HIGH:** Add text shadow for readability
5. **HIGH:** Implement parallax scroll effect
6. **MEDIUM:** Verify video loads (not image fallback)
7. **MEDIUM:** Check for missing CTA buttons
8. **LOW:** Add animations to text reveals

---

## VERIFICATION CHECKLIST

After fixes:
- [ ] Hero section renders 600px desktop, 400px mobile
- [ ] Video background shows (not fallback image)
- [ ] Gradient overlay visible on video
- [ ] Text centered vertically and horizontally
- [ ] Subtitle, H1, description properly spaced (8px grid)
- [ ] Scroll indicator hidden
- [ ] Text shadow applied (readable on video)
- [ ] Parallax effect works on scroll
- [ ] WCAG AA contrast verified (white text on dark overlay)
- [ ] Lighthouse score maintained ≥90
- [ ] Responsive at 375px, 768px, 1024px

