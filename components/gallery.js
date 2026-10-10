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

    countEl.setAttribute('role', 'status');
    document.querySelectorAll('.filter-btn').forEach((b) => b.setAttribute('aria-pressed', b.classList.contains('active')));
    document.querySelectorAll('.filter-btn').forEach((btn) => {
      btn.addEventListener('click', () => {
        document.querySelectorAll('.filter-btn').forEach((b) => { b.classList.remove('active'); b.setAttribute('aria-pressed', 'false'); });
        btn.classList.add('active');
        btn.setAttribute('aria-pressed', 'true');
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
    let trigger = null;
    const lbClose = document.getElementById('lb-close');
    const lbPrev = document.getElementById('lb-prev');
    const lbNext = document.getElementById('lb-next');
    lb.setAttribute('role', 'dialog');
    lb.setAttribute('aria-modal', 'true');
    lb.setAttribute('aria-label', 'Photo viewer');
    lbClose.setAttribute('aria-label', 'Close photo viewer');
    lbPrev.setAttribute('aria-label', 'Previous photo');
    lbNext.setAttribute('aria-label', 'Next photo');
    if (lbCounter) lbCounter.setAttribute('aria-live', 'polite');
    // Everything behind the dialog is inert while it is open (keeps Tab out of the Instagram iframe).
    // The lightbox may sit inside <main>, so inert every sibling along its ancestor path, never the path itself.
    const behind = () => {
      const out = [];
      for (let n = lb; n && n !== document.body; n = n.parentElement) {
        Array.from(n.parentElement.children).forEach((c) => { if (c !== n && c.tagName !== 'SCRIPT') out.push(c); });
      }
      return out;
    };
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
      if (!lb.classList.contains('open')) {
        trigger = document.activeElement;
        lb.classList.add('open');
        behind().forEach((el) => el.setAttribute('inert', ''));
        lbClose.focus();
      }
      document.body.style.overflow = 'hidden';
    }
    function close() {
      lb.classList.remove('open');
      behind().forEach((el) => el.removeAttribute('inert'));
      document.body.style.overflow = '';
      lbImg.src = '';
      if (trigger && trigger.focus) trigger.focus();
    }
    function navigate(dir) {
      const visible = getVisible();
      currentIdx = (currentIdx + dir + visible.length) % visible.length;
      open(currentIdx);
    }

    items.forEach((item) => {
      item.setAttribute('role', 'button');
      item.setAttribute('tabindex', '0');
      item.setAttribute('aria-label', 'Open photo: ' + item.dataset.title);
      item.addEventListener('click', () => open(getVisible().indexOf(item)));
      item.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); open(getVisible().indexOf(item)); }
      });
    });
    // Swipe left/right on touch screens.
    let touchX = null;
    lb.addEventListener('touchstart', (e) => { touchX = e.touches[0].clientX; }, { passive: true });
    lb.addEventListener('touchend', (e) => {
      if (touchX === null) return;
      const dx = e.changedTouches[0].clientX - touchX;
      touchX = null;
      if (Math.abs(dx) > 50) navigate(dx < 0 ? 1 : -1);
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
      if (e.key === 'Tab') {
        const ring = [lbClose, lbPrev, lbNext];
        const i = ring.indexOf(document.activeElement);
        e.preventDefault();
        ring[(i + (e.shiftKey ? -1 : 1) + ring.length) % ring.length].focus();
      }
    });
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
