import json, collections
d = json.load(open('projets/sailingmore/stages.json'))
o = d['offres']
print(list(o[0].keys()))
m = [e for e in o if not e.get('debut') and not e.get('hors_offre')]
print(len(m), sum(1 for e in o if e.get('hors_offre')))
k = [k for k in o[0] if k in ('ecole', 'ecole_id', 'id_ecole')]
c = collections.Counter(e.get(k[0]) if k else e['lien'].split('/')[2] for e in m)
print(c.most_common(20))
