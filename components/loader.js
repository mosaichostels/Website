// Initialize navbar and footer functionality
document.addEventListener('DOMContentLoaded', () => {
    initNavbar();
});

function initNavbar() {
    const navHam = document.getElementById('navHam');
    const navLinks = document.getElementById('navLinks');
    const navbar = document.getElementById('navbar');

    if (!navHam || !navLinks) return;

    // Mobile menu toggle
    navHam.addEventListener('click', () => {
        navLinks.classList.toggle('active');
        navHam.classList.toggle('active');
        navHam.setAttribute('aria-expanded', navLinks.classList.contains('active'));
    });

    // Close menu on link click
    navLinks.querySelectorAll('a').forEach(link => {
        link.addEventListener('click', () => {
            navLinks.classList.remove('active');
            navHam.classList.remove('active');
            navHam.setAttribute('aria-expanded', 'false');
        });
    });

    // Close menu on Escape
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && navLinks.classList.contains('active')) {
            navLinks.classList.remove('active');
            navHam.classList.remove('active');
            navHam.setAttribute('aria-expanded', 'false');
        }
    });

    // Navbar scroll effect
    window.addEventListener('scroll', () => {
        navbar.classList.toggle('scrolled', window.scrollY > 100);
    }, { passive: true });
}
