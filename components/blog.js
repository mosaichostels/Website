// components/blog.js — blog listing page only. Renders cards from blogRenderer metadata.
(function () {
  const map = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;' };
  const escapeHtml = (t) => String(t).replace(/[&<>"']/g, (m) => map[m]);

  async function renderBlogListing() {
    const container = document.getElementById('blog-listing');
    if (!container || !window.blogRenderer) return;
    try {
      const blogs = await window.blogRenderer.getAllBlogsMetadata();
      if (blogs.length === 0) { container.innerHTML = '<p>No blog posts yet.</p>'; return; }

      container.innerHTML = blogs.map((blog) => `
        <article class="blog-card reveal">
          <a href="/blog/${blog.slug}" class="blog-card-link">
            <h3 class="blog-card-title">${escapeHtml(blog.title)}</h3>
            <p class="blog-card-excerpt">${escapeHtml(blog.excerpt)}</p>
            <div class="blog-card-meta">
              <span class="blog-card-date">${escapeHtml(blog.date)}</span>
              <span class="blog-card-readmore">Read More →</span>
            </div>
          </a>
        </article>
      `).join('');

      // Observe newly added cards for reveal animation (shared observer from site.js)
      document.querySelectorAll('.blog-card').forEach((el) => window.MOSAIC.revealObserver.observe(el));
    } catch (error) {
      console.error('Error loading blog listing:', error);
      container.innerHTML = '<p>Error loading blog posts. Please try again later.</p>';
    }
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', renderBlogListing);
  else renderBlogListing();
})();
