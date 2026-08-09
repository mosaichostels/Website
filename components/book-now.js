// components/book-now.js — book-now page only (platform tiles, benefit icons, card tilt, booking widget).
(function () {
  const { LOGO_COLORS, PAL, pick, fillById, fillStrip, fillGrid } = window.MOSAIC;

  function init() {
    fillById('cardStrip', LOGO_COLORS);
    fillById('widgetStrip', LOGO_COLORS);
    initBookingWidget();
    initCancelForm();

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

    const stages = {
      search: document.getElementById('stageSearch'),
      results: document.getElementById('stageResults'),
      guest: document.getElementById('stageGuest'),
      confirm: document.getElementById('stageConfirm'),
    };
    function showStage(name) {
      Object.values(stages).forEach((el) => el.classList.remove('active'));
      stages[name].classList.add('active');
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
        adults: document.getElementById('adultsCount').value,
        children: document.getElementById('childrenCount').value,
        rooms: document.getElementById('roomsCount').value,
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
            <div class="room-option-total">₹${escapeHtml(String(room.total))}</div>
            <div class="room-option-pernight">₹${escapeHtml(String(room.per_night))}/night</div>
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
        cartBar.style.display = 'flex';
        cartBarSummary.innerHTML = `${totalQty} room${totalQty > 1 ? 's' : ''} selected <strong>₹${totalPrice}</strong>`;
      }

      cartContinue.onclick = () => {
        const totalQty = cart.reduce((n, c) => n + c.qty, 0);
        const adults = parseInt(searchParams.get('adults'), 10);
        if (totalQty > adults) {
          showMsg(searchMsg, 'Each room needs at least one adult — increase adults or select fewer rooms.', 'error');
          return;
        }
        selection = {
          check_in: searchParams.get('check_in'),
          check_out: searchParams.get('check_out'),
          adults: searchParams.get('adults'),
          children: searchParams.get('children'),
          items: cart.slice(),
          total: cart.reduce((n, c) => n + c.total * c.qty, 0),
        };
        const namesLabel = selection.items.map((c) => `${c.qty}× ${c.name}`).join(', ');
        widgetPrice.innerHTML = `<small>${escapeHtml(namesLabel)} · ${escapeHtml(selection.check_in)} → ${escapeHtml(selection.check_out)}</small>₹${escapeHtml(String(selection.total))}`;
        renderGuestRooms(selection.items);
        clearMsg(guestMsg);
        const childAgesField = document.getElementById('gChildAgesField');
        const childAgesInput = document.getElementById('gChildAges');
        const hasChildren = parseInt(selection.children, 10) > 0;
        childAgesField.style.display = hasChildren ? '' : 'none';
        childAgesInput.required = hasChildren;
        if (!hasChildren) childAgesInput.value = '';
        showStage('guest');
      };
    }

    document.getElementById('backToSearch').addEventListener('click', () => showStage('search'));
    document.getElementById('backToResults').addEventListener('click', () => showStage('results'));

    const guestRoomsContainer = document.getElementById('guestRoomsContainer');
    function renderGuestRooms(items) {
      guestRoomsContainer.innerHTML = '';
      let n = 0;
      items.forEach((item) => {
        for (let i = 0; i < item.qty; i++) {
          n++;
          const block = document.createElement('div');
          block.className = 'guest-room-block';
          block.innerHTML = `
            <div class="guest-room-label">${n}. ${escapeHtml(item.name)}</div>
            <div class="field-row three">
              <div class="field">
                <label>Title</label>
                <select class="gr-title"><option value=""></option><option>Mr.</option><option>Ms.</option><option>Mrs.</option></select>
              </div>
              <div class="field">
                <label>First Name</label>
                <input type="text" class="gr-fname" required>
              </div>
              <div class="field">
                <label>Last Name</label>
                <input type="text" class="gr-lname">
              </div>
            </div>
            <div class="field">
              <label>Gender</label>
              <select class="gr-gender"><option value="">Prefer not to say</option><option>Male</option><option>Female</option><option>Other</option></select>
            </div>`;
          guestRoomsContainer.appendChild(block);
        }
      });
    }

    if (guestForm) guestForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      if (!selection) { showStage('search'); return; }
      clearMsg(guestMsg);
      if (document.getElementById('gEmail').value !== document.getElementById('gEmailConfirm').value) {
        showMsg(guestMsg, 'Email addresses do not match.', 'error');
        return;
      }
      const guests = Array.from(guestRoomsContainer.querySelectorAll('.guest-room-block')).map((block) => ({
        title: block.querySelector('.gr-title').value,
        first_name: block.querySelector('.gr-fname').value,
        last_name: block.querySelector('.gr-lname').value,
        gender: block.querySelector('.gr-gender').value,
      }));
      const payload = {
        check_in: selection.check_in,
        check_out: selection.check_out,
        adults: selection.adults,
        children: selection.children,
        rooms: selection.items.map((i) => ({
          roomtypeunkid: i.roomtypeunkid,
          ratetypeunkid: i.ratetypeunkid,
          roomrateunkid: i.roomrateunkid,
          qty: i.qty,
        })),
        guests: guests,
        first_name: guests[0].first_name,
        last_name: guests[0].last_name,
        email: document.getElementById('gEmail').value,
        phone: document.getElementById('gPhone').value,
        special_request: document.getElementById('gRequest').value,
        arrival_time: document.getElementById('gArrival').value,
        child_ages: document.getElementById('gChildAges').value,
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
        prefill: { name: guest.first_name + ' ' + guest.last_name, email: guest.email, contact: guest.phone },
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

    function escapeHtml(text) {
      const map = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;' };
      return String(text).replace(/[&<>"']/g, (m) => map[m]);
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
