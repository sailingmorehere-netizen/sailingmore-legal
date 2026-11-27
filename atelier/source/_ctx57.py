import json, sys, re, urllib.request, html
slugs = sys.argv[1:]
d = json.load(open('projets/sailingmore/stages.json'))
cache = {}
for e in d['offres']:
    if e.get('ecole_slug') not in slugs or e.get('prix_eur') not in (None, '', 0) or e.get('hors_offre'):
        continue
    u = e['lien']
    if u not in cache:
        try:
            t = urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'}), timeout=15).read(900000).decode('utf-8', 'replace')
            t = re.sub(r'(?s)<(script|style).*?</\1>', ' ', t)
            t = re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', t)))
        except Exception as x:
            t = ''
        cache[u] = t
    t = cache[u]
    key = re.sub(r'\s*[\(–-].*$', '', e['titre'])[:30]
    i = t.find(key)
    print('==', e['ecole_slug'], '|', e['titre'], '|', u)
    print('   ', t[i:i+260] if i >= 0 else '(titre non trouvé)')
