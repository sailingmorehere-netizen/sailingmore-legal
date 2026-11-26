import json,collections,subprocess,sys
sys.argv=['x']
exec(open('scripts/remplit_debut.py').read().split("print('balisées'")[0])
c=collections.defaultdict(collections.Counter)
for o in d['o']:
    pass
old=json.load(open(F))['o']
for a,b in zip(old,d['o']):
    if not a[7] and b[7]: c[b[4]][b[7]]+=1
for k,v in c.items(): print(k,len(v),v.most_common(3))
