import json
P = 'projets/sailingmore/stages.json'
d = json.load(open(P + '.bak-avant-54', encoding='utf-8'))
n = 0
for e in d['offres']:
    if not e.get('niveau') and e['lien'].endswith('/rya_pwc_proficiency/'):
        e['niveau'] = 'debutant'; n += 1
json.dump(d, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('poses', n)
