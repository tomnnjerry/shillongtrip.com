# Shillong Trip (shillongtrip.com)

Django site for Meghalaya, Assam (Kaziranga, Majuli), Arunachal Pradesh (Tawang, Ziro, Mechuka) and the rest of Northeast India: 56 places, 60 packages, 63 guides, 9 FAQs on every content page, full JSON-LD, credited Wikimedia Commons photos.

Brief: [PROMPT.md](PROMPT.md). Research and verified facts: [research/](research/) (`facts-memo.md` is the source of truth for permits, parks, roads and festivals).

## Run it

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser   # for /admin/ (enquiries land there)
python manage.py runserver 4322
```

Production: set `DJANGO_DEBUG=0`, `DJANGO_SECRET_KEY`, optionally `DJANGO_ALLOWED_HOSTS`, `ENQUIRY_NOTIFY` (comma-separated emails) and the `DJANGO_EMAIL_BACKEND` / SMTP settings, run `python manage.py collectstatic`, then serve `shillongtrip.wsgi` with gunicorn or similar. WhiteNoise serves `/static/`.

## QA

```bash
DJANGO_DEBUG=0 DJANGO_SECRET_KEY=x DJANGO_SSL_REDIRECT=0 python scripts/smoke.py
```

Renders every sitemap URL and fails on non-200, a page without exactly one `<h1>`, a heading that ends in a full stop, bad JSON-LD, a content page without 9 FAQs, duplicate titles, or a broken enquiry endpoint.

## How it fits together

- `content/` is the database: `_plan.json` (slug registry), `places/*.json`, `packages/*.json` (day-by-day array is `itinerary`), `guides/*.md`, `permits.json`, `kaziranga.json`, `climate.json`, `images.generated.json`. `trips/content.py` loads it into memory; in DEBUG it reloads when a file changes.
- `trips/views.py` one view per page type; `trips/seo.py` JSON-LD; `trips/legal.py` + `trips/pagedata.json` policy text and shared FAQ copy.
- `trips/templatetags/trips_tags.py` icons, responsive images with credits, cards, FAQ block, route stepper, best-month heatmap, rain meter.
- `templates/` base layout, `templates/trips/*.html` pages, `templates/trips/c/*.html` components.
- `static/assets/app.css` and `app.js` are the front end (no framework); `static/img/` holds the processed photos.
- Enquiries from every form POST to `/api/enquiry/` (CSRF-protected, honeypot, stored in the `Enquiry` model, optional email via `ENQUIRY_NOTIFY`). If `site.config.json → leads.endpoint` is set, the Google Apps Script inbox still receives a copy.
- `/sitemap.xml`, `/robots.txt`, `/llms.txt`, `/search.json` and `/site.webmanifest` are Django views.

## Photos and logo

The processed photos are in `static/img/` (manifest: `content/images.generated.json`) and the logo files in `static/assets/`. The Node scripts that produced them have been removed; add new photos by hand and extend the manifest.

## Before launch

1. Fill `site.config.json`: `phone`, `whatsapp` (digits with country code), address, `social`, `company` (legal name, GSTIN, tourism registration), `grievance`, optionally `team` and `analytics.ga4`. Empty values are hidden.
2. Confirm the domain in `site.config.json → url`.
3. Have a lawyer review the policy pages (`trips/pagedata.json`, section `legal`).
4. Review `research/facts-memo.md` (especially the "do not publish" and addenda sections) and the helicopter-status conflict.
5. Submit `sitemap.xml` to Google Search Console and Bing Webmaster Tools.

## URL structure

`/packages/`, `/packages/<slug>/`, `/styles/<theme>/`, `/places/`, `/places/<slug>/`, `/states/<state>/`, `/guides/`, `/guides/<slug>/`, `/trip-tools/`, `/about/`, `/contact/`, `/faq/`, policies, `/sitemap/`, `/photo-credits/`. Unchanged from the static site, so existing links and rankings carry over. Only asset URLs moved: `/img/…` and `/assets/…` are now `/static/img/…` and `/static/assets/…`.

## House style

No full stop at the end of headings; short one-line headings; numbers over adjectives; indicative prices; "check current status before you travel" wherever rules change; no fabricated reviews or claims.
