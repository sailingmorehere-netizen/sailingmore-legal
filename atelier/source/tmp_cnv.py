import json, collections, re
d = json.load(open('/opt/data/cache/claude-nuit/travail/projets/sailingmore/stages.json', encoding='utf-8'))
L = d if isinstance(d, list) else max([v for v in d.values() if isinstance(v, list)], key=len)
v = [x for x in L if x.get('ecole') == 'Club Nautique de Versoix' and not x.get('hors_offre')]
c = collections.Counter()
for x in v:
    c[(re.sub(r' · .*', '', x['titre']), x.get('niveau'), x['lien'], x.get('type'))] += 1
for k, n in sorted(c.items(), key=lambda a: str(a)):
    print(n, k)
