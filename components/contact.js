// components/contact.js — contact page only (accent bars, WhatsApp form).
(function () {
  const { LOGO_COLORS, pick, fillById, fillStrip } = window.MOSAIC;
  const PALS = {
    wa: ['#25D366', '#1DAA56', '#128C7E', '#075E54'],
    'gold-teal': ['#C8860A', '#E8B84B', '#1A6B7A', '#2D9AAA'],
    'cobalt-sage': ['#1A3A6B', '#2A5A9B', '#3D6B3A', '#2D5A2A'],
  };

  function init() {
    fillById('formStrip', LOGO_COLORS);

    document.querySelectorAll('.cc-accent').forEach((el) => {
      const pal = PALS[el.dataset.pal] || LOGO_COLORS;
      for (let i = 0; i < 20; i++) fillStrip(el, [pick(pal)]);
    });

    const form = document.getElementById('contactForm');
    if (form) form.addEventListener('submit', onSubmit);
  }

  function onSubmit(e) {
    e.preventDefault();
    const fname = document.getElementById('fname').value;
    const lname = document.getElementById('lname').value;
    const email = document.getElementById('email').value;
    const topic = document.getElementById('topic').value;
    const message = document.getElementById('message').value;
    if (!fname || !email || !message) { alert('Please fill required fields'); return; }
    const name = fname + (lname ? ' ' + lname : '');
    const waMsg = `Hello Mosaic Hostel,\n\nName: ${name}\nEmail: ${email}\nTopic: ${topic}\n\nMessage:\n${message}`;
    window.open(`https://wa.me/919125492225?text=${encodeURIComponent(waMsg)}`, '_blank');
    const msg = document.getElementById('formMsg');
    msg.textContent = 'Opening WhatsApp...';
    msg.className = 'form-msg success';
    msg.style.display = 'block';
    setTimeout(() => { document.getElementById('contactForm').reset(); msg.style.display = 'none'; }, 2000);
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
