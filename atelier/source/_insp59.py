import json
L = json.load(open('projets/sailingmore/stages.json'))['offres']
b = json.load(open('projets/sailingmore/stages.json.bak-avant-59'))['offres']
n = 0
for e, o in zip(L, b):
    if e['niveau'] != o['niveau']:
        n += 1
        if n % 3 == 0:
            print(e['niveau'][:4], '|', e['titre'][:80])
# prix manquants par ecole avec lien
import collections
print(collections.Counter(e['ecole_slug'] for e in L if not e['prix_eur']).most_common(12))
