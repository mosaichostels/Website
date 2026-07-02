// components/footer.js
(function() {
  const footerHTML = `
    <footer>
      <div class="footer-top">
        <div>
          <img src="/images/mosaic-logo-main.png" alt="Mosaic Hostel" style="display:block;height:110px;width:auto;filter:brightness(0) invert(1);opacity:0.9;margin-bottom:16px;">
          <p class="footer-tagline">A hostel rooted in community, warmth, and the spirit of Varanasi. Every guest who stays becomes part of our story.</p>
        </div>
        <div></div>
        <div>
          <div class="footer-heading">Explore</div>
          <div class="footer-links">
            <a href="/gallery.html">Gallery</a>
            <a href="/about.html">About Us</a>
            <a href="/blog.html">Blog</a>
            <a href="/contact.html">Contact</a>
          </div>
        </div>
        <div>
          <div class="footer-heading">Connect</div>
          <div class="footer-links">
            <a href="https://www.instagram.com/mosaichostels" target="_blank">Instagram</a>
            <a href="https://wa.me/919125492225" target="_blank">WhatsApp</a>
            <a href="mailto:mosaichostels@gmail.com">Email Us</a>
            <a href="https://www.hostelworld.com/hostels/mosaic-hostel-varanasi/varanasi" target="_blank">Hostelworld</a>
            <a href="https://www.booking.com" target="_blank">Booking.com</a>
          </div>
        </div>
      </div>
      <div class="footer-bottom">
        <div class="footer-copy">© 2026 Mosaic Hostel. All rights reserved.</div>
        <div class="footer-tile-strip" id="footerStrip"></div>
        <div class="footer-copy">Made with ♥ in Varanasi</div>
      </div>
    </footer>
  `;

  function init() {
    const container = document.getElementById('footer-container');
    if (!container) return;
    container.innerHTML = footerHTML;

    // Fill footer stripe with accent colors
    const stripe = document.getElementById('footerStrip');
    if (stripe) {
      ['#C8860A', '#8B1A1A', '#1A6B7A', '#1A3A6B', '#3D6B3A'].forEach(color => {
        const span = document.createElement('span');
        span.style.flex = '1';
        span.style.background = color;
        stripe.appendChild(span);
      });
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
