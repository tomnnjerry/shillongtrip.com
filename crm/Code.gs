/**
 * TRIP DESK CRM — private web app on top of the "Leads" sheet written by intake.gs.
 *
 * Setup (see crm/README.md):
 *   1. script.google.com → New project "Trip Desk CRM". Add Code.gs (this file) and an HTML file named Index (Index.html).
 *   2. Set SHEET_ID below (the long id in the Leads spreadsheet URL).
 *   3. Run setupCrm() once and approve permissions (installs the 9 am daily digest).
 *   4. Deploy → New deployment → Web app. Execute as: User accessing the web app. Who has access: Anyone with a Google account.
 *   5. Share the spreadsheet (Editor) with each team member and list them in the Team sheet. Only they can open the CRM.
 */
const SHEET_ID = 'PASTE_YOUR_SHEET_ID_HERE';
const STAGES = ['New', 'Contacted', 'Quoted', 'Negotiating', 'Booked', 'Lost'];
const EDITABLE = ['stage', 'owner', 'quote_inr', 'booked_inr', 'followup', 'lost_reason', 'last_contact', 'name', 'phone', 'email', 'month', 'pax', 'tour', 'message'];
const SITE_NAMES = { 'shillongtrip.com': 'Shillong Trip' };

function doGet() {
  const me = Session.getActiveUser().getEmail();
  if (!isTeam_(me)) {
    return HtmlService.createHtmlOutput(`<div style="font:16px system-ui;padding:40px;max-width:520px"><h2>No access</h2><p>${me || 'Your account'} is not on the Team list. Ask an admin to add you to the Team sheet and share the spreadsheet with you.</p></div>`).setTitle('Trip Desk CRM');
  }
  return HtmlService.createTemplateFromFile('Index').evaluate()
    .setTitle('Trip Desk CRM').addMetaTag('viewport', 'width=device-width, initial-scale=1');
}

function setupCrm() {
  ScriptApp.getProjectTriggers().filter(t => t.getHandlerFunction() === 'dailyDigest').forEach(t => ScriptApp.deleteTrigger(t));
  ScriptApp.newTrigger('dailyDigest').timeBased().atHour(9).everyDays(1).inTimezone('Asia/Kolkata').create();
  assignMissingIds_();
  return 'CRM ready';
}

/* ---------- data helpers ---------- */
const ss_ = () => SpreadsheetApp.openById(SHEET_ID);
function table_(name) {
  const sh = ss_().getSheetByName(name);
  if (!sh || sh.getLastRow() < 1) return { sh, head: [], rows: [] };
  const vals = sh.getDataRange().getValues();
  const head = vals.shift().map(String);
  return { sh, head, rows: vals.map((r, i) => { const o = { _row: i + 2 }; head.forEach((h, j) => { o[h] = r[j] instanceof Date ? r[j].toISOString() : r[j]; }); return o; }) };
}
function team_() {
  return table_('Team').rows.filter(r => r.email && String(r.active).toUpperCase() !== 'FALSE')
    .map(r => ({ email: String(r.email).toLowerCase(), name: r.name || r.email, role: r.role || 'agent', whatsapp: r.whatsapp || '' }));
}
function isTeam_(email) {
  if (!email) return false;
  const t = team_();
  return !t.length || t.some(m => m.email === email.toLowerCase());
}
function guard_() {
  const me = Session.getActiveUser().getEmail();
  if (!isTeam_(me)) throw new Error('Not authorised');
  return me;
}
function assignMissingIds_() {
  const { sh, head, rows } = table_('Leads');
  const ii = head.indexOf('id'), si = head.indexOf('stage');
  rows.forEach(r => {
    if (!r.id) sh.getRange(r._row, ii + 1).setValue('L' + Math.random().toString(36).slice(2, 10).toUpperCase());
    if (!r.stage && si > -1) sh.getRange(r._row, si + 1).setValue('New');
  });
}

/* ---------- API (called from Index.html via google.script.run) ---------- */
function api_bootstrap() {
  const me = guard_();
  assignMissingIds_();
  const leads = table_('Leads').rows.map(r => { delete r._row; return r; });
  const notes = table_('Notes').rows;
  const counts = {}; notes.forEach(n => { counts[n.lead_id] = (counts[n.lead_id] || 0) + 1; });
  leads.forEach(l => { l.notes_count = counts[l.id] || 0; if (!l.stage) l.stage = 'New'; });
  const templates = table_('Templates').rows.map(t => ({ key: t.key, label: t.label, text: t.text }));
  return { me, stages: STAGES, team: team_(), templates, leads, siteNames: SITE_NAMES, now: new Date().toISOString() };
}

function api_updateLead(id, patch) {
  const me = guard_();
  const lock = LockService.getScriptLock(); lock.waitLock(10000);
  try {
    const { sh, head, rows } = table_('Leads');
    const r = rows.find(x => x.id === id);
    if (!r) throw new Error('Lead not found');
    const changes = [];
    Object.keys(patch || {}).filter(k => EDITABLE.includes(k)).forEach(k => {
      let col = head.indexOf(k);
      if (col < 0) { sh.getRange(1, head.length + 1).setValue(k).setFontWeight('bold'); head.push(k); col = head.length - 1; }
      const v = k === 'followup' && patch[k] ? new Date(patch[k]) : patch[k];
      sh.getRange(r._row, col + 1).setValue(typeof v === 'string' && /^[=+\-@]/.test(v) ? "'" + v : v);
      if (String(r[k] ?? '') !== String(patch[k] ?? '')) changes.push(k);
    });
    const ui = head.indexOf('updated_at'); if (ui > -1) sh.getRange(r._row, ui + 1).setValue(new Date());
    if (changes.includes('stage')) addNote_(id, me, 'status', `Stage: ${r.stage || 'New'} → ${patch.stage}${patch.lost_reason ? ' (' + patch.lost_reason + ')' : ''}`);
    if (changes.includes('owner')) addNote_(id, me, 'status', `Assigned to ${patch.owner || 'nobody'}`);
    return { ok: true };
  } finally { lock.releaseLock(); }
}

function api_notes(id) {
  guard_();
  return table_('Notes').rows.filter(n => n.lead_id === id).map(n => ({ at: n.at, by: n.by, type: n.type, text: n.text })).sort((a, b) => String(b.at).localeCompare(String(a.at)));
}

function api_addNote(id, type, text) {
  const me = guard_();
  addNote_(id, me, type || 'note', String(text || '').slice(0, 4000));
  if (['call', 'whatsapp', 'email'].includes(type)) {
    const { rows } = table_('Leads');
    const r = rows.find(x => x.id === id);
    const patch = { last_contact: new Date().toISOString() };
    if (r && (!r.stage || r.stage === 'New')) patch.stage = 'Contacted';
    api_updateLead(id, patch);
  }
  return api_notes(id);
}

function api_addLead(obj) {
  const me = guard_();
  const { sh, head } = table_('Leads');
  const now = new Date();
  const id = 'L' + Utilities.formatDate(now, 'Asia/Kolkata', 'yyMMdd') + '-' + Math.random().toString(36).slice(2, 6).toUpperCase();
  const row = { ...obj, id, created_at: now, updated_at: now, source: obj.source || 'manual', stage: 'New', owner: obj.owner || me };
  sh.appendRow(head.map(h => { const v = row[h]; return v === undefined ? '' : (typeof v === 'string' && /^[=+\-@]/.test(v) ? "'" + v : v); }));
  addNote_(id, me, 'status', 'Lead added manually');
  return id;
}

function addNote_(leadId, by, type, text) {
  const ss = ss_();
  let sh = ss.getSheetByName('Notes');
  if (!sh) { sh = ss.insertSheet('Notes'); sh.appendRow(['id', 'lead_id', 'at', 'by', 'type', 'text']); sh.setFrozenRows(1); }
  sh.appendRow(['N' + Math.random().toString(36).slice(2, 10), leadId, new Date(), by, type, /^[=+\-@]/.test(text) ? "'" + text : text]);
}

/* ---------- Daily digest (9 am IST) ---------- */
function dailyDigest() {
  const leads = table_('Leads').rows;
  const now = Date.now(), day = 864e5;
  const fresh = leads.filter(l => now - new Date(l.created_at).getTime() < day);
  const stale = leads.filter(l => (l.stage || 'New') === 'New' && now - new Date(l.created_at).getTime() > day);
  const due = leads.filter(l => l.followup && !['Booked', 'Lost'].includes(l.stage) && new Date(l.followup).getTime() < now + day);
  const line = l => `• ${l.name} (${l.phone}) · ${SITE_NAMES[l.site] || l.site || 'site'} · ${l.stage || 'New'}${l.owner ? ' · ' + l.owner : ''}`;
  const body = [
    `New in the last 24 hours: ${fresh.length}`, ...fresh.map(line), '',
    `Follow-ups due today or overdue: ${due.length}`, ...due.map(line), '',
    `Still "New" after 24 hours: ${stale.length}`, ...stale.map(line),
  ].join('\n');
  const to = team_().map(m => m.email).join(',');
  if (to && (fresh.length || due.length || stale.length)) MailApp.sendEmail(to, `Trip Desk: ${fresh.length} new, ${due.length} follow-ups, ${stale.length} waiting`, body);
}
