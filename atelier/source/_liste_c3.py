import json
L=json.load(open('projets/sailingmore/site/stages-proches.json'))['o']
lot=['Oltremare Vela','Sailway','Sailing Virgins','Segelschule Weber','Seafarer Sailing','Neilson','Club Nàutic Portitxol','Aquavitesse','PlymSail']
print(L[200])
from collections import Counter
v=[o for o in L if o[4] in lot]
print(Counter((o[4],bool(o[8])) for o in v))
