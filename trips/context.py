"""Template context available on every page: site config, nav data, JS config."""
import json
from pathlib import Path

from django.conf import settings

from . import content as C


def _build_id():
    try:
        return format(int(max(f.stat().st_mtime for f in (Path(settings.BASE_DIR) / 'static/assets').glob('app.*'))), 'x')
    except ValueError:
        return '1'


def site(request):
    c = C.get()
    s = c.site
    by_slug = c.pkg_by_slug
    mega_pk = [by_slug[x] for x in ['meghalaya-classic-4n', 'shillong-kaziranga-5n', 'tawang-6n', 'northeast-7n', 'meghalaya-root-bridges-5n', 'hornbill-festival-5n'] if x in by_slug]
    mega_styles = [dict(key=k, **C.THEMES[k]) for k in ['honeymoon', 'family', 'wildlife', 'trekking', 'festival', 'monsoon', 'snow', 'budget']]
    mega_places = [dict(state=st, places=[d for d in c.places if d['state'] == st['key']][:7]) for st in C.STATES.values()]
    pop = [c.guide_by_slug[x] for x in ['places-to-visit-in-meghalaya', 'kaziranga-safari-guide', 'arunachal-ilp-guide', 'meghalaya-trip-cost', 'guwahati-to-shillong',
                                        'best-time-to-visit-meghalaya', 'tawang-travel-guide'] if x in c.guide_by_slug]
    for g in pop:
        g['footer_title'] = C.trim_stop(g['title']).split(':')[0]
    leads = s.get('leads') or {}
    cfg = {'wa': s.get('whatsapp', ''), 'email': s.get('email', ''), 'lead': leads.get('endpoint', ''), 'api': '/api/enquiry/',
           'ga4': (s.get('analytics') or {}).get('ga4', ''),
           'pop': {'delay': leads.get('popupDelaySeconds', 45), 'scroll': leads.get('popupScrollPercent', 60), 'repeat': leads.get('popupRepeatDays', 7)}}
    tel = (s.get('phone') or '').replace(' ', '')
    addr = s.get('address') or {}
    return {
        'site': s, 'STATES': C.STATES, 'THEMES': C.THEMES, 'tel': tel, 'MONTHS_LONG': C.MONTHS_LONG,
        'address_line': ', '.join(x for x in [addr.get('street'), addr.get('locality'), addr.get('region')] if x),
        'mega_pk': mega_pk, 'mega_styles': mega_styles, 'mega_places': mega_places, 'footer_guides': pop,
        'footer_styles': [dict(key=k, name=C.THEMES[k]['name']) for k in ['honeymoon', 'family', 'wildlife', 'festival', 'trekking', 'luxury', 'budget']],
        'st_config': json.dumps(cfg).replace('<', '\u003c'), 'build_id': _build_id(),
    }
