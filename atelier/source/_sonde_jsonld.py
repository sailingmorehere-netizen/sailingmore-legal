import json
d = json.load(open('projets/sailingmore/regates.json'))
print(d.keys()); r = d['regates']; print(len(r)); print(r[0]); print(d.get('maj'))
g = json.load(open('scripts/regles.json')); print(g.keys()); print(g['regles'][0]); print(g['edition'])
l = json.load(open('projets/sailingmore/lexique.json')); print(l.keys()); print(l['themes'][0]['termes'][0])
