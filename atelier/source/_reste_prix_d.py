import json, collections, os, sys
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ECOLES = ['Segelschule Insel Reichenau', 'Compagnia della Vela', 'École de croisière Slowlife',
          'Urban Truant', 'Segelschule Grosse Freiheit', 'La Scuola della Vela', 'Soleil Scuola Nautica',
          'Segelschule Überlingen', 'EZS Zeilschool', 'Real Club de Mar', 'Blue Spirit', 'Solent Sail',
          'Vent du Large', 'Lagoo Segelschule Zürich', 'Segelschule Rehbach', 'Segelschule Schluchsee', 'Windzone']
L = json.load(open(os.path.join(R, 'projets/sailingmore/site/stages-proches.json'), encoding='utf-8'))['o']
c = collections.defaultdict(list)
for i, o in enumerate(L):
    if o[4] in ECOLES and o[8] in (None, '', 0):
        c[o[4]].append((i, o))
for k, v in c.items():
    print(k, len(v))
    for i, o in v[:2]:
        print('  ', i, o)
