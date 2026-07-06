// components/about.js — about page only (value icons, deco grid, stats, parallax).
(function () {
  const { LOGO_COLORS, FIVE, PAL, pick, fillById, fillGrid } = window.MOSAIC;

  function init() {
    fillById('storyLine', FIVE);
    fillById('whyLine', FIVE);
    fillById('fbStrip', LOGO_COLORS);

    // Value icon grids (4×4)
    [['vi1', [...PAL.gold, ...PAL.teal]], ['vi2', [...PAL.burg, ...PAL.cobalt]], ['vi3', [...PAL.sage, ...PAL.gold]]]
      .forEach(([id, pal]) => fillGrid(document.getElementById(id), pal, 16, { radius: '2px' }));

    // Deco tile grid (6×6) with hover re-colour
    const deco = document.getElementById('decoTiles');
    if (deco) {
      fillGrid(deco, LOGO_COLORS, 36, { radius: '3px', randomOpacity: true });
      deco.addEventListener('mouseenter', () => {
        deco.querySelectorAll('span').forEach((s) => {
          setTimeout(() => {
            s.style.background = pick(LOGO_COLORS);
            s.style.opacity = String(0.3 + Math.random() * 0.7);
          }, Math.random() * 300);
        });
      });
    }

    initParallax();
    initStatCounter();
  }

  function initParallax() {
    const fbPhoto = document.getElementById('fbPhoto');
    if (!fbPhoto) return;
    window.addEventListener('scroll', () => {
      const rect = fbPhoto.closest('.fullbleed').getBoundingClientRect();
      const pct = (window.innerHeight - rect.top) / (window.innerHeight + rect.height);
      fbPhoto.style.transform = `translateY(${(pct - 0.5) * 40}px)`;
    }, { passive: true });
  }

  function initStatCounter() {
    const statObs = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        const el = entry.target;
        const target = parseInt(el.dataset.count, 10);
        let start = 0; const dur = 1600;
        const step = (ts) => {
          if (!start) start = ts;
          const prog = Math.min((ts - start) / dur, 1);
          const ease = 1 - Math.pow(1 - prog, 3);
          el.textContent = Math.round(ease * target) + (target === 500 ? '+' : '');
          if (prog < 1) requestAnimationFrame(step);
        };
        requestAnimationFrame(step);
        statObs.unobserve(el);
      });
    }, { threshold: 0.5 });
    document.querySelectorAll('.stat-num[data-count]').forEach((el) => statObs.observe(el));
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
