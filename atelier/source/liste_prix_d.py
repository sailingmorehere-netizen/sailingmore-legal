import json, os, sys
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.argv = ['x']
src = open(os.path.join(R, 'scripts/verifie_stages_champ.py')).read().split('COL =')[0]
ns = {'__file__': os.path.join(R, 'scripts/verifie_stages_champ.py')}
exec(src, ns)
L = json.load(open(ns['F']))['o']
S = ns['LOTS']['prix_d']
for i, o in enumerate(L):
    if o[4] in S and not o[8]:
        print(i, o)
