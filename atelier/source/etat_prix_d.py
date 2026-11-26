import json, os, collections, sys
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
d = json.load(open(os.path.join(R, 'projets/sailingmore/site/stages-proches.json')))
L = d['o']
lots = ['Segelschule Insel Reichenau', 'Compagnia della Vela', 'École de croisière Slowlife', 'Urban Truant', 'Segelschule Grosse Freiheit', 'La Scuola della Vela', 'Soleil Scuola Nautica', 'Segelschule Überlingen', 'EZS Zeilschool', 'Real Club de Mar', 'Blue Spirit', 'Solent Sail', 'Vent du Large', 'Lagoo Segelschule Zürich', 'Segelschule Rehbach', 'Segelschule Schluchsee', 'Windzone']
print(list(d.keys()))
m = collections.Counter(); c = collections.Counter()
for o in L:
    if o[4] in lots:
        c[o[4]] += 1
        if o[8] in (None, '', 0): m[o[4]] += 1
print(dict(c)); print(dict(m))
n = 0
for o in L:
    if o[4] in lots and o[8] in (None, '', 0) and n < 3: print(o); n += 1
for o in L:
    if o[4] in lots and o[8] not in (None, '', 0): print(o); break
