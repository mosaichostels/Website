// components/home.js — index page only (rooms, philosophy, testimonials, lightbox).
(function () {
  const { LOGO_COLORS, PAL, pick, fillStrip, fillById, fillGrid, revealObserver } = window.MOSAIC;
  const FIVE_B = ['#C8860A', '#8B1A1A', '#1A6B7A', '#1A3A6B', '#5C3A1E'];

  function init() {
    // Hero tile icons + divider
    ['heroTileL', 'heroTileR'].forEach((id) => fillStrip(document.getElementById(id), LOGO_COLORS.slice(0, 9)));
    fillById('heroDivider', FIVE_B);
    fillById('expStrip', LOGO_COLORS);

    // Section title tile lines
    ['roomsTileLine', 'galTileLine', 'reviewsTileLine', 'testiTileLine'].forEach((id) => fillById(id, FIVE_B));

    // Room accent bars
    const roomPals = [
      [...PAL.gold, ...PAL.teal],
      [...PAL.teal, ...PAL.cobalt],
      [...PAL.burg, ...PAL.gold],
      [...PAL.cobalt, ...PAL.sage],
      [...PAL.sage, ...PAL.gold],
    ];
    [0, 1, 2, 3, 4, 5].forEach((i) => {
      const el = document.getElementById('ra' + i);
      if (!el) return;
      const pal = roomPals[i % roomPals.length];
      for (let k = 0; k < 20; k++) fillStrip(el, [pick(pal)]);
    });

    // Philosophy icon grids (4×4)
    [['pt1', [...PAL.gold, ...PAL.teal]], ['pt2', [...PAL.burg, ...PAL.cobalt]], ['pt3', [...PAL.sage, ...PAL.gold]]]
      .forEach(([id, pal]) => fillGrid(document.getElementById(id), pal, 16, { radius: '2px' }));

    // Testimonial accent bars
    [['ta1', PAL.gold, PAL.teal], ['ta2', PAL.burg, PAL.cobalt], ['ta3', PAL.sage, PAL.gold]].forEach(([id, p1, p2]) => {
      const el = document.getElementById(id);
      if (!el) return;
      for (let k = 0; k < 20; k++) fillStrip(el, [pick([...p1, ...p2])]);
    });

    initParallax();
    initStatCounter();
    initRoomTilt();
    initRoomLightbox();
  }

  function initParallax() {
    const expPhoto = document.getElementById('expPhoto');
    if (!expPhoto) return;
    window.addEventListener('scroll', () => {
      const rect = expPhoto.closest('.experience').getBoundingClientRect();
      const pct = (window.innerHeight - rect.top) / (window.innerHeight + rect.height);
      expPhoto.style.transform = `translateY(${(pct - 0.5) * 40}px)`;
    }, { passive: true });
  }

  function initStatCounter() {
    const statObserver = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        const el = entry.target;
        const text = el.textContent;
        const num = parseFloat(text.replace(/[^0-9.]/g, ''));
        if (!num || text.includes('★') || text.includes('Est')) return;
        const suffix = text.replace(/[\d.]/g, '');
        let start = 0; const dur = 1800;
        const step = (ts) => {
          if (!start) start = ts;
          const prog = Math.min((ts - start) / dur, 1);
          const ease = 1 - Math.pow(1 - prog, 3);
          el.textContent = Math.round(ease * num) + suffix;
          if (prog < 1) requestAnimationFrame(step);
        };
        requestAnimationFrame(step);
        statObserver.unobserve(el);
      });
    }, { threshold: 0.5 });
    document.querySelectorAll('.stat-num').forEach((el) => statObserver.observe(el));
  }

  function initRoomTilt() {
    document.querySelectorAll('.room-card').forEach((card) => {
      card.addEventListener('mousemove', (e) => {
        const rect = card.getBoundingClientRect();
        const x = ((e.clientX - rect.left) / rect.width - 0.5) * 12;
        const y = ((e.clientY - rect.top) / rect.height - 0.5) * -12;
        card.style.transform = `perspective(800px) rotateY(${x}deg) rotateX(${y}deg) scale(1.02)`;
        card.style.transition = 'transform 0.1s';
      });
      card.addEventListener('mouseleave', () => {
        card.style.transform = 'perspective(800px) rotateY(0) rotateX(0) scale(1)';
        card.style.transition = 'transform 0.4s ease';
      });
    });
  }

  function initRoomLightbox() {
    const lb = document.getElementById('lightbox');
    const lbImg = document.getElementById('lb-img');
    if (!lb || !lbImg) return;
    let currentIdx = 0;
    let trigger = null;
    const imgs = () => Array.from(document.querySelectorAll('.room-card .room-photo'));
    const lbClose = document.getElementById('lb-close');
    const lbPrev = document.getElementById('lb-prev');
    const lbNext = document.getElementById('lb-next');
    lb.setAttribute('role', 'dialog');
    lb.setAttribute('aria-modal', 'true');
    lb.setAttribute('aria-label', 'Room photo viewer');
    lbPrev.setAttribute('aria-label', 'Previous room photo');
    lbNext.setAttribute('aria-label', 'Next room photo');
    const behind = () => {
      const out = [];
      for (let n = lb; n && n !== document.body; n = n.parentElement) {
        Array.from(n.parentElement.children).forEach((c) => { if (c !== n && c.tagName !== 'SCRIPT') out.push(c); });
      }
      return out;
    };

    function open(idx) {
      const list = imgs();
      if (!list[idx]) return;
      currentIdx = idx;
      lbImg.src = list[idx].src;
      lbImg.alt = list[idx].alt;
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
      const list = imgs();
      currentIdx = (currentIdx + dir + list.length) % list.length;
      open(currentIdx);
    }

    imgs().forEach((img, idx) => {
      img.style.cursor = 'pointer';
      img.setAttribute('role', 'button');
      img.setAttribute('tabindex', '0');
      img.setAttribute('aria-label', 'Open photo: ' + img.alt);
      img.addEventListener('click', () => open(idx));
      img.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); open(idx); }
      });
    });
    lbClose.addEventListener('click', close);
    lbPrev.addEventListener('click', () => navigate(-1));
    lbNext.addEventListener('click', () => navigate(1));
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

  // Respect reduced-motion: the hero loops indefinitely, so show the poster frame instead.
  function stopHeroVideo() {
    const v = document.querySelector('.hero-video');
    if (v && window.matchMedia('(prefers-reduced-motion: reduce)').matches) { v.removeAttribute('autoplay'); v.pause(); }
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', () => { init(); stopHeroVideo(); });
  else { init(); stopHeroVideo(); }
})();
