import json,collections,os
R=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
d=json.load(open(R+'/projets/sailingmore/stages.json'))
L=d['offres']
by=collections.defaultdict(list)
for o in L: by[o['ecole']].append(o)
for e,l in sorted(by.items(),key=lambda x:-len(x[1])):
    v=[o for o in l if not o.get('lieu')]
    if not v: continue
    ll=collections.Counter((o.get('lat'),o.get('lon'),o.get('precision')) for o in v).most_common(3)
    lieux=collections.Counter(o['lieu'] for o in l if o.get('lieu')).most_common(5)
    print(e,len(v),'/',len(l),'| pos',ll,'| lieux',lieux)
