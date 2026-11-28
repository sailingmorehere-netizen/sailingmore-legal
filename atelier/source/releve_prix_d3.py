# © 2026 Sailing More — tous droits réservés. All rights reserved.
import json, os, re, subprocess, html
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
d = json.load(open(os.path.join(R, 'projets/sailingmore/site/stages-proches.json')))
for i, mot in ((169, r'\d{3}'), (170, r'Euro|Preis|Gebühr'), (172, r'Euro|Preis|Gebühr'), (118, r'prix|€|euro|\d{3}\s?'), (121, r'prix|€|euro'), (211, r'Euro|€|Preis'), (273, r'£|Fee|price'), (213, r'€')):
    o = d['o'][i]
    t = subprocess.run(['curl', '-sL', '-m', '25', '-A', 'Mozilla/5.0', o[10]], capture_output=True, timeout=40).stdout.decode('utf8', 'replace')
    t = re.sub(r'(?s)<(script|style).*?</\1>', ' ', t)
    t = html.unescape(re.sub(r'<[^>]+>', ' ', t)); t = re.sub(r'\s+', ' ', t)
    print(i, o[3][:40])
    for m in list(re.finditer(mot, t, re.I))[:5]:
        print('    ', t[max(0, m.start() - 60):m.end() + 60])
