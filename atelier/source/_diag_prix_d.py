import json
s = json.load(open('projets/sailingmore/stages.json'))
g = json.load(open('projets/sailingmore/site/go-liens.json'))
d = json.load(open('projets/sailingmore/site/stages-proches.json'))['o']
if isinstance(s, dict):
    s = next(v for v in s.values() if isinstance(v, list) and v and isinstance(v[0], dict))
byl = {o['lien']: o for o in s}
n = 0
for r in d:
    if r[8] in (None, '', 0):
        u = g.get(r[10].split('id=')[1].split('&')[0])
        o = byl.get(u)
        if o and o['prix']:
            n += 1
            print(r[4], r[3], o['prix'], o['devise'])
print('dispo', n)
