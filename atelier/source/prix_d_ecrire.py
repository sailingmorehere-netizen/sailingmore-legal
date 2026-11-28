# © 2026 Sailing More — tous droits réservés. All rights reserved.
import json,os
R=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
F=R+'/projets/sailingmore/site/stages-proches.json'
raw=open(F,encoding='utf8').read()
d=json.loads(raw)
# indice -> prix lu en ligne le 26/11/2026
PRIX={76:250.0,   # Compagnia della Vela, Junior : frais d'inscription 1re semaine 250 EUR
      211:105.0}  # Soleil, Corso BLSD : "Costo del corso 105 EUR"
for i,p in PRIX.items():
    assert d['o'][i][8] in (None,'',0)
    d['o'][i][8]=p
compact='\n' not in raw.strip()
json.dump(d,open(F,'w',encoding='utf8'),ensure_ascii=False,separators=(',',':') if compact else None,indent=None if compact else 1)
print('ok',len(PRIX))
