import json, os, collections
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
d = json.load(open(R + '/stages-proches.json', encoding='utf-8'))
print([k for k in d], {k: (v if k != 'o' else len(v)) for k, v in d.items() if k != 'o'} if True else '')
for r in d['o'][:3]: print(r)
print(collections.Counter(r[12] for r in d['o']).most_common(40))
for r in d['o']:
    if r[12] in ('AUT', 'POL', 'SWE'): print(r); break
s = json.load(open(R + '/projets/sailingmore/stages.json', encoding='utf-8'))
print([k for k in s], len(s['offres']))
print(s['offres'][0])
print(collections.Counter(o.get('pays') for o in s['offres']).most_common(40))
e = json.load(open(R + '/projets/sailingmore/ecoles.json', encoding='utf-8'))
print(type(e), list(e)[:10] if isinstance(e, dict) else e[:2])
src = json.load(open('/opt/data/projets/sailingmore/1-direction/europe-vague1-222-offres.json', encoding='utf-8'))
for k, v in src['pays'].items():
    print(k, {a: b for a, b in v.items() if a != 'offres'}, len(v['offres']))
print(collections.Counter(k for v in src['pays'].values() for o in v['offres'] for k in o))
print([k for k in src if k != 'pays'])
