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
    const imgs = () => Array.from(document.querySelectorAll('.room-card .room-photo'));

    function open(idx) {
      const list = imgs();
      if (!list[idx]) return;
      currentIdx = idx;
      lbImg.src = list[idx].src;
      lbImg.alt = list[idx].alt;
      lb.classList.add('open');
      document.body.style.overflow = 'hidden';
    }
    function close() {
      lb.classList.remove('open');
      document.body.style.overflow = '';
      lbImg.src = '';
    }
    function navigate(dir) {
      const list = imgs();
      currentIdx = (currentIdx + dir + list.length) % list.length;
      open(currentIdx);
    }

    document.querySelectorAll('.room-photo').forEach((img) => { img.style.cursor = 'pointer'; });
    document.addEventListener('click', (e) => {
      if (e.target.classList.contains('room-photo')) {
        const idx = imgs().indexOf(e.target);
        if (idx >= 0) open(idx);
      }
    });
    document.getElementById('lb-close').addEventListener('click', close);
    document.getElementById('lb-prev').addEventListener('click', () => navigate(-1));
    document.getElementById('lb-next').addEventListener('click', () => navigate(1));
    lb.addEventListener('click', (e) => { if (e.target === lb) close(); });
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
