import json, os
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
d = json.load(open(os.path.join(R, 'projets/sailingmore/site/stages-proches.json')))
L = d['o']
sch = ['Segelschule Insel Reichenau','Compagnia della Vela','École de croisière Slowlife','Urban Truant','Segelschule Grosse Freiheit','La Scuola della Vela','Soleil Scuola Nautica','Segelschule Überlingen','EZS Zeilschool','Real Club de Mar','Blue Spirit','Solent Sail','Vent du Large','Lagoo Segelschule Zürich','Segelschule Rehbach','Segelschule Schluchsee','Windzone']
print(list(d))
for i, o in enumerate(L):
    if o[4] in sch and o[8] in (None, '', 0):
        print(i, json.dumps(o, ensure_ascii=False)[:260])
