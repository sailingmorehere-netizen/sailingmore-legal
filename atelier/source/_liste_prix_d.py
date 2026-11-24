import json
d=json.load(open('projets/sailingmore/site/stages-proches.json'))
L=d['o']
S=['Segelschule Insel Reichenau','Compagnia della Vela','École de croisière Slowlife','Urban Truant','Segelschule Grosse Freiheit','La Scuola della Vela','Soleil Scuola Nautica','Segelschule Überlingen','EZS Zeilschool','Real Club de Mar','Blue Spirit','Solent Sail','Vent du Large','Lagoo Segelschule Zürich','Segelschule Rehbach','Segelschule Schluchsee','Windzone']
print(len(L), [k for k in d if k!='o'])
for i,o in enumerate(L):
    if o[4] in S and not o[8]: print(i,o)
