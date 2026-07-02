// components/navbar.js
(function() {
  const navbarHTML = `
    <nav id="mainNav">
      <div class="nav-logo">
        <a href="/home.html"><img src="/images/mosaic-logo-main.png" alt="Mosaic Hostel"></a>
      </div>
      <div class="nav-links">
        <a href="/home.html" class="nav-link" data-page="home">Home</a>
        <a href="/gallery.html" class="nav-link" data-page="gallery">Gallery</a>
        <a href="/about.html" class="nav-link" data-page="about">About</a>
        <a href="/contact.html" class="nav-link" data-page="contact">Contact</a>
        <a href="/blog.html" class="nav-link" data-page="blog">Blog</a>
        <a href="/privacy.html" class="nav-link" data-page="privacy">Privacy</a>
      </div>
      <button class="nav-hamburger" id="navHam" aria-label="Toggle menu"><span></span><span></span><span></span></button>
      <a href="/book-now.html" class="nav-book">Book Now</a>
    </nav>
  `;

  function init() {
    const container = document.getElementById('navbar-container');
    if (!container) return;

    container.innerHTML = navbarHTML;
    highlightCurrentPage();
    setupMobileMenu();
    setupScroll();
  }

  function highlightCurrentPage() {
    const path = window.location.pathname;
    let currentPage = 'home';

    if (path !== '/' && path !== '/home.html') {
      const match = path.match(/\/([^\/]+)\.html/);
      if (match) currentPage = match[1];
    }

    document.querySelectorAll('.nav-link').forEach(link => {
      link.classList.toggle('active', link.dataset.page === currentPage);
    });
  }

  function setupMobileMenu() {
    const hamburger = document.getElementById('navHam');
    const navLinks = document.querySelector('.nav-links');
    if (!hamburger || !navLinks) return;

    hamburger.addEventListener('click', (e) => {
      e.stopPropagation();
      navLinks.classList.toggle('open');
      hamburger.classList.toggle('open');
    });

    document.querySelectorAll('.nav-link').forEach(link => {
      link.addEventListener('click', () => {
        navLinks.classList.remove('open');
        hamburger.classList.remove('open');
      });
    });

    document.addEventListener('click', () => {
      navLinks.classList.remove('open');
      hamburger.classList.remove('open');
    });
  }

  function setupScroll() {
    const nav = document.getElementById('mainNav');
    if (!nav) return;
    const onScroll = () => nav.classList.toggle('scrolled', window.scrollY > 200);
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
