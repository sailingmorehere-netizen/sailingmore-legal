import json, os
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
d = json.load(open(os.path.join(R, 'projets/sailingmore/site/stages-proches.json')))
print({k: (v if not isinstance(v, list) else len(v)) for k, v in d.items() if k != 'o'})
lot = ['Segelschule Insel Reichenau', 'Compagnia della Vela', 'École de croisière Slowlife', 'Urban Truant',
       'Segelschule Grosse Freiheit', 'La Scuola della Vela', 'Soleil Scuola Nautica', 'Segelschule Überlingen',
       'EZS Zeilschool', 'Real Club de Mar', 'Blue Spirit', 'Solent Sail', 'Vent du Large',
       'Lagoo Segelschule Zürich', 'Segelschule Rehbach', 'Segelschule Schluchsee', 'Windzone']
for i, o in enumerate(d['o']):
    if o[4] in lot and o[8] in (None, '', 0):
        print(i, o)
