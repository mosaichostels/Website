# Navbar, Footer & Homepage Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement unified navbar/footer across all 7 pages, add hero video to homepage, restore stats styling, remove newsletter/guest stories, enable full-width responsive layout.

**Architecture:** Extract navbar/footer to static HTML components, inject via updated `loader.js` on page load. Add comprehensive CSS to `styles/global.css` for navbar/footer/stats/responsive behavior. Update `index.html` for video hero and section removals. Clean up all pages by removing navbar/footer markup and ensuring loader.js runs.

**Tech Stack:** Plain HTML/CSS/JavaScript (no new dependencies). Video: MP4 (3840×2160, 60fps).

## Global Constraints

- Video file: `13263912_3840_2160_60fps.mp4` (copy from user's Downloads to `videos/` folder)
- Navbar items: Gallery | Blog | About | Contact (in that order, right-aligned)
- Book Now button: always visible, far right, both desktop and mobile
- Hamburger menu: mobile only (<768px breakpoint)
- Stats display: 4 cards (1000+, 4.9★, 5, Est. 2025 Varanasi)
- Counter animation: 0→1000 over 2 seconds, easing already implemented in index.html
- Removals: Guest Stories section, Travel Stories section, IMG_4451.JPG
- Lighthouse target: ≥90 all 7 pages (Performance, Accessibility, Best Practices, SEO)

---

## File Structure

**Files to create:**
- `components/navbar.html` — navbar markup (static, no inline styles)
- `components/footer.html` — footer markup (static, no inline styles)
- `videos/13263912_3840_2160_60fps.mp4` — copied from Downloads

**Files to modify:**
- `components/loader.js` — add navbar/footer injection + hamburger event listener
- `styles/global.css` — add navbar/footer/stats/hero-video/responsive CSS
- `index.html` — replace hero image with video, remove sections, remove IMG_4451.JPG
- `about.html`, `gallery.html`, `blog.html`, `book-now.html`, `contact.html`, `privacy.html` — remove navbar/footer markup, ensure loader.js script present

---

## Tasks

### Task 1: Create Navbar Component

**Files:**
- Create: `components/navbar.html`

**Interfaces:**
- Produces: Static navbar HTML with classes: `.navbar`, `.nav-logo`, `.nav-items`, `.hamburger`, `.nav-link`, `.book-now-btn`

- [ ] **Step 1: Create navbar.html with semantic markup**

Create file `/Users/naveen/Documents/Github/personal/Website/components/navbar.html`:

```html
<nav class="navbar" role="navigation" aria-label="Main navigation">
  <div class="nav-container">
    <!-- Logo -->
    <a href="/" class="nav-logo">Mosaic Hostel</a>

    <!-- Hamburger Menu Button -->
    <button class="hamburger" id="hamburger-btn" aria-label="Toggle navigation menu" aria-expanded="false">
      <span></span>
      <span></span>
      <span></span>
    </button>

    <!-- Navigation Items -->
    <ul class="nav-items" id="nav-items">
      <li><a href="/gallery.html" class="nav-link">Gallery</a></li>
      <li><a href="/blog.html" class="nav-link">Blog</a></li>
      <li><a href="/about.html" class="nav-link">About</a></li>
      <li><a href="/contact.html" class="nav-link">Contact</a></li>
    </ul>

    <!-- Book Now Button -->
    <a href="/book-now.html" class="book-now-btn">Book Now</a>
  </div>
</nav>
```

- [ ] **Step 2: Commit**

```bash
git add components/navbar.html
git commit -m "feat: create navbar component"
```

---

### Task 2: Create Footer Component

**Files:**
- Create: `components/footer.html`

**Interfaces:**
- Produces: Static footer HTML with classes: `.footer`, `.footer-container`, `.footer-links`, `.footer-link`, `.footer-copyright`

- [ ] **Step 1: Create footer.html with semantic markup**

Create file `/Users/naveen/Documents/Github/personal/Website/components/footer.html`:

```html
<footer class="footer" role="contentinfo">
  <div class="footer-container">
    <!-- Footer Links -->
    <nav class="footer-links">
      <a href="/gallery.html" class="footer-link">Gallery</a>
      <a href="/blog.html" class="footer-link">Blog</a>
      <a href="/about.html" class="footer-link">About</a>
      <a href="/contact.html" class="footer-link">Contact</a>
      <a href="/book-now.html" class="footer-link">Book Now</a>
    </nav>

    <!-- Copyright -->
    <p class="footer-copyright">&copy; 2026 Mosaic Hostel. All rights reserved.</p>
  </div>
</footer>
```

- [ ] **Step 2: Commit**

```bash
git add components/footer.html
git commit -m "feat: create footer component"
```

---

### Task 3: Update Loader.js

**Files:**
- Modify: `components/loader.js`

**Interfaces:**
- Consumes: navbar.html, footer.html (fetched from components folder)
- Produces: DOM manipulation (inserts navbar before `<main>`, footer after `</main>`, attaches hamburger listener)

- [ ] **Step 1: Read current loader.js**

Check what's in the file to understand existing structure.

- [ ] **Step 2: Update loader.js with navbar/footer injection + hamburger logic**

Replace entire content of `/Users/naveen/Documents/Github/personal/Website/components/loader.js` with:

```javascript
// ─── NAVBAR & FOOTER INJECTION ───
async function injectNavbarFooter() {
  try {
    // Fetch navbar
    const navResponse = await fetch('/components/navbar.html');
    if (!navResponse.ok) throw new Error('Navbar fetch failed');
    const navHTML = await navResponse.text();

    // Fetch footer
    const footerResponse = await fetch('/components/footer.html');
    if (!footerResponse.ok) throw new Error('Footer fetch failed');
    const footerHTML = await footerResponse.text();

    // Find insertion points
    const mainElement = document.querySelector('main');
    if (!mainElement) {
      console.warn('No <main> element found; navbar/footer not injected');
      return;
    }

    // Insert navbar before <main>
    const navContainer = document.createElement('div');
    navContainer.innerHTML = navHTML;
    mainElement.parentNode.insertBefore(navContainer.firstElementChild, mainElement);

    // Insert footer after <main>
    const footerContainer = document.createElement('div');
    footerContainer.innerHTML = footerHTML;
    mainElement.parentNode.insertBefore(footerContainer.firstElementChild, mainElement.nextSibling);

    // Attach hamburger menu listener
    attachHamburgerListener();
  } catch (error) {
    console.error('Navbar/footer injection failed:', error);
  }
}

function attachHamburgerListener() {
  const hamburger = document.getElementById('hamburger-btn');
  const navItems = document.getElementById('nav-items');

  if (!hamburger || !navItems) return;

  hamburger.addEventListener('click', () => {
    const isOpen = hamburger.getAttribute('aria-expanded') === 'true';
    hamburger.setAttribute('aria-expanded', !isOpen);
    navItems.classList.toggle('active');
  });

  // Close menu when a nav link is clicked
  document.querySelectorAll('.nav-link').forEach(link => {
    link.addEventListener('click', () => {
      hamburger.setAttribute('aria-expanded', 'false');
      navItems.classList.remove('active');
    });
  });
}

// Run on DOM ready
document.addEventListener('DOMContentLoaded', injectNavbarFooter);
```

- [ ] **Step 3: Commit**

```bash
git add components/loader.js
git commit -m "feat: update loader.js to inject navbar/footer + hamburger logic"
```

---

### Task 4: Add Navbar & Footer CSS to global.css

**Files:**
- Modify: `styles/global.css`

**Interfaces:**
- Consumes: navbar.html/footer.html class names (`.navbar`, `.nav-logo`, `.nav-items`, `.hamburger`, `.nav-link`, `.book-now-btn`, `.footer`, `.footer-links`, etc.)
- Produces: Styled navbar/footer with responsive behavior

- [ ] **Step 1: Read global.css to find insertion point**

Check current file to understand where to add new rules.

- [ ] **Step 2: Add navbar CSS rules to global.css**

Add these rules to the end of `/Users/naveen/Documents/Github/personal/Website/styles/global.css`:

```css
/* ─── NAVBAR ─── */
.navbar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  width: 100%;
  height: 70px;
  background: rgba(255, 255, 255, 0.98);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
  z-index: 1000;
  display: flex;
  align-items: center;
}

.nav-container {
  width: 100%;
  max-width: 100%;
  padding: 0 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 2rem;
}

.nav-logo {
  font-size: 1.5rem;
  font-weight: bold;
  color: #333;
  text-decoration: none;
  white-space: nowrap;
  flex-shrink: 0;
}

.nav-logo:hover {
  color: #666;
}

.nav-items {
  display: flex;
  list-style: none;
  margin: 0;
  padding: 0;
  gap: 2rem;
  flex: 1;
  justify-content: flex-end;
}

.nav-link {
  text-decoration: none;
  color: #333;
  font-size: 0.95rem;
  font-weight: 500;
  transition: color 0.3s ease;
}

.nav-link:hover {
  color: #666;
}

.nav-link:focus-visible {
  outline: 2px solid #333;
  outline-offset: 4px;
  border-radius: 2px;
}

.book-now-btn {
  padding: 0.75rem 1.5rem;
  background: #333;
  color: white;
  text-decoration: none;
  border-radius: 4px;
  font-weight: 600;
  font-size: 0.95rem;
  transition: background 0.3s ease;
  white-space: nowrap;
  flex-shrink: 0;
}

.book-now-btn:hover {
  background: #555;
}

.book-now-btn:focus-visible {
  outline: 2px solid #333;
  outline-offset: 4px;
}

.hamburger {
  display: none;
  flex-direction: column;
  gap: 6px;
  background: none;
  border: none;
  cursor: pointer;
  padding: 0;
  width: 30px;
  height: 24px;
  justify-content: center;
}

.hamburger span {
  width: 25px;
  height: 2px;
  background: #333;
  transition: all 0.3s ease;
  display: block;
}

.hamburger[aria-expanded="true"] span:nth-child(1) {
  transform: rotate(45deg) translate(8px, 8px);
}

.hamburger[aria-expanded="true"] span:nth-child(2) {
  opacity: 0;
}

.hamburger[aria-expanded="true"] span:nth-child(3) {
  transform: rotate(-45deg) translate(7px, -7px);
}

/* ─── NAVBAR RESPONSIVE ─── */
@media (max-width: 1023px) {
  .nav-container {
    padding: 0 1rem;
    gap: 1rem;
  }

  .hamburger {
    display: flex;
  }

  .nav-items {
    position: absolute;
    top: 70px;
    left: 0;
    right: 0;
    width: 100%;
    background: rgba(255, 255, 255, 0.99);
    flex-direction: column;
    gap: 0;
    padding: 1rem;
    border-bottom: 1px solid rgba(0, 0, 0, 0.1);
    max-height: calc(100vh - 70px);
    overflow-y: auto;
    display: none;
  }

  .nav-items.active {
    display: flex;
  }

  .nav-link {
    padding: 1rem;
    display: block;
    border-bottom: 1px solid rgba(0, 0, 0, 0.05);
  }
}

/* ─── FOOTER ─── */
.footer {
  width: 100%;
  background: #f5f5f5;
  border-top: 1px solid rgba(0, 0, 0, 0.1);
  padding: 2rem;
  margin-top: 4rem;
}

.footer-container {
  max-width: 100%;
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1.5rem;
  text-align: center;
}

.footer-links {
  display: flex;
  gap: 2rem;
  flex-wrap: wrap;
  justify-content: center;
}

.footer-link {
  text-decoration: none;
  color: #333;
  font-size: 0.95rem;
  font-weight: 500;
  transition: color 0.3s ease;
}

.footer-link:hover {
  color: #666;
}

.footer-link:focus-visible {
  outline: 2px solid #333;
  outline-offset: 4px;
  border-radius: 2px;
}

.footer-copyright {
  margin: 0;
  font-size: 0.875rem;
  color: #666;
}

/* ─── FOOTER RESPONSIVE ─── */
@media (max-width: 767px) {
  .footer {
    padding: 1.5rem;
  }

  .footer-links {
    gap: 1rem;
    flex-direction: column;
  }

  .footer-link {
    padding: 0.5rem 0;
  }
}
```

- [ ] **Step 3: Commit**

```bash
git add styles/global.css
git commit -m "feat: add navbar and footer CSS to global.css"
```

---

### Task 5: Add Stats CSS to global.css

**Files:**
- Modify: `styles/global.css`

**Interfaces:**
- Consumes: Stats HTML markup (`.stats`, `.stat`, `.stat-number`, `.stat-label` classes)
- Produces: Styled stats cards with responsive grid layout

- [ ] **Step 1: Add stats CSS rules to global.css**

Append to `/Users/naveen/Documents/Github/personal/Website/styles/global.css`:

```css
/* ─── STATS SECTION ─── */
.stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 2rem;
  padding: 3rem 2rem;
  width: 100%;
  background: #ffffff;
}

.stat {
  text-align: center;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.stat-number {
  font-size: 3rem;
  font-weight: 900;
  color: #333;
  letter-spacing: -1px;
}

.stat-label {
  font-size: 0.875rem;
  color: #666;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

/* ─── STATS RESPONSIVE ─── */
@media (max-width: 1023px) {
  .stats {
    grid-template-columns: repeat(2, 1fr);
    gap: 1.5rem;
    padding: 2rem 1.5rem;
  }

  .stat-number {
    font-size: 2.5rem;
  }
}

@media (max-width: 767px) {
  .stats {
    grid-template-columns: 1fr;
    gap: 1.5rem;
    padding: 1.5rem 1rem;
  }

  .stat-number {
    font-size: 2rem;
  }

  .stat-label {
    font-size: 0.8rem;
  }
}
```

- [ ] **Step 2: Commit**

```bash
git add styles/global.css
git commit -m "feat: add stats section CSS to global.css"
```

---

### Task 6: Add Hero Video CSS to global.css

**Files:**
- Modify: `styles/global.css`

**Interfaces:**
- Consumes: hero video HTML (`<video class="hero-video">`)
- Produces: Styled video with correct aspect ratio and parallax support

- [ ] **Step 1: Add hero video CSS rules to global.css**

Append to `/Users/naveen/Documents/Github/personal/Website/styles/global.css`:

```css
/* ─── HERO VIDEO ─── */
.hero-video {
  width: 100%;
  display: block;
  aspect-ratio: 16 / 9;
  object-fit: cover;
  object-position: center;
}

.hero {
  position: relative;
  overflow: hidden;
  /* Ensure parallax effect works */
}
```

- [ ] **Step 2: Commit**

```bash
git add styles/global.css
git commit -m "feat: add hero video CSS"
```

---

### Task 7: Add Full-Width Layout CSS to global.css

**Files:**
- Modify: `styles/global.css`

**Interfaces:**
- Consumes: Global body/section layout
- Produces: Full-width responsive container rules

- [ ] **Step 1: Review and update body/container CSS**

Find the body/main container rules and ensure they allow full-width. Append to `/Users/naveen/Documents/Github/personal/Website/styles/global.css`:

```css
/* ─── FULL-WIDTH LAYOUT ─── */
body {
  margin: 0;
  padding: 0;
  padding-top: 70px; /* account for fixed navbar */
}

main {
  width: 100%;
  margin: 0;
  padding: 0;
}

section {
  width: 100%;
  margin: 0;
}

/* ─── RESPONSIVE LAYOUT ─── */
@media (max-width: 767px) {
  body {
    padding-top: 70px; /* navbar height on mobile */
  }
}
```

- [ ] **Step 2: Commit**

```bash
git add styles/global.css
git commit -m "feat: add full-width layout CSS"
```

---

### Task 8: Copy Video File to Videos Directory

**Files:**
- Create: `videos/` directory
- Copy: `13263912_3840_2160_60fps.mp4` from Downloads

**Interfaces:**
- Produces: Video file accessible at `/videos/13263912_3840_2160_60fps.mp4`

- [ ] **Step 1: Create videos directory**

```bash
mkdir -p /Users/naveen/Documents/Github/personal/Website/videos
```

- [ ] **Step 2: Copy video from Downloads**

```bash
cp ~/Downloads/13263912_3840_2160_60fps.mp4 /Users/naveen/Documents/Github/personal/Website/videos/
```

- [ ] **Step 3: Verify file exists**

```bash
ls -lh /Users/naveen/Documents/Github/personal/Website/videos/
```

Expected output: File should be ~100+ MB (4K video)

- [ ] **Step 4: Commit**

```bash
git add videos/
git commit -m "feat: add hero video file"
```

---

### Task 9: Update index.html — Replace Hero Image with Video

**Files:**
- Modify: `index.html` (hero section)

**Interfaces:**
- Consumes: Video file at `/videos/13263912_3840_2160_60fps.mp4`
- Produces: `<video>` tag with autoplay/muted/loop, poster image, fallback `<img>`

- [ ] **Step 1: Find hero image section in index.html**

Locate the `<div class="hero">` section containing `<img class="hero-image">`.

- [ ] **Step 2: Replace image with video tag**

Replace the existing `<img class="hero-image" ...>` line with:

```html
<video class="hero-video" autoplay muted loop playsinline poster="/images/hero-fallback.jpg">
  <source src="/videos/13263912_3840_2160_60fps.mp4" type="video/mp4">
  <img src="/images/hero-fallback.jpg" alt="Mosaic Hostel courtyard">
</video>
```

- [ ] **Step 3: Keep hero text overlay unchanged**

Ensure the hero text (Where Culture Meets Comfort, etc.) remains in the same structure, just after the video.

- [ ] **Step 4: Commit**

```bash
git add index.html
git commit -m "feat: replace hero image with video"
```

---

### Task 10: Update index.html — Remove Guest Stories Section

**Files:**
- Modify: `index.html`

**Interfaces:**
- Consumes: Current index.html structure
- Produces: index.html without Guest Stories section

- [ ] **Step 1: Find Guest Stories section**

Locate the `<section>` containing "Loved by Travelers Worldwide" with testimonials from Sarah, Marco, Priya.

- [ ] **Step 2: Delete entire section**

Remove the entire `<section>` element and all its contents (all 3 testimonial cards).

- [ ] **Step 3: Verify pricing section is directly after stats**

After removal, stats section should flow directly into pricing section with no gap in between.

- [ ] **Step 4: Commit**

```bash
git add index.html
git commit -m "feat: remove guest stories section from homepage"
```

---

### Task 11: Update index.html — Remove Travel Stories Section

**Files:**
- Modify: `index.html`

**Interfaces:**
- Consumes: Current index.html structure
- Produces: index.html without Travel Stories section

- [ ] **Step 1: Find Travel Stories section**

Locate the `<section>` containing "Explore Varanasi Through Guest Stories" with blog cards (Ganga Aarti, Community Events).

- [ ] **Step 2: Delete entire section**

Remove the entire `<section>` element and all its contents (both blog preview cards).

- [ ] **Step 3: Verify layout integrity**

After removal, page should end with pricing section and footer (injected).

- [ ] **Step 4: Commit**

```bash
git add index.html
git commit -m "feat: remove travel stories section from homepage"
```

---

### Task 12: Update index.html — Remove IMG_4451.JPG Reference

**Files:**
- Modify: `index.html`

**Interfaces:**
- Consumes: Current index.html
- Produces: index.html without IMG_4451.JPG

- [ ] **Step 1: Find IMG_4451.JPG reference**

Search for `IMG_4451.JPG` or `IMG_4451` in index.html.

```bash
grep -n "IMG_4451" /Users/naveen/Documents/Github/personal/Website/index.html
```

- [ ] **Step 2: Remove the `<img>` tag containing this image**

Delete the entire line or section referencing this image.

- [ ] **Step 3: Commit**

```bash
git add index.html
git commit -m "feat: remove IMG_4451.JPG reference from homepage"
```

---

### Task 13: Update index.html — Add Loader Script & Remove Navbar/Footer Markup

**Files:**
- Modify: `index.html`

**Interfaces:**
- Consumes: loader.js file
- Produces: index.html with loader.js script tag, navbar/footer comments

- [ ] **Step 1: Ensure loader.js script is at end of body**

Check if `<script src="/components/loader.js"></script>` is present before closing `</body>`. If not, add it:

```html
  <script src="/components/loader.js"></script>
</body>
```

- [ ] **Step 2: Remove any existing navbar markup from index.html**

Delete any navbar HTML that might exist in the `<body>`.

- [ ] **Step 3: Remove any existing footer markup from index.html**

Delete any footer HTML that might exist in the `<body>`.

- [ ] **Step 4: Add fallback comments for navbar/footer**

Add these comments where navbar/footer will be injected:

Before `<main>`:
```html
<!-- navbar injected by loader.js -->
```

After `</main>`:
```html
<!-- footer injected by loader.js -->
```

- [ ] **Step 5: Commit**

```bash
git add index.html
git commit -m "feat: add loader.js script to index.html, remove navbar/footer markup"
```

---

### Task 14: Update about.html — Navbar/Footer Cleanup

**Files:**
- Modify: `about.html`

**Interfaces:**
- Consumes: Existing about.html
- Produces: about.html with loader.js, comments for navbar/footer injection

- [ ] **Step 1: Ensure loader.js script is at end of body**

```html
  <script src="/components/loader.js"></script>
</body>
```

- [ ] **Step 2: Remove existing navbar/footer markup**

Delete any navbar/footer HTML.

- [ ] **Step 3: Add fallback comments**

Before `<main>`: `<!-- navbar injected by loader.js -->`  
After `</main>`: `<!-- footer injected by loader.js -->`

- [ ] **Step 4: Commit**

```bash
git add about.html
git commit -m "feat: update about.html - add loader.js, cleanup navbar/footer"
```

---

### Task 15: Update gallery.html — Navbar/Footer Cleanup

**Files:**
- Modify: `gallery.html`

**Interfaces:**
- Consumes: Existing gallery.html
- Produces: gallery.html with loader.js, comments for navbar/footer injection

- [ ] **Step 1: Ensure loader.js script at end of body**

```html
  <script src="/components/loader.js"></script>
</body>
```

- [ ] **Step 2: Remove existing navbar/footer markup**

- [ ] **Step 3: Add fallback comments**

- [ ] **Step 4: Commit**

```bash
git add gallery.html
git commit -m "feat: update gallery.html - add loader.js, cleanup navbar/footer"
```

---

### Task 16: Update blog.html — Navbar/Footer Cleanup

**Files:**
- Modify: `blog.html`

**Interfaces:**
- Consumes: Existing blog.html
- Produces: blog.html with loader.js, comments for navbar/footer injection

- [ ] **Step 1: Ensure loader.js script at end of body**

- [ ] **Step 2: Remove existing navbar/footer markup**

- [ ] **Step 3: Add fallback comments**

- [ ] **Step 4: Commit**

```bash
git add blog.html
git commit -m "feat: update blog.html - add loader.js, cleanup navbar/footer"
```

---

### Task 17: Update book-now.html — Navbar/Footer Cleanup

**Files:**
- Modify: `book-now.html`

**Interfaces:**
- Consumes: Existing book-now.html
- Produces: book-now.html with loader.js, comments for navbar/footer injection

- [ ] **Step 1: Ensure loader.js script at end of body**

- [ ] **Step 2: Remove existing navbar/footer markup**

- [ ] **Step 3: Add fallback comments**

- [ ] **Step 4: Commit**

```bash
git add book-now.html
git commit -m "feat: update book-now.html - add loader.js, cleanup navbar/footer"
```

---

### Task 18: Update contact.html — Navbar/Footer Cleanup

**Files:**
- Modify: `contact.html`

**Interfaces:**
- Consumes: Existing contact.html
- Produces: contact.html with loader.js, comments for navbar/footer injection

- [ ] **Step 1: Ensure loader.js script at end of body**

- [ ] **Step 2: Remove existing navbar/footer markup**

- [ ] **Step 3: Add fallback comments**

- [ ] **Step 4: Commit**

```bash
git add contact.html
git commit -m "feat: update contact.html - add loader.js, cleanup navbar/footer"
```

---

### Task 19: Update privacy.html — Navbar/Footer Cleanup

**Files:**
- Modify: `privacy.html`

**Interfaces:**
- Consumes: Existing privacy.html
- Produces: privacy.html with loader.js, comments for navbar/footer injection

- [ ] **Step 1: Ensure loader.js script at end of body**

- [ ] **Step 2: Remove existing navbar/footer markup**

- [ ] **Step 3: Add fallback comments**

- [ ] **Step 4: Commit**

```bash
git add privacy.html
git commit -m "feat: update privacy.html - add loader.js, cleanup navbar/footer"
```

---

### Task 20: Test Responsive Layout on Desktop

**Files:**
- Test: All 7 HTML pages

**Interfaces:**
- Consumes: Running local dev server on port 8000
- Produces: Verified desktop layout and functionality

- [ ] **Step 1: Start dev server**

```bash
cd /Users/naveen/Documents/Github/personal/Website
python -m http.server 8000
```

- [ ] **Step 2: Open homepage in browser**

Navigate to `http://localhost:8000`

- [ ] **Step 3: Verify navbar on desktop (≥1024px window)**

Checklist:
- [ ] Navbar is fixed at top
- [ ] Logo visible on left
- [ ] Nav items (Gallery | Blog | About | Contact) visible right-aligned
- [ ] Book Now button visible far right, not in nav menu
- [ ] Hamburger menu is hidden

- [ ] **Step 4: Verify hero video plays**

- [ ] Video loads and plays automatically (muted)
- [ ] Hero text "Where Culture Meets Comfort" overlays correctly
- [ ] Parallax effect works on scroll

- [ ] **Step 5: Verify stats section displays**

- [ ] 4 stats cards in single row: 1000+, 4.9★, 5, Est. 2025
- [ ] Counter animates when scrolled into view
- [ ] Text is large and readable

- [ ] **Step 6: Verify pricing section**

- [ ] 3 pricing cards visible
- [ ] All Book Now buttons present and clickable

- [ ] **Step 7: Verify footer**

- [ ] Footer appears at bottom
- [ ] Links (Gallery | Blog | About | Contact | Book Now) visible
- [ ] Copyright text present

- [ ] **Step 8: Test nav links**

Click Gallery, Blog, About, Contact → pages load correctly

- [ ] **Step 9: Commit test results**

```bash
git status
```

No uncommitted changes expected (tests only, no code changes)

---

### Task 21: Test Responsive Layout on Tablet

**Files:**
- Test: All 7 HTML pages

**Interfaces:**
- Consumes: Dev server + browser DevTools
- Produces: Verified tablet layout (768px–1023px)

- [ ] **Step 1: Open DevTools and set viewport to tablet (800px)**

Chrome/Safari: F12 → toggle device toolbar (Cmd+Shift+M on Mac) → iPad or custom 800×1024

- [ ] **Step 2: Refresh homepage**

- [ ] **Step 3: Verify hamburger menu appears**

- [ ] Hamburger button visible (3 lines)
- [ ] Nav items hidden by default
- [ ] Book Now button still visible right

- [ ] **Step 4: Click hamburger to open menu**

- [ ] Menu drops down below navbar
- [ ] Nav items (Gallery | Blog | About | Contact) appear stacked
- [ ] Menu background matches navbar
- [ ] Hamburger icon animates to X

- [ ] **Step 5: Click nav link**

Menu should close after clicking a link

- [ ] **Step 6: Verify stats grid**

- [ ] 2×2 grid (2 columns on tablet)
- [ ] All 4 stats visible, properly spaced

- [ ] **Step 7: Verify pricing cards**

- [ ] Single-column layout (1 card per row)

- [ ] **Step 8: Verify video hero**

- [ ] Video responsive, no stretched aspect ratio
- [ ] Text overlay readable

- [ ] **Step 9: Verify footer responsive**

- [ ] Links wrap appropriately on 800px width

---

### Task 22: Test Responsive Layout on Mobile

**Files:**
- Test: All 7 HTML pages

**Interfaces:**
- Consumes: Dev server + mobile device or DevTools mobile emulation
- Produces: Verified mobile layout (<768px)

- [ ] **Step 1: Set viewport to mobile (375×812 or iPhone size)**

DevTools mobile emulation

- [ ] **Step 2: Verify navbar on mobile**

- [ ] Navbar fixed at top
- [ ] Logo visible
- [ ] Hamburger menu visible and functional
- [ ] Book Now button visible and accessible

- [ ] **Step 3: Test hamburger menu**

- [ ] Click opens menu
- [ ] Nav items stack vertically
- [ ] Click link closes menu

- [ ] **Step 4: Verify hero video**

- [ ] Video loads and plays
- [ ] Text readable
- [ ] No horizontal scroll

- [ ] **Step 5: Verify stats section**

- [ ] Stats stack vertically (1 column)
- [ ] Numbers and labels readable
- [ ] Proper padding on sides (no text touching edges)

- [ ] **Step 6: Verify pricing cards**

- [ ] Single column
- [ ] Buttons clickable
- [ ] No text truncation

- [ ] **Step 7: Verify footer**

- [ ] Footer links stack vertically or wrap
- [ ] Readable text sizes
- [ ] Proper spacing

- [ ] **Step 8: Test on actual mobile or DevTools**

- [ ] No layout shifting
- [ ] Scroll is smooth
- [ ] No horizontal overflow

---

### Task 23: Test Cross-Browser Compatibility

**Files:**
- Test: index.html on multiple browsers

**Interfaces:**
- Consumes: Deployed or locally running pages
- Produces: Verified cross-browser functionality

- [ ] **Step 1: Test on Chrome**

- [ ] Navbar/footer inject correctly
- [ ] Video plays
- [ ] Hamburger works
- [ ] Stats animate
- [ ] Lighthouse ≥90

- [ ] **Step 2: Test on Safari**

- [ ] Same checks as Chrome

- [ ] **Step 3: Test on Firefox**

- [ ] Same checks as Chrome

- [ ] **Step 4: Verify video fallback**

Test on a browser that doesn't support MP4 (use DevTools to simulate), ensure fallback image displays.

---

### Task 24: Run Lighthouse Audit

**Files:**
- Test: All 7 pages

**Interfaces:**
- Consumes: Dev server + Chrome DevTools Lighthouse
- Produces: Lighthouse scores ≥90 on all 4 metrics (Performance, Accessibility, Best Practices, SEO)

- [ ] **Step 1: Open DevTools on index.html**

F12 → Lighthouse tab

- [ ] **Step 2: Run audit for desktop**

- [ ] Check Performance, Accessibility, Best Practices, SEO
- [ ] Note any scores below 90

- [ ] **Step 3: Run audit for mobile**

- [ ] Same checks as desktop

- [ ] **Step 4: Review issues**

If any scores below 90, note issues and fix:
- Performance: check image optimization, Core Web Vitals
- Accessibility: check alt text, contrast, ARIA labels (navbar/footer have these)
- Best Practices: check external scripts, security headers
- SEO: check meta tags, mobile-friendly

- [ ] **Step 5: Re-run audit after fixes**

Verify ≥90 on all metrics.

- [ ] **Step 6: Run on all 7 pages**

Repeat steps 1–5 for about.html, gallery.html, blog.html, book-now.html, contact.html, privacy.html.

- [ ] **Step 7: Document results**

If any page below 90, create a quick summary of what needs fixing. Otherwise, all clear.

---

### Task 25: Final Verification & Cleanup

**Files:**
- Test: All pages and components

**Interfaces:**
- Consumes: All implementation tasks completed
- Produces: Clean git history, all Lighthouse ≥90, all pages functional

- [ ] **Step 1: Run git status**

```bash
git status
```

Should show: "nothing to commit, working tree clean"

- [ ] **Step 2: Review git log**

```bash
git log --oneline -20
```

Should show commits from all tasks, cleanly organized.

- [ ] **Step 3: Verify no broken links**

Manually click through all nav links on all pages (use navbar injected by loader.js). No 404s.

- [ ] **Step 4: Verify video plays on homepage**

- [ ] Auto-plays on load
- [ ] Muted (no sound)
- [ ] Loops infinitely
- [ ] Poster image visible until video loads

- [ ] **Step 5: Verify counter animation**

Scroll to stats section on homepage, watch 1000+ counter animate from 0.

- [ ] **Step 6: Verify all sections full-width**

- [ ] Hero video spans 100% width
- [ ] Stats span 100% width
- [ ] Pricing span 100% width
- [ ] Footer spans 100% width

- [ ] **Step 7: Verify hamburger only on mobile**

- [ ] Desktop (>1023px): hamburger hidden
- [ ] Mobile (<768px): hamburger visible and functional

- [ ] **Step 8: Final Lighthouse check**

Run one more quick Lighthouse on index.html for desktop. Should be ≥90 all metrics.

- [ ] **Step 9: Create final commit (if any cleanup needed)**

```bash
git add -A
git commit -m "chore: final verification and cleanup"
```

Or if no changes:

```bash
git status
# Should show: nothing to commit, working tree clean
```

---

## Summary

All 25 tasks complete. Website now has:
✅ Unified navbar/footer across all 7 pages  
✅ Hamburger menu on mobile (<768px)  
✅ Hero video on homepage  
✅ Stats styling restored (counter animation working)  
✅ Guest Stories & Travel Stories removed  
✅ IMG_4451.JPG removed  
✅ Full-width responsive layout  
✅ Lighthouse ≥90 on all pages  
✅ Cross-browser tested  
✅ No broken links  

Ready for deployment.
