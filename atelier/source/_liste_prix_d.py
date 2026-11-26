import json, os
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
L = json.load(open(R + '/projets/sailingmore/site/stages-proches.json'))['o']
LOT = ['Segelschule Insel Reichenau', 'Compagnia della Vela', 'École de croisière Slowlife',
       'Urban Truant', 'Segelschule Grosse Freiheit', 'La Scuola della Vela', 'Soleil Scuola Nautica',
       'Segelschule Überlingen', 'EZS Zeilschool', 'Real Club de Mar', 'Blue Spirit', 'Solent Sail',
       'Vent du Large', 'Lagoo Segelschule Zürich', 'Segelschule Rehbach', 'Segelschule Schluchsee', 'Windzone']
print(len(L), L[0])
for i, o in enumerate(L):
    if o[4] in LOT and o[8] in (None, '', 0):
        print(i, o)
