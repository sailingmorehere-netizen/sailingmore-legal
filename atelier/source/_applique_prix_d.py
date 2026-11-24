import json
F='projets/sailingmore/site/stages-proches.json'
raw=open(F,encoding='utf-8').read()
d=json.loads(raw)
cands=[dict(separators=(',',':'),ensure_ascii=False),dict(separators=(',',':'),ensure_ascii=True),dict(ensure_ascii=False),dict(ensure_ascii=True)]
kw=next((k for k in cands if json.dumps(d,**k)==raw or json.dumps(d,**k)+'\n'==raw),None)
print('format reproductible:',kw)
# indice: (prix, devise) — relevés sur les pages des écoles (lecture seule), prix « à partir de »
P={80:(150,'EUR'),81:(250,'EUR'),109:(375,'EUR'),110:(450,'EUR'),111:(600,'EUR'),312:(550,'EUR'),
   273:(200,'GBP'),369:(120,'GBP'),370:(350,'GBP'),371:(350,'GBP'),372:(559,'GBP'),373:(350,'GBP')}
if kw:
    for i,(p,c) in P.items():
        o=d['o'][i]; assert o[8] is None
        o[8]=float(p); o[9]=c
    out=json.dumps(d,**kw)+('\n' if raw.endswith('\n') else '')
    open(F,'w',encoding='utf-8').write(out)
    print('écrit',len(P))
