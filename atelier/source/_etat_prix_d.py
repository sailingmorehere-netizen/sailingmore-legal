import json, os, importlib.util, sys
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
F = os.path.join(R, 'projets/sailingmore/site/stages-proches.json')
d = json.load(open(F))
print({k: (v if k != 'o' else len(v)) for k, v in d.items()})
LOT = ['Segelschule Insel Reichenau', 'Compagnia della Vela', 'École de croisière Slowlife',
       'Urban Truant', 'Segelschule Grosse Freiheit', 'La Scuola della Vela', 'Soleil Scuola Nautica',
       'Segelschule Überlingen', 'EZS Zeilschool', 'Real Club de Mar', 'Blue Spirit', 'Solent Sail',
       'Vent du Large', 'Lagoo Segelschule Zürich', 'Segelschule Rehbach', 'Segelschule Schluchsee', 'Windzone']
from collections import Counter
c = Counter(); ex = {}
for o in d['o']:
    if o[4] in LOT:
        c[(o[4], o[8] not in (None, '', 0))] += 1
        ex.setdefault(o[4], o)
for k, v in sorted(c.items()):
    print(k, v)
for k, o in ex.items():
    print(o)
