// components/book-now.js — book-now page only (platform tiles, benefit icons, card tilt, booking widget).
(function () {
  // Destructuring window.MOSAIC unguarded meant that if site.js failed to load,
  // this threw before init() and the booking widget silently never started —
  // the form still rendered, looked fine, and did nothing at all. Decorative
  // helpers degrade to no-ops; the booking flow does not depend on any of them.
  const M = window.MOSAIC || {};
  const noop = () => {};
  const LOGO_COLORS = M.LOGO_COLORS || [];
  const PAL = M.PAL || { gold: [], teal: [], burg: [], cobalt: [], sage: [] };
  const pick = M.pick || (() => '');
  const fillById = M.fillById || noop;
  const fillStrip = M.fillStrip || noop;
  const fillGrid = M.fillGrid || noop;
  if (!window.MOSAIC) {
    // Visible in the console rather than silent, so this is diagnosable.
    console.warn('[mosaic] site.js did not load; booking works, decoration is skipped.');
  }

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

    // Read the landing query string ONCE, before anything can rewrite it. The
    // search stage's own URL is the bare path, so syncHistory('search') strips
    // ?check_in= — and a deep link read after that finds nothing. Capturing
    // here makes restoreFromUrl() independent of bootstrap ordering.
    const landingParams = new URLSearchParams(window.location.search);

    const stages = {
      search: document.getElementById('stageSearch'),
      results: document.getElementById('stageResults'),
      guest: document.getElementById('stageGuest'),
      confirm: document.getElementById('stageConfirm'),
    };
    // mode: 'push' for forward navigation (adds a history entry, so Back
    // returns to the previous stage instead of leaving the site), 'replace' for
    // backward navigation and terminal states (so history doesn't grow every
    // time someone steps back and forward), 'none' when the change was itself
    // driven by popstate. Every call site states its mode — the flow used to
    // create no history at all, so Back from the guest form abandoned the
    // booking and left the site.
    function showStage(name, mode) {
      const changed = !stages[name].classList.contains('active');
      Object.values(stages).forEach((el) => el.classList.remove('active'));
      stages[name].classList.add('active');
      document.body.classList.toggle('booking-in-progress', name !== 'search');
      if (mode && mode !== 'none') syncHistory(name, mode);
      updateSteps(name);
      // Focus was left on a control inside the stage we just hid, so keyboard
      // and screen-reader users had no idea anything had happened. Moving it to
      // the new stage's heading announces the change and puts the tab order in
      // the right place. preventScroll keeps the page from jumping on mobile.
      if (changed) {
        const heading = stages[name].querySelector('.direct-title');
        if (heading) {
          heading.setAttribute('tabindex', '-1');
          try { heading.focus({ preventScroll: true }); } catch (err) { heading.focus(); }
        }
      }
    }

    // Selection state carried between stages — server re-validates all of it,
    // this is just what's shown to the guest and sent to create-order.php.
    let selection = null; // { check_in, check_out, adults, children, items: [{roomtypeunkid, ratetypeunkid, roomrateunkid, name, qty, per_night, total}], total }
    let cart = []; // same shape as items above, keyed by roomrateunkid while browsing results
    // Last Razorpay order created, so a retry after a failed or cancelled
    // payment reopens it rather than creating a second order for one booking.
    let lastOrder = null; // { order, payload, key, createdAt }
    // Reservation number already reported to GA4 as a purchase. Revenue
    // double-counting is worse than a missing event, so this is keyed by
    // reservation rather than being a plain boolean.
    let purchaseReported = null;
    const ORDER_REUSE_MS = 10 * 60 * 1000;

    const searchForm = document.getElementById('searchForm');
    const searchMsg = document.getElementById('searchMsg');
    const roomOptions = document.getElementById('roomOptions');
    const cartBar = document.getElementById('cartBar');
    const cartBarSummary = document.getElementById('cartBarSummary');
    const cartContinue = document.getElementById('cartContinue');
    const guestForm = document.getElementById('guestForm');
    const guestMsg = document.getElementById('guestMsg');
    const widgetPrice = document.getElementById('widgetPrice');
    const retryBtn = document.getElementById('retryPayment');
    const resultsMsg = document.getElementById('resultsMsg');

    // Sensible date bounds: check-in from today, check-out from check-in.
    const today = new Date().toISOString().slice(0, 10);
    const checkInEl = document.getElementById('checkIn');
    const checkOutEl = document.getElementById('checkOut');
    attachCalendar(checkInEl, () => today);
    attachCalendar(checkOutEl, () => checkInEl.value || today);

    // Dates live in the query string so a search can be linked, bookmarked or
    // pointed at from an ad, and so a refresh lands somewhere useful.
    function stageUrl(name) {
      const path = window.location.pathname;
      if (name === 'search' || !selection && !checkInEl.value) return path;
      const from = selection ? selection.check_in : checkInEl.value;
      const to = selection ? selection.check_out : checkOutEl.value;
      return (from && to) ? `${path}?check_in=${encodeURIComponent(from)}&check_out=${encodeURIComponent(to)}` : path;
    }

    // Stages are strictly ordered, so the number of history entries we own is
    // just the current stage's depth. That's what lets a backward move UNWIND
    // the stack instead of replacing the top of it — replacing meant every
    // "change dates" round trip left another entry behind, and twenty of them
    // left a guest pressing Back twenty times to escape the page.
    const STAGE_DEPTH = { search: 0, results: 1, guest: 2, confirm: 2 };

    function goBackTo(name) {
      const steps = (STAGE_DEPTH[stageName()] ?? 0) - (STAGE_DEPTH[name] ?? 0);
      // Show it straight away; popstate re-applies the same stage, which is a
      // no-op. Doing both means the UI still moves if history is unavailable.
      showStage(name, 'none');
      if (steps > 0 && steps <= 2 && window.history && window.history.go) {
        try { window.history.go(-steps); } catch (err) { syncHistory(name, 'replace'); }
      } else {
        syncHistory(name, 'replace');
      }
    }

    function stageName() {
      return Object.keys(stages).find((k) => stages[k].classList.contains('active')) || 'search';
    }

    function syncHistory(name, mode) {
      if (!window.history || !window.history.pushState) return;
      const state = { mosaicStage: name };
      try {
        if (mode === 'push') window.history.pushState(state, '', stageUrl(name));
        else window.history.replaceState(state, '', stageUrl(name));
      } catch (err) {
        // History is a nice-to-have; never let it break the booking.
      }
    }

    window.addEventListener('popstate', (e) => {
      const stage = e.state && e.state.mosaicStage;
      // No state of ours means the user has stepped back past where the widget
      // started — let the browser do what it was going to do.
      if (!stage || !stages[stage]) return;
      // Never restore a stage whose data is gone (e.g. Back after a completed
      // booking, which clears the selection): send them to the start instead.
      if ((stage === 'guest' || stage === 'confirm') && !selection) {
        showStage('search', 'none');
        return;
      }
      showStage(stage, 'none');
    });

    // Arriving with dates already in the URL — a shared link, a bookmark, an ad
    // — runs the search straight away instead of showing an empty form the
    // guest has to fill in again. Also what makes a refresh mid-flow land
    // somewhere useful rather than back at square one.
    function restoreFromUrl() {
      const from = landingParams.get('check_in') || '';
      const to = landingParams.get('check_out') || '';
      // Same YYYY-MM-DD strictness the calendar and the server apply; a bad
      // link should show the normal empty form, not an error.
      const valid = /^\d{4}-\d{2}-\d{2}$/;
      if (!valid.test(from) || !valid.test(to) || to <= from) return;
      checkInEl.value = from;
      checkOutEl.value = to;
      if (searchForm) searchForm.requestSubmit ? searchForm.requestSubmit() : searchForm.dispatchEvent(new Event('submit'));
    }

    // Errors are assertive, progress updates are polite. Without a role these
    // appeared silently — "Email addresses do not match", "Payment failed" and
    // "Confirming your booking..." all announced nothing at all.
    function showMsg(el, text, cls) {
      el.textContent = text;
      el.className = 'form-msg ' + cls;
      el.setAttribute('role', cls === 'error' ? 'alert' : 'status');
      el.setAttribute('aria-live', cls === 'error' ? 'assertive' : 'polite');
      el.style.display = 'block';
    }
    function clearMsg(el) {
      el.style.display = 'none';
      el.removeAttribute('role');
      el.removeAttribute('aria-live');
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
        track('view_item_list', {
          item_list_name: 'Availability results',
          nights: nightsBetween(params.get('check_in'), params.get('check_out')),
          items: (data.rooms || []).map((r) => ({ item_id: r.roomrateunkid, item_name: r.name, price: Number(r.total) || 0 })),
        });
        showStage('results', 'push');
      } catch (err) {
        showMsg(searchMsg, err.message || 'Could not check availability. Please try WhatsApp instead.', 'error');
      } finally {
        btn.disabled = false;
        btn.textContent = 'Check Availability';
      }
    });

    function renderRoomOptions(rooms, searchParams) {
      clearMsg(resultsMsg);
      // The prices below are stay totals, but the stage never said for which
      // dates or how many nights — so there was no way to sanity-check them.
      const from = searchParams.get('check_in');
      const to = searchParams.get('check_out');
      const nights = nightsBetween(from, to);
      const context = document.getElementById('resultsContext');
      if (context) context.textContent = `${from} → ${to} · ${nights} ${plural(nights, 'night')}`;
      roomOptions.innerHTML = '';
      cart = [];
      updateCartBar();
      if (rooms.length === 0) {
        roomOptions.innerHTML = '<div class="widget-empty">No rooms available for these dates. Try different dates or WhatsApp us — we may have options not shown here.</div>';
        return;
      }
      rooms.forEach((room) => {
        // Adults this rate covers. Dorm beds are priced per bed so this is 1
        // and no guest stepper appears; a private double covers 2, which is
        // the case that was previously impossible to express — a couple got
        // sent to eZee as a single guest. Above base occupancy eZee charges an
        // extra-adult rate we don't compute, so the server refuses it too.
        const baseAdults = Math.max(1, Number(room.base_adults) || 1);
        // Three states, not two: a real count, a confirmed zero, and eZee not
        // reporting one at all. Only the first is bookable here; the third gets
        // a WhatsApp link rather than a stepper that silently does nothing.
        const bookable = typeof room.available === 'number' && room.available > 0;
        const el = document.createElement('div');
        el.className = 'room-option';
        el.innerHTML = `
          <div class="room-option-info">
            <div class="room-option-name">${escapeHtml(room.name)}</div>
            <div class="room-option-desc">${escapeHtml(room.description || '')}</div>
            <div class="room-option-avail">${availabilityLabel(room)}</div>
          </div>
          <div class="room-option-price">
            <div class="room-option-total">₹${fmtPrice(room.total)}</div>
            <div class="room-option-pernight">₹${fmtPrice(room.per_night)}/night</div>
            ${room.base_total != null && room.tax_total != null ? `<div class="room-option-pernight">₹${fmtPrice(room.base_total)} + ₹${fmtPrice(room.tax_total)} tax</div>` : ''}
            ${!bookable ? `<div class="room-option-unavailable">${room.available === 0
              ? 'Sold out for these dates'
              : `<a href="https://wa.me/919125492225?text=${encodeURIComponent('Hi! Is the ' + room.name + ' available for ' + searchParams.get('check_in') + ' to ' + searchParams.get('check_out') + '?')}" target="_blank" rel="noopener">Ask us on WhatsApp</a>`}</div>` : ''}
            <div class="room-option-qty"${!bookable ? ' style="display:none"' : ''}>
              <span class="qty-label">Rooms</span>
              <button type="button" class="qty-btn qty-minus" aria-label="One fewer ${escapeHtml(room.name)}">−</button>
              <span class="qty-value">0</span>
              <button type="button" class="qty-btn qty-plus" aria-label="One more ${escapeHtml(room.name)}">+</button>
            </div>
            ${baseAdults > 1 ? `
            <div class="room-option-qty room-option-guests" style="display:none">
              <span class="qty-label">Guests each</span>
              <button type="button" class="qty-btn adults-minus" aria-label="One fewer guest per ${escapeHtml(room.name)}">−</button>
              <span class="adults-value">1</span>
              <button type="button" class="qty-btn adults-plus" aria-label="One more guest per ${escapeHtml(room.name)}">+</button>
            </div>` : ''}
          </div>`;
        const qtyEl = el.querySelector('.qty-value');
        const guestsRow = el.querySelector('.room-option-guests');
        const adultsEl = el.querySelector('.adults-value');
        let adults = 1;

        function setQty(qty) {
          const capped = Math.max(0, Math.min(room.available, qty));
          // Clicking + at the ceiling used to do nothing at all, with no reason
          // given — indistinguishable from a broken button.
          if (qty > capped) {
            showMsg(resultsMsg, `Only ${capped} ${plural(capped, 'room')} left of ${room.name} for these dates. For more, WhatsApp us.`, 'error');
          } else {
            clearMsg(resultsMsg);
          }
          qty = capped;
          qtyEl.textContent = String(qty);
          // Asking how many guests before a room is even selected is noise.
          if (guestsRow) guestsRow.style.display = qty > 0 ? 'flex' : 'none';
          const existing = cart.find((c) => c.roomrateunkid === room.roomrateunkid);
          if (qty === 0) {
            if (existing) cart = cart.filter((c) => c.roomrateunkid !== room.roomrateunkid);
          } else if (existing) {
            existing.qty = qty;
            existing.adults = adults;
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
              adults,
            });
          }
          updateCartBar();
          const previous = parseInt(qtyEl.dataset.prev || '0', 10);
          if (qty !== previous) {
            track(qty > previous ? 'add_to_cart' : 'remove_from_cart', {
              currency: 'INR',
              value: Number(room.total) * Math.abs(qty - previous),
              items: [{ item_id: room.roomrateunkid, item_name: room.name, price: Number(room.total) || 0, quantity: Math.abs(qty - previous) }],
            });
            qtyEl.dataset.prev = String(qty);
          }
        }
        function setAdults(next) {
          adults = Math.max(1, Math.min(baseAdults, next));
          adultsEl.textContent = String(adults);
          const existing = cart.find((c) => c.roomrateunkid === room.roomrateunkid);
          if (existing) existing.adults = adults;
          updateCartBar();
        }

        el.querySelector('.qty-plus').addEventListener('click', () => setQty(parseInt(qtyEl.textContent, 10) + 1));
        el.querySelector('.qty-minus').addEventListener('click', () => setQty(parseInt(qtyEl.textContent, 10) - 1));
        if (guestsRow) {
          el.querySelector('.adults-plus').addEventListener('click', () => setAdults(adults + 1));
          el.querySelector('.adults-minus').addEventListener('click', () => setAdults(adults - 1));
        }
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
        cartBarSummary.innerHTML = `${totalQty} ${plural(totalQty, 'room')} selected <strong>₹${fmtPrice(totalPrice)}</strong>`
          + `<div class="room-option-pernight">₹${fmtPrice(baseSum)} + ₹${fmtPrice(taxSum)} tax</div>`;
      }

      cartContinue.onclick = () => {
        selection = {
          check_in: searchParams.get('check_in'),
          check_out: searchParams.get('check_out'),
          items: cart.slice(),
          total: cart.reduce((n, c) => n + c.total * c.qty, 0),
        };
        renderPriceSummary();
        clearMsg(guestMsg);
        track('begin_checkout', { currency: 'INR', value: selection.total, items: trackItems(selection.items) });
        showStage('guest', 'push');
      };
    }

    document.getElementById('backToSearch').addEventListener('click', () => goBackTo('search'));
    document.getElementById('backToResults').addEventListener('click', () => {
      // Leaving the guest stage abandons any failed attempt with it — a retry
      // button left on screen would reopen an order for rooms they're changing.
      hideRetry();
      clearMsg(guestMsg);
      goBackTo('results');
    });

    if (guestForm) guestForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      if (!selection) { showStage('search', 'replace'); return; }
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
          adults: i.adults || 1,
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
        // Advisory: what the guest was shown. The server prices independently
        // and stops to ask if the two disagree — it never trusts this figure.
        expected_total: selection.total,
      };
      const btn = guestForm.querySelector('.form-submit');
      btn.disabled = true;
      btn.textContent = 'Preparing payment...';
      try {
        const payloadKey = JSON.stringify(payload);
        // A failed or cancelled payment is a retry of the same booking, not a
        // new one. Reopening the order we already created avoids leaving a
        // dead Razorpay order (and a dead pending/*.json) behind on every
        // attempt. Anything the guest actually changed produces a different
        // key, and a stale order is re-created so price and inventory get
        // re-validated server-side rather than being trusted indefinitely.
        if (lastOrder && lastOrder.key === payloadKey && Date.now() - lastOrder.createdAt < ORDER_REUSE_MS) {
          openRazorpay(lastOrder.order, payload);
          return;
        }
        const res = await fetch('/api/create-order.php', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload),
        });
        const order = await res.json();
        if (order && order.price_changed) {
          // Re-price the visible summary and let them decide. Submitting again
          // now sends the new figure and goes through.
          selection.total = order.new_total;
          renderPriceSummary();
          showMsg(guestMsg, `The rate for these dates changed from ₹${fmtPrice(order.old_total)} to ₹${fmtPrice(order.new_total)}. `
            + 'The summary above is updated — press Pay & Confirm Booking again to continue at the new rate.', 'error');
          return;
        }
        if (!res.ok || order.error) throw new Error(order.error || 'Could not start payment');
        lastOrder = { order, payload, key: payloadKey, createdAt: Date.now() };
        openRazorpay(order, payload);
      } catch (err) {
        showMsg(guestMsg, err.message || 'Something went wrong. Please try WhatsApp instead.', 'error');
      } finally {
        btn.disabled = false;
        btn.textContent = 'Pay & Confirm Booking';
      }
    });

    // Payment didn't complete: say so, and put the way forward on screen. The
    // guest previously had to work out for themselves that scrolling back up
    // and re-submitting the form was the retry.
    function offerRetry(message) {
      showMsg(guestMsg, message, 'error');
      if (retryBtn) retryBtn.style.display = 'block';
    }
    function hideRetry() {
      if (retryBtn) retryBtn.style.display = 'none';
    }
    if (retryBtn) retryBtn.addEventListener('click', () => {
      if (!lastOrder || Date.now() - lastOrder.createdAt >= ORDER_REUSE_MS) {
        // Rates and availability move; past the reuse window we re-price rather
        // than reopen a stale order.
        hideRetry();
        showMsg(guestMsg, 'This payment session has expired. Please press "Pay & Confirm Booking" to start a fresh one.', 'error');
        return;
      }
      hideRetry();
      clearMsg(guestMsg);
      openRazorpay(lastOrder.order, lastOrder.payload);
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
        description: (() => {
          const units = guest.rooms.reduce((n, r) => n + (r.qty || 1), 0);
          return `${units} ${plural(units, 'room')} · ${guest.check_in} → ${guest.check_out}`;
        })(),
        order_id: order.order_id,
        prefill: { name: guest.first_name + ' ' + guest.last_name, email: guest.email, contact: guest.phone_code + guest.phone },
        theme: { color: '#C8860A' },
        handler: async function (response) {
          await verifyPayment(response);
        },
        modal: {
          ondismiss: function () {
            offerRetry('Payment cancelled. Your rooms are still selected — pick up where you left off below.');
          },
        },
      });
      rzp.on('payment.failed', function () {
        offerRetry('That payment didn\'t go through. No money has been taken — try again, or book over WhatsApp.');
      });
      hideRetry();
      track('add_payment_info', {
        currency: 'INR',
        value: paidAmount(),
        payment_type: 'Razorpay',
        items: selection ? trackItems(selection.items) : [],
      });
      rzp.open();
    }

    // Badge, title and body of the confirmation stage move together, always.
    // The badge used to be fixed in the HTML as "Booking Confirmed" while only
    // the title and body were rewritten, so a guest whose booking had NOT
    // confirmed read a confirmation badge directly above the text telling them
    // it hadn't. Setting them apart is what allowed that; this is the only way
    // the stage is now shown.
    function showConfirmStage(state) {
      document.getElementById('confirmBadgeText').textContent = state.badge;
      document.getElementById('confirmBadge').classList.toggle('is-pending', state.pending === true);
      document.getElementById('confirmTitle').textContent = state.title;
      document.getElementById('confirmBody').innerHTML = state.bodyHtml;

      // What was booked, on the screen that confirms it. Until now this stage
      // showed a reservation number and nothing else — no dates, no room, no
      // amount — so there was nothing for the guest to check or screenshot.
      const summary = document.getElementById('confirmSummary');
      summary.innerHTML = selection ? summaryRows(selection) : '';

      // Actions depend on the outcome. "Make another booking" is deliberately
      // absent from the pending state: that guest has already paid and their
      // reservation is unresolved, so inviting them to start another one is
      // inviting a second payment.
      const actions = document.getElementById('confirmActions');
      actions.innerHTML = state.pending
        ? '<a class="widget-back" href="/">Return to home</a>'
        : '<button type="button" class="form-submit" id="bookAgain">Make another booking</button>'
          + '<a class="widget-back" href="/">Return to home</a>';
      const again = document.getElementById('bookAgain');
      if (again) again.addEventListener('click', resetWidget);

      showStage('confirm', 'replace');
    }

    function summaryRows(sel) {
      const nights = nightsBetween(sel.check_in, sel.check_out);
      // Amount charged comes from the order the SERVER priced, not the cart sum
      // the browser calculated — create-order.php re-fetches from eZee and can
      // legitimately arrive at a different figure. Per-room prices are left off
      // for the same reason: rows that don't add up to the total read as an
      // error, and this screen's job is what was booked and what was paid.
      const paid = paidAmount();
      const rooms = sel.items.map((c) =>
        `<div class="price-row"><span>Room</span><span>${c.qty}× ${escapeHtml(c.name)}${guestSuffix(c)}</span></div>`).join('');
      return `<div class="price-row"><span>Dates</span><span>${escapeHtml(sel.check_in)} → ${escapeHtml(sel.check_out)}</span></div>`
        + `<div class="price-row"><span>Nights</span><span>${nights}</span></div>`
        + rooms
        + `<div class="price-row price-row-divider"><span>Total paid</span><span>₹${fmtPrice(paid)}</span></div>`;
    }

    // "Make another booking" has to put the widget back to a genuinely clean
    // state — including re-enabling the pay button, which verifyPayment()
    // disables and never restores, and dropping lastOrder so the next booking
    // can't reopen this one's Razorpay order.
    function resetWidget() {
      selection = null;
      cart = [];
      lastOrder = null;
      hideRetry();
      roomOptions.innerHTML = '';
      cartBar.style.display = 'none';
      widgetPrice.innerHTML = '';
      if (searchForm) searchForm.reset();
      if (guestForm) {
        guestForm.reset();
        const payBtn = guestForm.querySelector('.form-submit');
        if (payBtn) {
          payBtn.disabled = false;
          payBtn.textContent = 'Pay & Confirm Booking';
        }
      }
      clearMsg(searchMsg);
      clearMsg(resultsMsg);
      clearMsg(guestMsg);
      goBackTo('search');
    }

    // A 409 from verify-payment.php does NOT mean the booking failed. It means
    // another path — the Razorpay webhook — claimed this order microseconds
    // earlier and is still inside eZee's InsertBooking, which can run to its
    // 15s timeout. The reservation is being created; announcing failure here
    // sends a guest with a perfectly good booking to WhatsApp. Network errors
    // are retried for the same reason: confirm_paid_order() is idempotent
    // behind its atomic rename() claim, so repeating the call is always safe.
    const VERIFY_RETRY_DELAYS = [1000, 2000, 3000, 5000, 5000]; // ~16s total

    async function verifyPayment(response) {
      showMsg(guestMsg, 'Confirming your booking...', 'success');
      // The pay button was re-enabled the moment Razorpay's modal opened, and
      // this can now sit here for ~16s — long enough for an anxious guest to
      // press it again and create a second order. It has no job left.
      const payBtn = guestForm.querySelector('.form-submit');
      if (payBtn) {
        payBtn.disabled = true;
        payBtn.textContent = 'Confirming...';
      }

      for (let attempt = 0; ; attempt++) {
        let res = null;
        try {
          res = await fetch('/api/verify-payment.php', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              razorpay_order_id: response.razorpay_order_id,
              razorpay_payment_id: response.razorpay_payment_id,
              razorpay_signature: response.razorpay_signature,
            }),
          });
        } catch (err) {
          res = null; // network failure — transient, same handling as a 409
        }

        if (res) {
          let result = null;
          try { result = await res.json(); } catch (err) { result = null; }
          if (res.ok && result && !result.error) {
            // Fire before the state below is cleared — this is the only
            // revenue signal the site has. Keyed on reservation number so a
            // repeated call can never double-count it.
            if (purchaseReported !== result.reservation_no) {
              track('purchase', {
                transaction_id: result.reservation_no,
                currency: 'INR',
                value: paidAmount(),
                items: selection ? trackItems(selection.items) : [],
              });
              purchaseReported = result.reservation_no;
            }
            showConfirmStage({
              badge: 'Booking Confirmed',
              title: 'You\'re All Set',
              bodyHtml: `Reservation <strong>#${escapeHtml(result.reservation_no)}</strong> is confirmed. A confirmation has been sent to your email. `
                + `Questions? <a href="https://wa.me/919125492225" target="_blank">WhatsApp us</a>.`,
            });
            // The booking is done. Drop the selection so pressing Back can't
            // walk into the guest form and pay for it a second time — the
            // summary above is already rendered HTML and doesn't need it.
            selection = null;
            cart = [];
            lastOrder = null;
            return;
          }
        }

        // Anything else — a 502 (eZee genuinely rejected the booking), a bad
        // signature, a malformed body — is terminal. Only keep waiting on the
        // two states that resolve themselves.
        const transient = !res || res.status === 409;
        if (transient && attempt < VERIFY_RETRY_DELAYS.length) {
          if (attempt === 0) {
            showMsg(guestMsg, 'Still confirming — this takes a few seconds. Please keep this page open.', 'success');
          }
          await new Promise((resolve) => setTimeout(resolve, VERIFY_RETRY_DELAYS[attempt]));
          continue;
        }

        showConfirmStage({
          badge: 'Confirmation Pending',
          pending: true,
          title: 'Payment Received',
          bodyHtml: `Your payment went through but we couldn't auto-confirm the reservation. Our team will confirm it shortly — `
            + `for immediate help, <a href="https://wa.me/919125492225?text=${encodeURIComponent('Hi, I just paid for a booking (order ' + response.razorpay_order_id + ') and need help confirming it.')}" target="_blank">message us on WhatsApp</a>.`,
        });
        return;
      }
    }

    // ₹12,500 not ₹12500.00 — Indian digit grouping, and paise only when there
    // actually are any. The rest of the site writes prices this way.
    const INR = new Intl.NumberFormat('en-IN', { minimumFractionDigits: 0, maximumFractionDigits: 2 });
    function fmtPrice(n) {
      if (n === null || n === undefined || n === '') return '—';
      const value = Number(n);
      if (!isFinite(value)) return '—';
      return INR.format(value);
    }

    // Extracted so the price-change path (N8) can redraw it after the server
    // reports a new rate, rather than leaving the guest looking at the old one.
    function renderPriceSummary() {
      if (!selection) return;
      const baseSum = selection.items.reduce((n, c) => n + (c.base_total ?? 0) * c.qty, 0);
      const taxSum = selection.items.reduce((n, c) => n + (c.tax_total ?? 0) * c.qty, 0);
      const nights = nightsBetween(selection.check_in, selection.check_out);
      const itemRows = selection.items.map((c) =>
        `<div class="price-row"><span>${c.qty}× ${escapeHtml(c.name)}${guestSuffix(c)}</span><span>₹${fmtPrice(c.total * c.qty)}</span></div>`).join('');
      widgetPrice.innerHTML = `<div class="price-header"><small>${escapeHtml(selection.check_in)} → ${escapeHtml(selection.check_out)} · ${nights} ${plural(nights, 'night')}</small><span>₹${fmtPrice(selection.total)}</span></div>`
        + `<div class="price-breakdown">${itemRows}`
        + `<div class="price-row price-row-divider"><span>Room rate</span><span>₹${fmtPrice(baseSum)}</span></div>`
        + `<div class="price-row"><span>Tax</span><span>₹${fmtPrice(taxSum)}</span></div></div>`;
    }

    const STEP_ORDER = ['search', 'results', 'guest', 'confirm'];
    function updateSteps(name) {
      const list = document.getElementById('widgetSteps');
      if (!list) return;
      const current = STEP_ORDER.indexOf(name);
      Array.prototype.forEach.call(list.children, (li, i) => {
        li.classList.toggle('is-done', i < current);
        li.classList.toggle('is-current', i === current);
        if (i === current) li.setAttribute('aria-current', 'step');
        else li.removeAttribute('aria-current');
      });
    }

    function availabilityLabel(room) {
      if (room.available === null || room.available === undefined) return 'Availability on request';
      if (room.available === 0) return 'Sold out';
      return `${room.available} ${plural(room.available, 'room')} left at this rate`;
    }

    function plural(n, word) {
      return Number(n) === 1 ? word : word + 's';
    }

    function nightsBetween(from, to) {
      return Math.round((new Date(to) - new Date(from)) / 86400000);
    }

    // Only worth saying when it isn't the default — a dorm bed is always one
    // guest, so labelling it would be noise on every line.
    function guestSuffix(item) {
      return item.adults > 1 ? ` · ${item.adults} guests` : '';
    }

    // ── MEASUREMENT ──
    // GA4 was loaded on this page but no event was ever sent from the booking
    // flow, so drop-off between stages, payment failure rate and revenue were
    // all unknowable. gtag may be absent entirely (ad blockers, consent tools),
    // and analytics must never be able to break a booking — hence the guard and
    // the swallowed error.
    function track(name, params) {
      if (typeof gtag !== 'function') return;
      try {
        gtag('event', name, params);
      } catch (err) {
        /* measurement is never worth a failed booking */
      }
    }

    // GA4 item shape. item_id is the rate-plan id, which is what eZee prices
    // against, so reports line up with the PMS rather than with display names.
    function trackItems(items) {
      return items.map((c) => ({
        item_id: c.roomrateunkid,
        item_name: c.name,
        price: Number(c.total) || 0,
        quantity: c.qty,
      }));
    }

    // The amount actually charged, from the order the server priced. Shared with
    // summaryRows() so the revenue figure GA4 reports and the "Total paid" the
    // guest reads can never disagree.
    function paidAmount() {
      if (lastOrder && lastOrder.order && lastOrder.order.amount != null) return lastOrder.order.amount / 100;
      return selection ? selection.total : 0;
    }

    // Bootstrap runs last, after every const in this scope exists. It used to
    // sit up by the calendar wiring, which put updateSteps() ahead of the
    // STEP_ORDER it reads — a temporal-dead-zone ReferenceError that aborted
    // the rest of initBookingWidget() on every page load.
    //
    // Marking the entry we landed on as the search stage matters because a
    // deep-linked arrival (?check_in=...) otherwise has a null state beneath
    // it, and "Change Dates" would navigate off the site instead of back.
    syncHistory('search', 'replace');
    updateSteps('search');
    restoreFromUrl();
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
    // Strict: the field is typable now, so this sees whatever the guest typed.
    // Returns null for anything that isn't a real YYYY-MM-DD — a loose parse
    // yields an Invalid Date, which is truthy, and open() would then read NaN
    // off it and render a "undefined NaN" calendar. Also rejects rollover
    // (2026-02-30 would otherwise silently become March 2).
    function parseISO(s) {
      const m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(String(s || '').trim());
      if (!m) return null;
      const [y, mo, day] = [+m[1], +m[2], +m[3]];
      const d = new Date(y, mo - 1, day);
      return (d.getFullYear() === y && d.getMonth() === mo - 1 && d.getDate() === day) ? d : null;
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
        const disabled = d < min;
        const cell = document.createElement('div');
        cell.className = 'cal-day';
        cell.textContent = String(day);
        // Selectable days are real controls, so they carry a role, a readable
        // name and a tab stop. ponytail: Tab-through only, no arrow-key grid
        // navigation — the input itself accepts a typed YYYY-MM-DD, which is
        // the faster keyboard path anyway. Add roving tabindex if that changes.
        if (disabled) {
          cell.classList.add('cal-disabled');
          cell.setAttribute('aria-disabled', 'true');
        } else {
          cell.setAttribute('role', 'button');
          cell.setAttribute('tabindex', '0');
          cell.setAttribute('aria-label', `${MONTHS[viewMonth]} ${day}, ${viewYear}`);
        }
        if (d.getTime() === t.getTime()) cell.classList.add('cal-today');
        if (selected && d.getTime() === selected.getTime()) {
          cell.classList.add('cal-selected');
          cell.setAttribute('aria-current', 'date');
        }
        const choose = () => {
          inputEl.value = toISO(d);
          inputEl.dispatchEvent(new Event('change'));
          close();
          inputEl.focus();
        };
        cell.addEventListener('click', () => { if (!disabled) choose(); });
        cell.addEventListener('keydown', (e) => {
          if (disabled) return;
          if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); choose(); }
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
    // Mouse users dismiss by clicking away; keyboard users need Escape, or the
    // popup is a one-way door once focus is inside it.
    function onEscape(e) {
      if (e.key === 'Escape' && pop) { close(); inputEl.focus(); }
    }
    function open() {
      if (pop) return;
      const base = parseISO(inputEl.value) || parseISO(getMinDate()) || todayDate();
      viewYear = base.getFullYear();
      viewMonth = base.getMonth();
      pop = document.createElement('div');
      pop.className = 'cal-pop';
      pop.setAttribute('role', 'dialog');
      pop.setAttribute('aria-label', 'Choose a date');
      document.body.appendChild(pop);
      position();
      render();
      requestAnimationFrame(() => pop.classList.add('open'));
      document.addEventListener('mousedown', onOutside, true);
      document.addEventListener('keydown', onEscape, true);
    }
    function close() {
      if (!pop) return;
      document.removeEventListener('mousedown', onOutside, true);
      document.removeEventListener('keydown', onEscape, true);
      pop.remove();
      pop = null;
    }

    inputEl.addEventListener('click', open);
    // ArrowDown is the conventional "open the picker" key, and unlike the
    // Enter/Space this replaced it doesn't swallow form submission or a
    // keystroke now that the field accepts a typed YYYY-MM-DD.
    inputEl.addEventListener('keydown', (e) => {
      if (e.key === 'ArrowDown') { e.preventDefault(); open(); }
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
        msg.textContent = `Reservation #${result.reservation_no} has been cancelled. ${result.refund_note || ''}`.trim();
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
