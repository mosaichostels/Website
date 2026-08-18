// components/book-now.js — book-now page only (platform tiles, benefit icons, card tilt, booking widget).
(function () {
  const { LOGO_COLORS, PAL, pick, fillById, fillStrip, fillGrid } = window.MOSAIC;

  // name|dial-code — India first (most guests), rest alphabetical. Not
  // exhaustive (~90 countries); add more if a guest's nationality is missing.
  const COUNTRIES = ('India|91,Afghanistan|93,Australia|61,Austria|43,Bangladesh|880,Belgium|32,Bhutan|975,'
    + 'Brazil|55,Canada|1,China|86,Denmark|45,Egypt|20,Finland|358,France|33,Germany|49,Greece|30,Hong Kong|852,'
    + 'Indonesia|62,Iran|98,Iraq|964,Ireland|353,Israel|972,Italy|39,Japan|81,Jordan|962,Kazakhstan|7,Kenya|254,'
    + 'Kuwait|965,Malaysia|60,Maldives|960,Mexico|52,Myanmar|95,Nepal|977,Netherlands|31,New Zealand|64,'
    + 'Nigeria|234,Norway|47,Oman|968,Pakistan|92,Philippines|63,Poland|48,Portugal|351,Qatar|974,Russia|7,'
    + 'Saudi Arabia|966,Singapore|65,South Africa|27,South Korea|82,Spain|34,Sri Lanka|94,Sweden|46,'
    + 'Switzerland|41,Thailand|66,Turkey|90,UAE|971,Ukraine|380,United Kingdom|44,United States|1,Vietnam|84')
    .split(',').map((s) => { const [name, code] = s.split('|'); return { name, code }; });

  function escapeHtml(text) {
    const map = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;' };
    return String(text).replace(/[&<>"']/g, (m) => map[m]);
  }

  function populateCountrySelects() {
    const phoneCodeEl = document.getElementById('gPhoneCode');
    const nationalityEl = document.getElementById('gNationality');
    if (phoneCodeEl) {
      phoneCodeEl.innerHTML = COUNTRIES.map((c) => `<option value="+${c.code}">+${c.code} ${escapeHtml(c.name)}</option>`).join('');
    }
    if (nationalityEl) {
      nationalityEl.innerHTML = '<option value=""></option>' + COUNTRIES.map((c) => `<option>${escapeHtml(c.name)}</option>`).join('');
    }
  }

  function init() {
    fillById('cardStrip', LOGO_COLORS);
    fillById('widgetStrip', LOGO_COLORS);
    fillById('policyModalStrip', LOGO_COLORS);
    initBookingWidget();
    initCancelForm();
    initPolicyModal();

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

  // ── BOOKING WIDGET (search → select room → guest details + pay → confirm) ──
  function initBookingWidget() {
    const widget = document.getElementById('bookingWidget');
    if (!widget) return;
    populateCountrySelects();

    const stages = {
      search: document.getElementById('stageSearch'),
      results: document.getElementById('stageResults'),
      guest: document.getElementById('stageGuest'),
      confirm: document.getElementById('stageConfirm'),
    };
    function showStage(name) {
      Object.values(stages).forEach((el) => el.classList.remove('active'));
      stages[name].classList.add('active');
      document.body.classList.toggle('booking-in-progress', name !== 'search');
    }

    // Selection state carried between stages — server re-validates all of it,
    // this is just what's shown to the guest and sent to create-order.php.
    let selection = null; // { check_in, check_out, adults, children, items: [{roomtypeunkid, ratetypeunkid, roomrateunkid, name, qty, per_night, total}], total }
    let cart = []; // same shape as items above, keyed by roomrateunkid while browsing results

    const searchForm = document.getElementById('searchForm');
    const searchMsg = document.getElementById('searchMsg');
    const roomOptions = document.getElementById('roomOptions');
    const cartBar = document.getElementById('cartBar');
    const cartBarSummary = document.getElementById('cartBarSummary');
    const cartContinue = document.getElementById('cartContinue');
    const guestForm = document.getElementById('guestForm');
    const guestMsg = document.getElementById('guestMsg');
    const widgetPrice = document.getElementById('widgetPrice');

    // Sensible date bounds: check-in from today, check-out from check-in.
    const today = new Date().toISOString().slice(0, 10);
    const checkInEl = document.getElementById('checkIn');
    const checkOutEl = document.getElementById('checkOut');
    attachCalendar(checkInEl, () => today);
    attachCalendar(checkOutEl, () => checkInEl.value || today);

    function showMsg(el, text, cls) {
      el.textContent = text;
      el.className = 'form-msg ' + cls;
      el.style.display = 'block';
    }
    function clearMsg(el) {
      el.style.display = 'none';
    }

    if (searchForm) searchForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      clearMsg(searchMsg);
      const params = new URLSearchParams({
        check_in: document.getElementById('checkIn').value,
        check_out: document.getElementById('checkOut').value,
        adults: '1',
        children: '0',
        rooms: '1',
      });
      const btn = searchForm.querySelector('.form-submit');
      btn.disabled = true;
      btn.textContent = 'Searching...';
      try {
        const res = await fetch('/api/availability.php?' + params.toString());
        const data = await res.json();
        if (!res.ok || data.error) throw new Error(data.error || 'Search failed');
        renderRoomOptions(data.rooms || [], params);
        showStage('results');
      } catch (err) {
        showMsg(searchMsg, err.message || 'Could not check availability. Please try WhatsApp instead.', 'error');
      } finally {
        btn.disabled = false;
        btn.textContent = 'Check Availability';
      }
    });

    function renderRoomOptions(rooms, searchParams) {
      roomOptions.innerHTML = '';
      cart = [];
      updateCartBar();
      if (rooms.length === 0) {
        roomOptions.innerHTML = '<div class="widget-empty">No rooms available for these dates. Try different dates or WhatsApp us — we may have options not shown here.</div>';
        return;
      }
      rooms.forEach((room) => {
        const el = document.createElement('div');
        el.className = 'room-option';
        el.innerHTML = `
          <div class="room-option-info">
            <div class="room-option-name">${escapeHtml(room.name)}</div>
            <div class="room-option-desc">${escapeHtml(room.description || '')}</div>
            <div class="room-option-avail">${escapeHtml(String(room.available))} left at this rate</div>
          </div>
          <div class="room-option-price">
            <div class="room-option-total">₹${fmtPrice(room.total)}</div>
            <div class="room-option-pernight">₹${fmtPrice(room.per_night)}/night</div>
            ${room.base_total != null && room.tax_total != null ? `<div class="room-option-pernight">₹${fmtPrice(room.base_total)} + ₹${fmtPrice(room.tax_total)} tax</div>` : ''}
            <div class="room-option-qty">
              <button type="button" class="qty-btn qty-minus" aria-label="Remove one">−</button>
              <span class="qty-value">0</span>
              <button type="button" class="qty-btn qty-plus" aria-label="Add one">+</button>
            </div>
          </div>`;
        const qtyEl = el.querySelector('.qty-value');
        function setQty(qty) {
          qty = Math.max(0, Math.min(room.available, qty));
          qtyEl.textContent = String(qty);
          const existing = cart.find((c) => c.roomrateunkid === room.roomrateunkid);
          if (qty === 0) {
            if (existing) cart = cart.filter((c) => c.roomrateunkid !== room.roomrateunkid);
          } else if (existing) {
            existing.qty = qty;
          } else {
            cart.push({
              roomtypeunkid: room.roomtypeunkid,
              ratetypeunkid: room.ratetypeunkid,
              roomrateunkid: room.roomrateunkid,
              name: room.name,
              per_night: room.per_night,
              total: room.total,
              base_total: room.base_total,
              tax_total: room.tax_total,
              qty,
            });
          }
          updateCartBar();
        }
        el.querySelector('.qty-plus').addEventListener('click', () => setQty(parseInt(qtyEl.textContent, 10) + 1));
        el.querySelector('.qty-minus').addEventListener('click', () => setQty(parseInt(qtyEl.textContent, 10) - 1));
        roomOptions.appendChild(el);
      });

      function updateCartBar() {
        const totalQty = cart.reduce((n, c) => n + c.qty, 0);
        const totalPrice = cart.reduce((n, c) => n + c.total * c.qty, 0);
        if (totalQty === 0) {
          cartBar.style.display = 'none';
          return;
        }
        const baseSum = cart.reduce((n, c) => n + (c.base_total ?? 0) * c.qty, 0);
        const taxSum = cart.reduce((n, c) => n + (c.tax_total ?? 0) * c.qty, 0);
        cartBar.style.display = 'flex';
        cartBarSummary.innerHTML = `${totalQty} room${totalQty > 1 ? 's' : ''} selected <strong>₹${fmtPrice(totalPrice)}</strong>`
          + `<div class="room-option-pernight">₹${fmtPrice(baseSum)} + ₹${fmtPrice(taxSum)} tax</div>`;
      }

      cartContinue.onclick = () => {
        selection = {
          check_in: searchParams.get('check_in'),
          check_out: searchParams.get('check_out'),
          items: cart.slice(),
          total: cart.reduce((n, c) => n + c.total * c.qty, 0),
        };
        const baseSum = selection.items.reduce((n, c) => n + (c.base_total ?? 0) * c.qty, 0);
        const taxSum = selection.items.reduce((n, c) => n + (c.tax_total ?? 0) * c.qty, 0);
        const itemRows = selection.items.map((c) =>
          `<div class="price-row"><span>${c.qty}× ${escapeHtml(c.name)}</span><span>₹${fmtPrice(c.total * c.qty)}</span></div>`).join('');
        widgetPrice.innerHTML = `<div class="price-header"><small>${escapeHtml(selection.check_in)} → ${escapeHtml(selection.check_out)}</small><span>₹${fmtPrice(selection.total)}</span></div>`
          + `<div class="price-breakdown">${itemRows}`
          + `<div class="price-row price-row-divider"><span>Room rate</span><span>₹${fmtPrice(baseSum)}</span></div>`
          + `<div class="price-row"><span>Tax</span><span>₹${fmtPrice(taxSum)}</span></div></div>`;
        clearMsg(guestMsg);
        showStage('guest');
      };
    }

    document.getElementById('backToSearch').addEventListener('click', () => showStage('search'));
    document.getElementById('backToResults').addEventListener('click', () => showStage('results'));

    if (guestForm) guestForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      if (!selection) { showStage('search'); return; }
      clearMsg(guestMsg);
      if (document.getElementById('gEmail').value !== document.getElementById('gEmailConfirm').value) {
        showMsg(guestMsg, 'Email addresses do not match.', 'error');
        return;
      }
      const guest = {
        title: document.getElementById('gTitle').value,
        first_name: document.getElementById('gFirstName').value,
        last_name: document.getElementById('gLastName').value,
        gender: document.getElementById('gGender').value,
      };
      const payload = {
        check_in: selection.check_in,
        check_out: selection.check_out,
        rooms: selection.items.map((i) => ({
          roomtypeunkid: i.roomtypeunkid,
          ratetypeunkid: i.ratetypeunkid,
          roomrateunkid: i.roomrateunkid,
          qty: i.qty,
        })),
        guest: guest,
        first_name: guest.first_name,
        last_name: guest.last_name,
        email: document.getElementById('gEmail').value,
        phone: document.getElementById('gPhone').value,
        phone_code: document.getElementById('gPhoneCode').value,
        nationality: document.getElementById('gNationality').value,
        special_request: document.getElementById('gRequest').value,
        arrival_time: document.getElementById('gArrival').value,
      };
      const btn = guestForm.querySelector('.form-submit');
      btn.disabled = true;
      btn.textContent = 'Preparing payment...';
      try {
        const res = await fetch('/api/create-order.php', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload),
        });
        const order = await res.json();
        if (!res.ok || order.error) throw new Error(order.error || 'Could not start payment');
        openRazorpay(order, payload);
      } catch (err) {
        showMsg(guestMsg, err.message || 'Something went wrong. Please try WhatsApp instead.', 'error');
      } finally {
        btn.disabled = false;
        btn.textContent = 'Pay & Confirm Booking';
      }
    });

    function openRazorpay(order, guest) {
      if (typeof Razorpay === 'undefined') {
        showMsg(guestMsg, 'Payment is temporarily unavailable. Please book via WhatsApp instead.', 'error');
        return;
      }
      const rzp = new Razorpay({
        key: order.key_id,
        amount: order.amount,
        currency: order.currency,
        name: 'Mosaic Hostel Varanasi',
        description: guest.rooms.length + ' room(s) · ' + guest.check_in + ' → ' + guest.check_out,
        order_id: order.order_id,
        prefill: { name: guest.first_name + ' ' + guest.last_name, email: guest.email, contact: guest.phone_code + guest.phone },
        theme: { color: '#C8860A' },
        handler: async function (response) {
          await verifyPayment(response);
        },
        modal: {
          ondismiss: function () {
            showMsg(guestMsg, 'Payment cancelled. Your room selection is still held below — try again when ready.', 'error');
          },
        },
      });
      rzp.on('payment.failed', function () {
        showMsg(guestMsg, 'Payment failed. Please try again or book via WhatsApp.', 'error');
      });
      rzp.open();
    }

    async function verifyPayment(response) {
      showMsg(guestMsg, 'Confirming your booking...', 'success');
      try {
        const res = await fetch('/api/verify-payment.php', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            razorpay_order_id: response.razorpay_order_id,
            razorpay_payment_id: response.razorpay_payment_id,
            razorpay_signature: response.razorpay_signature,
          }),
        });
        const result = await res.json();
        if (!res.ok || result.error) throw new Error(result.error || 'Could not confirm booking');
        document.getElementById('confirmBody').innerHTML =
          `Reservation <strong>#${escapeHtml(result.reservation_no)}</strong> is confirmed. A confirmation has been sent to your email. ` +
          `Questions? <a href="https://wa.me/919125492225" target="_blank">WhatsApp us</a>.`;
        showStage('confirm');
      } catch (err) {
        document.getElementById('confirmTitle').textContent = 'Payment Received';
        document.getElementById('confirmBody').innerHTML =
          `Your payment went through but we couldn't auto-confirm the reservation. Our team will confirm it shortly — ` +
          `for immediate help, <a href="https://wa.me/919125492225?text=${encodeURIComponent('Hi, I just paid for a booking (order ' + response.razorpay_order_id + ') and need help confirming it.')}" target="_blank">message us on WhatsApp</a>.`;
        showStage('confirm');
      }
    }

    function fmtPrice(n) {
      return Number(n).toFixed(2);
    }
  }

  // ── CUSTOM CALENDAR (replaces native <input type=date> popup, which can't
  // be restyled, with one matching the site's fonts/palette) ──
  function attachCalendar(inputEl, getMinDate) {
    if (!inputEl) return;
    const MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];
    const WEEKDAYS = ['Su', 'Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa'];
    let pop = null;
    let viewYear, viewMonth;

    function todayDate() {
      const d = new Date();
      d.setHours(0, 0, 0, 0);
      return d;
    }
    function parseISO(s) {
      if (!s) return null;
      const [y, m, d] = s.split('-').map(Number);
      return new Date(y, m - 1, d);
    }
    function toISO(d) {
      return d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') + '-' + String(d.getDate()).padStart(2, '0');
    }

    function render() {
      const min = parseISO(getMinDate()) || todayDate();
      const selected = parseISO(inputEl.value);
      const t = todayDate();
      pop.innerHTML = `
        <div class="cal-head">
          <button type="button" class="cal-nav cal-prev">‹</button>
          <div class="cal-month">${MONTHS[viewMonth]} ${viewYear}</div>
          <button type="button" class="cal-nav cal-next">›</button>
        </div>
        <div class="cal-weekdays">${WEEKDAYS.map((d) => `<span>${d}</span>`).join('')}</div>
        <div class="cal-days"></div>`;
      const daysEl = pop.querySelector('.cal-days');
      const startWeekday = new Date(viewYear, viewMonth, 1).getDay();
      const daysInMonth = new Date(viewYear, viewMonth + 1, 0).getDate();
      for (let i = 0; i < startWeekday; i++) {
        const empty = document.createElement('div');
        empty.className = 'cal-day cal-empty';
        daysEl.appendChild(empty);
      }
      for (let day = 1; day <= daysInMonth; day++) {
        const d = new Date(viewYear, viewMonth, day);
        const cell = document.createElement('div');
        cell.className = 'cal-day';
        cell.textContent = String(day);
        if (d < min) cell.classList.add('cal-disabled');
        if (d.getTime() === t.getTime()) cell.classList.add('cal-today');
        if (selected && d.getTime() === selected.getTime()) cell.classList.add('cal-selected');
        cell.addEventListener('click', () => {
          inputEl.value = toISO(d);
          inputEl.dispatchEvent(new Event('change'));
          close();
        });
        daysEl.appendChild(cell);
      }
      pop.querySelector('.cal-prev').addEventListener('click', () => {
        viewMonth--;
        if (viewMonth < 0) { viewMonth = 11; viewYear--; }
        render();
      });
      pop.querySelector('.cal-next').addEventListener('click', () => {
        viewMonth++;
        if (viewMonth > 11) { viewMonth = 0; viewYear++; }
        render();
      });
    }

    function position() {
      const r = inputEl.getBoundingClientRect();
      pop.style.top = (window.scrollY + r.bottom + 8) + 'px';
      pop.style.left = (window.scrollX + r.left) + 'px';
    }
    function onOutside(e) {
      if (pop && !pop.contains(e.target) && e.target !== inputEl) close();
    }
    function open() {
      if (pop) return;
      const base = parseISO(inputEl.value) || parseISO(getMinDate()) || todayDate();
      viewYear = base.getFullYear();
      viewMonth = base.getMonth();
      pop = document.createElement('div');
      pop.className = 'cal-pop';
      document.body.appendChild(pop);
      position();
      render();
      requestAnimationFrame(() => pop.classList.add('open'));
      document.addEventListener('mousedown', onOutside, true);
    }
    function close() {
      if (!pop) return;
      document.removeEventListener('mousedown', onOutside, true);
      pop.remove();
      pop = null;
    }

    inputEl.addEventListener('click', open);
    inputEl.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); open(); }
    });
  }

  // ── HOSTEL RULES & POLICIES MODAL ──
  function initPolicyModal() {
    const overlay = document.getElementById('policyModal');
    const openLink = document.getElementById('openPolicyModal');
    const closeBtn = document.getElementById('closePolicyModal');
    if (!overlay || !openLink || !closeBtn) return;
    const open = () => overlay.classList.add('open');
    const close = () => overlay.classList.remove('open');
    openLink.addEventListener('click', (e) => { e.preventDefault(); open(); });
    closeBtn.addEventListener('click', close);
    overlay.addEventListener('click', (e) => { if (e.target === overlay) close(); });
    document.addEventListener('keydown', (e) => { if (e.key === 'Escape') close(); });
  }

  // ── MANAGE / CANCEL A BOOKING ──
  function initCancelForm() {
    const form = document.getElementById('cancelForm');
    if (!form) return;
    const msg = document.getElementById('cancelMsg');
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      msg.style.display = 'none';
      const btn = form.querySelector('.form-submit');
      btn.disabled = true;
      btn.textContent = 'Cancelling...';
      try {
        const res = await fetch('/api/cancel-booking.php', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            reservation_no: document.getElementById('cResNo').value,
            email: document.getElementById('cEmail').value,
          }),
        });
        const result = await res.json();
        if (!res.ok || result.error) throw new Error(result.error || 'Could not cancel booking');
        msg.textContent = `Reservation #${result.reservation_no} has been cancelled.`;
        msg.className = 'form-msg success';
        msg.style.display = 'block';
        form.reset();
      } catch (err) {
        msg.textContent = err.message || 'Something went wrong. Please try WhatsApp instead.';
        msg.className = 'form-msg error';
        msg.style.display = 'block';
      } finally {
        btn.disabled = false;
        btn.textContent = 'Cancel Booking';
      }
    });
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
