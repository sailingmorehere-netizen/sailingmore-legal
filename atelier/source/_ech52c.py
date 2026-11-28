import json, re, sys, html, urllib.request, collections
d = json.load(open('projets/sailingmore/stages.json'))
m = [e for e in d['offres'] if not e.get('debut') and not e.get('hors_offre')]
lc = collections.Counter(e['lien'] for e in d['offres'])
for e in m:
    if e['ecole'] in sys.argv[1:]:
        print(e['ecole'], '|', e['titre'][:50], '|', e['lien'], lc[e['lien']])
