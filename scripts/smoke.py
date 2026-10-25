"""Render every sitemap URL with the Django test client; fail on non-200, template errors, bad JSON-LD or heading full stops.
Usage: DJANGO_DEBUG=0 python scripts/smoke.py"""
import json
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shillongtrip.settings')
import django
django.setup()
from django.test import Client
from trips import views

c = Client()
urls = [p for p, _ in views._sitemap_urls()] + ['/sitemap.xml', '/robots.txt', '/ads.txt', '/llms.txt', '/search.json', '/site.webmanifest']
bad, titles, faq_pages = [], {}, 0
for u in urls:
    r = c.get(u)
    if r.status_code != 200:
        bad.append(f'{u} -> {r.status_code}')
        continue
    if not r['Content-Type'].startswith('text/html'):
        continue
    h = r.content.decode()
    h1 = len(re.findall(r'<h1[\s>]', h))
    if h1 != 1:
        bad.append(f'{u}: {h1} h1')
    for m in re.finditer(r'<h([1-3])[^>]*>(.*?)</h\1>', h, re.S):
        t = re.sub(r'<[^>]+>', '', m.group(2)).strip()
        if re.search(r'[^.]\.$', t) and not re.search(r'\b(St|Mt|approx|etc)\.$', t):
            bad.append(f'{u}: heading full stop "{t}"')
    for j in re.findall(r'<script type="application/ld\+json">(.*?)</script>', h, re.S):
        try:
            o = json.loads(j)
            if o.get('@type') == 'FAQPage':
                faq_pages += 1
                if len(o['mainEntity']) != 9 and u != '/faq/':
                    bad.append(f'{u}: {len(o["mainEntity"])} FAQs')
        except ValueError:
            bad.append(f'{u}: bad JSON-LD')
    t = re.search(r'<title>(.*?)</title>', h, re.S).group(1)
    if t in titles:
        bad.append(f'{u}: duplicate title with {titles[t]}')
    titles[t] = u
    if '{{' in h or '{%' in h or re.search(r'="None"', re.sub(r'<script.*?</script>', '', h, flags=re.S)):
        bad.append(f'{u}: unrendered template text or "None"')
r = c.get('/nope-not-here/')
if r.status_code != 404:
    bad.append(f'404 page returned {r.status_code}')
import json as _j
for body, want in [({'name': 'Test', 'phone': '+91 98765 43210', 'month': 'October', 'source': 'smoke', 'attribution': {'first': {'landing': '/'}}}, 200),
                   ({'name': 'Test', 'phone': '123'}, 400), ({'name': 'Bot', 'phone': '9876543210', 'company': 'x'}, 200)]:
    r = c.post('/api/enquiry/', _j.dumps(body), content_type='application/json')
    if r.status_code != want:
        bad.append(f'enquiry {body["phone"]} -> {r.status_code} (wanted {want})')
from trips.models import Enquiry
if Enquiry.objects.filter(source='smoke').count() != 1:
    bad.append('enquiry not stored exactly once')
Enquiry.objects.filter(source='smoke').delete()
print(f'Rendered {len(urls)} URLs, {faq_pages} FAQ blocks.')
print('\n'.join(bad[:60]) if bad else 'All OK')
sys.exit(1 if bad else 0)
