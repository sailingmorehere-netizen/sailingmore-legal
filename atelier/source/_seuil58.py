import json
from pathlib import Path
S = Path(__file__).resolve().parent.parent / "projets/sailingmore/site"
d = json.load(open(S / "bateaux-fiches.json"))
for b in d["bateaux"]:
    n = len({(s["url"], s["citation"]) for s in b["sources"]})
    print(b["slug"], n, sorted(set(b) - {"slug","nom","constructeur","architecte","loa_m","beam_m","draft_min_m","draft_max_m","deplacement_kg","production_debut","production_fin","sources","divergences","notes","confiance"}))
for s in ("beneteau-oceanis-37", "jeanneau-sun-odyssey-33i"):
    b = [x for x in d["bateaux"] if x["slug"] == s][0]
    print(json.dumps({k: v for k, v in b.items() if k != "sources"}, ensure_ascii=False)[:1500])
    print(b["sources"][0])
