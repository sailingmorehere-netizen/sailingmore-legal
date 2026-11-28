import json
P = 'projets/sailingmore/stages.json'
d = json.load(open(P, encoding='utf-8'))
for e in d['offres']:
    if e['lien'] in ('https://segelschule-ueberlingen.de/sailart-20-mira-neu-in-2015/', 'https://www.ezs.nl/stcw-cursussen.html'):
        e['debut'] = e['fin'] = e['duree_jours'] = None
json.dump(d, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
