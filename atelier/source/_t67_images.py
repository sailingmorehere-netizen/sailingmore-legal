"""Tâche 67 : og:image de la page `lien` (sinon page d'accueil de la même école) -> stages-img/<hash> -> stages.json.
Lecture seule du réseau. Jamais d'image d'une autre école."""
import json, os, re, hashlib, urllib.request, urllib.parse
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
F = R + '/projets/sailingmore/stages.json'
D = R + '/projets/sailingmore/site/stages-img/'
UA = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:120.0) Gecko/20100101 Firefox/120.0', 'Accept': '*/*'}
CIN = ('debirt', 'rueckenwind', 'weber', 'zeezeil', 'plasmenai')
raw = open(F, encoding='utf-8').read()
d = json.loads(raw)
L = d['offres']


def get(u, binaire=False):
    b = urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=20).read(6_000_000)
    return b if binaire else b.decode('utf-8', 'replace')


def og(html, base):
    for p in (r'<meta[^>]+property=["\']og:image(?::secure_url)?["\'][^>]+content=["\']([^"\']+)',
              r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+property=["\']og:image',
              r'<meta[^>]+name=["\']twitter:image["\'][^>]+content=["\']([^"\']+)'):
        m = re.search(p, html, re.I)
        if m:
            return urllib.parse.urljoin(base, m.group(1).replace('&amp;', '&'))
    # repli : première image de contenu (jpg/webp), hors logos, icônes, drapeaux, captures
    for src in re.findall(r'<img[^>]+src=["\']([^"\']+)', html, re.I):
        s = src.lower().split('?')[0]
        if s.endswith(('.jpg', '.jpeg', '.webp')) and not any(w in s for w in ('logo', 'icon', 'flag', 'screenshot', 'avatar', 'plus')):
            return urllib.parse.urljoin(base, src.replace('&amp;', '&'))


def telecharge(img):
    if 'logo' in img.lower() or 'plus.png' in img:
        return None
    nom0 = hashlib.sha256(img.encode()).hexdigest()[:16]
    for ext in ('.jpg', '.png', '.webp'):
        if os.path.exists(D + nom0 + ext):
            return 'stages-img/' + nom0 + ext
    b = get(img, True)
    if len(b) < 3000:
        return None
    if b[:3] == b'\xff\xd8\xff':
        ext = '.jpg'
    elif b[:4] == b'\x89PNG':
        ext = '.png'
    elif b[:4] == b'RIFF':
        ext = '.webp'
    else:
        return None
    open(D + nom0 + ext, 'wb').write(b)
    return 'stages-img/' + nom0 + ext


cache = {}


def image_de(u):
    if u not in cache:
        try:
            i = og(get(u), u)
            cache[u] = telecharge(i) if i else None
        except Exception as e:
            print('  échec', u, str(e)[:60])
            cache[u] = None
    return cache[u]


for s in CIN:
    S = [e for e in L if e['ecole_slug'] == s and not e.get('image')]
    propre = 0
    for e in S:
        im = image_de(e['lien'])
        if im:
            e['image'] = im
            propre += 1
    # repli : page d'accueil de l'école, puis image déjà obtenue pour cette école
    reste = [e for e in S if not e.get('image')]
    if reste:
        p = urllib.parse.urlparse(reste[0]['lien'])
        im = image_de(p.scheme + '://' + p.netloc + '/')
        if not im:
            c = [e['image'] for e in S if e.get('image')]
            im = max(set(c), key=c.count) if c else None
        for e in reste:
            if im:
                e['image'] = im
    print(s, 'propre', propre, 'repli', len(reste), 'restent', sum(1 for e in S if not e.get('image')))

sep = (',', ':') if ', ' not in raw[:300] and ': ' not in raw[:300] else None
json.dump(d, open(F, 'w', encoding='utf-8'), ensure_ascii=False, separators=sep, indent=None if sep else 2)
print('total sans image', sum(1 for e in L if not e.get('image')))
