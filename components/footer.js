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

  function init() {
    const container = document.getElementById('footer-container');
    if (container) {
      container.innerHTML = footerHTML;
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
