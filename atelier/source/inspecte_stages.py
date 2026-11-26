import json, collections
d = json.load(open('/opt/data/cache/claude-nuit/travail/projets/sailingmore/stages.json', encoding='utf-8'))
for e in d['offres']:
    if e.get('prix_eur') in (None, '', []) and e['ecole'] in ('De Bird', 'Tip Top Sailing', 'UKSA', 'Solent Boat Training'):
        print(e['ecole'][:6], '|', e['titre'][:50], '|', e['lien'])
