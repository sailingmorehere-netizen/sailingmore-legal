import json, os
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
d = json.load(open(R + '/stages-proches.json', encoding='utf-8'))
P6 = ('AUT', 'SWE', 'DNK', 'NOR', 'CZE', 'POL')
n = sum(1 for r in d['o'] if r[12] in P6)
print('EU1', n)
for r in d['o']:
    if r[12] in P6 and (r[4].startswith(('Marselis', 'Gryf', 'Malm')) or 'Malm' in r[5]):
        print(r[3], '|', r[4], '|', r[8], r[9])
d2 = json.load(open(R + '/projets/sailingmore/site/stages-proches.json', encoding='utf-8'))
print('site/', sum(1 for r in d2['o'] if r[12] in P6))
e = json.load(open(R + '/projets/sailingmore/ecoles.json', encoding='utf-8'))
print('ecoles', len(e), sum(1 for x in e if x.get('pays') in P6), e[-1])
src = json.load(open('/opt/data/projets/sailingmore/1-direction/europe-vague1-222-offres.json', encoding='utf-8'))
for k, v in src['pays'].items():
    for o in v['offres']:
        if o.get('controle') or o.get('duree_statut'):
            print(k, o['ecole'], o['prix'], o.get('controle'), o.get('duree_jours'), o.get('duree_statut'), o.get('duree_texte')); break
