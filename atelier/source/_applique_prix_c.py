import json
F='projets/sailingmore/site/stages-proches.json'
raw=open(F,encoding='utf-8').read()
d=json.loads(raw)
cands=[dict(separators=(',',':'),ensure_ascii=False),dict(separators=(',',':'),ensure_ascii=True),dict(ensure_ascii=False),dict(ensure_ascii=True)]
kw=next((k for k in cands if json.dumps(d,**k) in (raw,raw.rstrip('\n'))),None)
print('format reproductible:',kw)
# indice: (prix, devise) — relevés sur les pages des écoles le 25/11/2026 (lecture seule), prix « à partir de »,
# tarif normal quand la page distingue le Black Friday.
P={125:(538,'GBP'),126:(600,'GBP'),127:(982,'GBP'),129:(600,'GBP'),130:(199,'GBP'),131:(499,'GBP'),132:(499,'GBP'),
   133:(220,'EUR'),134:(250,'EUR'),135:(220,'EUR'),136:(350,'EUR'),137:(300,'EUR'),138:(190,'EUR'),139:(220,'EUR'),
   141:(440,'EUR'),142:(440,'EUR'),143:(110,'EUR'),144:(400,'EUR'),145:(250,'EUR'),146:(880,'EUR'),
   154:(310,'GBP'),156:(70,'EUR'),160:(60,'EUR'),
   198:(125,'EUR'),199:(65,'EUR'),200:(55,'EUR'),201:(125,'EUR'),202:(135,'EUR'),203:(65,'EUR'),209:(400,'EUR'),
   218:(795,'GBP'),219:(370,'GBP'),221:(275,'GBP'),223:(796,'GBP'),224:(1295,'GBP'),
   377:(4190,'USD'),378:(4190,'USD'),379:(4690,'USD'),380:(4190,'USD'),381:(3990,'USD'),382:(3990,'USD'),
   383:(8500,'USD'),384:(4990,'USD'),385:(4190,'USD'),
   390:(390,'EUR'),391:(80,'EUR'),392:(80,'EUR'),393:(150,'EUR'),394:(150,'EUR'),395:(150,'EUR'),396:(150,'EUR'),
   397:(690,'EUR'),398:(200,'EUR')}
if kw:
    for i,(p,c) in P.items():
        o=d['o'][i]; assert o[8] is None, i
        o[8]=float(p); o[9]=c
    out=json.dumps(d,**kw)+('\n' if raw.endswith('\n') else '')
    open(F,'w',encoding='utf-8').write(out)
    print('écrit',len(P))
