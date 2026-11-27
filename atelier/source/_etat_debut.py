import json, os, collections
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
o = json.load(open(os.path.join(R, 'projets/sailingmore/stages.json')))['offres']
m = [e for e in o if not e.get('debut')]
real = [e for e in m if not e.get('hors_offre')]
print(len(m), 'sans debut;', len(real), 'hors hors_offre')
print(collections.Counter(e.get('type') for e in real))
print(collections.Counter(e['lien'] for e in real).most_common(5))
print(len(set(e['lien'] for e in real)), 'liens distincts')
for e in real[:25]:
    print(e['ecole_slug'], '|', e['titre'], '|', e['lien'], '|', e.get('prix'), e.get('duree_jours'))
print(sorted(f for f in os.listdir(os.path.join(R, 'scripts')) if 'date' in f or 'stage' in f))
