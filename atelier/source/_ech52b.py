import json, re, sys, html, urllib.request, collections
d = json.load(open('projets/sailingmore/stages.json'))
m = [e for e in d['offres'] if not e.get('debut') and not e.get('hors_offre')]
seen = collections.Counter()
for e in m:
    if seen[e['ecole']] >= 1 or e['ecole'] not in sys.argv[1:]: continue
    seen[e['ecole']] += 1
    try:
        r = urllib.request.Request(e['lien'], headers={'User-Agent': 'Mozilla/5.0'})
        t = urllib.request.urlopen(r, timeout=15).read().decode('utf8', 'ignore')
        t = re.sub(r'<(script|style)[\s\S]*?</\1>', ' ', t)
        t = re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', t)))
    except Exception as x:
        print(e['ecole'], e['lien'], 'ERR', x); continue
    print('==', e['ecole'], e['lien'], len(t))
    for mm in list(re.finditer(r'.{50}(2026|2027).{50}', t))[:5]:
        print('   ', mm.group(0))
