import json, os, collections
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
L = json.load(open(os.path.join(R, 'projets/sailingmore/site/stages-proches.json')))
print([k for k in L if k != 'o'])
B = ['De Bird', 'UKSA', 'Segelschule Rückenwind', 'Zeilschool Ûp', 'BH Marine']
s = [o for o in L['o'] if o[4] in B and o[8] in (None, '', 0)]
print(len(s), collections.Counter(o[4] for o in s))
for o in s[:5]: print(o)
for o in L['o']:
    if o[4] in B and o[8] not in (None, '', 0):
        print('rempli', o); break
