"""In-memory content catalogue: content/*.json and content/guides/*.md (port of src/lib.mjs).

No database for content. In DEBUG the catalogue is rebuilt when any content file changes.
"""
import html
import json
import re
from datetime import date, datetime
from pathlib import Path

import markdown
import yaml
from django.conf import settings
from django.utils.safestring import mark_safe

MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
MONTHS_LONG = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

STATES = {
    'meghalaya': dict(key='meghalaya', name='Meghalaya', short='Meghalaya', hub='Shillong', hero='laitlum-canyons', color='var(--st-meg)',
                      title='Meghalaya Tour Packages & Places: Shillong, Sohra, Dawki',
                      line='Waterfalls, living root bridges and the clearest river in India, three hours from Guwahati.'),
    'assam': dict(key='assam', name='Assam', short='Assam', hub='Guwahati', hero='kaziranga', color='var(--st-asm)',
                  title='Assam Tours: Kaziranga, Majuli, Guwahati and Tea Country',
                  line='One-horned rhinos, river islands on the Brahmaputra and tea bungalows older than the roads.'),
    'arunachal': dict(key='arunachal', name='Arunachal Pradesh', short='Arunachal', hub='Tawang', hero='tawang-monastery', color='var(--st-aru)',
                      title='Arunachal Tour Packages: Tawang, Ziro, Mechuka',
                      line='High passes, a 17th-century monastery and valleys where the road ends at the Chinese border.'),
    'northeast': dict(key='northeast', name='More Northeast', short='Nagaland & more', hub='Kohima', hero='dzukou-valley', color='var(--st-ne)',
                      title='Nagaland, Manipur, Mizoram and Tripura Tours',
                      line='Hornbill in Kohima, floating islands on Loktak and rock carvings at Unakoti.'),
}

THEMES = {
    'honeymoon': dict(name='Honeymoon', icon='heart', h1='Meghalaya and Northeast honeymoon packages', desc='Lake-view rooms, private cars and days paced for two.'),
    'family': dict(name='Family', icon='users', h1='Northeast family tour packages', desc='Short drives, easy walks and safaris the kids will talk about.'),
    'wildlife': dict(name='Wildlife', icon='paw', h1='Kaziranga and Northeast wildlife tours', desc='Rhinos, elephants, hoolock gibbons and more than 450 bird species.'),
    'adventure': dict(name='Adventure', icon='bolt', h1='Northeast adventure tours', desc='High passes, caves, canyons and river camps.'),
    'trekking': dict(name='Treks', icon='boot', h1='Meghalaya and Nagaland treks', desc='Root-bridge trails, Dzukou Valley and village walks.'),
    'culture': dict(name='Culture', icon='drum', h1='Northeast culture tours', desc='Satras, monasteries, living traditions and village stays.'),
    'festival': dict(name='Festivals', icon='spark', h1='Northeast festival tours', desc='Hornbill, Ziro Festival of Music, Bihu and more, timed right.'),
    'offbeat': dict(name='Offbeat', icon='compass', h1='Offbeat Northeast tours', desc='Jaintia hills, Mechuka, Garo hills and places tour buses skip.'),
    'monsoon': dict(name='Monsoon', icon='rain', h1='Monsoon Meghalaya tours', desc='The wettest places on Earth, when the falls are at full roar.'),
    'snow': dict(name='Snow', icon='snow', h1='Tawang and Sela snow tours', desc='Frozen lakes and snow on the passes between December and March.'),
    'luxury': dict(name='Luxury', icon='star', h1='Luxury Northeast tours', desc='The best resorts, tea bungalows and private guides.'),
    'budget': dict(name='Budget', icon='wallet', h1='Budget Meghalaya and Northeast tours', desc='Clean homestays and shared costs without missing the best bits.'),
    'photography': dict(name='Photography', icon='camera', h1='Northeast photography tours', desc='Routes timed for mist, light and the dry-season clear water.'),
    'tea': dict(name='Tea', icon='leaf', h1='Assam tea garden tours', desc='Bungalow stays, plucking seasons and factory visits.'),
    'short-break': dict(name='Short break', icon='clock', h1='Short Shillong and Kaziranga trips', desc='Two to four nights that still feel like a proper trip.'),
    'seniors': dict(name='Seniors', icon='chair', h1='Northeast tours for senior citizens', desc='Easy pacing, fewer steps and comfortable cars.'),
    'solo': dict(name='Solo', icon='user', h1='Solo trips to Meghalaya and the Northeast', desc='Routes and stays that work for one.'),
    'international': dict(name='International', icon='globe', h1='Northeast India tours for foreign nationals', desc='Routes that work with permit rules for non-Indian passports.'),
}

MONTH_NOTES = [
    'Cool, dry and clear. Kaziranga in full season; snow on Sela and around Tawang.',
    'Dry and crisp. Good for Meghalaya treks; Losar and Torgya in Tawang in some years.',
    'Warming up. Rhododendrons start in Arunachal; clear water at Dawki.',
    'Rongali Bihu in Assam. Pre-monsoon storms begin in Meghalaya.',
    'Hot in the plains, pleasant in Shillong. Kaziranga usually closes for the season.',
    'Monsoon arrives. Waterfalls at full roar; Dawki turns muddy; treks get slippery.',
    'Peak rain in Sohra and Mawsynram. Beautiful, wet and prone to landslides.',
    'Wet and green. Behdienkhlam (July) and monsoon tours; Kaziranga closed.',
    'Rain eases late in the month. Ziro Festival of Music in Arunachal.',
    'Clear skies return. Durga Puja crowds; Kaziranga reopens in phases.',
    'The best all-round month: dry trails, clear rivers, Wangala in Garo Hills, Cherry Blossom in Shillong.',
    'Hornbill Festival 1–10 Dec in Kohima. Cold nights in Shillong and Tawang.',
]

FOREIGN_NO = {'bum-la-pass': 'Bum La', 'madhuri-lake': 'Madhuri Lake'}
STATE_FALLBACK = {'meghalaya': 'shillong', 'assam': 'kaziranga', 'arunachal': 'tawang', 'northeast': 'kohima'}


# ---------- helpers ----------
def trim_stop(s):
    return re.sub(r'[.\s]+$', '', str(s or ''))


def indian(n):
    """Indian digit grouping: 1,23,456."""
    n = int(round(float(n)))
    neg = n < 0
    s = str(abs(n))
    if len(s) > 3:
        head, tail = s[:-3], s[-3:]
        parts = []
        while len(head) > 2:
            parts.insert(0, head[-2:])
            head = head[:-2]
        if head:
            parts.insert(0, head)
        s = ','.join(parts + [tail])
    return ('-' if neg else '') + s


def inr(n):
    return '₹' + indian(n)


def short_name(n):
    n = re.sub(r'\s*\(.*?\)', '', str(n))
    return re.sub(r' and the .*', '', n)


def months_label(ms):
    if not ms or len(ms) == 12:
        return 'Year-round'
    s = sorted(set(ms))
    runs, start, prev = [], s[0], s[0]
    for m in s[1:] + [99]:
        if m == prev + 1:
            prev = m
            continue
        runs.append([start, prev])
        start = prev = m
    if len(runs) > 1 and runs[0][0] == 1 and runs[-1][1] == 12:
        first = runs.pop(0)
        runs[-1][1] = first[1]
    return ', '.join(MONTHS[a - 1] if a == b else f'{MONTHS[a - 1]}–{MONTHS[b - 1]}' for a, b in runs)


def slugify(s):
    s = re.sub(r'<[^>]+>', '', str(s).lower())
    s = re.sub(r'&[a-z]+;', '', s)
    return re.sub(r'^-|-$', '', re.sub(r'[^a-z0-9]+', '-', s))


def site_url(path=''):
    return get().site['url'].rstrip('/') + path


# ---------- loading ----------
def _read_json(p, fallback=None):
    try:
        return json.loads(Path(p).read_text(encoding='utf8'))
    except Exception:
        return fallback


def _md_to_html(md_text):
    """Markdown -> (html, toc) with trimmed-stop headings, ids, scrollable tables, external links in new tab."""
    md_text = re.sub(r'^#\s.+\n', '', md_text, count=1)
    # CommonMark lets a list start right after a paragraph line; Python-Markdown needs a blank line first.
    lines, out, in_fence = md_text.split('\n'), [], False
    for ln in lines:
        if ln.lstrip().startswith('```'):
            in_fence = not in_fence
        starts_list = not in_fence and re.match(r'^\s{0,3}([-*+]|\d+[.)])\s+\S', ln)
        if starts_list and out and out[-1].strip() and not re.match(r'^\s*([-*+]|\d+[.)])\s+\S', out[-1]) and not out[-1].startswith((' ', '\t')):
            out.append('')
        out.append(ln)
    md_text = '\n'.join(out)
    body = markdown.markdown(md_text, extensions=['tables', 'sane_lists', 'fenced_code'])
    toc = []

    def head(m):
        depth = max(2, int(m.group(1)))
        text = trim_stop(m.group(2))
        hid = slugify(text)
        if int(m.group(1)) == 2:
            toc.append({'id': hid, 'text': mark_safe(text)})
        return f'<h{depth} id="{hid}">{text}</h{depth}>'

    body = re.sub(r'<h([1-6])>(.*?)</h\1>', head, body, flags=re.S)
    base = get().site.get('url', '')

    def link(m):
        href = m.group(1)
        ext = re.match(r'https?://', href) and not href.startswith(base)
        return m.group(0) if not ext else m.group(0).replace('<a ', '<a rel="noopener" target="_blank" ', 1)

    body = re.sub(r'<a href="([^"]*)"[^>]*>', link, body)
    body = body.replace('<table>', '<div class="tbl" tabindex="0"><table>').replace('</table>', '</table></div>')
    return mark_safe(body), toc


class Catalogue:
    def __init__(self):
        c = Path(settings.CONTENT_DIR)
        self.site = _read_json(settings.SITE_CONFIG, {})
        self.plan = _read_json(c / '_plan.json', {})
        self.images = _read_json(c / 'images.generated.json', {})
        self.permits = _read_json(c / 'permits.json')
        self.climate = _read_json(c / 'climate.json')
        self.kaziranga = _read_json(c / 'kaziranga.json')
        self.logo = _read_json(Path(settings.BASE_DIR) / 'static/assets/logo.json', {'width': 240, 'height': 60})

        plan_places = [dict(slug=s, name=n, state=st) for st, lst in (self.plan.get('places') or {}).items() for s, n in lst]
        place_order = {d['slug']: i for i, d in enumerate(plan_places)}
        pkg_order = {t[0]: i for i, t in enumerate(self.plan.get('packages') or [])}
        guide_order = {b[0]: i for i, b in enumerate(self.plan.get('guides') or [])}
        self._plan_places = {d['slug']: d for d in plan_places}

        places = [_read_json(f) for f in sorted((c / 'places').glob('*.json')) if not f.name.startswith('_')]
        self.places = sorted([d for d in places if d and d.get('slug') in place_order], key=lambda d: place_order[d['slug']])

        pk = [_read_json(f) for f in sorted((c / 'packages').glob('*.json')) if not f.name.startswith('_')]
        pk = [t for t in pk if t and t.get('slug') in pkg_order]
        for t in pk:
            it = t.get('itinerary')
            t['itinerary'] = it if isinstance(it, list) else (t.get('days') if isinstance(t.get('days'), list) else [])
            t['nights1'] = t['nights'] + 1
            t['title_clean'] = trim_stop(t['title'])
        self.packages = sorted(pk, key=lambda t: pkg_order[t['slug']])

        guides = []
        for f in sorted((c / 'guides').glob('*.md')):
            if f.name.startswith('_'):
                continue
            raw = f.read_text(encoding='utf8')
            m = re.match(r'^---\s*\n(.*?)\n---\s*\n(.*)$', raw, re.S)
            if not m:
                continue
            data = yaml.safe_load(m.group(1)) or {}
            for k in ('date', 'updated'):
                if isinstance(data.get(k), (date, datetime)):
                    data[k] = data[k].isoformat()[:10]
            data['body'] = m.group(2)
            if data.get('slug') in guide_order:
                data['title_clean'] = trim_stop(data.get('title'))
                guides.append(data)
        self.guides = sorted(guides, key=lambda g: str(g.get('date')), reverse=True)

        for d in self.places:
            d['state_info'] = STATES.get(d['state'])
        self.place_by_slug = {d['slug']: d for d in self.places}
        self.pkg_by_slug = {t['slug']: t for t in self.packages}
        self.guide_by_slug = {g['slug']: g for g in self.guides}

    # --- lookups ---
    def place_name(self, slug):
        return (self.place_by_slug.get(slug) or self._plan_places.get(slug) or {}).get('name', slug)

    def place_state(self, slug):
        return (self.place_by_slug.get(slug) or self._plan_places.get(slug) or {}).get('state')

    def packages_for(self, slug):
        return [t for t in self.packages if slug in (t.get('places') or [])]

    def images_for(self, key):
        if self.images.get(key):
            return self.images[key]
        st = self.place_state(key)
        if st and self.images.get(STATE_FALLBACK.get(st)):
            return self.images[STATE_FALLBACK[st]]
        return self.images.get('_hero-meghalaya', [])

    def img(self, key):
        lst = self.images_for(key)
        return lst[0] if lst else None

    def foreign_status(self, t):
        no = [FOREIGN_NO[s] for s in (t.get('places') or []) if s in FOREIGN_NO]
        return {'ok': not no, 'no': no}

    def in_theme(self, t, k):
        if k == 'international':
            return self.foreign_status(t)['ok'] and 'northeast' not in (t.get('states') or [])
        return k in (t.get('themes') or [])

    def themes_with_packages(self):
        return [k for k in THEMES if any(self.in_theme(t, k) for t in self.packages)]


_cat = None
_stamp = None


def _stamp_now():
    c = Path(settings.CONTENT_DIR)
    fs = [settings.SITE_CONFIG, *c.glob('*.json'), *c.glob('*/*.json'), *c.glob('guides/*.md')]
    return max((f.stat().st_mtime for f in fs), default=0), len(fs)


def get():
    """Return the catalogue; in DEBUG rebuild it when content files change."""
    global _cat, _stamp
    if _cat is None:
        _cat, _stamp = Catalogue(), _stamp_now()
    elif settings.DEBUG:
        s = _stamp_now()
        if s != _stamp:
            _cat, _stamp = Catalogue(), s
    return _cat


def render_markdown(md_text):
    return _md_to_html(md_text)


def word_count(s):
    return len(str(s or '').split())
