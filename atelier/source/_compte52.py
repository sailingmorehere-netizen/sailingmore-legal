import json, collections
d = json.load(open('projets/sailingmore/stages.json', encoding='utf-8'))
V = [x for x in d['offres'] if x.get('ecole') == 'Club Nautique de Versoix' and not x.get('hors_offre')]
print(len(V), collections.Counter(str(x.get('niveau')) for x in V))
