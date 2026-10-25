"""Page views. Each builds a context dict, then renders a template (port of src/pages/*.mjs)."""
import json
import re
from datetime import date

from django.conf import settings
from django.core.mail import send_mail
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import render
from django.templatetags.static import static
from django.views.decorators.http import require_POST

from . import content as C
from . import legal as L
from . import seo
from .models import Enquiry
from .templatetags.trips_tags import station_for

PD = L.pagedata()


# ---------- shared ----------
def page(request, template, *, title, description, path, jsonld=None, image=None, preload_im=None, over=False, og_type='website', noindex=False, **ctx):
    s = C.get().site
    full = title if s['name'] in title else f"{title} | {s['name']}"
    ctx.update(
        page_title=title, page_full_title=full, page_description=description, page_path=path, canonical=seo.abs_url(path),
        og_image=image or seo.abs_url(static('assets/logo.png')), og_type=og_type, noindex=noindex, preload_im=preload_im, over=over,
        jsonld=[seo.org_ld(), *(jsonld or [])],
    )
    return render(request, template, ctx)


def _pk(slugs):
    c = C.get()
    return [c.pkg_by_slug[s] for s in slugs if s in c.pkg_by_slug]


def _faq_spread(lists, limit=9):
    """Take the first FAQ of each item, then the second, etc., up to `limit`."""
    out = []
    for r in range(9):
        for faqs in lists:
            if r < len(faqs) and len(out) < limit:
                out.append(faqs[r])
    return out


# ---------- home ----------
def home(request):
    c = C.get()
    h1 = c.img('_hero-meghalaya')
    h2 = c.img('_one-horned-rhino') or c.img('kaziranga')
    h3 = c.img('_hero-tawang') or c.img('tawang')
    popular = _pk(['meghalaya-classic-4n', 'shillong-kaziranga-5n', 'northeast-7n', 'tawang-6n', 'meghalaya-root-bridges-5n', 'kaziranga-2n', 'hornbill-festival-5n', 'ziro-valley-4n'])
    styles = [dict(key=k, **C.THEMES[k]) for k in ['honeymoon', 'family', 'wildlife', 'trekking', 'festival', 'monsoon', 'snow', 'culture', 'offbeat', 'luxury', 'budget', 'photography']]
    facts = [('car', 'Guwahati to Shillong', 'about 3 hours by road'), ('paw', 'Kaziranga safaris', 'roughly Oct/Nov to Apr'),
             ('drop', 'Mawsynram & Sohra', 'among the wettest places on Earth'), ('mountain', 'Sela Pass', 'about 4,170 m on the Tawang road'),
             ('drum', 'Hornbill Festival', '1–10 December, Kohima'), ('route', 'Guwahati to Tawang', 'usually 2 days by road')]
    lead = c.guide_by_slug.get('places-to-visit-in-meghalaya') or c.guides[0]
    side = [g for g in (c.guide_by_slug.get(s) for s in ['best-time-to-visit-meghalaya', 'kaziranga-safari-guide', 'arunachal-ilp-guide', 'meghalaya-trip-cost']) if g and g is not lead][:4]
    tabs = []
    for st in C.STATES.values():
        tabs.append(dict(st=st, hero=c.img(st['hero']), places=[d for d in c.places if d['state'] == st['key']][:4],
                         packages=[t for t in c.packages if st['key'] in (t.get('states') or [])][:3]))
    faqs = PD['home_faqs']
    return page(request, 'trips/home.html',
                title='Shillong Trip: Meghalaya, Kaziranga & Northeast Tour Packages',
                description='Meghalaya, Shillong, Kaziranga, Tawang and Northeast India tour packages with day-by-day plans, permit help and written quotes. Plan with local experts.',
                path='/', preload_im=h1, h1=h1, h2=h2, h3=h3, popular=popular, styles=styles, facts=facts + facts, nfacts=len(facts), lead=lead, side=side, tabs=tabs,
                faqs=faqs, has_sohra=bool((c.climate or {}).get('stations', {}).get('sohra')),
                jsonld=[seo.website_ld(), seo.faq_ld(faqs), seo.item_list_ld([dict(url=f"/packages/{t['slug']}/", name=t['title']) for t in popular])])


# ---------- packages ----------
def _related(t):
    c = C.get()
    scored = []
    for o in c.packages:
        if o['slug'] == t['slug']:
            continue
        score = len([d for d in (o.get('places') or []) if d in (t.get('places') or [])]) * 2 + len([x for x in (o.get('themes') or []) if x in (t.get('themes') or [])]) - abs(o['nights'] - t['nights']) * 0.3
        scored.append((score, o))
    scored.sort(key=lambda x: -x[0])
    return [o for _, o in scored[:4]]


def _pk_title(t):
    b = C.trim_stop(t['title'])
    n = t['nights']
    for cand in (f'{b} Tour Package ({n}N/{n + 1}D)', f'{b} ({n}N/{n + 1}D)'):
        if len(cand) <= 58:
            return cand
    return b


def package_detail(request, slug):
    c = C.get()
    t = c.pkg_by_slug.get(slug)
    if not t:
        raise Http404
    path = f'/packages/{slug}/'
    hero_key = t.get('hero') or (t.get('places') or [''])[0]
    stops = [c.place_by_slug[s] for s in (t.get('places') or []) if s in c.place_by_slug]
    gal = [x for x in [c.img(hero_key)] + [c.img(d['slug']) for d in stops if d['slug'] != hero_key][:4] if x][:5]
    crumb_list = [('Home', '/'), ('Packages', '/packages/'), (C.trim_stop(t['title']), path)]
    msg = f'Hi, I\'m interested in "{t["title"]}" ({t["nights"]}N/{t["nights"] + 1}D). Month: __, travellers: __.'
    f = c.foreign_status(t)
    reads = [g for g in c.guides if slug in (g.get('packages') or [])][:3]
    route = [dict(slug=s, name=C.short_name(c.place_name(s))) for s in (t.get('places') or [])]
    trip = {
        '@context': 'https://schema.org', '@type': 'TouristTrip', 'name': t['title'], 'description': t.get('meta_description'), 'url': seo.abs_url(path),
        'image': seo.img_url(hero_key), 'touristType': [C.THEMES[k]['name'] for k in (t.get('themes') or []) if k in C.THEMES],
        'provider': {'@id': seo.org_id()},
        'itinerary': {'@type': 'ItemList', 'numberOfItems': len(stops), 'itemListElement': [
            {'@type': 'ListItem', 'position': i + 1, 'item': {'@type': 'TouristDestination', 'name': d['name'], 'url': seo.abs_url(f"/places/{d['slug']}/")}} for i, d in enumerate(stops)]},
        'offers': {'@type': 'Offer', 'price': t['price_from_inr'], 'priceCurrency': 'INR', 'availability': 'https://schema.org/InStock', 'url': seo.abs_url(path)},
    }
    return page(request, 'trips/package.html', title=_pk_title(t), description=t.get('meta_description', ''), path=path, image=seo.img_url(hero_key),
                preload_im=gal[0] if gal else None, jsonld=[trip, seo.faq_ld(t.get('faqs') or []), seo.crumbs_ld(crumb_list)],
                t=t, crumb_list=crumb_list, gal=gal, route=route, f=f, reads=reads, stops=stops[:8], msg=msg, related=_related(t), hero_key=hero_key,
                difficulty=(t.get('difficulty') or 'easy').capitalize())


def packages_index(request):
    c = C.get()
    path = '/packages/'
    crumb_list = [('Home', '/'), ('Packages', path)]
    lowest = min(t['price_from_inr'] for t in c.packages)
    return page(request, 'trips/packages_index.html', title='Northeast Tour Packages: Meghalaya, Kaziranga, Tawang',
                description=f'Compare Northeast India tour packages for Meghalaya, Assam, Arunachal and Nagaland by state, length, month and style. Day-by-day plans from {C.inr(lowest)}.',
                path=path, crumb_list=crumb_list, packages=c.packages, themes=[dict(key=k, **v) for k, v in C.THEMES.items()],
                jsonld=[seo.crumbs_ld(crumb_list), seo.item_list_ld([dict(url=f"/packages/{t['slug']}/", name=t['title']) for t in c.packages])])


def _style_faqs(lst):
    seen, out = set(), []
    for r in range(9):
        for t in lst:
            faqs = t.get('faqs') or []
            if r >= len(faqs):
                continue
            q = faqs[r]
            stem = ' '.join(re.sub(r'[^a-z ]', '', q['q'].lower()).split(' ')[:4])
            if stem in seen:
                continue
            seen.add(stem)
            out.append(q)
            if len(out) == 9:
                return out
    return out


def style_detail(request, key):
    c = C.get()
    th = C.THEMES.get(key)
    if not th:
        raise Http404
    lst = [t for t in c.packages if c.in_theme(t, key)]
    if not lst:
        raise Http404
    path = f'/styles/{key}/'
    crumb_list = [('Home', '/'), ('Packages', '/packages/'), (th['name'], path)]
    min_p = min(t['price_from_inr'] for t in lst)
    im = c.img(lst[0].get('hero'))
    faqs = _style_faqs(lst)
    h1 = th['h1'][:1].upper() + th['h1'][1:]
    title = f'{h1} with Prices'
    rows = [dict(t=t, states=', '.join(C.STATES[s]['short'] for s in (t.get('states') or []) if s in C.STATES)) for t in lst]
    return page(request, 'trips/style.html', title=title if len(title) <= 58 else h1,
                description=f"{h1} from {C.inr(min_p)} per person. {th['desc']}"[:158], path=path, crumb_list=crumb_list,
                th=th, h1=h1, min_p=min_p, im=im, plan_msg=f"Hi, I'm looking for {th['h1']}.", faqs=faqs, rows=rows, lst=lst,
                other_themes=[dict(key=k, **v) for k, v in C.THEMES.items() if k != key], key=key,
                jsonld=[seo.crumbs_ld(crumb_list), seo.item_list_ld([dict(url=f"/packages/{t['slug']}/", name=t['title']) for t in lst]), seo.faq_ld(faqs)])


# ---------- places ----------
SPOTS = {'falls', 'waterfall', 'cave', 'monastery', 'temple', 'viewpoint', 'lake', 'pass', 'root-bridge', 'monoliths', 'forest'}


def _pl_title(d):
    n = C.short_name(d['name'])
    for t in (f'{n} Travel Guide: How to Reach, Best Time, Tips', f'{n}: How to Reach, Best Time & Tips', f'{n} Travel Guide 2026', n):
        if len(t) <= 56:
            return t
    return n


def place_detail(request, slug):
    c = C.get()
    d = c.place_by_slug.get(slug)
    if not d:
        raise Http404
    path = f'/places/{slug}/'
    st = C.STATES.get(d['state'])
    crumb_list = [('Home', '/'), ('Places', '/places/'), (st['name'] if st else 'State', f"/states/{d['state']}/"), (d['name'], path)]
    ims = c.images_for(slug)
    hero = ims[0] if ims else None
    pks = c.packages_for(slug)[:6]
    near = [c.place_by_slug[s] for s in (d.get('nearby') or []) if s in c.place_by_slug]
    reads = [g for g in c.guides if slug in (g.get('places') or [])][:3]
    msg = f"Hi, I'd like to include {d['name']} in my trip."
    is_spot = any(x in SPOTS for x in (d.get('types') or []))
    place_ld = {
        '@context': 'https://schema.org', '@type': 'TouristAttraction' if is_spot else 'TouristDestination', 'name': d['name'], 'description': d.get('meta_description'), 'url': seo.abs_url(path),
        'image': [seo.abs_url(f"{static('img/')}{im['id']}-{im['widths'][-1]}.webp") for im in ims[:3]],
        'containedInPlace': {'@type': 'AdministrativeArea', 'name': f"{d.get('state_name') or (st or {}).get('name')}, India"},
    }
    if d.get('coords'):
        place_ld['geo'] = {'@type': 'GeoCoordinates', 'latitude': d['coords'][0], 'longitude': d['coords'][1], 'elevation': d.get('altitude_m')}
    permit_req = bool((d.get('permit') or {}).get('required'))
    return page(request, 'trips/place.html', title=_pl_title(d), description=d.get('meta_description', ''), path=path, image=seo.img_url(slug), preload_im=hero,
                jsonld=[place_ld, seo.faq_ld(d.get('faqs') or []), seo.crumbs_ld(crumb_list)],
                d=d, st=st, crumb_list=crumb_list, ims=ims, hero=hero, pks=pks, near=near, reads=reads, msg=msg, station=station_for(d), permit_req=permit_req,
                gal_cols=min(len(ims), 4), osm=(f"https://www.openstreetmap.org/?mlat={d['coords'][0]}&mlon={d['coords'][1]}#map=12/{d['coords'][0]}/{d['coords'][1]}" if d.get('coords') else ''))


def places_index(request):
    c = C.get()
    path = '/places/'
    crumb_list = [('Home', '/'), ('Places', path)]
    groups = [dict(st=st, places=[d for d in c.places if d['state'] == st['key']]) for st in C.STATES.values()]
    return page(request, 'trips/places_index.html', title='Places to Visit in Northeast India by State',
                description='Places to visit in Meghalaya, Assam, Arunachal, Nagaland, Manipur, Mizoram and Tripura, with altitude, permits, best months and distances from the nearest hub.',
                path=path, crumb_list=crumb_list, groups=groups, count=len(c.places),
                jsonld=[seo.crumbs_ld(crumb_list), seo.item_list_ld([dict(url=f"/places/{d['slug']}/", name=d['name']) for d in c.places])])


def state_detail(request, key):
    c = C.get()
    s = C.STATES.get(key)
    if not s:
        raise Http404
    path = f'/states/{key}/'
    crumb_list = [('Home', '/'), ('Places', '/places/'), (s['name'], path)]
    lst = [d for d in c.places if d['state'] == key]
    pks = [t for t in c.packages if key in (t.get('states') or [])]
    hero = c.img(s['hero'])
    slugs = {d['slug'] for d in lst}
    reads = [g for g in c.guides if any(p in slugs for p in (g.get('places') or []))][:6]
    faqs = _faq_spread([d.get('faqs') or [] for d in lst])
    return page(request, 'trips/state.html', title=s['title'], description=f"{s['line']} Places, packages, permits, altitudes and best months."[:158], path=path,
                image=seo.img_url(s['hero']), preload_im=hero, s=s, crumb_list=crumb_list, places=lst, pks=pks[:8], hero=hero, reads=reads, faqs=faqs,
                jsonld=[seo.crumbs_ld(crumb_list), seo.item_list_ld([dict(url=f"/places/{d['slug']}/", name=d['name']) for d in lst]), seo.faq_ld(faqs)])


# ---------- guides ----------
GUIDE_CATS = ['Planning', 'Itineraries', 'Places', 'Stays', 'Seasons', 'Wildlife', 'Culture', 'Food', 'Treks']


def guide_detail(request, slug):
    c = C.get()
    g = c.guide_by_slug.get(slug)
    if not g:
        raise Http404
    path = f'/guides/{slug}/'
    crumb_list = [('Home', '/'), ('Guides', '/guides/'), (C.trim_stop(g['title']), path)]
    if '_html' not in g:
        g['_html'], g['_toc'] = C.render_markdown(g.get('body') or '')
    places = g.get('places') or []
    hero_key = places[0] if places else '_hero-meghalaya'
    im = c.img(hero_key)
    pks = [c.pkg_by_slug[s] for s in (g.get('packages') or []) if s in c.pkg_by_slug][:4]
    rel = [o for o in c.guides if o['slug'] != slug and (o.get('category') == g.get('category') or any(p in places for p in (o.get('places') or [])))][:3]
    words = C.word_count(g.get('body'))
    mins = g.get('read_minutes') or max(5, round(words / 220))
    share_url = seo.abs_url(path)
    art = {
        '@context': 'https://schema.org', '@type': 'BlogPosting', 'headline': g['title'], 'description': g.get('description'), 'image': seo.img_url(hero_key),
        'datePublished': g.get('date'), 'dateModified': g.get('updated') or g.get('date'), 'wordCount': words, 'mainEntityOfPage': share_url,
        'articleSection': g.get('category'), **({'keywords': g['keyword']} if g.get('keyword') else {}),
        'author': {'@type': 'Organization', 'name': f"{c.site['name']} Travel Desk", 'url': seo.abs_url('/about/')}, 'publisher': {'@id': seo.org_id()},
        'about': [{'@type': 'Place', 'name': c.place_by_slug[p]['name']} for p in places if p in c.place_by_slug],
    }
    return page(request, 'trips/guide.html', title=C.trim_stop(g['title']), description=g.get('description', ''), path=path, og_type='article',
                image=seo.img_url(hero_key), preload_im=im, jsonld=[art, seo.faq_ld(g.get('faqs') or []), seo.crumbs_ld(crumb_list)],
                g=g, crumb_list=crumb_list, im=im, pks=pks, rel=rel, mins=mins, hero_key=hero_key, share_url=share_url, html=g['_html'], toc=g['_toc'])


def guides_index(request):
    c = C.get()
    path = '/guides/'
    crumb_list = [('Home', '/'), ('Guides', path)]
    lead, rest = c.guides[0], c.guides[1:]
    return page(request, 'trips/guides_index.html', title='Northeast India Travel Guides: Meghalaya, Assam, Arunachal',
                description='Northeast India travel guides: permits, best time to visit, Kaziranga safaris, Tawang, root bridge treks, costs, hotels and itineraries. Updated 2026.',
                path=path, crumb_list=crumb_list, cats=GUIDE_CATS, lead=lead, side=rest[:4], rest=rest[4:],
                jsonld=[seo.crumbs_ld(crumb_list), seo.item_list_ld([dict(url=f"/guides/{g['slug']}/", name=g['title']) for g in c.guides])])


# ---------- tools, contact, faq, about, credits, legal ----------
def tools(request):
    c = C.get()
    path = '/trip-tools/'
    crumb_list = [('Home', '/'), ('Trip tools', path)]
    stations = [dict(key=k, name=v['name']) for k, v in ((c.climate or {}).get('stations') or {}).items()]
    kaz = c.kaziranga
    return page(request, 'trips/tools.html', title='Northeast Trip Tools: Permits, Budget, Kaziranga',
                description='Free Northeast India trip tools: ILP and permit checker by state and passport, budget builder, Kaziranga safari planner, best months and rainfall by place.',
                path=path, crumb_list=crumb_list, permits=c.permits, permit_areas_json=json.dumps((c.permits or {}).get('areas') or []).replace('<', '\\u003c'),
                kaz=kaz, stations=stations, month_notes=C.MONTH_NOTES, month_notes_json=json.dumps(C.MONTH_NOTES).replace('<', '\\u003c'),
                month_note=C.MONTH_NOTES[date.today().month - 1], tool_months=4 if kaz else 3, tool_rain=5 if kaz else 4,
                jsonld=[seo.crumbs_ld(crumb_list)])


def contact(request):
    path = '/contact/'
    crumb_list = [('Home', '/'), ('Contact', path)]
    return page(request, 'trips/contact.html', title='Contact Us & Plan My Northeast Trip',
                description='Tell us your dates and travellers and get a day-by-day Meghalaya, Assam, Arunachal or Northeast itinerary with a clear quote. WhatsApp or email.',
                path=path, crumb_list=crumb_list, jsonld=[seo.crumbs_ld(crumb_list)])


def faq(request):
    path = '/faq/'
    crumb_list = [('Home', '/'), ('FAQs', path)]
    return page(request, 'trips/faq.html', title='Northeast India Travel FAQs: Permits, Costs, Seasons',
                description='Answers to common Meghalaya, Assam and Arunachal travel questions: permits, best time, costs, Kaziranga safaris, airports, network, payments and road closures.',
                path=path, crumb_list=crumb_list, faqs_a=PD['home_faqs'], faqs_b=PD['more_faqs'],
                jsonld=[seo.crumbs_ld(crumb_list), seo.faq_ld(PD['home_faqs'] + PD['more_faqs'])])


def about(request):
    c = C.get()
    path = '/about/'
    crumb_list = [('Home', '/'), ('About us', path)]
    a = c.img('_root-bridge') or c.img('nongriat-root-bridges')
    b = c.img('_khasi-culture') or c.img('mawlynnong')
    cc = c.img('_one-horned-rhino') or c.img('kaziranga')
    co = c.site.get('company') or {}
    facts = [(k, v) for k, v in [('Legal name', co.get('legalName')), ('Tourism registration', co.get('tourismRegistration')), ('GSTIN', co.get('gstin')),
                                 ('Planning trips since', co.get('foundedYear'))] if v]
    team = [m for m in (c.site.get('team') or []) if m.get('name')]
    for m in team:
        m['initials'] = ''.join(w[0] for w in m['name'].split())[:2]
    return page(request, 'trips/about.html', title='About Shillong Trip: Northeast India Travel Specialists',
                description='Shillong Trip plans Meghalaya, Assam, Arunachal and Northeast India trips with honest routing, permit and safari handling, local drivers and written quotes.',
                path=path, preload_im=a, crumb_list=crumb_list, pa=a, pb=b, pc=cc, facts=facts, team=team,
                promises=[dict(icon=p[0], h=p[1], t=p[2]) for p in PD['promises']], steps=[dict(n=s[0], h=s[1], t=s[2]) for s in PD['steps']], faqs=PD['about_faqs'],
                jsonld=[{'@context': 'https://schema.org', '@type': 'AboutPage', 'name': f"About {c.site['name']}", 'url': seo.abs_url(path), 'mainEntity': {'@id': seo.org_id()}},
                        seo.faq_ld(PD['about_faqs']), seo.crumbs_ld(crumb_list)])


def credits(request):
    c = C.get()
    path = '/photo-credits/'
    crumb_list = [('Home', '/'), ('Photo credits', path)]
    rows = [im for lst in c.images.values() for im in lst]
    return page(request, 'trips/credits.html', title='Photo Credits',
                description='Credits and licences for the Wikimedia Commons photographs used on Shillong Trip, with links to every original file.',
                path=path, crumb_list=crumb_list, rows=rows, jsonld=[seo.crumbs_ld(crumb_list)])


def legal_view(request, key):
    d = L.legal_page(key)
    crumb_list = [('Home', '/'), (d['title'], d['path'])]
    return page(request, 'trips/legal.html', title=d['title'], description=d['description'], path=d['path'], crumb_list=crumb_list, d=d, jsonld=[seo.crumbs_ld(crumb_list)])


def sitemap_page(request):
    c = C.get()
    path = '/sitemap/'
    crumb_list = [('Home', '/'), ('Sitemap', path)]
    cols = [
        ('Main pages', [('/', 'Home'), ('/packages/', 'All packages'), ('/places/', 'All places'), ('/guides/', 'Travel guides'), ('/trip-tools/', 'Trip tools'), ('/about/', 'About us'), ('/contact/', 'Contact'), ('/faq/', 'FAQs')]),
        ('States', [(f'/states/{k}/', s['name']) for k, s in C.STATES.items()]),
        ('Travel styles', [(f'/styles/{k}/', C.THEMES[k]['h1'][:1].upper() + C.THEMES[k]['h1'][1:]) for k in C.THEMES if any(k in (t.get('themes') or []) for t in c.packages)]),
        ('Policies', [('/terms/', 'Terms & conditions'), ('/cancellation-refund-policy/', 'Cancellation & refund policy'), ('/privacy/', 'Privacy policy'),
                      ('/cookie-policy/', 'Cookie policy'), ('/disclaimer/', 'Disclaimer'), ('/photo-credits/', 'Photo credits')]),
        ('Packages', [(f"/packages/{t['slug']}/", C.trim_stop(t['title'])) for t in c.packages]),
        ('Places', [(f"/places/{d['slug']}/", d['name']) for d in c.places]),
        ('Guides', [(f"/guides/{g['slug']}/", C.trim_stop(g['title'])) for g in c.guides]),
    ]
    return page(request, 'trips/sitemap.html', title='Sitemap', description='All pages on Shillong Trip: packages, places, states, travel guides, trip tools and policies for Northeast India travel.',
                path=path, crumb_list=crumb_list, cols=cols, jsonld=[seo.crumbs_ld(crumb_list)])


def not_found(request, exception=None):
    resp = page(request, 'trips/404.html', title='Page not found', description='This page could not be found on Shillong Trip.', path=request.path, noindex=True)
    resp.status_code = 404
    return resp


# ---------- machine-readable files ----------
def _sitemap_urls():
    c = C.get()
    urls = [('/', 1), ('/packages/', .9)]
    urls += [(f"/packages/{t['slug']}/", .8) for t in c.packages]
    urls += [(f'/styles/{k}/', .8) for k in c.themes_with_packages()]
    urls += [('/places/', .9)] + [(f'/states/{k}/', .8) for k in C.STATES] + [(f"/places/{d['slug']}/", .7) for d in c.places]
    urls += [('/guides/', .7)] + [(f"/guides/{g['slug']}/", .7) for g in c.guides]
    urls += [('/trip-tools/', .7), ('/contact/', .6), ('/about/', .5), ('/faq/', .6), ('/photo-credits/', .2), ('/privacy/', .2), ('/terms/', .2),
             ('/cookie-policy/', .1), ('/cancellation-refund-policy/', .3), ('/disclaimer/', .1), ('/sitemap/', .2)]
    return urls


def sitemap_xml(request):
    today = date.today().isoformat()
    rows = '\n'.join(f'  <url><loc>{seo.abs_url(p)}</loc><lastmod>{today}</lastmod><priority>{pr:.1f}</priority></url>' for p, pr in _sitemap_urls())
    return HttpResponse(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{rows}\n</urlset>\n', content_type='application/xml')


def robots_txt(request):
    return HttpResponse(f"User-agent: *\nAllow: /\nDisallow: /search.json\nDisallow: /admin/\nDisallow: /api/\n\nSitemap: {seo.abs_url('/sitemap.xml')}\n", content_type='text/plain')


def ads_txt(request):
    return HttpResponse('google.com, pub-9304666313639850, DIRECT, f08c47fec0942fa0\n', content_type='text/plain')


def llms_txt(request):
    c = C.get()
    s = c.site
    today = date.today().isoformat()
    a = seo.abs_url
    txt = f"""# {s['name']}

> {s['tagline']}. Trip planning for Meghalaya (Shillong, Sohra/Cherrapunji, Dawki, Mawlynnong), Assam (Guwahati, Kaziranga, Majuli), Arunachal Pradesh (Tawang, Ziro, Mechuka) and Nagaland, Manipur, Mizoram and Tripura. Facts checked {today}.

Key facts:
- Gateway: Guwahati (GAU airport, Guwahati railway station). Shillong is about 100 km / 3 hours by road from Guwahati.
- Indian citizens need an Inner Line Permit for Arunachal Pradesh, Nagaland, Mizoram and Manipur; none for Meghalaya, Assam or Tripura. Bum La (Tawang) needs a separate pass and is for Indian nationals.
- Kaziranga National Park is usually open for safaris from about November to April.
- Best months for Meghalaya: October–April (dry, clear rivers at Dawki); June–September is peak monsoon.

## Core pages
- [Packages]({a('/packages/')}): Northeast tour packages with day-by-day plans and prices
- [Places]({a('/places/')}): places to visit with altitude, permits and best months
- [Trip tools]({a('/trip-tools/')}): permit checker, budget builder, Kaziranga safari planner
- [FAQs]({a('/faq/')})

## States
{chr(10).join(f"- [{v['name']}]({a(f'/states/{k}/')}): {v['line']}" for k, v in C.STATES.items())}

## Guides
{chr(10).join(f"- [{C.trim_stop(g['title'])}]({a('/guides/' + g['slug'] + '/')}): {g.get('description', '')}" for g in c.guides)}

## Packages
{chr(10).join(f"- [{C.trim_stop(t['title'])}]({a('/packages/' + t['slug'] + '/')}): {t['nights']} nights, from {C.inr(t['price_from_inr'])} per person" for t in c.packages)}

## Places
{chr(10).join(f"- [{d['name']}]({a('/places/' + d['slug'] + '/')}): {d.get('altitude_m')} m, {d.get('state_name') or C.STATES[d['state']]['name']}" for d in c.places)}
"""
    return HttpResponse(txt, content_type='text/plain; charset=utf-8')


def webmanifest(request):
    s = C.get().site
    return JsonResponse({'name': s['name'], 'short_name': 'Shillong Trip', 'start_url': '/', 'display': 'standalone', 'background_color': '#F3F6F3', 'theme_color': '#0E4B36',
                         'icons': [{'src': static('assets/icon-192.png'), 'sizes': '192x192', 'type': 'image/png'}, {'src': static('assets/icon-512.png'), 'sizes': '512x512', 'type': 'image/png'}]},
                        content_type='application/manifest+json')


def search_json(request):
    c = C.get()
    cap = lambda s: s[:1].upper() + s[1:]
    items = [dict(t=d['name'], u=f"/places/{d['slug']}/", k='Place', s=f"{C.STATES[d['state']]['name']} · {d.get('altitude_m')} m", x=' '.join([d.get('tagline') or '', d.get('district') or '', *(d.get('types') or [])])) for d in c.places]
    items += [dict(t=C.trim_stop(t['title']), u=f"/packages/{t['slug']}/", k='Package', s=f"{t['nights']}N · from {C.inr(t['price_from_inr'])}",
                   x=' '.join([*(t.get('themes') or []), *(c.place_name(p) for p in (t.get('places') or []))])) for t in c.packages]
    items += [dict(t=C.trim_stop(g['title']), u=f"/guides/{g['slug']}/", k='Guide', s=g.get('category'), x=f"{g.get('keyword') or ''} {g.get('description') or ''}") for g in c.guides]
    items += [dict(t=cap(C.THEMES[k]['h1']), u=f'/styles/{k}/', k='Style', s=C.THEMES[k]['name'], x=C.THEMES[k]['desc']) for k in c.themes_with_packages()]
    items += [dict(t=s['name'], u=f'/states/{k}/', k='State', s='State guide', x=s['line']) for k, s in C.STATES.items()]
    items += [dict(t='Permit checker (ILP, PAP)', u='/trip-tools/#permits', k='Tool', s='By state and passport', x='permit ilp pap arunachal nagaland mizoram manipur foreigners inner line'),
              dict(t='Trip budget builder', u='/trip-tools/#budget', k='Tool', s='Estimate costs', x='cost price budget estimate'),
              dict(t='Kaziranga safari planner', u='/trip-tools/#safari', k='Tool', s='Zones and timings', x='kaziranga safari jeep elephant zones booking')]
    return JsonResponse(items, safe=False, json_dumps_params={'ensure_ascii': False, 'separators': (',', ':')})


# ---------- enquiries ----------
def _clip(v, n):
    return str(v or '').strip()[:n]


@require_POST
def enquiry(request):
    try:
        data = json.loads(request.body.decode('utf8') or '{}')
    except ValueError:
        return JsonResponse({'ok': False, 'error': 'Bad request'}, status=400)
    if data.get('company'):  # honeypot: pretend success
        return JsonResponse({'ok': True})
    name, phone = _clip(data.get('name'), 120), _clip(data.get('phone'), 40)
    if not name or len(re.sub(r'\D', '', phone)) < 8:
        return JsonResponse({'ok': False, 'error': 'Please add your name and a full phone or WhatsApp number.'}, status=400)
    email = _clip(data.get('email'), 254)
    if email and not re.match(r'^[^@\s]+@[^@\s]+\.[^@\s]+$', email):
        email = ''
    attr = data.get('attribution')
    e = Enquiry.objects.create(
        source=_clip(data.get('source'), 40), name=name, phone=phone, email=email, month=_clip(data.get('month'), 20), nights=_clip(data.get('nights'), 10),
        pax=_clip(data.get('pax'), 80), states=_clip(data.get('states'), 200), tier=_clip(data.get('tier'), 20), tour=_clip(data.get('tour'), 300),
        message=_clip(data.get('message'), 4000), page=_clip(data.get('page'), 300), page_title=_clip(data.get('page_title'), 300),
        shortlist=_clip(data.get('shortlist'), 500), attribution=attr if isinstance(attr, dict) else None)
    if settings.ENQUIRY_NOTIFY:
        body = '\n'.join(f'{k}: {v}' for k, v in [('Name', e.name), ('Phone', e.phone), ('Email', e.email), ('Month', e.month), ('Nights', e.nights), ('Travellers', e.pax),
                                                  ('States', e.states), ('Hotels', e.tier), ('Package', e.tour), ('Notes', e.message), ('Page', e.page), ('Source', e.source)] if v)
        try:
            send_mail(f'New trip enquiry: {e.name}', body, settings.DEFAULT_FROM_EMAIL, settings.ENQUIRY_NOTIFY, fail_silently=True)
        except Exception:
            pass
    return JsonResponse({'ok': True})
