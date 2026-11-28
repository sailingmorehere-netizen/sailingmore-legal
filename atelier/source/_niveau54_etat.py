import json, collections, urllib.parse
P = 'projets/sailingmore/stages.json'
L = json.load(open(P, encoding='utf-8'))['offres']
m = [e for e in L if not e.get('niveau')]
cb = json.load(open('scripts/_niveau58_corps.json'))
ct = json.load(open('scripts/_niveau58_cache.json'))
print(len(m), 'cles', sorted(m[0].keys()))
print(collections.Counter(urllib.parse.urlparse(e.get('lien') or '').netloc for e in m).most_common(12))
print('sans corps cache', sum(1 for e in m if e.get('lien') not in cb), 'corps vides', sum(1 for e in m if e.get('lien') in cb and not cb[e['lien']]))
print(m[0])
