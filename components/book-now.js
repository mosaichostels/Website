// components/book-now.js — book-now page only (platform tiles, benefit icons, card tilt).
(function () {
  const { LOGO_COLORS, PAL, pick, fillById, fillStrip, fillGrid } = window.MOSAIC;

  function init() {
    fillById('cardStrip', LOGO_COLORS);

    // Platform card accent bars
    const platformPals = [
      PAL.gold, PAL.teal, PAL.burg, PAL.cobalt, PAL.sage,
      [...PAL.gold, ...PAL.teal], [...PAL.burg, ...PAL.sage],
      [...PAL.cobalt, ...PAL.gold], [...PAL.teal, ...PAL.burg],
    ];
    [1, 2, 3, 4, 5, 6, 7, 8, 9].forEach((i) => {
      const el = document.getElementById('pt' + i);
      if (!el) return;
      const pal = platformPals[(i - 1) % platformPals.length];
      for (let k = 0; k < 20; k++) fillStrip(el, [pick(pal)]);
    });

    // Benefit icon grids (3×3)
    [[...PAL.gold, ...PAL.teal], [...PAL.burg, ...PAL.cobalt], [...PAL.sage, ...PAL.gold], [...PAL.teal, ...PAL.burg]]
      .forEach((pal, i) => fillGrid(document.getElementById('bi' + (i + 1)), pal, 9, { radius: '2px' }));

    // Platform card 3D tilt
    document.querySelectorAll('.platform-card').forEach((card) => {
      card.addEventListener('mousemove', (e) => {
        const r = card.getBoundingClientRect();
        const x = ((e.clientX - r.left) / r.width - 0.5) * 8;
        const y = ((e.clientY - r.top) / r.height - 0.5) * -8;
        card.style.transform = `perspective(600px) rotateY(${x}deg) rotateX(${y}deg)`;
        card.style.transition = 'transform .1s';
      });
      card.addEventListener('mouseleave', () => {
        card.style.transform = '';
        card.style.transition = 'transform .4s ease';
      });
    });
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
