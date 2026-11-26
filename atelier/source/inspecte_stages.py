import json, collections
p = '/opt/data/cache/claude-nuit/travail/projets/sailingmore/stages.json'
d = json.load(open(p, encoding='utf-8'))
L = d['offres'] if 'offres' in d else max([v for v in d.values() if isinstance(v, list)], key=len)
print([k for k in d])
for e in L:
    if not e.get('debut') and e['ecole'] in ('Tip Top Sailing', 'De Bird', 'Oltremare Vela', 'Compagnia della Vela', 'Zeilschool Ûp'):
        print(e['ecole'][:8], '|', e['titre'][:50], '|', e['lien'])
