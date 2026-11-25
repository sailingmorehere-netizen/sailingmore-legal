"""Lecture seule du réseau : og:image de la page d'une école sans visuel -> stages-img/<hash>.jpg -> toutes ses offres.
Puis repli : école ayant déjà une image -> offres sans image (même école)."""
import json, os, re, hashlib, collections, urllib.request, urllib.parse
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
F = R + '/projets/sailingmore/site/stages-proches.json'
D = R + '/projets/sailingmore/site/stages-img/'
raw = open(F).read()
d = json.loads(raw)
o = d['o']
UA = {'User-Agent': 'Mozilla/5.0 (compatible; lecture)'}


def get(u, bin=False):
    r = urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=20)
    b = r.read(6_000_000)
    return b if bin else b.decode('utf-8', 'replace')


def og(html, base):
    for p in (r'<meta[^>]+property=["\']og:image(?::secure_url)?["\'][^>]+content=["\']([^"\']+)',
              r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+property=["\']og:image',
              r'<meta[^>]+name=["\']twitter:image["\'][^>]+content=["\']([^"\']+)',
              r'<img[^>]+src=["\']([^"\']+\.(?:jpe?g|webp|png))["\']'):
        m = re.search(p, html, re.I)
        if m:
            return urllib.parse.urljoin(base, m.group(1).replace('&amp;', '&'))
    return None


have = {x[4] for x in o if x[11]}
for ecole in sorted({x[4] for x in o if not x[11]} - have):
    try:
        offre = next(x for x in o if x[4] == ecole)
        img = None
        p = urllib.parse.urlparse(offre[10])
        for u in (offre[10], p.scheme + '://' + p.netloc + '/'):
            try:
                img = og(get(u), u)
            except Exception as e:
                print('  page', u, e); continue
            if img and 'plus.png' not in img and 'logo' not in img.lower():
                break
            img = None
        if not img:
            print('pas d\'image', ecole); continue
        b = get(img, True)
        if len(b) < 3000 or b[:4] not in (b'\xff\xd8\xff\xe0', b'\xff\xd8\xff\xe1', b'\xff\xd8\xff\xdb', b'\x89PNG', b'RIFF'):
            if not b[:3] == b'\xff\xd8\xff':
                print('format refusé', ecole, img); continue
        ext = '.jpg' if b[:2] == b'\xff\xd8' else ('.png' if b[:4] == b'\x89PNG' else '.webp')
        nom = hashlib.sha256(img.encode()).hexdigest()[:16] + ext
        open(D + nom, 'wb').write(b)
        for x in o:
            if x[4] == ecole and not x[11]:
                x[11] = 'stages-img/' + nom
        print('ok', ecole, img, len(b))
    except Exception as e:
        print('échec', ecole, e)

by = collections.defaultdict(collections.Counter)
for x in o:
    if x[11]:
        by[x[4]][x[11]] += 1
n = 0
for x in o:
    if not x[11] and by[x[4]]:
        x[11] = by[x[4]].most_common(1)[0][0]; n += 1
print('repli école', n)
sep = (',', ':') if ', ' not in raw[:200] and ': ' not in raw[:200] else None
json.dump(d, open(F, 'w'), ensure_ascii=False, separators=sep)
print('restent', sum(1 for x in o if not x[11]))
