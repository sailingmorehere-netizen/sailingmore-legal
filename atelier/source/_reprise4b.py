import json, re
D = "/opt/data/cache/claude-nuit/travail/projets/sailingmore/"
s = json.load(open(D + "stages.json"))
print("stages type", type(s).__name__, list(s.keys())[:12] if isinstance(s, dict) else len(s))
if isinstance(s, dict):
    for k, v in s.items():
        if isinstance(v, list):
            print(k, len(v), json.dumps(v[0], ensure_ascii=False)[:500] if v else "")
l = json.load(open(D + "lexique.json"))
print("lexique", type(l).__name__, list(l.keys())[:8] if isinstance(l, dict) else len(l))
th = l.get("themes", []) if isinstance(l, dict) else []
n = 0; img = 0; cles = set()
for t in th:
    for m in t.get("termes", []):
        n += 1; cles.update(m.keys())
        if any(k in m for k in ("image", "img", "schema", "figure")): img += 1
print("termes", n, "avec image/schema", img, "cles", sorted(cles))
h = open("/opt/data/cache/claude-nuit/travail/sortie-test/enligne-lexique.html", encoding="utf-8").read()
print("lexique <img>", len(re.findall(r"<img", h)), "<svg", len(re.findall(r"<svg", h)))
r = open("/opt/data/cache/claude-nuit/travail/sortie-test/enligne-regles-de-course.html", encoding="utf-8").read()
print("regles <img>", len(re.findall(r"<img", r)), "h3", len(re.findall(r"<h3", r)))
print("regles jsonld", re.findall(r'"@type":\s*"(\w+)"', r))
