"""Tâche 68 — contrôle de l'entrée en carrés. `pavillons_cours` et `simulateur_exercice` manquent dans la copie
de travail : on les remplace par des bouchons, ce qui contrôle NOTRE logique (carrés, familles, ancres,
sommaire), pas le poids final de cours.html. Écrit la page de test dans sortie-test/cours68.html.

    python3 scripts/_verif68.py
"""
import re
import sys
import types
from pathlib import Path

ICI = Path(__file__).resolve().parent
sys.path.insert(0, str(ICI))

stub = types.ModuleType("pavillons_cours")
stub.CHAPITRE_PAVILLONS = 13
stub.CSS = ""
stub.baliser = lambda s: s
stub.rendre = lambda s: s
stub.bloc = lambda *a, **k: ""
stub.ecrire_pages = lambda *a, **k: None


def _poser(textes):
    for lang, t in textes.items():
        for cid in ("pavillons", "signaux_course", "vhf"):
            t["ch"][cid] = {"t": f"Chapitre {cid} ({lang})", "p": ["x"], "q": "q", "a": "a"}


stub.poser_textes = _poser
sys.modules["pavillons_cours"] = stub

import cours_page  # noqa: E402

html = cours_page.page_cours()
sortie = ICI.parent / "sortie-test"
sortie.mkdir(exist_ok=True)
(sortie / "cours68.html").write_text(html, encoding="utf-8")

erreurs = 0
n_attendu = sum(1 for c in cours_page.COURS if c["statut"] == "écrit")
for lang in cours_page.LANGUES:
    m = re.search(rf'<div data-l="{lang}".*?(?=<div data-l="|</div>\n<script>)', html, re.S)
    bloc = m.group(0)
    carres = re.findall(r'<a class="case" href="#([^"]+)"', bloc)
    fam = re.findall(r"<h3>([^<]+)</h3><p class=\"sous-fam\">", bloc)
    ids = set(re.findall(r'id="([^"]+)"', bloc))
    manque = [h for h in carres if h not in ids]
    mauvaise_langue = [h for h in carres if not h.endswith("-" + lang)]
    h2_entree = len(re.findall(r'<section class="entree"[^>]*><h2', bloc))
    details = bloc.count("<details><summary>" + cours_page.ENTREE["sommaire"][lang])
    ok = (len(carres) == n_attendu and len(fam) == 4 and not manque and not mauvaise_langue
          and h2_entree == 1 and details == 1)
    erreurs += 0 if ok else 1
    print(lang, "carrés", len(carres), "familles", len(fam), "ancres sans id", manque, "mauvaise langue", mauvaise_langue,
          "h2", h2_entree, "sommaire replié", details, "OK" if ok else "ÉCHEC")
print("attendu", n_attendu, "carrés par langue ;", "ÉCHEC" if erreurs else "tout passe")
sys.exit(1 if erreurs else 0)
