import json, re
D = "/opt/data/cache/claude-nuit/travail/"
def blob(page, ident):
    h = open(D + "sortie-test/enligne-" + page + ".html", encoding="utf-8").read()
    m = re.search(r'<script[^>]*id="%s"[^>]*>(.*?)</script>' % ident, h, re.S)
    return json.loads(m.group(1)) if m else None, h
r, hr = blob("regles-de-course", "donnees-regles")
print("regles cles", list(r.keys()))
rg = r["regles"]; print("nb regles", len(rg)); print("champs", list(rg[0].keys()))
print("parties", [(p.get("id"), str(p.get("nom"))[:40]) for p in r["parties"]])
for k in ("exemple", "ex", "exemples", "schema", "image", "video"):
    print(k, sum(1 for x in rg if x.get(k)))
print("exemple type", {k: (str(v)[:60]) for k, v in rg[0].items()})
print("ids", [x.get("num") or x.get("id") for x in rg][:200])
l, hl = blob("lexique", "donnees-lexique")
t = [x for th in l["themes"] for x in th["termes"]]
print("termes", len(t), "champs", list(t[0].keys()))
for k in t[0].keys():
    print(" ", k, sum(1 for x in t if x.get(k)))
print("themes", [(th.get("nom", {}) if not isinstance(th.get("nom"), dict) else th["nom"].get("fr"), len(th["termes"])) for th in l["themes"]])
print("svg/img dans lexique html", len(re.findall(r"<svg", hl)), len(re.findall(r"<img", hl)))
s = json.load(open(D + "projets/sailingmore/stages.json"))
print("stages maj", s["maj"]); print(json.dumps(s["offres"], ensure_ascii=False)[:1500])
hs = open(D + "sortie-test/enligne-stages.html", encoding="utf-8").read()
print("og index", len(re.findall("og:", open(D + "sortie-test/enligne-index.html", encoding="utf-8").read())))
print("stages-proches.js refs", len(re.findall("stages-proches", hs)))
