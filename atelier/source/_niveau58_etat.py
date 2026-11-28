import json, collections, urllib.parse
d = json.load(open('projets/sailingmore/stages.json', encoding='utf-8'))
L = d['offres'] if isinstance(d, dict) and 'offres' in d else d
m = [e for e in L if not e.get('niveau')]
print(list(L[0].keys()))
print(collections.Counter(urllib.parse.urlparse(e.get('lien') or '').netloc for e in m).most_common(15))
print(len({e.get('lien') for e in m}), 'liens distincts')
for e in m[:5]:
    print(e.get('titre'), e.get('lien'))
