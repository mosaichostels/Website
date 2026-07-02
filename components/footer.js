// components/footer.js
(function() {
  const footerHTML = `
    <footer>
      <div class="footer-top">
        <div>
          <img src="/images/mosaic-logo-main.png" alt="Mosaic Hostel" style="display:block;height:110px;width:auto;filter:brightness(0) invert(1);opacity:0.9;margin-bottom:16px;">
          <p class="footer-tagline">A hostel rooted in community, warmth, and the spirit of Varanasi. Every guest who stays becomes part of our story.</p>
        </div>
        <div>
          <div class="footer-heading">Stay</div>
          <div class="footer-links">
            <a href="/book-now.html">Private Room</a>
            <a href="/book-now.html">8-Bed Mixed Dorm</a>
            <a href="/book-now.html">6-Bed Mixed Dorm</a>
            <a href="/book-now.html">4-Bed Mixed Dorm</a>
            <a href="/book-now.html">6-Bed Female Dorm</a>
          </div>
        </div>
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

  function fillStrip(id, colors) {
    const el = document.getElementById(id);
    if (!el) return;
    colors.forEach(c => {
      const s = document.createElement('span');
      s.style.flex = '1';
      s.style.background = c;
      el.appendChild(s);
    });
  }

  function init() {
    const container = document.getElementById('footer-container');
    if (container) {
      container.innerHTML = footerHTML;
      fillStrip('footerStrip', ['#C8860A', '#8B1A1A', '#1A6B7A', '#1A3A6B', '#3D6B3A']);
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
