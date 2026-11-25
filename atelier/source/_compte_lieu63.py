import json, os
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
p = os.path.join(R, 'projets/sailingmore/stages.json')
d = json.load(open(p, encoding='utf-8'))
L = max([v for v in d.values() if isinstance(v, list)], key=len) if isinstance(d, dict) else d
vides = [e for e in L if e.get('lieu') in (None, '', [])]
print(p, len(L), 'vides', len(vides))
print(list(L[0].keys()))
for e in vides[:5]:
    print({k: e.get(k) for k in ('ecole', 'titre', 'lien', 'url')})
