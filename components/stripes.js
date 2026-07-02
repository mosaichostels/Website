// components/stripes.js
// Fill colored stripe elements used in hero, dividers, and feature sections
(function() {
  const LOGO_COLORS = ['#C8860A','#8B1A1A','#1A6B7A','#1A3A6B','#5C3A1E','#E8B84B','#3D6B3A','#A02020','#2D9AAA','#7A4F2A'];
  const ACCENT_COLORS = ['#C8860A','#8B1A1A','#1A6B7A','#1A3A6B','#3D6B3A'];

  function fillStripe(el, colors) {
    if (!el) return;
    colors.forEach(c => {
      const span = document.createElement('span');
      span.style.flex = '1';
      span.style.background = c;
      el.appendChild(span);
    });
  }

  function fillById(id, colors) {
    fillStripe(document.getElementById(id), colors);
  }

  function initStripes() {
    // Hero and divider stripes (appear on multiple pages)
    fillById('heroStripe', LOGO_COLORS);
    ['div0', 'div1', 'div2', 'div3', 'div4'].forEach(id => {
      fillById(id, LOGO_COLORS);
    });

    // About page accent lines
    fillById('storyLine', ACCENT_COLORS);
    fillById('whyLine', ACCENT_COLORS);

    // Feature section stripes (page-specific; silently skip if not present)
    fillById('fbStrip', LOGO_COLORS);
    fillById('mapStrip', LOGO_COLORS);
    fillById('ctaStripe', LOGO_COLORS);
    fillById('formStrip', LOGO_COLORS);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initStripes);
  } else {
    initStripes();
  }
})();
