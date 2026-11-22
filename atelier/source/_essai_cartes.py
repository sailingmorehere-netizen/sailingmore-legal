"""Essai : génère les deux pages dans sortie-test/ et compte les positions. Peut être supprimé."""
import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import regates_page as R, stages_page as S
ici = Path(__file__).resolve().parent.parent
out = ici / "sortie-test"; out.mkdir(exist_ok=True)
d = json.loads((ici / "projets/sailingmore/regates.json").read_text())
ep = R.epreuves_pour_page(d)
tot = len(ep); avec = sum(1 for e in ep if "lat" in e); prec = sum(1 for e in ep if "lat" in e and not e["ap"]); ap = avec - prec
print("regates affichables", tot, "avec lat/lon", avec, "(précises", prec, ", centre du pays", ap, ") sans", tot-avec)
print("total regates.json", len(d["regates"]))
(out / "regates.html").write_text(R.construire(d), encoding="utf-8")
(out / "stages.html").write_text(S.construire(), encoding="utf-8")
for n in ("regates.html", "stages.html"):
    print(n, (out / n).stat().st_size)
