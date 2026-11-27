import json, collections
d = json.load(open('/opt/data/cache/claude-nuit/travail/projets/sailingmore/stages.json', encoding='utf-8'))
L = d if isinstance(d, list) else max([v for v in d.values() if isinstance(v, list)], key=len)
u = [x for x in L if x.get('ecole') == 'UKSA' and not x.get('hors_offre')]
c = collections.Counter((x['titre'], x['lien'], x.get('niveau'), x.get('type')) for x in u)
for k, v in c.most_common(): print(v, k)
print(collections.Counter(x['lieu'] for x in u))
print(sorted(set(k for x in u for k in x)))
