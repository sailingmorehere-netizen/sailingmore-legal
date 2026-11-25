import json
d = json.load(open('projets/sailingmore/stages.json', encoding='utf-8'))
EC = ['Zeezeilschool Scheveningen', 'De Bird', 'Tip Top Sailing', 'Zeilschool Ûp', 'Compagnia della Vela', 'Oltremare Vela']
for e in d['offres']:
    if e['ecole'] in EC and not e.get('debut'):
        print(e['ecole'][:8], '|', e['titre'][:60], '|', e.get('duree_jours'), '|', e['lien'])
