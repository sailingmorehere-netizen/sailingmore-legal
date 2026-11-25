import json, collections, os
B = 'projets/sailingmore/'
print('realpath', os.path.realpath(B + 'regates.json'), os.path.exists('/opt/data/projets/sailingmore/regates.json'))
d = json.load(open(B + 'regates.json', encoding='utf-8'))
L = d['regates']
sans = [e for e in L if not e.get('lien')]
print(len(L), len(sans))
c = json.load(open(B + 'regates-clubs.json', encoding='utf-8'))
print(type(c), len(c))
n = sum(len(v) for v in c.values() if isinstance(v, list))
print('evts clubs', n)
# club -> liens connus (domaine) dans regates.json
dom = collections.defaultdict(collections.Counter)
for e in L:
    if e.get('lien') and e.get('club'):
        dom[e['club']][e['lien']] += 1
print('sans: club renseigne', sum(1 for e in sans if e.get('club')))
print('sources sans', collections.Counter(s for e in sans for s in e.get('sources', [])).most_common(8))
for e in sans[:5]:
    print(e['nom'], e['club'], e['sources'], e['debut'])
print([k for k in c][:10])
print(os.listdir(B)[:60])
