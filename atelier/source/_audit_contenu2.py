import json, re, collections
R = "/opt/data/cache/claude-nuit/travail/"
S = R + "projets/sailingmore/"
st = json.load(open(S + "stages.json"))
o = st["offres"]
print("stages maj", st["maj"], "offres", len(o), "cles", sorted(o[0]) if isinstance(o, list) else list(o)[:3])
if isinstance(o, list):
    for k in ("prix", "url", "ecole", "pays", "langue", "niveau", "duree", "date", "dates"):
        if k in o[0]:
            v = [x.get(k) for x in o]
            print(k, "vides:", sum(1 for x in v if x in (None, "", 0, [])), "distincts:", len(set(map(str, v))))
    print("ecoles", len({x.get("ecole") or x.get("organisme") for x in o}))
    print("exemple", json.dumps(o[0], ensure_ascii=False)[:500])
lx = json.load(open(S + "lexique.json"))
n = 0; cles = collections.Counter(); img = 0
for t in lx["themes"]:
    for m in t["termes"]:
        n += 1
        for k, v in m.items():
            if v not in (None, "", [], {}):
                cles[k] += 1
print("lexique termes", n, "themes", len(lx["themes"]), dict(cles))
print("theme exemple", {k: (v if k != "termes" else len(v)) for k, v in lx["themes"][0].items()})
rg = json.load(open(R + "scripts/regles.json"))
print("regles", len(rg["regles"]), "complet", rg["complet"], rg["_note"][:300], rg.get("_suite"))
print("parties", [(p.get("id") or p.get("num"), (p.get("nom") or {}).get("fr") if isinstance(p.get("nom"), dict) else p.get("nom")) for p in rg["parties"]])
r0 = rg["regles"][0]
print("cles regle", sorted(r0))
c = collections.Counter(); ex = 0
for r in rg["regles"]:
    for k, v in r.items():
        if v not in (None, "", [], {}):
            c[k] += 1
print(dict(c))
print("par partie", collections.Counter(str(r.get("partie")) for r in rg["regles"]))
print("themes", [(t.get("id"), (t.get("nom") or {}).get("fr") if isinstance(t.get("nom"), dict) else t.get("nom")) for t in rg["themes"]])
# lexique en ligne : mots avec image / schema
h = open(R + "sortie-test/enligne-lexique.html", encoding="utf-8").read()
print("lexique en ligne: svg", len(re.findall(r"<svg", h)), "img", len(re.findall(r"<img", h)), "schema", len(re.findall(r"schema|schéma", h, re.I)))
h = open(R + "sortie-test/enligne-regles-de-course.html", encoding="utf-8").read()
print("regles en ligne: svg", len(re.findall(r"<svg", h)), "video", len(re.findall(r"video|youtube", h, re.I)), "details", len(re.findall(r"<details", h)))
