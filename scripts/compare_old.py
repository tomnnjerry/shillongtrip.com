"""One-off migration check: compare Django output with the old Node build in dist/ (visible text + key structure)."""
import difflib, html, os, re, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shillongtrip.settings')
import django; django.setup()
from django.test import Client
from trips import views

def norm(h):
    h = re.sub(r'<(script|style)[^>]*>.*?</\1>', '', h, flags=re.S)
    h = re.sub(r'<time[^>]*data-checked[^>]*>.*?</time>', 'DATE', h, flags=re.S)
    h = re.sub(r'<link[^>]*>|<meta[^>]*>', '', h)
    h = h.replace('/static/img/', '/img/').replace('/static/assets/', '/assets/')
    h = re.sub(r'\?v=[a-z0-9]+', '', h)
    h = re.sub(r'&#x27;|&#39;', "'", h)
    h = re.sub(r'&quot;', '"', h)
    h = re.sub(r'<!--.*?-->', '', h, flags=re.S)
    t = re.sub(r'<[^>]+>', ' ', h)
    t = html.unescape(t)
    return re.sub(r'\s+', ' ', t).strip()

def tags(h):
    h = re.sub(r'<(script|style)[^>]*>.*?</\1>', '', h, flags=re.S)
    return len(re.findall(r'<a ', h)), len(re.findall(r'<img ', h)), len(re.findall(r'<details', h)), len(re.findall(r'<article', h)), len(re.findall(r'<li[ >]', h))

c = Client()
worst = []
for p, _ in views._sitemap_urls():
    f = ROOT / 'dist' / p.strip('/') / 'index.html'
    if not f.exists():
        print('no old file', p); continue
    old = f.read_text(encoding='utf8'); new = c.get(p).content.decode()
    a, b = norm(old), norm(new)
    r = difflib.SequenceMatcher(None, a, b, autojunk=False).quick_ratio() if len(a) < 400000 else 1
    ta, tb = tags(old), tags(new)
    if a != b or ta != tb:
        worst.append((r, p, ta, tb))
worst.sort()
print(len(worst), 'pages differ')
for r, p, ta, tb in worst[:25]:
    print(f'{r:.4f} {p} old={ta} new={tb}')
