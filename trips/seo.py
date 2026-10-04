"""JSON-LD builders and absolute URLs (port of the structured-data helpers in src/lib.mjs)."""
from . import content as C


def abs_url(path):
    return C.get().site['url'].rstrip('/') + path


def org_id():
    return abs_url('/#org')


def img_url(key, w=1600):
    from django.templatetags.static import static
    im = C.get().img(key)
    if not im:
        return abs_url(static('assets/logo.png'))
    width = w if w in im['widths'] else im['widths'][-1]
    return abs_url(f"{static('img/')}{im['id']}-{width}.webp")


def org_ld():
    c = C.get()
    s = c.site
    a = s.get('address') or {}
    from django.templatetags.static import static
    o = {
        '@context': 'https://schema.org', '@type': 'TravelAgency', '@id': org_id(), 'name': s['name'], 'url': abs_url('/'),
        'logo': {'@type': 'ImageObject', 'url': abs_url(static('assets/logo.png')), 'width': 1200, 'height': 300, 'caption': s['name']},
        'image': img_url('_hero-meghalaya'), 'description': s.get('tagline'), 'email': s.get('email'),
        'areaServed': ['Meghalaya', 'Assam', 'Arunachal Pradesh', 'Nagaland', 'Manipur', 'Mizoram', 'Tripura'],
        'address': {'@type': 'PostalAddress', 'addressLocality': a.get('locality'), 'addressRegion': a.get('region'),
                    'postalCode': a.get('postalCode'), 'addressCountry': a.get('country'), **({'streetAddress': a['street']} if a.get('street') else {})},
    }
    if s.get('phone'):
        o['telephone'] = s['phone']
    same = [v for v in (s.get('social') or {}).values() if v]
    if same:
        o['sameAs'] = same
    return o


def website_ld():
    s = C.get().site
    return {'@context': 'https://schema.org', '@type': 'WebSite', 'name': s['name'], 'url': abs_url('/'), 'publisher': {'@id': org_id()}}


def faq_ld(faqs):
    return {'@context': 'https://schema.org', '@type': 'FAQPage',
            'mainEntity': [{'@type': 'Question', 'name': f['q'], 'acceptedAnswer': {'@type': 'Answer', 'text': f['a']}} for f in faqs]}


def crumbs_ld(crumbs):
    return {'@context': 'https://schema.org', '@type': 'BreadcrumbList',
            'itemListElement': [{'@type': 'ListItem', 'position': i + 1, 'name': n, 'item': abs_url(u)} for i, (n, u) in enumerate(crumbs)]}


def item_list_ld(items):
    return {'@context': 'https://schema.org', '@type': 'ItemList',
            'itemListElement': [{'@type': 'ListItem', 'position': i + 1, 'url': abs_url(it['url']), 'name': it['name']} for i, it in enumerate(items)]}
