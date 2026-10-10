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
    if (!fname || !message) { showMsg('Please add your first name and a message.', 'error'); return; }
    const name = fname + (lname ? ' ' + lname : '');
    const waMsg = `Hello Mosaic Hostel,\n\nName: ${name}${email ? '\nEmail: ' + email : ''}${topic ? '\nTopic: ' + topic : ''}\n\nMessage:\n${message}`;
    if (window.MOSAIC.trackLead) window.MOSAIC.trackLead('contact_form');
    const waUrl = `https://wa.me/919125492225?text=${encodeURIComponent(waMsg)}`;
    window.open(waUrl, '_blank', 'noopener');
    // Keep what the guest typed: if WhatsApp did not open, they can retry or email the same text.
    const mail = `mailto:mosaichostels@gmail.com?subject=${encodeURIComponent('Enquiry from ' + name)}&body=${encodeURIComponent(message)}`;
    showMsg('', 'success', `WhatsApp should have opened with your message. Nothing happened? <a href="${waUrl}" target="_blank" rel="noopener">Open WhatsApp</a> or <a href="${mail}">send it by email</a>.`);
  }

  function showMsg(text, kind, html) {
    const msg = document.getElementById('formMsg');
    if (html) msg.innerHTML = html; else msg.textContent = text;
    msg.className = 'form-msg ' + kind;
    msg.style.display = 'block';
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
