import json, re
R = "/opt/data/cache/claude-nuit/travail/"
e = json.load(open(R + "sortie-test/etude-six-langues.json"))
for p in e["pages"]:
    if p["page"] in ("regles-de-course.html", "stages.html", "lexique.html"):
        print(p["page"], json.dumps({k: p[k] for k in p if k not in ("page",)}, ensure_ascii=False)[:1800])
        print()
# contenu
S = R + "projets/sailingmore/"
st = json.load(open(S + "stages.json"))
print("stages type", type(st).__name__, (list(st)[:6] if isinstance(st, dict) else len(st)))
lx = json.load(open(S + "lexique.json"))
print("lexique type", type(lx).__name__, (list(lx)[:6] if isinstance(lx, dict) else len(lx)))
rg = json.load(open(R + "scripts/regles.json"))
print("regles type", type(rg).__name__, (list(rg)[:8] if isinstance(rg, dict) else len(rg)))
