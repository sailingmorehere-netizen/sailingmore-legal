# © 2026 Sailing More — tous droits réservés. All rights reserved.
import json, os, sys, collections
sys.argv = ['x', 'none']
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
L = json.load(open(os.path.join(R, 'projets/sailingmore/site/stages-proches.json')))['o']
D = ['Segelschule Insel Reichenau', 'Compagnia della Vela', 'École de croisière Slowlife', 'Urban Truant',
     'Segelschule Grosse Freiheit', 'La Scuola della Vela', 'Soleil Scuola Nautica', 'Segelschule Überlingen',
     'EZS Zeilschool', 'Real Club de Mar', 'Blue Spirit', 'Solent Sail', 'Vent du Large',
     'Lagoo Segelschule Zürich', 'Segelschule Rehbach', 'Segelschule Schluchsee', 'Windzone']
c = collections.Counter()
for i, o in enumerate(L):
    if o[4] in D:
        c[(o[4], bool(o[8]))] += 1
for k, v in sorted(c.items()):
    print(k, v)
for i, o in enumerate(L):
    if o[4] in D and not o[8]:
        print(i, o)
