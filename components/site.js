// components/site.js — shared site behaviour, loaded on every page.
// Exposes helpers on window.MOSAIC for page-specific scripts.
(function () {
  const LOGO_COLORS = ['#C8860A', '#8B1A1A', '#1A6B7A', '#1A3A6B', '#5C3A1E', '#E8B84B', '#3D6B3A', '#A02020', '#2D9AAA', '#7A4F2A'];
  const FIVE = ['#C8860A', '#8B1A1A', '#1A6B7A', '#1A3A6B', '#3D6B3A']; // footer / divider palette
  const PAL = {
    gold: ['#C8860A', '#E8B84B', '#D4930F', '#F0C060'],
    teal: ['#1A6B7A', '#2D9AAA', '#0D4A55'],
    burg: ['#8B1A1A', '#A02020', '#6B1010'],
    cobalt: ['#1A3A6B', '#2A5A9B', '#0D1A40'],
    brown: ['#5C3A1E', '#7A4F2A', '#3A2010'],
    sage: ['#3D6B3A', '#2D5A2A'],
  };
  const pick = (arr) => arr[Math.floor(Math.random() * arr.length)];

  // Fill a horizontal stripe element with equal-flex colour spans.
  function fillStrip(el, cols) {
    if (!el) return;
    cols.forEach((c) => {
      const s = document.createElement('span');
      s.style.flex = '1';
      s.style.background = c;
      el.appendChild(s);
    });
  }
  function fillById(id, cols) { fillStrip(document.getElementById(id), cols); }

  // Fill a CSS-grid element with `count` coloured tiles (icons / deco grids).
  function fillGrid(el, palette, count, opts = {}) {
    if (!el) return;
    for (let i = 0; i < count; i++) {
      const s = document.createElement('span');
      s.style.background = pick(palette);
      s.style.display = 'block';
      if (opts.radius) s.style.borderRadius = opts.radius;
      if (opts.randomOpacity) s.style.opacity = String(0.3 + Math.random() * 0.7);
      el.appendChild(s);
    }
  }

  window.MOSAIC = { LOGO_COLORS, FIVE, PAL, pick, fillStrip, fillById, fillGrid };

  // ── UNIVERSAL STRIPE FILLS (only fills IDs present on the page) ──
  const FILL_MAP = {
    heroStripe: LOGO_COLORS,
    div0: LOGO_COLORS,
    div1: LOGO_COLORS,
    mapStrip: LOGO_COLORS,
    footerStrip: FIVE,
  };
  function runUniversalFills() {
    Object.entries(FILL_MAP).forEach(([id, cols]) => fillById(id, cols));
  }

  // ── CUSTOM CURSOR ──
  function initCursor() {
    const cur = document.getElementById('cursor');
    const ring = document.getElementById('cursor-ring');
    if (!cur || !ring) return;
    document.addEventListener('mousemove', (e) => {
      cur.style.left = e.clientX + 'px'; cur.style.top = e.clientY + 'px';
      ring.style.left = e.clientX + 'px'; ring.style.top = e.clientY + 'px';
    });
    document.querySelectorAll('a,button,input,select,textarea,.room-card,.gal-item,.platform-card').forEach((el) => {
      el.addEventListener('mouseenter', () => {
        cur.style.width = '18px'; cur.style.height = '18px';
        ring.style.width = '48px'; ring.style.height = '48px';
      });
      el.addEventListener('mouseleave', () => {
        cur.style.width = '10px'; cur.style.height = '10px';
        ring.style.width = '36px'; ring.style.height = '36px';
      });
    });
  }

  // ── NAV SCROLL SHADOW ──
  function initNavScroll() {
    const nav = document.getElementById('mainNav');
    if (nav) window.addEventListener('scroll', () => nav.classList.toggle('scrolled', window.scrollY > 80));
  }

  // ── SCROLL PROGRESS BAR ──
  // Uses #progress if present, else injects a fixed bar (index has no #progress).
  function initProgress() {
    let bar = document.getElementById('progress');
    if (!bar) {
      bar = document.createElement('div');
      bar.style.cssText = 'position:fixed;top:0;left:0;height:3px;background:linear-gradient(90deg,#C8860A,#8B1A1A,#1A6B7A);z-index:9999;width:0%;transition:width 0.1s;pointer-events:none;';
      document.body.appendChild(bar);
    }
    window.addEventListener('scroll', () => {
      const pct = (window.scrollY / (document.body.scrollHeight - window.innerHeight)) * 100;
      bar.style.width = pct + '%';
    }, { passive: true });
  }

  // ── SCROLL REVEAL ── (exposed so dynamically-added cards can be observed)
  const revealObserver = new IntersectionObserver((entries) => {
    entries.forEach((e) => { if (e.isIntersecting) e.target.classList.add('visible'); });
  }, { threshold: 0.12 });
  window.MOSAIC.revealObserver = revealObserver;
  function initReveal() {
    document.querySelectorAll('.reveal').forEach((el) => revealObserver.observe(el));
  }

  // ── MAGNETIC BUTTONS + RIPPLE ──
  const MAG_SELECTOR = '.btn-gold,.btn-primary,.btn-outline,.hero-cta,.nav-book,.wa-cta,.email-cta,.form-submit,.wa-btn,.email-btn';
  function initMagnetic() {
    document.querySelectorAll(MAG_SELECTOR).forEach((btn) => {
      btn.addEventListener('mousemove', (e) => {
        const r = btn.getBoundingClientRect();
        btn.style.transform = `translate(${(e.clientX - r.left - r.width / 2) * 0.2}px,${(e.clientY - r.top - r.height / 2) * 0.2}px)`;
        btn.style.transition = 'transform 0.1s';
      });
      btn.addEventListener('mouseleave', () => {
        btn.style.transform = 'translate(0,0)';
        btn.style.transition = 'transform 0.4s ease';
      });
    });
  }
  function initRipple() {
    document.querySelectorAll('.btn-gold,.btn-primary,.hero-cta,.nav-book').forEach((btn) => {
      btn.style.overflow = 'hidden'; btn.style.position = 'relative';
      btn.addEventListener('click', (e) => {
        const r = document.createElement('span');
        const rect = btn.getBoundingClientRect();
        const size = Math.max(rect.width, rect.height) * 2;
        r.style.cssText = `position:absolute;width:${size}px;height:${size}px;border-radius:50%;background:rgba(255,255,255,0.25);transform:translate(-50%,-50%) scale(0);left:${e.clientX - rect.left}px;top:${e.clientY - rect.top}px;animation:ripple 0.6s ease-out forwards;pointer-events:none;`;
        btn.appendChild(r);
        setTimeout(() => r.remove(), 700);
      });
    });
  }

  // ── MAPS DIALOG (about / contact / privacy) ──
  window.openMapsDialog = function (e) {
    e.preventDefault();
    const addr = 'B1/85C, Assi Ghat Road, Varanasi, Uttar Pradesh 221005';
    const choice = confirm('Open directions in:\n\nOK = Google Maps\nCancel = Apple Maps');
    if (choice) window.open(`https://maps.google.com/?q=${encodeURIComponent(addr)}`, '_blank');
    else window.open(`maps://maps.apple.com/?address=${encodeURIComponent(addr)}`);
  };

  function init() {
    runUniversalFills();
    initCursor();
    initNavScroll();
    initProgress();
    initReveal();
    initMagnetic();
    initRipple();
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
