"""Template tags and filters: icons, responsive images, cards, FAQ block, charts (port of src/ui.mjs + src/graphics.mjs)."""
from datetime import date, timedelta
from urllib.parse import quote

from django import template
from django.utils.html import escape, format_html
from django.utils.safestring import mark_safe

from .. import content as C
from ..icons import ICONS, SOCIAL

register = template.Library()


# ---------- filters ----------
@register.filter
def inr(n):
    return C.inr(n)


@register.filter
def num(n):
    return C.indian(n or 0)


@register.filter
def trimstop(s):
    return C.trim_stop(s)


@register.filter
def shortname(s):
    return C.short_name(s)


@register.filter
def placename(slug):
    return C.get().place_name(slug)


@register.filter
def monthslabel(ms):
    return C.months_label(ms)


@register.filter
def cap(s):
    s = str(s)
    return s[:1].upper() + s[1:]


@register.filter
def plus1(n):
    return int(n) + 1


@register.filter
def pad2(n):
    return f'{int(n):02d}'


@register.filter
def urlq(s):
    return quote(str(s), safe="-_.!~*'()")


@register.filter
def hasval(lst, v):
    return v in (lst or [])


@register.filter
def spacejoin(lst):
    return ' '.join(str(x) for x in (lst or []))


@register.filter
def pretty_date(s):
    try:
        d = date.fromisoformat(str(s)[:10])
    except ValueError:
        return s
    return f'{d.day} {C.MONTHS_LONG[d.month - 1]} {d.year}'


@register.filter
def coord(v):
    return f'{float(v):.3f}'


@register.filter
def start_name(s):
    import re
    return re.sub(r'\s*\(.*?\)', '', str(s or 'Guwahati'))


@register.filter
def get_item(d, k):
    return (d or {}).get(k)


# ---------- simple tags ----------
@register.simple_tag
def icon(name, cls=''):
    return format_html(
        '<svg class="ic {}" viewBox="0 0 24 24" aria-hidden="true" focusable="false" fill="none" stroke="currentColor" '
        'stroke-width="2" stroke-linecap="round" stroke-linejoin="round">{}</svg>', cls, mark_safe(ICONS.get(name, '')))


@register.simple_tag
def wa_link(text=''):
    s = C.get().site
    if s.get('whatsapp'):
        return f"https://wa.me/{s['whatsapp']}?text={quote(text)}"
    return '/contact/' + (f'?msg={quote(text)}' if text else '')


@register.simple_tag
def wa_attrs():
    return mark_safe(' rel="noopener" target="_blank"') if C.get().site.get('whatsapp') else ''


@register.simple_tag
def checked_date():
    d = date.today() - timedelta(days=1)
    return format_html('<time data-checked datetime="{}">{} {} {}</time>', d.isoformat(), d.day, C.MONTHS[d.month - 1], d.year)


def _static(path):
    from django.templatetags.static import static
    return static(path)


def _img_url(im, w):
    return f"{_static('img/')}{im['id']}-{w}.webp"


@register.simple_tag
def img(im, sizes='100vw', cls='', eager=False, alt=None):
    if not im:
        return format_html('<span class="img-ph {}" role="img" aria-label="{}"></span>', cls, alt or 'Photo coming soon')
    widths = im['widths']
    srcset = ', '.join(f'{_img_url(im, w)} {w}w' for w in widths)
    mid = 960 if 960 in widths else widths[-1]
    h = round(im['h'] * (mid / im['w']))
    a = im['alt'] if alt is None else alt
    return format_html(
        '<img class="{}" src="{}" srcset="{}" sizes="{}" width="{}" height="{}" alt="{}"{}{} decoding="async">',
        cls, _img_url(im, mid), srcset, sizes, mid, h, a,
        mark_safe(' role="presentation"') if a == '' else '',
        mark_safe(' fetchpriority="high"') if eager else mark_safe(' loading="lazy"'))


@register.simple_tag
def credit(im):
    if not im:
        return ''
    who = format_html('<a href="{}" rel="noopener nofollow" target="_blank">{}</a>', im['author_url'], im['author']) if im.get('author_url') else escape(im['author'])
    return format_html('<small class="cr">{} · <a href="{}" rel="noopener" target="_blank">Commons</a> · <a href="{}" rel="noopener license" target="_blank">{}</a></small>',
                       who, im['source'], im['license_url'], im['license'])


@register.simple_tag
def img_of(key):
    return C.get().img(key)


@register.simple_tag
def images_of(key):
    return C.get().images_for(key)


@register.simple_tag
def logo_img(white=False, h=44):
    c = C.get()
    w = round(c.logo['width'] / c.logo['height'] * h)
    name = c.site['name']

    def tag(src, cls, alt):
        return format_html('<img class="brand__img {}" src="{}" alt="{}" width="{}" height="{}" decoding="async"{}>',
                           cls, _static(src), alt, w, h, '' if alt else mark_safe(' role="presentation"'))
    if white:
        return tag('assets/logo-white.svg', '', f'{name} logo')
    return tag('assets/logo.svg', 'brand__img--on-light', f'{name} logo') + tag('assets/logo-white.svg', 'brand__img--on-dark', '')


@register.simple_tag
def socials(cls=''):
    social = C.get().site.get('social') or {}
    items = []
    for k, (label, p) in SOCIAL.items():
        url = social.get(k) or ''
        attrs = mark_safe(' rel="noopener me" target="_blank"') if url else mark_safe(' data-social-empty')
        items.append(format_html(
            '<li><a href="{}"{} aria-label="{}"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" '
            'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{}</svg></a></li>', url or '#', attrs, label, mark_safe(p)))
    return format_html('<ul class="soc {}">{}</ul>', cls, mark_safe(''.join(items)))


@register.simple_tag
def state_chip(key):
    s = C.STATES.get(key)
    return format_html('<span class="chip-st" style="--c:{}">{}</span>', s['color'] if s else '', s['short'] if s else key)


@register.simple_tag
def month_pills(best):
    best = best or []
    spans = ''.join(format_html('<span class="{}">{}</span>', 'on' if i + 1 in best else '', m[0]) for i, m in enumerate(C.MONTHS))
    return format_html('<div class="mpills" role="img" aria-label="Best months: {}">{}</div>', C.months_label(best), mark_safe(spans))


@register.simple_tag
def preload_link(im):
    if not im:
        return ''
    ss = ', '.join(f'{_img_url(im, w)} {w}w' for w in im['widths'])
    return format_html('<link rel="preload" as="image" imagesrcset="{}" imagesizes="100vw" fetchpriority="high">', ss)


# ---------- inclusion tags ----------
@register.inclusion_tag('trips/c/crumbs.html')
def crumbs(items):
    return {'items': items}


@register.inclusion_tag('trips/c/faq.html')
def faq_block(faqs, title='Frequently asked questions', id='faq', intro=''):
    return {'faqs': faqs or [], 'title': C.trim_stop(title), 'id': id, 'intro': intro}


@register.inclusion_tag('trips/c/pk_card.html')
def pk_card(t, eager=False):
    c = C.get()
    places = t.get('places') or []
    return {'t': t, 'im': c.img(t.get('hero') or (places[0] if places else '')), 'stops': [C.short_name(c.place_name(s)) for s in places[:5]],
            'more': len(places) - 5 if len(places) > 5 else 0, 'f': c.foreign_status(t), 'eager': eager}


@register.inclusion_tag('trips/c/place_card.html')
def place_card(d, size=''):
    return {'d': d, 'im': C.get().img(d['slug']), 'size': size}


@register.inclusion_tag('trips/c/guide_card.html')
def guide_card(g, big=False):
    places = g.get('places') or []
    return {'g': g, 'im': C.get().img(places[0] if places else '_hero-meghalaya'), 'big': big}


@register.inclusion_tag('trips/c/cta.html')
def cta_panel(title='Tell us your dates, we’ll plan the route',
              text='Share when you’re travelling and who’s coming. A planner replies with a day-by-day route, hotel options and a clear price, usually within a working day.',
              img='_hero-meghalaya', msg='Hi, I would like help planning a Northeast trip.'):
    return {'title': C.trim_stop(title), 'text': text, 'im': C.get().img(img), 'msg': msg}


@register.inclusion_tag('trips/c/lead_form.html')
def lead_form(source, title='Get a free trip plan', compact=False, cls=''):
    return {'source': source, 'title': title, 'compact': compact, 'cls': cls, 'months': C.MONTHS_LONG}


# ---------- charts ----------
@register.simple_tag
def route_stepper(t):
    stops = []
    for d in t.get('itinerary') or []:
        if stops and stops[-1]['stay'] == d.get('stay'):
            stops[-1]['nights'] += 1
            stops[-1]['days'].append(d['day'])
            continue
        stops.append({'stay': d.get('stay') or '—', 'alt': int(d.get('altitude_m') or 0), 'nights': 1, 'days': [d['day']]})
    if len(stops) < 2:
        return ''
    top = max([t.get('max_altitude_m') or 0, 1000] + [s['alt'] for s in stops])
    out = ['<div class="rs" role="list" aria-label="Route and overnight altitude">']
    for i, s in enumerate(stops):
        h = max(6, round(s['alt'] / top * 100))
        if i < len(stops) - 1 or s['nights'] > 1:
            days = f"Days {s['days'][0]}–{s['days'][-1]}" if len(s['days']) > 1 else f"Day {s['days'][0]}"
        else:
            days = f"Day {s['days'][0]}"
        alt = f"{C.indian(s['alt'])} m" if s['alt'] else ''
        out.append(format_html(
            '<div class="rs__stop" role="listitem" style="--h:{}%"><span class="rs__bar"><span></span></span><span class="rs__dot"></span>'
            '<b class="rs__name">{}</b><small class="rs__info">{} · {}</small></div>', h, s['stay'], alt, days))
    out.append('</div>')
    if t.get('max_altitude_m'):
        out.append(format_html('<p class="rs__peak">Highest point on this trip: <b>{} m</b></p>', C.indian(t['max_altitude_m'])))
    return mark_safe(''.join(str(x) for x in out))


HEAT_PICK = ['shillong', 'sohra', 'nongriat-root-bridges', 'dawki-umngot', 'mawlynnong', 'kaziranga', 'majuli', 'manas', 'tawang', 'sela-pass',
             'ziro-valley', 'mechuka', 'kohima', 'dzukou-valley', 'loktak-lake']


@register.simple_tag
def heatmap(id='heat'):
    c = C.get()
    rows = [c.place_by_slug[s] for s in HEAT_PICK if s in c.place_by_slug]
    if not rows:
        return ''
    head = ''.join(format_html('<th scope="col"><button type="button" data-heat-m="{}" aria-label="{}">{}</button></th>', i + 1, C.MONTHS_LONG[i], m)
                   for i, m in enumerate(C.MONTHS))
    body = ''
    for d in rows:
        cells = ''
        for i in range(12):
            on = (i + 1) in (d.get('best_months') or [])
            cells += format_html('<td class="{}" data-m="{}"><span class="sr">{}: {}</span></td>', 'on' if on else '', i + 1, C.MONTHS_LONG[i], 'good' if on else 'not ideal')
        body += format_html('<tr><th scope="row"><a href="/places/{}/"><i style="background:{}"></i>{}</a></th>{}</tr>',
                            d['slug'], C.STATES[d['state']]['color'], C.short_name(d['name']), mark_safe(cells))
    return format_html(
        '<div class="heat" id="{}" data-heat><div class="tbl tbl--heat" tabindex="0"><table><caption class="sr">Best months to visit each place</caption>'
        '<thead><tr><th scope="col">Place</th>{}</tr></thead><tbody>{}</tbody></table></div>'
        '<p class="heat__key"><span class="on"></span> Best months <span></span> Possible, with trade-offs</p></div>', id, mark_safe(head), mark_safe(body))


STATION_FOR = {
    'meghalaya': lambda d: 'sohra' if d['slug'] in ['sohra', 'nohkalikai-falls', 'mawsmai-cave', 'nongriat-root-bridges', 'wei-sawdong-falls', 'mawsynram', 'laitlum-canyons'] else 'shillong',
    'assam': lambda d: 'kaziranga' if d['slug'] in ['kaziranga', 'nameri', 'tezpur', 'jorhat', 'majuli', 'sivasagar', 'dibrugarh', 'dibru-saikhowa'] else 'guwahati',
    'arunachal': lambda d: 'ziro' if d['slug'] in ['ziro-valley', 'itanagar', 'pasighat', 'mechuka', 'namdapha', 'roing-mayodia'] else 'tawang',
    'northeast': lambda d: 'kohima',
}


def station_for(d):
    f = STATION_FOR.get(d.get('state'))
    return f(d) if f else 'shillong'


@register.simple_tag
def rain_meter(station_key, title=''):
    clim = C.get().climate or {}
    st = (clim.get('stations') or {}).get(station_key)
    if not st or not st.get('rain_mm'):
        return ''
    rain = st['rain_mm']
    mx, total = max(rain), sum(rain)
    cols = ''
    for i, mm in enumerate(rain):
        temp = st.get('temp')
        label = f"{C.MONTHS_LONG[i]}: about {C.indian(mm)} mm" + (f', {temp[i]}' if temp else '')
        cols += format_html(
            '<div class="rain__col" tabindex="0" style="--h:{}%" aria-label="{}"><span class="rain__v">{}</span><span class="rain__bar"></span>'
            '<span class="rain__m">{}</span>{}</div>',
            f'{max(2, mm / mx * 100):.1f}', label, C.indian(mm), C.MONTHS[i][0], format_html('<span class="rain__t">{}</span>', temp[i]) if temp else '')
    src = format_html('<p class="rain__src">Source: <a href="{}" rel="noopener" target="_blank">{}</a></p>', st['source'], st.get('source_name') or 'climate normals') if st.get('source') else ''
    return format_html(
        '<figure class="rain" data-rain><figcaption><b>{}</b><span>About {} mm a year · approximate monthly averages</span></figcaption>'
        '<div class="rain__bars">{}</div>{}</figure>',
        title or f"Rain meter: {st['name']}", C.indian(round(total / 10) * 10), mark_safe(cols), src)


@register.simple_tag
def station_rain(d):
    return rain_meter(station_for(d))


@register.simple_tag
def json_script_ld(obj):
    import json
    return mark_safe('<script type="application/ld+json">' + json.dumps(obj, ensure_ascii=False, separators=(',', ':')).replace('<', '\\u003c') + '</script>')
