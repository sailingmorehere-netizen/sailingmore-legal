import json, collections, os
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
d = json.load(open(R + '/projets/sailingmore/site/stages-proches.json'))
print([k for k in d])
L = d['o']
print(L[0])
print(collections.Counter(o[7] for o in L).most_common(6))
print(collections.Counter(len(o) for o in L))
print([o for o in L if o[7]][:3])
print(collections.Counter(o[4] for o in L if not o[7]).most_common(15))
