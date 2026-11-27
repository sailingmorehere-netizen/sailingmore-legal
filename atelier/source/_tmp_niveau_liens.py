import json,sys
o=json.load(open('projets/sailingmore/stages.json'))['offres']
for e in o:
    if not e.get('niveau') and e['ecole_slug'] in sys.argv[1:]:
        print(e['ecole_slug'],e['titre'],e['lien'])
