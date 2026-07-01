// Fetch and inject navbar/footer components into DOM
async function injectNavbarFooter() {
    // Guard: Don't inject if already done
    if (document.getElementById('navbar')) {
        console.warn('Navbar already injected, skipping duplicate injection');
        return;
    }

    try {
        // Fetch and inject navbar
        const navRes = await fetch('components/navbar.html');
        if (!navRes.ok) throw new Error(`Failed to fetch navbar: ${navRes.status}`);
        const navHTML = await navRes.text();
        const navDiv = document.createElement('div');
        navDiv.innerHTML = navHTML;
        document.body.insertBefore(navDiv.firstElementChild, document.body.firstChild);

        // Guard: Don't inject footer if already exists
        if (!document.querySelector('footer')) {
            const footRes = await fetch('components/footer.html');
            if (!footRes.ok) throw new Error(`Failed to fetch footer: ${footRes.status}`);
            const footHTML = await footRes.text();
            const footDiv = document.createElement('div');
            footDiv.innerHTML = footHTML;
            document.body.appendChild(footDiv.firstElementChild);
        }

        // Mark as injected to prevent duplicate injection
        document.body.dataset.componentInjected = 'true';

        // Attach hamburger listener after navbar is injected
        attachHamburgerListener();
    } catch (e) {
        console.error('Component injection failed:', e);
    }
}

// Set up hamburger menu toggle and nav link listeners
function attachHamburgerListener() {
    const hamburgerBtn = document.querySelector('.hamburger');
    const navItems = document.querySelector('.nav-items');

    // Return early if elements don't exist
    if (!hamburgerBtn || !navItems) return;

    // Toggle menu visibility on hamburger click
    hamburgerBtn.addEventListener('click', () => {
        navItems.classList.toggle('active');
        const isExpanded = navItems.classList.contains('active');
        hamburgerBtn.setAttribute('aria-expanded', isExpanded);
    });

    // Close menu when nav link is clicked
    navItems.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', () => {
            navItems.classList.remove('active');
            hamburgerBtn.setAttribute('aria-expanded', 'false');
        });
    });

    // Close menu on Escape key
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && navItems.classList.contains('active')) {
            navItems.classList.remove('active');
            hamburgerBtn.setAttribute('aria-expanded', 'false');
        }
    });

    // Navbar scroll effect (optional enhancement)
    const navbar = document.querySelector('.navbar');
    if (navbar) {
        window.addEventListener('scroll', () => {
            navbar.classList.toggle('scrolled', window.scrollY > 100);
        }, { passive: true });
    }
}

// Wait for DOM ready and inject components
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', injectNavbarFooter);
} else {
    injectNavbarFooter();
}
