// Inject unified navbar and footer (with deduplication guard)
async function injectComponents() {
    // Guard: Don't inject if already done
    if (document.getElementById('navbar')) {
        console.warn('Navbar already injected, skipping duplicate injection');
        return;
    }

    try {
        // Fetch and inject navbar
        const navRes = await fetch('components/navbar.html');
        const navHTML = await navRes.text();
        const navDiv = document.createElement('div');
        navDiv.innerHTML = navHTML;
        document.body.insertBefore(navDiv.firstElementChild, document.body.firstChild);

        // Guard: Don't inject footer if already exists
        if (!document.querySelector('footer')) {
            const footRes = await fetch('components/footer.html');
            const footHTML = await footRes.text();
            const footDiv = document.createElement('div');
            footDiv.innerHTML = footHTML;
            document.body.appendChild(footDiv.firstElementChild);
        }

        // Mark as injected to prevent Hostinger snippets from re-injecting
        document.body.dataset.componentInjected = 'true';

        // Initialize navbar after injection
        initNavbar();
    } catch (e) {
        console.error('Component injection failed:', e);
    }
}

// Wait for DOM ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', injectComponents);
} else {
    injectComponents();
}

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
