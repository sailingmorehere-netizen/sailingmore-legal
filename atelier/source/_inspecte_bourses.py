import json
d = json.load(open('projets/sailingmore/bourses.json', encoding='utf-8'))
L = d if isinstance(d, list) else max((v for v in d.values() if isinstance(v, list)), key=len)
for e in L:
    print(e.get('groupe'), '|', e.get('ou'), '|', e.get('port'), '|', e.get('lat'), e.get('lon'), '|', e.get('methode'))
