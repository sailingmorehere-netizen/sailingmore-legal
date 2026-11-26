import json,collections
d=json.load(open('projets/sailingmore/stages.json',encoding='utf-8'))['offres']
print(len(d), sum(1 for e in d if e.get('debut')))
c=collections.Counter(e['ecole'] for e in d if not e.get('debut'))
for k,v in c.most_common(12):
    ex=[e for e in d if e['ecole']==k and not e.get('debut')][:2]
    print(v,k,[ (e['titre'][:40],e['lien']) for e in ex])
