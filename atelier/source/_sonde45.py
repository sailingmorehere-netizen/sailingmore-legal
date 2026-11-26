import json, collections, os
RAC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
d = json.load(open(os.path.join(RAC, 'projets/sailingmore/stages.json'), encoding='utf-8'))
L = max([v for v in d.values() if isinstance(v, list)], key=len) if isinstance(d, dict) else d
m = [e for e in L if e.get('debut') in (None, '', [])]
cles = ('zeezeil', 'bird', 'tip', 'up', 'compagnia', 'oltremare')
c = collections.Counter((e.get('ecole'), e.get('ecole_slug')) for e in m)
for k, n in c.items():
    if any(x in (k[1] or '').lower() or x in (k[0] or '').lower() for x in cles):
        print(k, n)
