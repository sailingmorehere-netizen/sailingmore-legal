import json, re, urllib.request, html, sys
d=json.load(open('projets/sailingmore/site/stages-proches.json'))
L=d['o']
S=['Segelschule Insel Reichenau','Compagnia della Vela','École de croisière Slowlife','Urban Truant','Segelschule Grosse Freiheit','La Scuola della Vela','Soleil Scuola Nautica','Segelschule Überlingen','EZS Zeilschool','Real Club de Mar','Blue Spirit','Solent Sail','Vent du Large','Lagoo Segelschule Zürich','Segelschule Rehbach','Segelschule Schluchsee','Windzone']
P=re.compile(r'(?:[€£]\s?\d[\d.,]*|\d[\d.,]*\s?(?:€|EUR|£|CHF|Euro)\b)')
for i,o in enumerate(L):
    if o[4] in S and not o[8]:
        try:
            r=urllib.request.Request(o[10],headers={'User-Agent':'Mozilla/5.0'})
            b=urllib.request.urlopen(r,timeout=20).read().decode('utf-8','ignore')
            t=html.unescape(re.sub(r'<(script|style)[\s\S]*?</\1>|<[^>]+>',' ',b))
            t=re.sub(r'\s+',' ',t)
            out=[]
            for m in P.finditer(t):
                out.append(t[max(0,m.start()-50):m.end()+10])
                if len(out)>=4: break
            print(i,o[4],'|',o[3][:40],'|',len(t),out,flush=True)
        except Exception as e:
            print(i,o[4],'ERR',str(e)[:60],flush=True)
