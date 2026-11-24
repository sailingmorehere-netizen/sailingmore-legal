"""Lecture seule : second passage sur les pages sans montant repéré (mots-clés prix/Preis/precio/tariff + chiffre)."""
import json, os, re, subprocess, html
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
d = json.load(open(os.path.join(R, 'projets/sailingmore/site/stages-proches.json')))
KW = re.compile(r'(prix|tarif|Preis|Kosten|precio|prezzo|costo|price|cost|Euro|euros|€|CHF|£)\W{0,12}\D{0,25}\d', re.I)
for i in (118,119,120,121,122,164,167,168,171,173,174,211,212,214,215,216,272,311,313,375,401,76,77,78,79,227,229,231,374,123,165,166):
    o = d['o'][i]
    t = subprocess.run(['curl', '-sL', '-m', '25', '-A', 'Mozilla/5.0', o[10]], capture_output=True, timeout=40).stdout.decode('utf8', 'replace')
    t = re.sub(r'(?s)<(script|style).*?</\1>', ' ', t)
    t = html.unescape(re.sub(r'<[^>]+>', ' ', t)); t = re.sub(r'\s+', ' ', t)
    print(i, o[4], '|', o[3][:50])
    n = 0
    for m in KW.finditer(t):
        print('    ', t[max(0, m.start() - 50):m.end() + 40]); n += 1
        if n >= 4: break
