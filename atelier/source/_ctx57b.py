import json, sys, re, urllib.request, html
slugs = sys.argv[1:]
d = json.load(open('projets/sailingmore/stages.json'))
seen = set()
PAT = re.compile(r'\d[\d.,]*\s?(€|£|EUR|Ft|RON|lei|euro)|(€|£)\s?\d')
for e in d['offres']:
    if e.get('ecole_slug') not in slugs or e.get('prix_eur') not in (None, '', 0) or e.get('hors_offre'):
        continue
    u = e['lien']
    print('==', e['ecole_slug'], '|', e['titre'], '|', u)
    if u in seen:
        continue
    seen.add(u)
    try:
        t = urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'}), timeout=15).read(900000).decode('utf-8', 'replace')
        t = re.sub(r'(?s)<(script|style).*?</\1>', ' ', t)
        t = re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', t)))
    except Exception as x:
        print('   ERR', x); continue
    for m in list(PAT.finditer(t))[:7]:
        print('    ~', t[max(0, m.start()-90):m.end()+20])
