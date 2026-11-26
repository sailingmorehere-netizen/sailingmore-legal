import json,collections
L=json.load(open('projets/sailingmore/site/stages-proches.json'))['o']
print(len(L))
for o in L[:2]:print(o)
print([o for o in L if o[7]][:3])
print(collections.Counter(o[4] for o in L if not o[7]).most_common(15))
