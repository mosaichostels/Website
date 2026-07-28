// components/navbar.js
(function() {
  function init() {
    const nav = document.getElementById('mainNav');
    if (!nav) return;
    highlightCurrentPage();
    setupMobileMenu();
    setupScroll();
  }

  function highlightCurrentPage() {
    const path = window.location.pathname;
    const match = path.match(/\/([a-z-]+)(\.html)?/);
    const currentPage = (path === '/' || !match) ? 'home' : match[1];
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

    // Apply scrolled state based on scroll position (consistent across all pages)
    const onScroll = () => nav.classList.toggle('scrolled', window.scrollY > 80);
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
