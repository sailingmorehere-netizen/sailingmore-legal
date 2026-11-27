import json, sys
d = json.load(open('projets/sailingmore/stages.json'))
for e in d['offres']:
    if not e.get('debut') and e['ecole_slug'] in sys.argv[1:]:
        print(e['ecole_slug'], e['titre'][:50], e.get('hors_offre'), e['lien'])
