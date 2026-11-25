import json,collections
d=json.load(open('projets/sailingmore/site/stages-proches.json'))
print(list(d))
L=d['o']
B=['De Bird','UKSA','Segelschule Rückenwind','Zeilschool Ûp','BH Marine']
c=collections.Counter((o[4],bool(o[8])) for o in L if o[4] in B)
print(c)
for o in [o for o in L if o[4] in B and not o[8]][:4]: print(o)
