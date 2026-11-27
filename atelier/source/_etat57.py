import json, sys
d = json.load(open('projets/sailingmore/stages.json'))
for e in d['offres']:
    if e.get('ecole_slug') in sys.argv[1:] and e.get('prix_eur') in (None, '', 0):
        print(e['ecole_slug'], '|', e['titre'], '|', e.get('debut'), '|', e['lien'], '|', e.get('hors_offre'))
