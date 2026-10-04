# Trip Desk CRM

A free lead CRM for **Shillong Trip**, built on Google Sheets and Google Apps Script. No server, no subscription. The website sends enquiries to one Google Sheet, and the CRM is a private web app on top of it.

Preview it locally with sample data: open `crm/Index.html` in a browser (it runs in demo mode outside Google).

## What it does

- **Pipeline:** drag leads across New → Contacted → Quoted → Negotiating → Booked / Lost, with quote totals per stage.
- **Lead drawer:**
  - one-tap WhatsApp, call and email;
  - WhatsApp reply templates filled with the lead's name, month and package;
  - stage, owner, quote and booked value, follow-up date, lost reason;
  - an activity log for notes, calls, WhatsApp and email;
  - a "returning enquirer" flag when the same phone number has enquired before.
- **All leads:** a sortable table with stage filter and CSV export.
- **Follow-ups:** overdue, due today, not yet contacted, and coming up.
- **Dashboard:**
  - leads per day, first-reply backlog, conversion, open pipeline and booked value;
  - breakdowns by website, form, campaign source, landing page and owner, plus lost reasons.
- **Automation:**
  - round-robin assignment to active team members;
  - an instant email for each new lead (to you and the owner);
  - a 9 am IST daily digest of new leads, follow-ups due and leads still waiting.
- **Attribution on every lead:** site, form, enquiry page, first landing page, referrer, UTM tags, and Google or Meta ad click IDs.

## Setup (about 15 minutes)

### 1. The lead sheet and intake (receives leads from the websites)
1. Create a Google Sheet called **Trip Desk Leads**.
2. **Extensions → Apps Script**. Replace the code with `crm/intake.gs` (the same file is in each site's `tools/leads-apps-script.gs`).
3. Set `NOTIFY_EMAIL` at the top.
4. Select `setupIntake` and click **Run**. Approve permissions. This creates the `Leads`, `Notes`, `Team` and `Templates` tabs and adds you as admin.
5. **Deploy → New deployment → Web app**. Set *Execute as* to **Me** and *Who has access* to **Anyone**. Copy the `/exec` URL.
6. Paste that URL into `leads.endpoint` in `site.config.json`.

The intake only accepts leads; it never returns data, so "Anyone" access is safe.

### 2. The CRM app (private)
1. Go to <https://script.google.com> → **New project** → name it **Trip Desk CRM**.
2. Paste `crm/Code.gs` into `Code.gs`. Add an HTML file named **Index** and paste `crm/Index.html`.
3. In `Code.gs`, set `SHEET_ID` to the long ID in the Trip Desk Leads sheet URL (between `/d/` and `/edit`).
4. Run `setupCrm` once and approve permissions. This installs the daily digest.
5. **Deploy → New deployment → Web app**. Set *Execute as* to **User accessing the web app** and *Who has access* to **Anyone with a Google account**. Open the URL and bookmark it.

### 3. Your team
- Share the **Trip Desk Leads** sheet (Editor) with each team member.
- Add them to the **Team** tab: `email`, `name`, `role` (admin/agent), `active` (TRUE/FALSE).
- Only people on the Team tab who can open the sheet can use the CRM. New leads rotate between active members.

### 4. Reply templates
Edit the **Templates** tab. Placeholders: `{first}`, `{name}`, `{me}`, `{site}`, `{month}`, `{tour}`, `{tourbit}`.

## Notes
- Everything is stored in your own Google account; nothing goes to a third party.
- Leads are stored as plain rows, so you can filter, pivot or chart them in Sheets as usual.
- After editing `Code.gs` or `Index.html`, use **Deploy → Manage deployments → Edit → New version** to publish changes.
