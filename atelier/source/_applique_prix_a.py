import json
F='projets/sailingmore/site/stages-proches.json'
raw=open(F,encoding='utf-8').read()
d=json.loads(raw)
cands=[dict(separators=(',',':'),ensure_ascii=False),dict(separators=(',',':'),ensure_ascii=True),dict(ensure_ascii=False),dict(ensure_ascii=True)]
kw=next((k for k in cands if json.dumps(d,**k) in (raw,raw.rstrip('\n'))),None)
print('format reproductible:',kw)
# Prix relevés sur les pages le 25/11/2026 (lecture seule). « À partir de » : le plus bas affiché, tarif plein
# (pas la remise). Vide si la page n'affiche aucun prix de l'offre elle-même (pages d'info, destinations, prérequis,
# suppléments type boordkas / prix de bateau).
P={}
for i,p in {21:1150,22:1150,23:1150,24:1150,26:695,27:875,28:830,30:1705,31:1705,32:2130,34:200,35:75,36:600,37:650,
            38:2950,39:1250,41:1155,42:525,43:450,45:420,46:620}.items(): P[i]=(p,'EUR')       # Seven Seas
for i,p in {230:129,231:299,233:399,234:99,235:299,236:300,239:499,240:3999,245:699,247:99,248:125,254:49,255:49,
            256:89,257:299,258:349,259:349,260:39,266:20,267:20}.items(): P[i]=(p,'GBP')         # Solent Boat Training
for i,p in {278:895,290:350,291:1350,292:165,294:195,295:1352.5,297:795,298:475,301:425,302:1295,303:275,305:125}.items(): P[i]=(p,'EUR')  # Tip Top
for i,p in {341:890,342:850,343:890,344:1850,345:1190,346:1190,347:690,349:1090,350:350,351:290,352:1090,353:590,355:1990}.items(): P[i]=(p,'EUR')  # Ultra
if kw:
    for i,(p,c) in P.items():
        o=d['o'][i]; assert o[8] is None, i
        o[8]=float(p); o[9]=c
    open(F,'w',encoding='utf-8').write(json.dumps(d,**kw)+('\n' if raw.endswith('\n') else ''))
    print('écrit',len(P))
