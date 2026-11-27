import json, re, unicodedata, collections
B = '/opt/data/cache/claude-nuit/travail/projets/sailingmore/'
d = json.load(open(B + 'regates.json', encoding='utf-8'))
L = d['regates'] if 'regates' in d else max([v for v in d.values() if isinstance(v, list)], key=len)
c = json.load(open(B + 'regates-clubs.json', encoding='utf-8'))
def n(s):
    s = unicodedata.normalize('NFD', s or '').lower()
    return re.sub(r'[^a-z0-9]+', ' ', ''.join(ch for ch in s if unicodedata.category(ch) != 'Mn')).strip()
cl = [e for k, v in c.items() if isinstance(v, list) for e in v if isinstance(e, dict)]
print(len(c), len(cl), sum(1 for e in cl if e.get('lien')))
idx = collections.defaultdict(list)
for e in cl:
    if e.get('lien'): idx[(n(e['nom']), e['debut'])].append(e['lien'])
v = [x for x in L if not x.get('lien')]
hit = [x for x in v if (n(x['nom']), x['debut']) in idx]
print('exact nom+debut', len(hit))
print(collections.Counter(x['pays'] for x in v).most_common(8))
print(collections.Counter(x['debut'][:7] for x in v).most_common(8))
print(collections.Counter(tuple(x['sources']) for x in v).most_common(5))
print([k for k in d if not isinstance(d[k], list)], list(d)[:5])
