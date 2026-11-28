import json
A = json.load(open('projets/sailingmore/stages.json.bak-avant-54', encoding='utf-8'))['offres']
B = json.load(open('projets/sailingmore/stages.json', encoding='utf-8'))['offres']
for a, b in zip(A, B):
    if a.get('niveau') != b.get('niveau'):
        print(b['ecole_slug'], '|', b['titre'][:60], '|', b['niveau'], '|', b['lien'])
