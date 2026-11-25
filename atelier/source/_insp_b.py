import json, os
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
L = json.load(open(R + '/projets/sailingmore/site/stages-proches.json'))['o']
B = ['De Bird', 'UKSA', 'Segelschule Rückenwind', 'Zeilschool Ûp', 'BH Marine']
for i, o in enumerate(L):
    if o[4] in B and not o[8]:
        print(i, o[4][:6], o[3][:40], o[10])
