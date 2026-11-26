import json, sys
S = json.load(open('projets/sailingmore/stages.json', encoding='utf-8'))['offres']
for e in S:
    if e['ecole'] == sys.argv[1] and not e.get('debut'):
        print(e['titre'][:50], '|', e['lien'])
