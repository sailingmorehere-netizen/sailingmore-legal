# © 2026 Sailing More — tous droits réservés. All rights reserved.
"""Lecture seule : télécharge les 60 pages sans prix du lot D et liste les montants repérés (€, CHF, £, EUR)."""
import json, os, re, subprocess, sys, html
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
noms = re.findall(r"'([^']+)'", re.search(r"'prix_d': \[(.*?)\],\n\}", open(os.path.join(R, 'scripts/verifie_stages_champ.py')).read(), re.S).group(1))
d = json.load(open(os.path.join(R, 'projets/sailingmore/site/stages-proches.json')))
PAT = re.compile(r'(?:€\s?\d[\d.,\s]*\d|\d[\d.,]*\s?(?:€|EUR|CHF|Fr\.|£|euro)|(?:CHF|EUR|£|ab)\s?\d[\d.,\']*)', re.I)
out = {}
for i, o in enumerate(d['o']):
    if o[4] in noms and o[8] in (None, '', 0):
        try:
            t = subprocess.run(['curl', '-sL', '-m', '25', '-A', 'Mozilla/5.0', o[10]], capture_output=True, timeout=40).stdout.decode('utf8', 'replace')
        except Exception as e:
            out[i] = ['ERR %s' % e]; continue
        t = re.sub(r'(?s)<(script|style).*?</\1>', ' ', t)
        t = html.unescape(re.sub(r'<[^>]+>', ' ', t))
        t = re.sub(r'\s+', ' ', t)
        res = []
        for m in PAT.finditer(t):
            res.append(t[max(0, m.start() - 40):m.end() + 15])
            if len(res) >= 6: break
        out[i] = [len(t)] + res
        print(i, o[4], '|', o[3], '|', len(t))
        for r in res: print('    ', r)
json.dump(out, open(os.path.join(R, 'releve_prix_d.json'), 'w'), ensure_ascii=False, indent=1)
