import json, os
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
d = json.load(open(os.path.join(R, 'projets/sailingmore/site/stages-proches.json')))
n = 0
for o in d['o']:
    if o[8] not in (None, '', 0) and o[4] in ('Segelschule Weber', 'Segelschule Rückenwind', 'Oltremare Vela', 'Lagoo Segelschule Zürich', 'EZS Zeilschool'):
        print(o[3][:40], '|', o[4], '|', repr(o[8]), o[9]); n += 1
        if n > 8: break
