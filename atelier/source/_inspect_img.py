import json,collections
d=json.load(open('projets/sailingmore/site/stages-proches.json'))
L=d['o']
by=collections.defaultdict(collections.Counter)
for o in L:
    if o[11]: by[o[4]][o[11]]+=1
for e in ['UKSA','Sailway','Sailing Virgins','Neilson','Segelschule Grosse Freiheit','Segelschule Rehbach','De Bird']:
    print(e,len(by[e]),by[e].most_common(2))
