import json, re, urllib.request, html, sys
o = json.load(open('projets/sailingmore/stages.json'))['offres']
for e in o:
    if e['ecole_slug'] == sys.argv[1] and not e.get('niveau'):
        print(e['titre'][:80], '|', e['lien'])
for u in sys.argv[2:]:
    print('#####', u)
    t = urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'}), timeout=30).read().decode('utf8', 'ignore')
    t = re.sub(r'(?s)<(script|style).*?</\1>', ' ', t)
    t = re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', t)))
    for m in re.finditer(r'(?i)beginner|niveau|ervaring|gevorderd|level', t):
        print('..', t[max(0, m.start()-100):m.end()+140])
