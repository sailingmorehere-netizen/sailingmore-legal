import json, os, collections
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
L = json.load(open(R + '/projets/sailingmore/site/stages-proches.json'))['o']
NOMS = ['Segelschule Insel Reichenau', 'Compagnia della Vela', 'École de croisière Slowlife',
        'Urban Truant', 'Segelschule Grosse Freiheit', 'La Scuola della Vela', 'Soleil Scuola Nautica',
        'Segelschule Überlingen', 'EZS Zeilschool', 'Real Club de Mar', 'Blue Spirit', 'Solent Sail',
        'Vent du Large', 'Lagoo Segelschule Zürich', 'Segelschule Rehbach', 'Segelschule Schluchsee', 'Windzone']
c = collections.Counter()
for i, o in enumerate(L):
    if o[4] in NOMS and o[8] in (None, '', 0):
        c[(o[4], repr(o[16])[:40])] += 1
        print(i, o[4], '|', o[3][:45], '|', o[16], '|', o[9], '|', o[10][:60])
print(len(L[0]), L[0])
