# Interactive Mosaic Hostels Website — Design Specification

**Date:** 2026-06-30  
**Project:** Mosaic Hostels Website Redesign  
**Scope:** Full interactive website with Canvas-based mosaic tiles + HTML content  
**Status:** Approved for Implementation

---

## 1. Vision & Goals

Create a unique, colorful, classy website that embodies the true meaning of "Mosaic": diverse travelers (each with their own color, culture, identity) coming together to create something unified and beautiful. The website should feel alive through cursor-responsive interactions while maintaining premium aesthetic.

**Key Objectives:**
- Celebrate traveler diversity through tile colors representing cultures/backgrounds
- Implement mystical, fluid cursor interactions (color blends, ripples, gradient shifts)
- Maintain classy, sophisticated design despite vibrant colors
- Create organic, artistic layout (floating tiles, overlaps) vs. rigid grid
- Build single-page app with smooth transitions across 6 pages

---

## 2. Visual System

### 2.1 Color Palette

**Base Neutrals (Classy Foundation)**
- Cream: #F5F1EB (primary background)
- Deep Ink: #2B2520 (primary text)
- Refined Gold: #B8860B (accents, borders)

**Traveler Tile Colors (Full Spectrum Diversity)**
Each tile represents one traveler; color represents cultural background:

- Warm Tones: #FF6B6B (Brazil red), #FFA500 (India orange), #FFD700 (Egypt gold)
- Cool Tones: #4A90E2 (Australia blue), #2E7D32 (Japan green), #9C27B0 (Poland purple)
- Vibrant Accents: #FF1493 (Magenta), #00CED1 (Cyan), #FF4500 (OrangeRed), #32CD32 (Lime Green)

**Color Distribution Strategy:**
- Traveler database maps 6+ core travelers to their tile colors
- Each traveler consistently represented by same color across pages
- Gallery/Stories tiles use full spectrum for visual richness
- Cursor interaction reveals gradient shifts (left = cool, right = warm)

### 2.2 Typography

**Headings:** Playfair Display 700-900 (serif)
- Hero: 72px, letter-spacing -1px
- Section headings: 52px
- Card headings: 24-28px
- Refined, timeless, elegant

**Body Text:** Lato 300-400 (sans-serif)
- Body copy: 15px, font-weight 300, line-height 1.7
- Labels/UI: 12px, font-weight 600, uppercase, letter-spacing 1px
- Refined, highly readable

**Canvas Text:** Lato 700, white with subtle shadow
- Tile names: 14px
- Country labels: 11px

### 2.3 Spacing & Layout

- Section padding: 120px vertical
- Card padding: 40-60px
- Whitespace emphasis: generous gaps between elements
- Organic tile overlap: 20-40px overlaps in canvas sections
- Tile stagger: Random angle rotation -15° to +15°
- No rigid grid; floating, artistic composition

---

## 3. Canvas Interaction & Tile Behavior

### 3.1 Tile Properties

Each tile (traveler or experience) has:
- **Size:** 80-200px (varied for organic feel)
- **Position:** Random floating within canvas bounds
- **Color:** Assigned based on traveler culture or experience type
- **Label:** Name + country emoji (e.g., "Sophie 🇦🇺")
- **Rotation:** -15° to +15°, maintained or slow drift (6-8s cycle)
- **State:** Default, hovered, clicked, blending

### 3.2 Cursor Interaction — Mystical & Fluid

**Proximity Glow**
- When cursor within 150px of tile, tile emits glow in its native color
- Glow radius expands/contracts as cursor distance changes
- Glow intensity: 0 (far) → 1 (very close)
- Color brightness increases 20-50% during glow

**Color Blend Wave**
- As cursor moves across canvas, tiles along path blend 30-70% toward cursor "influence color"
- Influence color: interpolate between cursor's left-to-right position (blue → red gradient)
- Blend fades back to original color over 2s after cursor passes
- Creates "wave" visual following mouse trail

**Ripple Effect**
- When cursor stationary for 500ms, concentric ripples emanate from cursor point
- Ripples expand outward at 200px/s
- Tiles within ripple radius are pushed back slightly (5-15px repulsion)
- Tile rotation increases 10-20° near ripple center
- Ripple fade: 1s total duration

**Gradient Following (Background)**
- Background canvas gradient shifts hue based on cursor position
- Left 25% of canvas: Cool colors (blues, purples) - HSL rotate -30°
- Right 75% of canvas: Warm colors (reds, oranges) - HSL rotate +30°
- Smooth transition across spectrum
- Updates every frame, follows cursor smoothly

### 3.3 Passive Animation Loop

**Continuous Drift**
- Each tile drifts in place using sine wave (6-8s cycle, amplitude 20px)
- Staggered: Tile N starts at offset of 1s * N (prevents all tiles moving together)

**Organic Repositioning**
- Every 8-12s, tiles shift positions slightly (30-80px in random direction)
- Transition over 1.5s (ease-out)
- Collision detection: Tiles don't overlap more than allowed (maintain readability)

**Rotation Variation**
- Base rotation maintained (-15° to +15°)
- During ripples/glow: rotation +10-20° temporarily, eases back
- Creates sense of "responsiveness" even without cursor interaction

---

## 4. Page Structure & Canvas Integration

### 4.1 Home Page

**Canvas Section (Full Viewport Hero)**
- ~30 traveler tiles rendered as floating mosaic
- All cursor interactions active (glow, blend wave, ripples)
- Canvas covers 100vh initially
- Clicking any tile shows tooltip: name + country + 1-line quote

**HTML Section (Below Canvas)**
- "Why Mosaic" section with 3 feature cards
- Smooth fade-in as user scrolls
- Canvas background fades out as HTML content appears
- Cards: Playfair headlines, Lato body, classy spacing

**Navigation**
- Fixed top nav floats over canvas with high z-index
- Semi-transparent background (rgba(245,241,235,0.95))
- Smooth pointer underline animation (500ms)

### 4.2 Community Page

**Canvas Section**
- All 6+ core travelers rendered as tiles with full names
- Cursor interactions: glow, blend, ripples all active
- Hover any tile → shows expanded info:
  - Name, country emoji, flag
  - Quote/bio snippet
  - Country name

**Click Behavior**
- Clicking tile expands full profile (modal or sidebar)
- Shows: photo placeholder (colored background), full bio, travel history, social links

**HTML Sidebar (Optional)**
- Right side list of travelers (text-based)
- Filter by region/continent
- Duplicate info to canvas for accessibility

### 4.3 Gallery Page

**Canvas Section (Reduced Scale)**
- 12 gallery items as colorful tiles (not traveler-mapped)
- Each tile: emoji or gradient fill representing photo type
- Cursor interactions active but less intense (no ripples, just glow)
- Clicking tile → modal opens with:
  - Full emoji/visual representation
  - Description (e.g., "Rooftop gathering at sunset")
  - Share/save buttons

**HTML Navigation**
- Gallery filter buttons: "All", "Rooms", "Events", "Travelers", "Food"
- Clicking filter updates canvas tile rendering

### 4.4 Stories Page

**Canvas Hero (Abstract Tiles)**
- ~20 abstract color tiles (not traveler-mapped)
- Pure color diversity, no labels
- Cursor interactions: glow + gradient shift (no ripples)
- Fade out as user scrolls (transition to text content)

**HTML Content Section**
- 3-5 blog posts with refined typography
- Playfair headlines, Lato body, serif quotes
- Author byline with traveler name + country

**Scroll Behavior**
- Canvas remains fixed at top, fades to transparent
- HTML content scrolls over canvas, canvas fades to transparency as user scrolls past hero

### 4.5 Contact Page

**Canvas Background**
- Small mosaic tile background (20-30 tiles, muted colors, lower opacity)
- Cursor effects minimal (no ripples, subtle glow only)
- Visual interest without distraction from form

**HTML Foreground**
- Contact form: Name, Email, Message
- Contact info grid: Location, Phone, Email, Hours
- Form validation + success feedback

**Accessibility**
- Canvas is decorative only; form is fully accessible via HTML
- ARIA labels, semantic HTML, keyboard navigation

### 4.6 Book Now (Reserve) Page

**Canvas Section (Dual Purpose)**
- Tiles act as "room type selector"
- 3 main tiles: Dorm (blue), Private (gold), Double (purple)
- Larger tiles (150-200px) with clear labels
- Clicking tile selects room type (tile highlights, form updates)
- Other tiles fade (opacity 0.3) when one is selected

**HTML Form Section**
- Booking details: Check-in, Check-out, Guests, Name, Email, Phone
- Below canvas, smooth transition
- Form validation, booking confirmation

**Visual Feedback**
- Selected tile: Glows brightly in its color, slightly enlarged (scale 1.1)
- Unselected tiles: Muted, smaller glow
- Form updates when tile selected

---

## 5. Technical Architecture

### 5.1 Canvas Rendering Engine

**Core Structure**
```
MosaicCanvas {
  canvas: HTMLCanvasElement
  ctx: CanvasRenderingContext2D
  tiles: Tile[]
  cursorX: number
  cursorY: number
  animationFrame: number
  
  render(): void
  update(): void
  drawTile(tile: Tile): void
  handleCursorMove(x, y): void
  handleCursorStop(): void
}
```

**Tile Data Structure**
```
Tile {
  id: string
  x: number
  y: number
  vx: number (velocity x)
  vy: number (velocity y)
  rotation: number
  baseColor: string (hex)
  glowIntensity: number (0-1)
  blendAmount: number (0-1)
  size: number
  name: string
  country: string
  type: 'traveler' | 'experience' | 'room'
}
```

**Render Loop**
- 60fps using `requestAnimationFrame`
- Each frame:
  1. Clear canvas
  2. Update all tile positions/rotations/animations
  3. Calculate cursor distance to each tile
  4. Update glow/blend based on proximity
  5. Draw all tiles
  6. Draw background gradient
  7. Request next frame

### 5.2 Cursor Tracking & Interaction

**Event Listeners**
- `mousemove`: Update cursor position, calculate tile distances, apply glow/blend
- `mousedown` (optional): Track click position for interaction
- `window.resize`: Recalculate canvas size, reposition tiles proportionally

**Cursor Logic**
- Store cursor position as `{ x, y }`
- For each tile:
  - Calculate distance: `Math.hypot(tile.x - cursor.x, tile.y - cursor.y)`
  - If distance < 150px: Apply glow (intensity = 1 - (distance / 150))
  - If distance < 200px: Apply color blend (blend amount = 1 - (distance / 200))
  - Calculate ripple (if cursor stopped > 500ms): Push tiles away from cursor

**Color Blend Algorithm**
- Cursor influence color: Gradient from blue (left) to red (right)
  - `hue = 240 + (cursorX / canvasWidth) * 120` (blue 240° to red 360°)
- For each nearby tile:
  - `blendedColor = interpolate(tileColor, influenceColor, blendAmount)`
  - Ease back to original color over 2s after cursor leaves

**Ripple Calculation**
- When cursor stationary > 500ms:
  - Create ripple: `{ x: cursorX, y: cursorY, radius: 0, maxRadius: 300 }`
  - For each frame: `ripple.radius += 200 * deltaTime`
  - For each tile: If distance(tile, ripple.center) < ripple.radius:
    - Push tile outward: `tile.x += normalize(tile - ripple) * repulsion`
    - Rotate tile: `tile.rotation += 20°`
  - Fade ripple over 1s

### 5.3 HTML/Canvas Communication

**Canvas Instance**
- Global: `window.mosaicCanvas`
- Accessible to HTML layer: `mosaicCanvas.selectTile(id)`, `mosaicCanvas.getSelectedTile()`

**Custom Events**
- `tileHovered`: Triggered when cursor enters tile glow zone
- `tileClicked`: Triggered when tile clicked
- `tileSelected`: Triggered when tile selected (for room booking)
- HTML layer listens via `canvas.addEventListener('tileClicked', handler)`

**Two-Way Binding**
- Canvas emits events: HTML responds (e.g., show modal)
- HTML updates state: Canvas re-renders (e.g., highlight selected tile)
- Loose coupling via event bus pattern

### 5.4 Performance Optimization

**Rendering Efficiency**
- Single canvas context, batch rendering
- No individual tile object rendering; render all in one pass
- Use `requestAnimationFrame` (browser optimizes refresh rate)
- Debounce cursor calculations: Only recalc on mousemove, not every frame

**Memory Management**
- Tile count capped at 50-100 (maintainable)
- No memory leaks: Clean up event listeners on page unload
- Reuse Tile objects; don't create new ones each frame

**Canvas Size Optimization**
- Dynamic canvas sizing based on viewport
- Resize handler recalculates on window.resize
- Use device pixel ratio for crisp rendering on high-DPI screens

**Browser Support**
- Canvas API: All modern browsers (90%+ support)
- Pointer Events API: All modern browsers
- Fallback: Static HTML for older browsers (graceful degradation)

### 5.5 Dependencies

**Zero External Libraries**
- Canvas API: Native browser feature
- Pointer Events: Native browser API
- Pure JavaScript (ES6+)
- No jQuery, React, Vue, or animation libraries
- CSS only for non-canvas HTML sections

**File Structure**
```
/index.html               # Single-page app with all HTML
/js/mosaic-canvas.js      # Canvas rendering + interaction
/js/app.js                # Page navigation, state management
/css/style.css            # Typography, layout, non-canvas styling
```

### 5.6 State Management

**Global State**
- Current page: `app.currentPage` ('home' | 'community' | 'gallery' | 'stories' | 'contact' | 'booking')
- Canvas instance: `window.mosaicCanvas`
- Traveler data: `app.travelers` (array of Traveler objects)
- Selected tile: `app.selectedTile` (for booking, community expand)

**Traveler Data Structure**
```
Traveler {
  id: string
  name: string
  country: string
  emoji: string
  color: string (hex)
  quote: string
  bio: string
  story: string
}
```

**Booking State**
- Selected room type: `app.selectedRoom` ('dorm' | 'private' | 'double')
- Booking form data: `app.bookingForm { checkIn, checkOut, guests, name, email, phone }`

---

## 6. User Interactions & Flows

### 6.1 Browsing (Passive)

1. User lands on Home page
2. Canvas hero displays 30 floating traveler tiles
3. Tiles drift, rotate slowly (passive animation)
4. User scrolls down; canvas fades, HTML content appears
5. User clicks nav link to another page
6. Page transition: Canvas fades out, new page canvas fades in

### 6.2 Exploration (Cursor Interaction)

1. User moves mouse over canvas
2. Tiles near cursor glow in their colors
3. Colors blend as cursor passes; gradient shifts based on cursor position
4. Ripples emanate if cursor stops for 500ms
5. User continues moving; tiles respond in real-time
6. Creates sense of "alive" interface responding to presence

### 6.3 Selection (Community Page)

1. User hovers over traveler tile
2. Tile glows; name/quote appears
3. User clicks tile
4. Profile expands (modal or sidebar)
5. Shows full bio, country, travel experience
6. User clicks back/close to dismiss

### 6.4 Booking (Reserve Page)

1. User sees 3 room-type tiles (Dorm, Private, Double)
2. Hovers over each; glow and color effects active
3. Clicks desired room type
4. Tile highlights, others fade
5. Form below updates (e.g., price per night)
6. User fills form (dates, guests, contact info)
7. Submits booking

---

## 7. Accessibility & Fallbacks

### 7.1 Accessibility

- **Canvas Labeling:** `<canvas aria-label="Interactive traveler mosaic">`
- **Alternative Content:** HTML list of travelers (for screen readers)
- **Keyboard Navigation:** Tab through nav, form fields, button-equivalents
- **Color Contrast:** Text always 4.5:1+ on backgrounds
- **Focus States:** Clear focus rings on interactive elements

### 7.2 Graceful Degradation

- **No Canvas Support:** Show static HTML version (old browsers)
- **JavaScript Disabled:** Forms still work, navigation via page reloads
- **Mobile:** Canvas touch events supported; cursor interactions map to touch position
- **Low-End Devices:** Reduce tile count, simplify animations

---

## 8. Success Criteria

✓ Website loads and runs at 60fps on modern browsers  
✓ Canvas renders 30-50 tiles without performance degradation  
✓ Cursor interactions (glow, blend, ripples) feel responsive and mystical  
✓ Color diversity celebrates traveler backgrounds authentically  
✓ Classy aesthetic maintained despite vibrant colors  
✓ All 6 pages functional with smooth transitions  
✓ Forms (contact, booking) fully operational  
✓ Accessible via keyboard and screen readers  
✓ Responsive on mobile (touch support)  
✓ Gallery modal lightbox works  
✓ Traveler profiles expand/collapse smoothly  

---

## 9. Timeline & Phases

**Phase 1: Canvas Engine** (Day 1)
- Build MosaicCanvas class
- Implement tile rendering + passive animation
- Cursor tracking + glow effect

**Phase 2: Interactions** (Day 2)
- Color blend wave
- Ripple effect
- Background gradient following cursor

**Phase 3: Pages & HTML** (Day 3)
- Build all 6 pages with HTML/CSS
- Integrate canvas into each page
- Navigation + page transitions

**Phase 4: Refinement** (Day 4)
- Polish interactions
- Performance optimization
- Accessibility audit
- Mobile testing

---

## 10. Open Questions / Future Enhancements

- Mobile touch interactions: Should tiles respond to touch the same as mouse?
- Accessibility: Should canvas be optional/decorative-only for screen readers?
- Data persistence: Should selected room/booking be saved to localStorage?
- Social sharing: Should travelers be shareable (one tile per social card)?
- Analytics: Track which tiles users interact with most?

---

**Spec Status:** ✅ Ready for implementation  
**Approved By:** User (brainstorming session)  
**Next Step:** Invoke writing-plans skill to create detailed implementation plan
