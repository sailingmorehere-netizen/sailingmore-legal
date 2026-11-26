import json, collections, sys
sys.argv = ['x']
exec(open('scripts/remplit_debut.py').read().split("print('balisées'")[0])
nopage = collections.Counter(); nourl = 0; rej = collections.defaultdict(collections.Counter)
for o in d['o']:
    if o[7] and False: pass
old = json.load(open(F))['o']
for a, o in zip(old, d['o']):
    if a[7]: continue
    u = G.get(a[10].split('id=')[1].split('&')[0])
    if not u: nourl += 1; continue
    if not S.page(u): nopage[a[4]] += 1
    elif o[7] == '' or not o[7]: pass
print('sans url', nourl, 'sans page en cache', sum(nopage.values()), nopage.most_common(8))
for a, o in zip(old, d['o']):
    if not a[7] and not o[7]:
        u = G.get(a[10].split('id=')[1].split('&')[0])
        h = S.page(u) if u else None
        if h: rej[a[4]][tuple(S.dates(h))[:3]] += 1
for k, v in list(rej.items())[:12]: print(k, v.most_common(2))
