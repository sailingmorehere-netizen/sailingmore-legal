import json, collections, os
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
o = json.load(open(os.path.join(R, 'projets/sailingmore/stages.json')))['offres']
print(json.dumps(o[0], ensure_ascii=False)[:1500])
print(collections.Counter(e.get('niveau') for e in o))
print(collections.Counter(e.get('ecole_slug') for e in o if not e.get('niveau')).most_common(15))
