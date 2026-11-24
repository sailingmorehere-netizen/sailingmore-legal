import json
d = json.load(open('projets/sailingmore/site/stages-proches.json'))['o']
for o in d:
    if o[4] in ('Solent Boat Training', 'Tip Top Sailing', 'Seven Seas School of Yachting', 'UKSA', 'Segelschule Weber', 'Urban Truant', 'Lagoo Segelschule Zürich') and o[8]:
        print(o[4], '|', o[3], '|', o[8], o[9], o[10])
print(set(o[9] for o in d))
