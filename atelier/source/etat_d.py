import json,os
R=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
S=R+'/projets/sailingmore/site/'
L=json.load(open(S+'stages-proches.json'))['o']
G=json.load(open(S+'go-liens.json'))
G=G.get('o',G) if isinstance(G,dict) else G
NOMS=set(['Segelschule Insel Reichenau','Compagnia della Vela','École de croisière Slowlife','Urban Truant','Segelschule Grosse Freiheit','La Scuola della Vela','Soleil Scuola Nautica','Segelschule Überlingen','EZS Zeilschool','Real Club de Mar','Blue Spirit','Solent Sail','Vent du Large','Lagoo Segelschule Zürich','Segelschule Rehbach','Segelschule Schluchsee','Windzone'])
for i,o in enumerate(L):
    if o[4] in NOMS and o[8] in (None,'',0) and not o[16]:
        print(i, o[3][:50], G.get(o[10].split('id=')[1].split('&')[0]))
