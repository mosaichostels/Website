// Initialize navbar and footer functionality
document.addEventListener('DOMContentLoaded', () => {
    initNavbar();
});

function initNavbar() {
    const navHam = document.getElementById('navHam');
    const navLinks = document.getElementById('navLinks');
    const navbar = document.getElementById('navbar');
    const cursor = document.getElementById('cursor');
    const cursorRing = document.getElementById('cursor-ring');

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

    // Custom cursor
    if (cursor && cursorRing) {
        let cursorX = 0, cursorY = 0, cursorRingX = 0, cursorRingY = 0;

        document.addEventListener('mousemove', (e) => {
            cursorX = e.clientX;
            cursorY = e.clientY;
            cursor.style.left = cursorX + 'px';
            cursor.style.top = cursorY + 'px';

            cursorRingX += (cursorX - cursorRingX) * 0.2;
            cursorRingY += (cursorY - cursorRingY) * 0.2;
            cursorRing.style.left = cursorRingX + 'px';
            cursorRing.style.top = cursorRingY + 'px';
        });

        document.querySelectorAll('a, button, input, select, textarea').forEach(el => {
            el.addEventListener('mouseenter', () => {
                cursor.style.width = '16px';
                cursor.style.height = '16px';
                cursorRing.style.width = '48px';
                cursorRing.style.height = '48px';
            });
            el.addEventListener('mouseleave', () => {
                cursor.style.width = '10px';
                cursor.style.height = '10px';
                cursorRing.style.width = '36px';
                cursorRing.style.height = '36px';
            });
        });
    }
}
