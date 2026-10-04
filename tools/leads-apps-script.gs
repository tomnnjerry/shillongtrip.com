/**
 * LEAD INTAKE — receives enquiries from the Shillong Trip website
 * and writes them to the "Leads" sheet that the CRM reads.
 *
 * Setup: see crm/README.md. In short:
 *   1. Create a Google Sheet (e.g. "Trip Desk Leads"). Extensions → Apps Script. Paste this file.
 *   2. Set NOTIFY_EMAIL. Run setupIntake() once and approve permissions.
 *   3. Deploy → New deployment → Web app. Execute as: Me. Who has access: Anyone.
 *   4. Paste the /exec URL into each site's site.config.json → leads.endpoint and rebuild the site.
 *
 * This deployment only ACCEPTS leads. It never returns lead data, so "Anyone" access is safe.
 */
const NOTIFY_EMAIL = 'hello@shillongtrip.com';

const LEAD_COLUMNS = [
  'id', 'created_at', 'site', 'source', 'name', 'phone', 'email', 'month', 'nights', 'pax', 'tier', 'tour', 'states', 'message',
  'page', 'page_title', 'shortlist', 'utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content', 'gclid', 'fbclid',
  'first_landing', 'first_referrer', 'pages_viewed',
  'stage', 'owner', 'quote_inr', 'booked_inr', 'followup', 'lost_reason', 'last_contact', 'updated_at', 'duplicate_of',
];

function setupIntake() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  ensureSheet_(ss, 'Leads', LEAD_COLUMNS);
  ensureSheet_(ss, 'Notes', ['id', 'lead_id', 'at', 'by', 'type', 'text']);
  ensureSheet_(ss, 'Team', ['email', 'name', 'role', 'active', 'whatsapp']);
  ensureSheet_(ss, 'Templates', ['key', 'label', 'text']);
  const team = ss.getSheetByName('Team');
  if (team.getLastRow() < 2) team.appendRow([Session.getEffectiveUser().getEmail(), 'Admin', 'admin', true, '']);
  const tpl = ss.getSheetByName('Templates');
  if (tpl.getLastRow() < 2) {
    [
      ['first', 'First reply', 'Hi {first}, this is {me} from {site}. Thanks for your enquiry{tourbit}. Could you share your travel dates and how many of you are travelling? I’ll send a day-by-day plan with a clear price.'],
      ['quote', 'Quote sent', 'Hi {first}, I’ve sent the day-by-day plan and quote{tourbit}. Happy to change the pace, hotels or places. What would you like to adjust?'],
      ['follow', 'Follow-up', 'Hi {first}, just checking in on your {month} trip. Rooms and permits get busy closer to the date. Shall I hold the hotels for you?'],
      ['confirm', 'Booking confirmed', 'Hi {first}, your trip is confirmed. I’ll share hotel vouchers, driver details and the permit checklist a week before you travel.'],
    ].forEach(r => tpl.appendRow(r));
  }
  return 'Intake ready';
}

function doPost(e) {
  const lock = LockService.getScriptLock();
  lock.tryLock(10000);
  try {
    const d = JSON.parse((e && e.postData && e.postData.contents) || '{}');
    if (d.company) return ok_();                                    // honeypot: ignore bots
    if (!d.name || !d.phone) return ok_();
    const ss = SpreadsheetApp.getActiveSpreadsheet();
    const sh = ensureSheet_(ss, 'Leads', LEAD_COLUMNS);
    const head = sh.getRange(1, 1, 1, sh.getLastColumn()).getValues()[0];
    const a = d.attribution || {}, first = a.first || {}, last = a.last || {};
    const now = new Date();
    const id = 'L' + Utilities.formatDate(now, 'Asia/Kolkata', 'yyMMdd') + '-' + Math.random().toString(36).slice(2, 6).toUpperCase();
    const row = {
      ...d, id, created_at: now, site: d.site || '', stage: 'New', owner: nextOwner_(ss),
      utm_source: first.utm_source || last.utm_source || '', utm_medium: first.utm_medium || last.utm_medium || '',
      utm_campaign: first.utm_campaign || last.utm_campaign || '', utm_term: first.utm_term || '', utm_content: first.utm_content || '',
      gclid: first.gclid || last.gclid || '', fbclid: first.fbclid || last.fbclid || '',
      first_landing: first.landing || '', first_referrer: first.referrer || '', pages_viewed: a.pages || '',
      duplicate_of: findDuplicate_(sh, head, d.phone), updated_at: now,
    };
    sh.appendRow(head.map(h => clean_(row[h])));
    notify_(row);
    return ok_();
  } catch (err) {
    console.error(err);
    return ok_();
  } finally {
    lock.releaseLock();
  }
}

function ensureSheet_(ss, name, cols) {
  let sh = ss.getSheetByName(name);
  if (!sh) { sh = ss.insertSheet(name); sh.appendRow(cols); sh.setFrozenRows(1); sh.getRange(1, 1, 1, cols.length).setFontWeight('bold'); return sh; }
  const head = sh.getRange(1, 1, 1, Math.max(1, sh.getLastColumn())).getValues()[0].filter(String);
  const missing = cols.filter(c => !head.includes(c));
  if (missing.length) sh.getRange(1, head.length + 1, 1, missing.length).setValues([missing]).setFontWeight('bold');
  return sh;
}

// Round-robin across active team members
function nextOwner_(ss) {
  const t = ss.getSheetByName('Team');
  if (!t || t.getLastRow() < 2) return '';
  const rows = t.getRange(2, 1, t.getLastRow() - 1, 4).getValues().filter(r => r[0] && String(r[3]).toUpperCase() !== 'FALSE');
  if (!rows.length) return '';
  const props = PropertiesService.getScriptProperties();
  const i = (Number(props.getProperty('rr') || 0) + 1) % rows.length;
  props.setProperty('rr', String(i));
  return rows[i][0];
}

function findDuplicate_(sh, head, phone) {
  const digits = String(phone || '').replace(/\D/g, '').slice(-10);
  if (digits.length < 10 || sh.getLastRow() < 2) return '';
  const pi = head.indexOf('phone'), ii = head.indexOf('id');
  const vals = sh.getRange(2, 1, sh.getLastRow() - 1, head.length).getValues();
  for (let r = vals.length - 1; r >= 0; r--) if (String(vals[r][pi]).replace(/\D/g, '').slice(-10) === digits) return vals[r][ii];
  return '';
}

function clean_(v) {
  if (v === undefined || v === null) return '';
  if (v instanceof Date) return v;
  const s = String(v).slice(0, 2000);
  return /^[=+\-@]/.test(s) ? "'" + s : s;                           // block formula injection
}

function notify_(r) {
  const to = [NOTIFY_EMAIL, r.owner].filter(Boolean).join(',');
  if (!to) return;
  const wa = String(r.phone || '').replace(/\D/g, '');
  const lines = [
    `Site: ${r.site}   Form: ${r.source}   Page: ${r.page}`, `Name: ${r.name}`, `Phone: ${r.phone}`, r.email && `Email: ${r.email}`,
    r.month && `Month: ${r.month}`, r.nights && `Nights: ${r.nights}`, r.pax && `Travellers: ${r.pax}`, r.tour && `Package: ${r.tour}`,
    r.message && `Notes: ${r.message}`, r.utm_source && `Campaign: ${r.utm_source} / ${r.utm_medium} / ${r.utm_campaign}`,
    r.duplicate_of && `Returning enquirer (earlier lead ${r.duplicate_of})`, r.owner && `Assigned to: ${r.owner}`,
    '', wa && `WhatsApp: https://wa.me/${wa.length === 10 ? '91' + wa : wa}`,
  ].filter(Boolean);
  MailApp.sendEmail(to, `New lead (${r.site || 'website'}): ${r.name}${r.month ? ' · ' + r.month : ''}`, lines.join('\n'));
}

function ok_() { return ContentService.createTextOutput(JSON.stringify({ ok: true })).setMimeType(ContentService.MimeType.JSON); }
