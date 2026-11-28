# © 2026 Sailing More — tous droits réservés. All rights reserved.
import json, os, re
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = open(os.path.join(R, 'scripts/verifie_stages_champ.py')).read()
m = re.search(r"'prix_d': \[(.*?)\]", src, re.S)
ecoles = re.findall(r"'([^']+)'", m.group(1))
d = json.load(open(os.path.join(R, 'projets/sailingmore/site/stages-proches.json')))
print(list(d.keys()))
for k in d:
    if k != 'o':
        print(k, str(d[k])[:300])
sel = [o for o in d['o'] if o[4] in ecoles]
from collections import Counter
c = Counter((o[4], bool(o[8])) for o in sel)
for k, v in sorted(c.items()):
    print(k, v)
for o in sel:
    if not o[8]:
        print(json.dumps(o, ensure_ascii=False))
        break
for o in sel:
    if o[8]:
        print(json.dumps(o, ensure_ascii=False))
        break
