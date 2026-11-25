import json,re,urllib.request,html
L=json.load(open('projets/sailingmore/site/stages-proches.json'))['o']
lot=['Oltremare Vela','Sailway','Sailing Virgins','Segelschule Weber','Seafarer Sailing','Neilson','Club Nàutic Portitxol','Aquavitesse','PlymSail']
cache={}
pat=re.compile(r'(?:€|£|\$|EUR|GBP|USD)\s?\d[\d.,]*|\d[\d.,]*\s?(?:€|£|\$|EUR|euro|GBP)',re.I)
out=[]
for i,o in enumerate(L):
    if o[4] in lot and not o[8]:
        u=o[10]
        if u not in cache:
            try:
                r=urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0'})
                t=urllib.request.urlopen(r,timeout=20).read().decode('utf-8','ignore')
                t=re.sub(r'(?s)<(script|style).*?</\1>',' ',t); t=html.unescape(re.sub(r'<[^>]+>',' ',t)); t=re.sub(r'\s+',' ',t)
                cache[u]=[t[max(0,m.start()-50):m.end()+30] for m in pat.finditer(t)][:6]
            except Exception as e: cache[u]=['ERR '+str(e)[:50]]
        out.append(f'{i} | {o[4]} | {o[3][:50]} | {u}\n   '+'\n   '.join(cache[u]))
open('sonde_prix_c.txt','w').write('\n'.join(out))
print(len(out))
