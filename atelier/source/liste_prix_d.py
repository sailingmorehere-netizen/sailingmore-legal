import json, os, re
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = open(os.path.join(R, 'scripts/verifie_stages_champ.py')).read()
d = json.load(open(os.path.join(R, 'projets/sailingmore/site/stages-proches.json')))
noms = re.findall(r"'([^']+)'", re.search(r"'prix_d': \[(.*?)\],\n\}", src, re.S).group(1))
print({k: (v if k != 'o' else '...') for k, v in d.items()})
print(d['o'][0])
for i, o in enumerate(d['o']):
    if o[4] in noms and o[8] in (None, '', 0):
        print(i, o)
