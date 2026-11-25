import json
import sys

JSON_F = 'projets/sailingmore/chants-de-marin.json'
SNAP = 'cache/chants/avant.json'
mode = sys.argv[1]
c = json.load(open(JSON_F))['chants']
if mode == 'save':
    json.dump({x['id']: x.get('paroles') for x in c}, open(SNAP, 'w'), ensure_ascii=False)
else:
    avant = json.load(open(SNAP))
    for x in c:
        a = avant.get(x['id'])
        b = x.get('paroles')
        if a is None:
            continue
        if a != b:
            la, lb = (a or '').splitlines(), (b or '').splitlines()
            ajout = [l for l in lb if l not in la]
            perdu = [l for l in la if l not in lb]
            print('##', x['id'], 'ajoutées:', ajout, 'perdues:', perdu)
