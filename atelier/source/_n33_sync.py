"""Tâche 33 : recopie debut de stages.json vers stages-proches.json (colonne 7), par (école, titre) sans ambiguïté."""
import json, collections
S = json.load(open('projets/sailingmore/stages.json', encoding='utf-8'))['offres']
F = 'projets/sailingmore/site/stages-proches.json'
raw = open(F, encoding='utf8').read()
d = json.loads(raw)
for sep, asc in (((',', ':'), False), ((', ', ': '), False), ((',', ':'), True)):
    if json.dumps(d, separators=sep, ensure_ascii=asc) == raw.rstrip('\n'):
        break
else:
    raise SystemExit('format non reproductible, je n ecris rien')
g = collections.defaultdict(set)
for e in S:
    g[(e['ecole'], e['titre'])].add(e.get('debut') or '')
n = 0
for o in d['o']:
    if not o[7]:
        v = g.get((o[4], o[3]), set())
        if len(v) == 1 and list(v)[0]:
            o[7] = list(v)[0]
            n += 1
open(F, 'w', encoding='utf8').write(json.dumps(d, separators=sep, ensure_ascii=asc) + ('\n' if raw.endswith('\n') else ''))
print('recopiés', n, '| total rempli', sum(1 for o in d['o'] if o[7]), '/', len(d['o']))
