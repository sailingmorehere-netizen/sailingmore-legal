import json, os
d = json.load(open('projets/sailingmore/stages.json', encoding='utf-8'))
L = d['offres']
v = sum(1 for e in L if not e.get('image'))
print('copie: image vides', v, 'sur', len(L), '(max 160)')
man = [e['image'] for e in L if e.get('image') and not os.path.exists('projets/sailingmore/site/' + e['image'])]
print('fichiers manquants', len(man))
