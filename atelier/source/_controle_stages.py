"""Contrôles de stages.html (copie de travail) + essai d'injection du bloc sur une page temporaire."""
import json, re, shutil, sys, tempfile
from pathlib import Path

ICI = Path(__file__).resolve().parent
sys.path.insert(0, str(ICI))
import stages_page

site = ICI.parent / "projets/sailingmore/site"
h = (site / "stages.html").read_text(encoding="utf-8")
m = re.search(r'<script id="donnees" type="application/json">(.*?)</script>', h, re.S)
d = json.loads(m.group(1).replace("<\\/", "</"))
o = d["offres"]
print("offres", len(o), "liens distincts", len({x["lien"] for x in o}), "poids Ko", len(h) // 1024)
visible = re.sub(r'<script.*?</script>|<style.*?</style>', "", h, flags=re.S)
print("None/null/undefined visibles", len(re.findall(r'\b(None|null|undefined)\b', visible)))
print("img sans src", len(re.findall(r'<img(?![^>]*\bsrc=)', h)))
print("images citées sans fichier", sum(1 for x in o if x.get("image") and not (site / x["image"]).exists()))
j = json.loads((site / "stages-proches.json").read_text())
print("proches", len(j["o"]), "sans lien", sum(1 for r in j["o"] if not r[10]))
# injection sur une page jetable
t = Path(tempfile.mkdtemp(dir=ICI.parent / "sortie-test"))
(t / "index.html").write_text("<html><body><main>x</main></body></html>")
print("injecté", stages_page.injecter_bloc(t), "puis", stages_page.injecter_bloc(t))
