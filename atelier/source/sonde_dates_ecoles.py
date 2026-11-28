#!/usr/bin/env python3
# © 2026 Sailing More — tous droits réservés. All rights reserved.
"""Sonde (lecture seule) : une page par école sans debut, extraits contenant une année 2026/2027."""
import json, re, html, urllib.request, collections, concurrent.futures as cf
o = json.load(open('projets/sailingmore/stages.json'))['offres']
m = [e for e in o if not e.get('debut') and not e.get('hors_offre')]
par = collections.OrderedDict()
for e in m:
    par.setdefault(e['ecole_slug'], []).append(e)
def texte(u):
    r = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'})
    t = urllib.request.urlopen(r, timeout=15).read().decode('utf8', 'ignore')
    t = re.sub(r'<(script|style)[\s\S]*?</\1>', ' ', t)
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', t)))
def f(item):
    s, L = item
    try:
        t = texte(L[0]['lien'])
    except Exception as x:
        return s, len(L), 'ERR ' + str(x)[:40]
    ex = [t[max(0, k.start() - 40):k.end() + 20] for k in re.finditer(r'\b(2026|2027)\b', t)][:3]
    return s, len(L), ' || '.join(ex)
with cf.ThreadPoolExecutor(8) as ex:
    for s, n, r in ex.map(f, list(par.items())):
        print(s, n, '->', r[:330])
