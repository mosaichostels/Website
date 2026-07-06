// components/gallery.js — gallery page only (accent bars, filter, lightbox).
(function () {
  const { LOGO_COLORS, pick, fillStrip } = window.MOSAIC;
  const PALS = {
    'gold-teal': ['#C8860A', '#E8B84B', '#D4930F', '#1A6B7A', '#2D9AAA'],
    'teal-cobalt': ['#1A6B7A', '#2D9AAA', '#0D4A55', '#1A3A6B', '#2A5A9B'],
    'burg-gold': ['#8B1A1A', '#A02020', '#6B1010', '#C8860A', '#E8B84B'],
    'cobalt-sage': ['#1A3A6B', '#2A5A9B', '#3D6B3A', '#2D5A2A'],
    'sage-gold': ['#3D6B3A', '#2D5A2A', '#C8860A', '#E8B84B'],
  };

  function init() {
    // Gallery item accent bars
    document.querySelectorAll('.gal-accent').forEach((el) => {
      const pal = PALS[el.dataset.pal] || PALS['gold-teal'];
      for (let i = 0; i < 20; i++) fillStrip(el, [pick(pal)]);
    });

    initFilter();
    initLightbox();
  }

  function initFilter() {
    const items = Array.from(document.querySelectorAll('.gal-item'));
    const countEl = document.getElementById('photoCount');
    const noRes = document.getElementById('noResults');
    if (!countEl) return;

    function applyFilter(cat) {
      let visible = 0;
      items.forEach((item) => {
        const match = cat === 'all' || item.dataset.cat === cat;
        item.classList.toggle('hidden', !match);
        if (match) visible++;
      });
      countEl.textContent = visible + ' Photo' + (visible !== 1 ? 's' : '');
      if (noRes) noRes.style.display = visible === 0 ? 'block' : 'none';
    }

    document.querySelectorAll('.filter-btn').forEach((btn) => {
      btn.addEventListener('click', () => {
        document.querySelectorAll('.filter-btn').forEach((b) => b.classList.remove('active'));
        btn.classList.add('active');
        applyFilter(btn.dataset.filter);
      });
    });
    countEl.textContent = items.length + ' Photos';
  }

  function initLightbox() {
    const items = Array.from(document.querySelectorAll('.gal-item'));
    const lb = document.getElementById('lightbox');
    const lbImg = document.getElementById('lb-img');
    if (!lb || !lbImg) return;
    const lbTitle = document.getElementById('lb-title');
    const lbCat = document.getElementById('lb-cat');
    const lbStrip = document.getElementById('lb-strip');
    const lbCounter = document.getElementById('lb-counter');
    let currentIdx = 0;
    const getVisible = () => items.filter((i) => !i.classList.contains('hidden'));

    function open(idx) {
      const visible = getVisible();
      if (!visible[idx]) return;
      currentIdx = idx;
      const item = visible[idx];
      lbImg.src = item.dataset.full || item.querySelector('.gal-photo').src;
      lbImg.alt = item.dataset.title;
      if (lbTitle) lbTitle.textContent = item.dataset.title;
      if (lbCat) lbCat.textContent = item.querySelector('.gal-cat-tag').textContent;
      if (lbStrip) { lbStrip.innerHTML = ''; fillStrip(lbStrip, LOGO_COLORS.slice(0, 6)); }
      if (lbCounter) lbCounter.textContent = (idx + 1) + ' / ' + visible.length;
      lb.classList.add('open');
      document.body.style.overflow = 'hidden';
    }
    function close() {
      lb.classList.remove('open');
      document.body.style.overflow = '';
      lbImg.src = '';
    }
    function navigate(dir) {
      const visible = getVisible();
      currentIdx = (currentIdx + dir + visible.length) % visible.length;
      open(currentIdx);
    }

    items.forEach((item) => {
      item.addEventListener('click', () => open(getVisible().indexOf(item)));
    });
    document.getElementById('lb-close').addEventListener('click', close);
    document.getElementById('lb-prev').addEventListener('click', () => navigate(-1));
    document.getElementById('lb-next').addEventListener('click', () => navigate(1));
    lb.addEventListener('click', (e) => { if (e.target === lb) close(); });
    document.addEventListener('keydown', (e) => {
      if (!lb.classList.contains('open')) return;
      if (e.key === 'ArrowLeft') navigate(-1);
      if (e.key === 'ArrowRight') navigate(1);
      if (e.key === 'Escape') close();
    });
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
