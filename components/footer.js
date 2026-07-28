// components/footer.js
(function() {
  function init() {
    const stripe = document.getElementById('footerStrip');
    if (!stripe) return;

    // Fill footer stripe with accent colors
    ['#C8860A', '#8B1A1A', '#1A6B7A', '#1A3A6B', '#3D6B3A'].forEach(color => {
      const span = document.createElement('span');
      span.style.flex = '1';
      span.style.background = color;
      stripe.appendChild(span);
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
