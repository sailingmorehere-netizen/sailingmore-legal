import json
L=json.load(open('projets/sailingmore/site/stages-proches.json'))['o']
n=0
for o in L:
    if o[8] and o[4] in ('Urban Truant','Solent Sail','Segelschule Überlingen','EZS Zeilschool','Compagnia della Vela','UKSA','Tip Top Sailing'):
        print(o[3][:40],o[4],o[8],o[9]); n+=1
for o in L:
    if o[8] and n<12 and o[9]!='EUR': print(o[4],o[8],o[9]); n+=1
print(set(type(o[8]).__name__ for o in L), set(o[9] for o in L))
