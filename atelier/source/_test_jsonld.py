"""Essai en mémoire (rien n'est écrit) : chaque page produit exactement un bloc JSON-LD, JSON valide."""
import json, re, sys, py_compile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))

for f in ("accueil_site", "cours_page", "regates_page", "regles_page", "lexique_page", "stages_page", "bateaux_page", "jsonld"):
    py_compile.compile(str(Path(__file__).resolve().parent / f"{f}.py"), doraise=True)
print("compilation ok")

import cours_page, regates_page, regles_page, lexique_page, stages_page, jsonld

pages = {
    "cours": cours_page.page_cours(),
    "regates": regates_page.construire(regates_page.charger()),
    "regles": regles_page.page_regles(),
    "lexique": lexique_page.page_lexique(),
}
try:
    pages["stages"] = stages_page._html({"ui": stages_page.UI, "offres": [], "langues": stages_page.LANGUES,
                                         "pays": [], "ecoles": [], "pays_ecole": [], "langues_presentes": [],
                                         "niveaux": [], "types": []})
except Exception as ex:  # noqa: BLE001
    print("stages: essai impossible:", repr(ex))
pages["index(jsonld seul)"] = jsonld.bloc(jsonld.site_web(), jsonld.organisation())

for nom, h in pages.items():
    blocs = re.findall(r'<script type="application/ld\+json">(.*?)</script>', h, re.S)
    ok = len(blocs) == 1
    j = json.loads(blocs[0]) if blocs else {}
    types = [n.get("@type") for n in j.get("@graph", [])]
    from collections import Counter
    print(nom, "blocs:", len(blocs), "OK" if ok else "KO", "octets:", len(blocs[0]) if blocs else 0, dict(Counter(types)))
    print("  canonical:", "canonical" in h)
