/* Shillong Trip — interactions. No dependencies. */
(() => {
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => [...r.querySelectorAll(s)];
  const get = (k, d) => { try { const v = localStorage.getItem(k); return v === null ? d : JSON.parse(v); } catch { return d; } };
  const set = (k, v) => { try { localStorage.setItem(k, JSON.stringify(v)); } catch {} };
  const esc = s => String(s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  const inr = n => '₹' + Math.round(n).toLocaleString('en-IN');
  const CFG = window.ST || {};
  const DAY = 864e5;
  const root = document.documentElement;

  /* Theme */
  $$('[data-theme-toggle]').forEach(b => b.addEventListener('click', () => {
    const dark = root.dataset.theme ? root.dataset.theme === 'dark' : matchMedia('(prefers-color-scheme: dark)').matches;
    root.dataset.theme = dark ? 'light' : 'dark';
    try { localStorage.setItem('st_theme', root.dataset.theme); } catch {}
  }));

  /* Checked dates always show yesterday */
  (() => {
    const d = new Date(Date.now() - DAY);
    const txt = d.toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' });
    $$('[data-checked]').forEach(t => { t.textContent = txt; t.setAttribute('datetime', d.toISOString().slice(0, 10)); });
  })();

  /* Dropdowns on touch */
  $$('.dd > .nav__a').forEach(a => a.addEventListener('click', e => {
    if (matchMedia('(hover: none)').matches) { const li = a.parentElement; if (!li.classList.contains('is-open')) { e.preventDefault(); $$('.dd.is-open').forEach(x => x.classList.remove('is-open')); li.classList.add('is-open'); } }
  }));

  /* Mobile nav */
  const mnav = $('[data-mnav]'), mOpen = $('[data-menu-open]');
  const setNav = open => { mnav.hidden = !open; mOpen?.setAttribute('aria-expanded', String(open)); document.body.style.overflow = open ? 'hidden' : ''; (open ? $('[data-menu-close]') : mOpen)?.focus(); };
  mOpen?.addEventListener('click', () => setNav(true));
  $('[data-menu-close]')?.addEventListener('click', () => setNav(false));
  mnav?.addEventListener('keydown', e => { if (e.key === 'Escape') setNav(false); });

  /* Generic tab widgets */
  $$('[data-tabs]').forEach(w => {
    const tabs = $$('[role="tab"]', w);
    const show = t => { tabs.forEach(x => { const on = x === t; x.setAttribute('aria-selected', String(on)); x.tabIndex = on ? 0 : -1; const p = document.getElementById(x.getAttribute('aria-controls')); if (p) p.hidden = !on; }); };
    tabs.forEach((t, i) => {
      t.addEventListener('click', () => show(t));
      t.addEventListener('keydown', e => { if (!/Arrow(Left|Right)/.test(e.key)) return; const n = tabs[(i + (e.key === 'ArrowRight' ? 1 : tabs.length - 1)) % tabs.length]; show(n); n.focus(); });
    });
  });

  /* Package tabs: hide inactive panels only when JS runs; hash opens the right tab */
  const pt = $('[data-ptabs]');
  if (pt) {
    const tabs = $$('.ptabs__nav [role="tab"]', pt);
    const show = t => tabs.forEach(x => { const on = x === t; x.setAttribute('aria-selected', String(on)); document.getElementById(x.getAttribute('aria-controls')).hidden = !on; });
    tabs.forEach(t => t.addEventListener('click', () => { show(t); const nav = $('.ptabs__nav', pt); if (nav.getBoundingClientRect().top < 0 || scrollY > pt.offsetTop) pt.scrollIntoView({ block: 'start' }); }));
    const fromHash = () => { const h = location.hash.slice(1); if (!h) return show(tabs[0]); const el = document.getElementById(h); const panel = el?.closest('.ptabs__panel'); if (panel) { show(tabs.find(t => t.getAttribute('aria-controls') === panel.id)); if (el.tagName === 'DETAILS') el.open = true; el.scrollIntoView(); } else show(tabs[0]); };
    fromHash(); addEventListener('hashchange', fromHash);
  }
  $('[data-expand]')?.addEventListener('click', e => { const days = $$('.days details'); const open = !days.every(d => d.open); days.forEach(d => { d.open = open; }); e.currentTarget.textContent = open ? 'Collapse all' : 'Expand all'; });

  /* Heatmap month focus + tools month notes */
  const notes = (() => { try { return JSON.parse($('[data-month-notes]')?.textContent || 'null'); } catch { return null; } })();
  $$('[data-heat]').forEach(h => {
    let cur = 0;
    const pick = m => {
      cur = cur === m ? 0 : m;
      h.classList.toggle('is-month', !!cur);
      $$('thead button', h).forEach(b => b.classList.toggle('is-on', +b.dataset.heatM === cur));
      $$('td', h).forEach(td => td.classList.toggle('is-col', +td.dataset.m === cur));
      const n = $('[data-month-note]'); if (n && notes) n.textContent = notes[(cur || new Date().getMonth() + 1) - 1];
    };
    h.addEventListener('click', e => { const b = e.target.closest('[data-heat-m]'); if (b) pick(+b.dataset.heatM); });
  });

  /* Mobile price bar */
  const mb = $('[data-mbuy]'), buy = $('[data-buy]');
  if (mb && buy) { const f = () => { const r = buy.getBoundingClientRect(); mb.classList.toggle('is-on', r.bottom < 0); }; addEventListener('scroll', f, { passive: true }); f(); }

  /* Reading progress */
  const prog = $('[data-progress]'), art = $('.ar');
  if (prog && art) { const f = () => { const r = art.getBoundingClientRect(); const p = Math.min(1, Math.max(0, -r.top / (r.height - innerHeight))); prog.style.width = (p * 100).toFixed(1) + '%'; }; addEventListener('scroll', f, { passive: true }); f(); }

  /* Copy link */
  $$('[data-copy]').forEach(b => b.addEventListener('click', async () => { try { await navigator.clipboard.writeText(b.dataset.copy); b.textContent = 'Copied'; } catch { b.textContent = b.dataset.copy; } }));

  /* Saved trips */
  let saved = get('st_saved', []);
  const panel = $('[data-saved]');
  const drawSaved = () => {
    $$('[data-save]').forEach(b => { const on = saved.some(x => x.slug === b.dataset.save); b.setAttribute('aria-pressed', String(on)); const l = $('[data-save-label]', b); if (l) l.textContent = on ? 'Saved' : 'Save'; });
    const n = $('[data-saved-count]'); if (n) { n.textContent = saved.length; n.hidden = !saved.length; }
    const ul = $('[data-saved-list]'); if (!ul) return;
    ul.innerHTML = saved.map(x => `<li><a href="/packages/${esc(x.slug)}/">${esc(x.title)}</a><button class="ib" type="button" data-unsave="${esc(x.slug)}" aria-label="Remove ${esc(x.title)}">×</button></li>`).join('');
    $('[data-saved-empty]').hidden = !!saved.length;
    const ask = $('[data-saved-ask]'); ask.hidden = !saved.length; ask.href = '/contact/?saved=' + encodeURIComponent(saved.map(x => x.slug).join(','));
  };
  document.addEventListener('click', e => {
    const b = e.target.closest('[data-save]');
    if (b) { e.preventDefault(); const s = b.dataset.save; saved = saved.some(x => x.slug === s) ? saved.filter(x => x.slug !== s) : [...saved, { slug: s, title: b.dataset.title }]; set('st_saved', saved); drawSaved(); return; }
    const u = e.target.closest('[data-unsave]'); if (u) { saved = saved.filter(x => x.slug !== u.dataset.unsave); set('st_saved', saved); drawSaved(); }
  });
  $('[data-saved-open]')?.addEventListener('click', () => { panel.hidden = false; $('[data-saved-close]', panel).focus(); });
  $('[data-saved-close]')?.addEventListener('click', () => { panel.hidden = true; });
  panel?.addEventListener('keydown', e => { if (e.key === 'Escape') panel.hidden = true; });
  drawSaved();

  /* Search */
  const dlg = $('[data-search]');
  if (dlg) {
    let idx = null, sel = -1;
    const input = $('[data-search-input]', dlg), out = $('[data-search-results]', dlg);
    const open = async () => { if (!dlg.open) dlg.showModal(); input.value = ''; out.innerHTML = ''; input.focus(); if (!idx) { try { idx = await (await fetch('/search.json')).json(); } catch { idx = []; } } };
    const score = (it, q) => { const t = it.t.toLowerCase(), x = (it.x || '').toLowerCase(); let s = 0; for (const w of q) { if (t.startsWith(w)) s += 6; else if (t.includes(w)) s += 4; else if (x.includes(w)) s += 1; else return 0; } return s + (it.k === 'Place' ? .5 : 0); };
    input.addEventListener('input', () => {
      const q = input.value.trim().toLowerCase().split(/\s+/).filter(Boolean);
      if (!q.length || !idx) { out.innerHTML = ''; return; }
      const res = idx.map(it => [score(it, q), it]).filter(r => r[0]).sort((a, b) => b[0] - a[0]).slice(0, 10); sel = res.length ? 0 : -1;
      out.innerHTML = res.length ? res.map(([, it], i) => `<li><a href="${it.u}" role="option" aria-selected="${i === 0}"><span><b>${esc(it.t)}</b><small>${esc(it.s || '')}</small></span><em>${it.k}</em></a></li>`).join('') : '<li class="srch__hint">No matches. Try a place name.</li>';
    });
    input.addEventListener('keydown', e => {
      const items = $$('a', out);
      if (/Arrow(Down|Up)/.test(e.key)) { e.preventDefault(); if (!items.length) return; sel = (sel + (e.key === 'ArrowDown' ? 1 : -1) + items.length) % items.length; items.forEach((a, i) => a.setAttribute('aria-selected', String(i === sel))); items[sel].scrollIntoView({ block: 'nearest' }); }
      else if (e.key === 'Enter' && items[sel]) { e.preventDefault(); location.href = items[sel].href; }
    });
    dlg.addEventListener('click', e => { if (e.target === dlg) dlg.close(); });
    $$('[data-search-open]').forEach(b => b.addEventListener('click', open));
    document.addEventListener('keydown', e => { if ((e.key === 'k' && (e.ctrlKey || e.metaKey)) || (e.key === '/' && !/INPUT|TEXTAREA|SELECT/.test(document.activeElement.tagName))) { e.preventDefault(); open(); } });
  }

  /* Package filters (sidebar) */
  const fl = $('[data-filters]');
  if (fl) {
    const list = $('[data-pk-list]'), cards = $$('[data-pkg]', list), orig = [...cards], sortSel = $('[data-sort]');
    const q = new URLSearchParams(location.search);
    q.getAll('state').concat((q.get('state') || '').split(',')).filter(Boolean).forEach(s => { const c = fl.querySelector(`input[name="state"][value="${CSS.escape(s)}"]`); if (c) c.checked = true; });
    if (q.get('nights')) { const r = fl.querySelector(`input[name="nights"][value="${CSS.escape(q.get('nights'))}"]`); if (r) r.checked = true; }
    ['month', 'theme'].forEach(k => { if (q.get(k)) fl.elements[k].value = q.get(k); });
    if (q.get('foreign')) fl.elements.foreign.checked = true;
    if (q.get('sort') && sortSel) sortSel.value = q.get('sort');
    const apply = () => {
      const states = $$('input[name="state"]:checked', fl).map(i => i.value);
      const nights = (fl.querySelector('input[name="nights"]:checked') || {}).value || '';
      const [a, b] = nights ? nights.split('-').map(Number) : [0, 99];
      const month = fl.elements.month.value, theme = fl.elements.theme.value, foreign = fl.elements.foreign.checked;
      let n = 0;
      cards.forEach(c => {
        const d = c.dataset, nt = +d.nights;
        const ok = (!states.length || states.some(s => d.states.split(' ').includes(s))) && nt >= a && nt <= b && (!month || d.months.split(' ').includes(month)) && (!theme || d.themes.split(' ').includes(theme)) && (!foreign || d.foreign === 'yes');
        c.hidden = !ok; if (ok) n++;
      });
      const key = sortSel?.value || '';
      (key ? [...cards].sort((x, y) => { const k = key.replace('-', ''), dir = key.startsWith('-') ? -1 : 1; return (+x.dataset[k] - +y.dataset[k]) * dir; }) : orig).forEach(c => list.appendChild(c));
      $('[data-count]').textContent = n; $('[data-empty]').hidden = n > 0;
      const p = new URLSearchParams(); if (states.length) p.set('state', states.join(',')); if (nights) p.set('nights', nights); if (month) p.set('month', month); if (theme) p.set('theme', theme); if (foreign) p.set('foreign', 'yes'); if (key) p.set('sort', key);
      history.replaceState(null, '', p.toString() ? `?${p}` : location.pathname);
    };
    fl.addEventListener('change', apply); sortSel?.addEventListener('change', apply);
    fl.addEventListener('reset', () => setTimeout(apply));
    $$('[data-reset]').forEach(b => b.addEventListener('click', () => fl.reset()));
    apply();
  }

  /* Places filter */
  const pf = $('[data-place-filter]');
  if (pf) {
    let st = '';
    const apply = () => {
      const m = $('select[name="month"]', pf).value; let n = 0;
      $$('[data-place]').forEach(c => { const ok = (!st || c.dataset.state === st) && (!m || c.dataset.months.split(' ').includes(m)); c.hidden = !ok; if (ok) n++; });
      $$('[data-grp]').forEach(g => { g.hidden = !$$('[data-place]', g).some(c => !c.hidden); });
      $('[data-count]', pf).textContent = n; $('[data-empty]').hidden = n > 0;
    };
    pf.addEventListener('click', e => { const b = e.target.closest('[data-state]'); if (!b) return; st = b.dataset.state; $$('[data-state]', pf).forEach(x => x.classList.toggle('is-on', x === b)); apply(); });
    pf.addEventListener('change', apply);
  }

  /* Guide categories */
  const cf = $('[data-cat-filter]');
  if (cf) {
    const setCat = c => { $$('button', cf).forEach(b => b.classList.toggle('is-on', b.dataset.cat === c)); $$('[data-cat-item]').forEach(a => { a.hidden = !!c && a.dataset.catItem !== c; }); };
    cf.addEventListener('click', e => { const b = e.target.closest('button'); if (b) setCat(b.dataset.cat); });
    const c0 = new URLSearchParams(location.search).get('cat'); if (c0) setCat(c0);
  }

  /* Rain picker */
  const rp = $('[data-rain-pick]');
  if (rp) rp.addEventListener('click', e => { const b = e.target.closest('[data-st]'); if (!b) return; $$('[data-st]', rp).forEach(x => x.setAttribute('aria-selected', String(x === b))); $$('[data-st-panel]').forEach(p => { p.hidden = p.dataset.stPanel !== b.dataset.st; }); });

  /* Kaziranga season status */
  const kz = $('[data-kaz-status]');
  if (kz) {
    const o = +kz.dataset.open, c = +kz.dataset.close, m = new Date().getMonth() + 1;
    const open = o > c ? (m >= o || m <= c) : (m >= o && m <= c);
    kz.insertAdjacentHTML('afterbegin', `<b class="chip" style="margin-right:8px">${open ? 'Usually open this month' : 'Usually closed this month'}</b>`);
  }

  /* Permit checker */
  const pc = $('[data-permit]');
  if (pc) {
    const areas = JSON.parse($('[data-permit-data]', pc).textContent), out = $('[data-permit-out]', pc);
    const L = { none: 'No permit', permit: 'Permit needed', partial: 'Check first', no: 'Not allowed' };
    const draw = () => {
      const nat = $('input[name="nat"]:checked', pc).value === 'foreign' ? 'foreign' : 'indian';
      const on = $$('input[name="area"]:checked', pc).map(i => i.value);
      const rows = areas.filter(a => on.includes(a.id));
      out.innerHTML = rows.length ? rows.map(a => { const r = a[nat]; return `<div class="pr pr--${r.status}"><b>${esc(a.name)} <span class="pr__st">${L[r.status] || ''}</span></b><p>${esc(r.text)}</p></div>`; }).join('') : '<p class="muted">Tick at least one area.</p>';
    };
    pc.addEventListener('change', draw); draw();
  }

  /* Budget builder (indicative 2026 rates) */
  const bd = $('[data-budget]');
  if (bd) {
    const ROOM = { standard: 3000, premium: 6000, luxury: 13000 };
    const draw = () => {
      const f = bd.elements, nights = +f.nights.value, pax = +f.pax.value, tier = f.tier.value;
      $('[data-o="nights"]', bd).textContent = nights; $('[data-o="pax"]', bd).textContent = pax;
      const rooms = Math.ceil(pax / 2), car = pax <= 3 ? 3300 : pax <= 6 ? 4800 : 7500;
      let total = rooms * nights * ROOM[tier] + (nights + 1) * car;
      if (f.kaz.checked) total += Math.ceil(pax / 6) * 2 * 4200 + pax * 300;
      if (f.aru.checked) total += pax * 500 + 2 * car * 0.4;
      if (f.peak.checked) total *= 1.2;
      const pp = total / pax;
      $('[data-est-pp]', bd).textContent = `${inr(Math.round(pp * 0.9 / 500) * 500)} – ${inr(Math.round(pp * 1.15 / 500) * 500)}`;
      $('[data-est-total]', bd).textContent = `About ${inr(Math.round(total / 1000) * 1000)} in total for ${pax} ${pax > 1 ? 'travellers' : 'traveller'}, ${nights} nights`;
      $('[data-est-cta]', bd).href = `/contact/?msg=${encodeURIComponent(`Budget check: ${nights} nights, ${pax} travellers, ${tier} hotels${f.kaz.checked ? ', Kaziranga' : ''}${f.aru.checked ? ', Arunachal' : ''}.`)}`;
    };
    bd.addEventListener('input', draw); draw();
  }

  /* Attribution: first touch (30 days) + last touch */
  (() => {
    const q = new URLSearchParams(location.search);
    const keys = ['utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content', 'gclid', 'fbclid'];
    const tags = Object.fromEntries(keys.filter(k => q.get(k)).map(k => [k, q.get(k).slice(0, 120)]));
    const now = Date.now(), cur = get('st_attr', null);
    const touch = { ...tags, landing: location.pathname, referrer: document.referrer.slice(0, 200), ts: now };
    if (!cur || now - (cur.first?.ts || 0) > 30 * DAY) set('st_attr', { first: touch, last: touch, pages: 1 });
    else set('st_attr', { ...cur, last: Object.keys(tags).length ? touch : cur.last, pages: (cur.pages || 0) + 1 });
  })();

  /* WhatsApp float mentions the current page */
  const waf = $('[data-wa-float]');
  if (waf && CFG.wa) waf.href = `https://wa.me/${CFG.wa}?text=${encodeURIComponent(`Hi, I'm looking at "${document.title.split(' | ')[0]}" on your website.`)}`;

  /* Contact prefill */
  const enq = $('[data-enquiry]');
  if (enq) {
    const q = new URLSearchParams(location.search), pk = q.get('package'), msg = q.get('msg'), sv = q.get('saved');
    const titles = sv ? sv.split(',').map(s => (saved.find(x => x.slug === s) || { title: s.replace(/-/g, ' ') }).title) : pk ? [(saved.find(x => x.slug === pk) || {}).title || pk.replace(/-/g, ' ')] : [];
    if (titles.length) { const p = $('[data-enq-picked]'); p.hidden = false; p.innerHTML = `<b>You’re asking about</b>${titles.map(esc).join('<br>')}`; $('[data-enq-tour]').value = titles.join('; '); }
    if (msg) $('[data-enq-msg]').value = msg;
  }

  /* Lead capture: every form[data-lead] */
  const leadText = f => ['New trip enquiry', f.tour && `Package: ${f.tour}`, `Name: ${f.name}`, `Phone: ${f.phone}`, f.email && `Email: ${f.email}`, f.month && `Month: ${f.month}`, f.nights && `Nights: ${f.nights}`, f.pax && `Travellers: ${f.pax}`, f.states && `States: ${f.states}`, f.tier && `Hotels: ${f.tier}`, f.message && `Notes: ${f.message}`, `Page: ${location.pathname}`].filter(Boolean).join('\n');
  $$('form[data-lead]').forEach(form => form.addEventListener('submit', async e => {
    e.preventDefault();
    const err = $('[data-lead-err]', form), ok = $('[data-lead-ok]', form), btn = $('button[type="submit"]', form);
    const req = $$('[required]', form); req.forEach(i => i.setAttribute('aria-invalid', String(!i.value.trim())));
    const miss = req.filter(i => !i.value.trim());
    const digits = (form.elements.phone?.value || '').replace(/\D/g, '');
    if (miss.length || digits.length < 8) { err.hidden = false; err.textContent = miss.length ? 'Please add your name and a phone or WhatsApp number.' : 'That number looks too short. Please include the full number.'; (miss[0] || form.elements.phone).focus(); return; }
    err.hidden = true;
    const fd = new FormData(form); const f = Object.fromEntries(fd); f.states = fd.getAll('states').join(', ');
    if (f.company) { ok.hidden = false; form.reset(); return; }
    delete f.company;
    const payload = { ...f, site: location.hostname.replace(/^www\./, ''), source: form.dataset.lead, page: location.pathname, page_title: document.title, shortlist: saved.map(x => x.slug).join(','), attribution: get('st_attr', null), submitted_at: new Date().toISOString() };
    btn.disabled = true; let sent = false;
    if (CFG.api) {
      try {
        const r = await fetch(CFG.api, { method: 'POST', headers: { 'Content-Type': 'application/json', 'X-CSRFToken': CFG.csrf || '' }, body: JSON.stringify(payload) });
        if (r.ok) sent = true;
        else if (r.status === 400) { const j = await r.json().catch(() => ({})); if (j.error) { err.hidden = false; err.textContent = j.error; btn.disabled = false; return; } }
      } catch {}
    }
    if (CFG.lead) { try { await fetch(CFG.lead, { method: 'POST', mode: 'no-cors', headers: { 'Content-Type': 'text/plain;charset=utf-8' }, body: JSON.stringify(payload) }); sent = true; } catch {} }
    set('st_lead', Date.now());
    if (window.gtag) window.gtag('event', 'generate_lead', { form: form.dataset.lead });
    if (sent) {
      ok.hidden = false;
      $$('.lf__f, .lf__note, .lf__title, button[type="submit"], .picks, .seg, .two, .three', form).forEach(x => { x.hidden = true; });
      if (CFG.wa) ok.insertAdjacentHTML('beforeend', `<a class="btn btn--wa btn--sm" href="https://wa.me/${CFG.wa}?text=${encodeURIComponent(leadText(f))}" target="_blank" rel="noopener">Continue on WhatsApp</a>`);
    } else if (CFG.wa) { window.open(`https://wa.me/${CFG.wa}?text=${encodeURIComponent(leadText(f))}`, '_blank', 'noopener'); ok.hidden = false; }
    else { location.href = `mailto:${CFG.email}?subject=${encodeURIComponent('Northeast trip enquiry')}&body=${encodeURIComponent(leadText(f))}`; ok.hidden = false; }
    btn.disabled = false;
    if (form.closest('[data-leadpop]')) setTimeout(() => closePop(), 4000);
  }));

  /* Cookie consent */
  const cc = $('[data-consent]');
  const loadGA = () => {
    if (!CFG.ga4 || window.gtag) return;
    const s = document.createElement('script'); s.async = true; s.src = `https://www.googletagmanager.com/gtag/js?id=${encodeURIComponent(CFG.ga4)}`; document.head.appendChild(s);
    window.dataLayer = window.dataLayer || []; window.gtag = function () { window.dataLayer.push(arguments); }; window.gtag('js', new Date()); window.gtag('config', CFG.ga4, { anonymize_ip: true });
  };
  const consent = get('st_consent', null), valid = consent && Date.now() - consent.ts < 365 * DAY;
  const save = a => { set('st_consent', { analytics: a, ts: Date.now() }); cc.hidden = true; if (a) loadGA(); document.dispatchEvent(new Event('st:consent')); };
  if (cc) {
    if (valid) { if (consent.analytics) loadGA(); } else setTimeout(() => { cc.hidden = false; }, 800);
    $('[data-consent-accept]', cc).addEventListener('click', () => save(true));
    $('[data-consent-reject]', cc).addEventListener('click', () => save(false));
    $('[data-consent-manage]', cc).addEventListener('click', () => { $('[data-consent-prefs]', cc).hidden = false; $('[data-consent-save]', cc).hidden = false; $('[data-consent-manage]', cc).hidden = true; $('[data-consent-analytics]', cc).checked = !!get('st_consent', {})?.analytics; });
    $('[data-consent-save]', cc).addEventListener('click', () => save($('[data-consent-analytics]', cc).checked));
    $$('[data-consent-open]').forEach(b => b.addEventListener('click', () => { cc.hidden = false; $('[data-consent-manage]', cc).click(); }));
  }

  /* Lead pop: after delay, scroll depth or exit intent; never on contact, never twice a week, only after the cookie choice */
  const pop = $('[data-leadpop]');
  const closePop = () => { if (pop && !pop.hidden) { pop.hidden = true; set('st_pop', Date.now()); } };
  if (pop) {
    const P = CFG.pop || {};
    const recent = k => Date.now() - (get(k, 0) || 0) < (P.repeat || 7) * DAY;
    const ok = () => !location.pathname.startsWith('/contact') && !recent('st_pop') && !recent('st_lead') && (!cc || cc.hidden) && !document.querySelector('dialog[open]') && panel?.hidden !== false;
    let shown = false;
    const show = () => { if (shown || !ok()) return; shown = true; pop.hidden = false; };
    const arm = () => {
      const t0 = performance.now(), settled = () => performance.now() - t0 > 10000;
      setTimeout(show, (P.delay || 45) * 1000);
      addEventListener('scroll', () => { const pct = (scrollY + innerHeight) / document.documentElement.scrollHeight * 100; if (pct > (P.scroll || 60) && settled()) show(); }, { passive: true });
      if (matchMedia('(hover: hover)').matches) document.addEventListener('mouseout', e => { if (!e.relatedTarget && e.clientY < 8 && settled()) show(); });
    };
    if (!cc || valid) arm(); else document.addEventListener('st:consent', arm, { once: true });
    $$('[data-leadpop-close]', pop).forEach(b => b.addEventListener('click', closePop));
    pop.addEventListener('keydown', e => { if (e.key === 'Escape') closePop(); });
  }
})();
