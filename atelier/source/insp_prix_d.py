# © 2026 Sailing More — tous droits réservés. All rights reserved.
import json, collections
d = json.load(open('projets/sailingmore/site/stages-proches.json'))
L = d['o']
print(list(d.keys()))
print(L[0])
S = ['Segelschule Insel Reichenau', 'Compagnia della Vela', 'École de croisière Slowlife', 'Urban Truant',
     'Segelschule Grosse Freiheit', 'La Scuola della Vela', 'Soleil Scuola Nautica', 'Segelschule Überlingen',
     'EZS Zeilschool', 'Real Club de Mar', 'Blue Spirit', 'Solent Sail', 'Vent du Large',
     'Lagoo Segelschule Zürich', 'Segelschule Rehbach', 'Segelschule Schluchsee', 'Windzone']
c = collections.Counter()
m = collections.Counter()
for o in L:
    if o[4] in S:
        c[o[4]] += 1
        if o[8] in (None, '', 0):
            m[o[4]] += 1
for k in c:
    print(k, c[k], m[k])
