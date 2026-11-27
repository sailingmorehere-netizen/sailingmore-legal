import json, sys, re, urllib.request, html
from concurrent.futures import ThreadPoolExecutor
SKIP = ('debirt', 'tiptop', 'uksa', 'solentboat')
d = json.load(open('projets/sailingmore/stages.json'))
cands = [e for e in d['offres'] if e.get('prix_eur') in (None, '', 0) and e.get('ecole_slug') not in SKIP and not e.get('hors_offre')]
PAT = re.compile(r'(£|€|EUR|HUF|RON|Ft|lei)\s?\d[\d.,\s]*|\d[\d.,]*\s?(€|£|euro|EUR|Ft|HUF|RON|lei)')

def get(e):
    u = e['lien']
    try:
        r = urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'}), timeout=15)
        t = r.read(600000).decode('utf-8', 'replace')
    except Exception as x:
        return e, None
    t = re.sub(r'(?s)<(script|style).*?</\1>', ' ', t)
    t = html.unescape(re.sub(r'<[^>]+>', ' ', t))
    t = re.sub(r'\s+', ' ', t)
    return e, [t[max(0, m.start()-60):m.end()+30] for m in PAT.finditer(t)][:3]

with ThreadPoolExecutor(12) as ex:
    for e, h in ex.map(get, cands):
        if h:
            print('==', e['ecole_slug'], '|', e['titre'][:50], '|', e['lien'])
            for x in h:
                print('    ', x)
print(len(cands), 'candidats')
