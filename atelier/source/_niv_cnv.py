import json, collections
o = json.load(open('projets/sailingmore/stages.json'))['offres']
c = [e for e in o if e['ecole_slug'] == 'cnv-versoix']
print(len(c), collections.Counter(e.get('niveau') for e in c))
print(collections.Counter(e['lien'] for e in c))
for e in c[:3]:
    print(e)
for e in c:
    if e.get('niveau'):
        print(e['niveau'], e['titre'], e['lien']); break
