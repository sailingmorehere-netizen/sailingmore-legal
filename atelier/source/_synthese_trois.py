import json
D = "/opt/data/cache/claude-nuit/travail/"
e = json.load(open(D + "sortie-test/etude-six-langues.json"))
for p in e["pages"]:
    if p["page"] in ("regles-de-course.html", "stages.html", "lexique.html"):
        q = {k: v for k, v in p.items() if k != "data_t_sans_table"}
        print(json.dumps(q, ensure_ascii=False)[:1800]); print()
for f in ("stages.json", "lexique.json"):
    s = json.load(open(D + "projets/sailingmore/" + f))
    print(f, type(s).__name__, list(s.keys())[:10] if isinstance(s, dict) else len(s))
    if isinstance(s, dict):
        for k, v in list(s.items())[:6]:
            print(" ", k, type(v).__name__, len(v) if hasattr(v, "__len__") else v)
