import json, os, re, sys, collections
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _niveau47 import MAP
c = json.load(open(os.path.join(R, 'scripts/_niveau47_cache.json')))
d = json.load(open(os.path.join(R, 'projets/sailingmore/stages.json')))['offres']
res = collections.Counter(); ex = collections.defaultdict(list)
for e in d:
    if e.get('niveau') or e['ecole_slug'] == 'cnv-versoix': continue
    t = c.get(e['lien'], '')
    if len(t) > 15000 or t.startswith('ERR'): res['long/err'] += 1; continue
    got = {k for k, p in MAP if re.search(p, t, re.I)}
    key = ','.join(sorted(got)) or 'rien'
    res[key] += 1
    if len(got) == 1 and len(ex[key]) < 12: ex[key].append((e['ecole_slug'], e['titre'][:45], len(t)))
print(res)
for k, v in ex.items():
    print(k)
    for x in v: print('  ', x)
