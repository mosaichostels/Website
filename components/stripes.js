// components/stripes.js
(function() {
  const LOGO_COLORS = ['#C8860A','#8B1A1A','#1A6B7A','#1A3A6B','#5C3A1E','#E8B84B','#3D6B3A','#A02020','#2D9AAA','#7A4F2A'];
  const ACCENT_COLORS = ['#C8860A','#8B1A1A','#1A6B7A','#1A3A6B','#3D6B3A'];

  function fillStrip(el, cols) {
    if (!el) return;
    cols.forEach(c => {
      const s = document.createElement('span');
      s.style.flex = '1';
      s.style.background = c;
      el.appendChild(s);
    });
  }

  function fillById(id, cols) {
    fillStrip(document.getElementById(id), cols);
  }

  function initStripes() {
    // Hero stripe
    fillById('heroStripe', LOGO_COLORS);

    // Divider stripes
    ['div0', 'div1', 'div2', 'div3', 'div4'].forEach(id => {
      fillById(id, LOGO_COLORS);
    });

    // Specialty stripes
    fillById('footerStrip', ACCENT_COLORS);
    fillById('storyLine', ACCENT_COLORS);
    fillById('whyLine', ACCENT_COLORS);
    fillById('fbStrip', LOGO_COLORS);
    fillById('mapStrip', LOGO_COLORS);
    fillById('ctaStripe', [...LOGO_COLORS, ...LOGO_COLORS]);
    fillById('formStrip', LOGO_COLORS);
    fillById('cardStrip', LOGO_COLORS);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initStripes);
  } else {
    initStripes();
  }
})();
