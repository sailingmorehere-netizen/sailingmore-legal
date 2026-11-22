"""Compare deux regates.html : épreuves embarquées (JSON #donnees). Usage : _comparer_regates.py AVANT APRES
Sans argument : copie la page de la copie vers sortie-test/regates_avant.html (baseline)."""
import json, re, sys, shutil
from pathlib import Path
ICI = Path(__file__).resolve().parent.parent
def charge(p):
    h = Path(p).read_text(encoding="utf-8")
    m = re.search(r'<script type="application/json" id="donnees">(.*?)</script>', h, re.S)
    return json.loads(m.group(1)), len(h)
if len(sys.argv) < 3:
    shutil.copy(ICI / "projets/sailingmore/site/regates.html", ICI / "sortie-test/regates_avant.html")
    print("baseline copiée"); raise SystemExit
a, la = charge(sys.argv[1]); b, lb = charge(sys.argv[2])
cle = lambda e: (e["nom"], e["debut"], e["fin"], e["ville"])
sa = {cle(e) for e in a["epreuves"]}; sb = {cle(e) for e in b["epreuves"]}
print("avant", len(a["epreuves"]), "après", len(b["epreuves"]), "octets", la, lb)
print("perdues", len(sa - sb), sorted(sa - sb)[:10]); print("gagnées", len(sb - sa), sorted(sb - sa)[:10])
print("aujourdhui", a["aujourdhui"], b["aujourdhui"])
