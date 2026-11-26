import json
p = 'projets/sailingmore/stages.json'
d = json.load(open(p, encoding='utf-8'))
R = {'10 Essentials for RYA Competent Crew': 'debutant',
     '10 Essentials for RYA Day Skipper Practical': 'intermediaire',
     'Preparation for RYA Coastal Skipper Practical Sail': 'confirme'}
n = 0
for e in d['offres']:
    if e['ecole_slug'] == 'solentboat' and e.get('niveau') in (None, '', []) and e['titre'].strip() in R:
        e['niveau'] = R[e['titre'].strip()]
        n += 1
json.dump(d, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print('ecrits', n)
