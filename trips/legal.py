"""Policy pages. Text lives in pagedata.json (generated from the old legal.mjs); site-config values are filled in here."""
import html
import json
import re
from pathlib import Path

from django.utils.html import escape
from django.utils.safestring import mark_safe

from . import content as C

_DATA = json.loads((Path(__file__).parent / 'pagedata.json').read_text(encoding='utf8'))
UPDATED = '30 September 2026'
DOT = '·'

SLUGS = {'refund': 'cancellation-refund-policy', 'terms': 'terms', 'privacy': 'privacy', 'cookies': 'cookie-policy', 'disclaimer': 'disclaimer'}


def pagedata():
    return _DATA


def _fill(text):
    s = C.get().site
    co, g, a = s.get('company') or {}, s.get('grievance') or {}, s.get('address') or {}
    e = escape
    contact = f' {DOT} '.join(x for x in [f'<a href="mailto:{e(s["email"])}">{e(s["email"])}</a>', e(s.get('phone') or ''),
                                          e(', '.join(p for p in [a.get('street'), a.get('locality'), a.get('region'), a.get('postalCode')] if p))] if x)
    sentinel_contact = f' {DOT} '.join(['<a href="mailto:@@EMAIL@@">@@EMAIL@@</a>', '@@PHONE@@', '@@STREET@@, @@LOC@@, @@REGION@@, @@PIN@@'])
    text = text.replace(sentinel_contact, contact)
    sentinel_who = '<b>@@GNAME@@</b>, Grievance Officer'
    text = text.replace(sentinel_who, f'<b>{e(g["name"])}</b>, Grievance Officer' if g.get('name') else 'Our Grievance Officer')
    gmail = g.get('email') or s['email']
    how = f' {DOT} '.join(x for x in [f'<a href="mailto:{e(gmail)}">{e(gmail)}</a>', e(g.get('phone') or '')] if x)
    text = text.replace(f'<a href="mailto:@@GEMAIL@@">@@GEMAIL@@</a> {DOT} @@GPHONE@@', how)
    text = text.replace(', registered with the state tourism department (registration @@REG@@)',
                        f', registered with the state tourism department (registration {e(co["tourismRegistration"])})' if co.get('tourismRegistration') else '')
    text = text.replace(', GSTIN @@GSTIN@@', f', GSTIN {e(co["gstin"])}' if co.get('gstin') else '')
    text = text.replace('@@LEGAL@@', e(co.get('legalName') or s['name'])).replace('@@EMAIL@@', e(s['email']))
    return text


def legal_page(key):
    d = _DATA['legal'][key]
    s = C.get().site
    co = s.get('company') or {}
    body = _fill(d['body'])
    toc = [{'id': m.group(1), 'text': html.unescape(m.group(2))} for m in re.finditer(r'<h2 id="([^"]+)">(.*?)</h2>', body)]
    return {'title': html.unescape(d['title']), 'path': d['path'], 'description': html.unescape(d['description']), 'lede': mark_safe(d['lede']),
            'body': mark_safe(body), 'toc': toc, 'updated': UPDATED, 'operator': co.get('legalName') or s['name']}
