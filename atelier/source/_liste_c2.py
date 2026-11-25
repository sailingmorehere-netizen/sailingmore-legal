import json
L=json.load(open('projets/sailingmore/site/stages-proches.json'))['o']
lot=['Oltremare Vela','Sailway','Sailing Virgins','Segelschule Weber','Seafarer Sailing','Neilson','Club Nàutic Portitxol','Aquavitesse','PlymSail']
for i,o in enumerate(L):
    if o[4] in lot: print(i,o[4],o[8],o[9],str(o[:4])[:90], str(o[12:])[:120])
