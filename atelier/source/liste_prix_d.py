import json, os, sys
sys.argv = ['x']
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = open(os.path.join(R, 'scripts/verifie_stages_champ.py')).read().split('COL =')[0]
ns = {}
exec(src.replace('__file__', repr(os.path.join(R, 'scripts/x.py'))), ns)
S = set(sum([ns['LOTS']['prix_d']], []))
d = json.load(open(ns['F']))
print(list(d.keys()))
for i, o in enumerate(d['o']):
    if o[4] in S and o[8] in (None, '', 0):
        print(i, json.dumps(o, ensure_ascii=False))
