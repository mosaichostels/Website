# Component Refactor Implementation Plan

> **For agentic workers:** Use superpowers:subagent-driven-development or superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Extract navbar and footer from duplicated HTML in 7 pages into reusable JavaScript components, reducing page size by 70% and creating a single source of truth for navigation.

**Architecture:** Two JavaScript files (navbar.js, footer.js) inject HTML at DOM ready time into placeholder divs. Active page detection via URL parsing. Mobile menu toggle handled by navbar.js. Single CSS file (components.css) styles both components with responsive breakpoints.

**Tech Stack:** Vanilla JavaScript (no frameworks), CSS3 (Grid, Flexbox, media queries)

## Global Constraints

- Keep 7 core pages only: home.html, gallery.html, about.html, contact.html, book-now.html, blog.html, privacy.html
- Delete: index.html, images-index.html
- Navbar links: Home (/home.html), Gallery, About, Contact, Book Now, Blog, Privacy
- Footer contact: Phone (+91-9125492225), Email (mosaichostels@gmail.com), Address (B1/85C Assi Ghat, Varanasi)
- Mobile breakpoint: 768px
- Active page highlighting: CSS class "active" on current nav link
- Mobile menu: Simple toggle (open/close), auto-close on link click

---

## File Structure

**Create:**
- `components/navbar.js` — Navbar injection + active page detection + mobile menu
- `components/footer.js` — Footer injection
- `styles/components.css` — Navbar + footer styling (responsive)

**Modify:**
- `home.html` — Remove inline navbar/footer, add container divs, add script tags
- `gallery.html` — Remove inline navbar/footer, add container divs, add script tags
- `about.html` — Remove inline navbar/footer, add container divs, add script tags
- `contact.html` — Remove inline navbar/footer, add container divs, add script tags
- `book-now.html` — Remove inline navbar/footer, add container divs, add script tags
- `blog.html` — Remove inline navbar/footer, add container divs, add script tags
- `privacy.html` — Remove inline navbar/footer, add container divs, add script tags

**Delete:**
- `index.html`
- `images-index.html`

---

## Task 1: Create navbar.js

**Files:**
- Create: `components/navbar.js`

**Produces:** 
- Navbar injection logic + active page detection + mobile menu

**Steps:**

- [ ] **Step 1: Create navbar.js file**

Create `components/navbar.js`:

```javascript
// components/navbar.js
(function() {
  const navbarHTML = `
    <nav id="mainNav">
      <div class="nav-logo">
        <a href="/home.html">Mosaic Hostel</a>
      </div>
      <div class="nav-links">
        <a href="/home.html" class="nav-link" data-page="home">Home</a>
        <a href="/gallery.html" class="nav-link" data-page="gallery">Gallery</a>
        <a href="/about.html" class="nav-link" data-page="about">About</a>
        <a href="/contact.html" class="nav-link" data-page="contact">Contact</a>
        <a href="/book-now.html" class="nav-link" data-page="book-now">Book Now</a>
        <a href="/blog.html" class="nav-link" data-page="blog">Blog</a>
        <a href="/privacy.html" class="nav-link" data-page="privacy">Privacy</a>
      </div>
      <button class="nav-hamburger" id="navHam" aria-label="Toggle menu">☰</button>
    </nav>
  `;

  function initNavbar() {
    const container = document.getElementById('navbar-container');
    if (!container) return;

    container.innerHTML = navbarHTML;
    highlightActivePage();
    setupMobileMenu();
  }

  function highlightActivePage() {
    // Get current page from URL path
    const path = window.location.pathname;
    let currentPage = 'home'; // default

    if (path === '/' || path === '/home.html') {
      currentPage = 'home';
    } else {
      // Extract filename without .html (e.g., /gallery.html -> gallery)
      const match = path.match(/\/([^\/]+)\.html/);
      if (match) {
        currentPage = match[1];
      }
    }

    // Add 'active' class to matching link
    document.querySelectorAll('.nav-link').forEach(link => {
      if (link.dataset.page === currentPage) {
        link.classList.add('active');
      } else {
        link.classList.remove('active');
      }
    });
  }

  function setupMobileMenu() {
    const hamburger = document.getElementById('navHam');
    const navLinks = document.querySelector('.nav-links');

    if (!hamburger || !navLinks) return;

    // Toggle menu on hamburger click
    hamburger.addEventListener('click', (e) => {
      e.stopPropagation();
      navLinks.classList.toggle('open');
    });

    // Close menu when a link is clicked
    document.querySelectorAll('.nav-link').forEach(link => {
      link.addEventListener('click', () => {
        navLinks.classList.remove('open');
      });
    });

    // Close menu when clicking outside
    document.addEventListener('click', () => {
      navLinks.classList.remove('open');
    });
  }

  // Initialize when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initNavbar);
  } else {
    initNavbar();
  }
})();
```

- [ ] **Step 2: Verify file created**

Run: `ls -lh components/navbar.js`  
Expected: File exists, ~2KB

---

## Task 2: Create footer.js

**Files:**
- Create: `components/footer.js`

**Steps:**

- [ ] **Step 1: Create footer.js file**

Create `components/footer.js`:

```javascript
// components/footer.js
(function() {
  const footerHTML = `
    <footer id="mainFooter">
      <div class="footer-container">
        <div class="footer-section">
          <h4>Mosaic Hostel</h4>
          <p>Budget hostel in Varanasi near Assi Ghat. Perfect for backpackers and solo travelers.</p>
          <div class="social-links">
            <a href="https://www.instagram.com/mosaichostels" target="_blank">Instagram</a>
            <a href="https://www.facebook.com/mosaichostels/" target="_blank">Facebook</a>
            <a href="https://www.threads.com/@mosaichostels" target="_blank">Threads</a>
          </div>
        </div>
        <div class="footer-section">
          <h4>Contact</h4>
          <p><strong>Phone:</strong> +91-9125492225</p>
          <p><strong>Email:</strong> mosaichostels@gmail.com</p>
          <p><strong>Address:</strong> B1/85C Assi Ghat Road, Varanasi</p>
        </div>
        <div class="footer-section">
          <h4>Quick Links</h4>
          <ul>
            <li><a href="/home.html">Home</a></li>
            <li><a href="/gallery.html">Gallery</a></li>
            <li><a href="/about.html">About</a></li>
            <li><a href="/contact.html">Contact</a></li>
            <li><a href="/blog.html">Blog</a></li>
            <li><a href="/privacy.html">Privacy</a></li>
          </ul>
        </div>
      </div>
      <div class="footer-bottom">
        <p>&copy; 2026 Mosaic Hostels. All Rights Reserved.</p>
      </div>
    </footer>
  `;

  function initFooter() {
    const container = document.getElementById('footer-container');
    if (!container) return;

    container.innerHTML = footerHTML;
  }

  // Initialize when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initFooter);
  } else {
    initFooter();
  }
})();
```

- [ ] **Step 2: Verify file created**

Run: `ls -lh components/footer.js`  
Expected: File exists, ~1.5KB

---

## Task 3: Create components.css

**Files:**
- Create: `styles/components.css`

**Steps:**

- [ ] **Step 1: Create components.css file**

Create `styles/components.css` (same as previous plan - see full plan for content)

---

## Task 4-10: Update 7 pages (home, gallery, about, contact, book-now, blog, privacy)

For each page, follow this pattern:
- Remove inline navbar/footer HTML
- Add container divs: `<div id="navbar-container"></div>` and `<div id="footer-container"></div>`
- Add script tags: `<script src="components/navbar.js"></script>` and `<script src="components/footer.js"></script>`
- Add CSS link: `<link rel="stylesheet" href="styles/components.css">`

---

## Task 11: Delete index.html and images-index.html

**Steps:**

- [ ] **Step 1: Delete files**

Run: `rm index.html images-index.html`

- [ ] **Step 2: Verify**

Run: `ls *.html | wc -l`  
Expected: 7 files

---

## Task 12: Test & Deploy

Test all 7 pages locally, verify navbar/footer injection, test mobile menu, then deploy to production.

---

**Plan ready for execution.**

**Execution choice:**

**1. Subagent-Driven** — Fresh subagent per task  
**2. Inline Execution** — Execute here with checkpoints

Which?
