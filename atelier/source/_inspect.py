import json,re
d=json.load(open('projets/sailingmore/stages.json'))
m=[e for e in d['offres'] if not e.get('debut') and not e.get('hors_offre')]
n=0
for e in m:
    if re.search(r'\d{1,2}\.(\d{1,2}\.)?[–-]?\d{0,2}\.?\d{0,2}\.?20\d\d|\d{1,2}[.–-]+\d{1,2}\.\d{1,2}\.',e['titre']):
        n+=1;print(e['ecole_slug'],e['titre'],e.get('duree_jours'))
print(n)
