# © 2026 Sailing More — tous droits réservés. All rights reserved.
import json, os, re
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = open(os.path.join(R, 'scripts/verifie_stages_champ.py')).read()
m = re.search(r"'prix_d': \[(.*?)\]", src, re.S)
ec = re.findall(r"'([^']+)'", m.group(1))
d = json.load(open(os.path.join(R, 'projets/sailingmore/site/stages-proches.json')))
for i, o in enumerate(d['o']):
    if o[4] in ec and not o[8]:
        print(i, o[4], '|', o[3], '|', o[10], '|', o[6])
