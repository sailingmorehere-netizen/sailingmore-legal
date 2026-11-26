import json, collections, sys
B = '/opt/data/cache/claude-nuit/travail/projets/sailingmore/'
d = json.load(open(B + 'regates.json', encoding='utf-8'))
R = d['regates']
c = json.load(open(B + 'regates-clubs.json', encoding='utf-8'))
print('regates', len(R), 'total declare', d.get('total'))
sans = [r for r in R if r.get('lien') in (None, '', [])]
print('sans lien', len(sans))
print('clubs.json: sources', len(c), [(k, len(v)) for k, v in c.items()])
# table club -> liens des entrees de clubs.json
tab = collections.defaultdict(set)
for k, v in c.items():
    for e in v:
        if e.get('club') and e.get('lien'):
            tab[e['club']].add(e['lien'])
print('clubs avec lien dans clubs.json', {k: list(v) for k, v in tab.items()})
cl = collections.Counter(r.get('club') or '' for r in sans)
print('sans lien : sans club', cl.get('', 0), 'distincts clubs', len(cl))
print(cl.most_common(15))
print('sources', collections.Counter(tuple(r.get('sources') or []) for r in sans).most_common(8))
print('club de sans-lien present dans clubs.json:', sum(1 for r in sans if r.get('club') in tab))
# liens (autres regates) par club : un club a-t-il un site unique ?
lc = collections.defaultdict(collections.Counter)
for r in R:
    if r.get('lien') and r.get('club'):
        lc[r['club']][r['lien']] += 1
print('exemples', [(k, list(v.items())[:2]) for k, v in list(lc.items())[:3]])
