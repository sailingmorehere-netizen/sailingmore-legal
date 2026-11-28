# © 2026 Sailing More — tous droits réservés. All rights reserved.
import json, os, sys
sys.argv = ['x', 'prix_d']
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
d = json.load(open(os.path.join(R, 'projets/sailingmore/site/stages-proches.json')))
print(list(d.keys()))
L = d['o']
print(L[0])
for i, o in enumerate(L):
    if o[4] in ['Windzone', 'Real Club de Mar', 'Blue Spirit', 'Solent Sail', 'Vent du Large', 'Urban Truant'] or not o[8]:
        if o[4] in ['Segelschule Insel Reichenau', 'Compagnia della Vela', 'École de croisière Slowlife', 'Urban Truant', 'Segelschule Grosse Freiheit', 'La Scuola della Vela', 'Soleil Scuola Nautica', 'Segelschule Überlingen', 'EZS Zeilschool', 'Real Club de Mar', 'Blue Spirit', 'Solent Sail', 'Vent du Large', 'Lagoo Segelschule Zürich', 'Segelschule Rehbach', 'Segelschule Schluchsee', 'Windzone']:
            print(i, o)
