import json, re, collections
D = "/opt/data/cache/claude-nuit/travail/"
S = D + "sortie-test/"
def blob(page, ident):
    h = open(S + "enligne-" + page + ".html", encoding="utf-8").read()
    m = re.search(r'<script[^>]*id="%s"[^>]*>(.*?)</script>' % ident, h, re.S)
    return json.loads(m.group(1))
L = ["fr", "de", "en", "it", "es", "pt"]
r = blob("regles-de-course", "donnees-regles")
rg = r["regles"]
print("langues", r["langues"], "ui cles", len(r["ui"]))
print("parties cles", [p if isinstance(p, str) else list(p.keys()) for p in r["parties"]][:2])
par = collections.Counter(x["partie"] for x in rg)
print("par partie", dict(par))
print("appendices", sorted({x["appendice"] for x in rg if x["appendice"]}))
print("avec exemples", sum(1 for x in rg if x["exemples"]), "total exemples", sum(len(x["exemples"]) for x in rg))
print("distribution nb ex", dict(collections.Counter(len(x["exemples"]) for x in rg)))
print("sans exemple hors defs", [x["num"] or x["cle"] for x in rg if not x["exemples"] and x["partie"] != "defs"])
print("sanction renseignee", sum(1 for x in rg if x["sanction"]))
for f in ("titre", "resume"):
    print(f, {l: sum(1 for x in rg if isinstance(x[f], dict) and x[f].get(l)) for l in L})
ex = [e for x in rg for e in x["exemples"]]
print("type exemple", type(ex[0]).__name__, str(ex[0])[:200] if ex else None)
if ex and isinstance(ex[0], dict):
    print("ex langues", {l: sum(1 for e in ex if any(isinstance(v, dict) and v.get(l) for v in e.values()) or e.get(l)) for l in L})
# longueur du resume en fr, de, ..
print("long resume moyenne", {l: round(sum(len(x["resume"].get(l, "")) for x in rg) / len(rg)) for l in L})
print("themes", [(t if isinstance(t, str) else t) for t in r["themes"]][:3])
# lexique
l = blob("lexique", "donnees-lexique")
print("lex langues", l["langues"], "theme0", {k: (str(v)[:80]) for k, v in l["themes"][0].items() if k != "termes"})
t = [x for th in l["themes"] for x in th["termes"]]
print("terme0", json.dumps(t[0], ensure_ascii=False)[:400])
for lg in L:
    n = 0
    for x in t:
        for k in ("mot", "def"):
            v = x.get(k)
            if isinstance(v, dict) and v.get(lg):
                n += 1
    print("lexique", lg, n, "valeurs sur", 2 * len(t))
dup = [k for k, c in collections.Counter(x["mot"].get("fr") if isinstance(x["mot"], dict) else x["mot"] for x in t).items() if c > 1]
print("mots doublons", dup)
ld = [len((x["def"].get("fr") if isinstance(x["def"], dict) else x["def"]) or "") for x in t]
print("def fr longueur min/moy/max", min(ld), round(sum(ld) / len(ld)), max(ld))
# lexique -> liens internes entre mots / vers regles
h = open(S + "enligne-lexique.html", encoding="utf-8").read()
print("lexique liens vers regles", len(re.findall("regles-de-course", h)), "vers cours", len(re.findall("cours.html", h)), "ancres id", len(re.findall(r'id="t-', h)))
# stages
s = json.load(open(D + "projets/sailingmore/stages.json"))
print("offres", len(s["offres"]), "ecoles", len({o["ecole"] for o in s["offres"]}), "niveau renseigne", sum(1 for o in s["offres"] if o["niveau"]))
hs = open(S + "enligne-stages.html", encoding="utf-8").read()
print("stages: <article/li/tr/carte>", len(re.findall(r'class="[^"]*(?:offre|carte|card|stage)[^"]*"', hs)))
print("stages: data-t cles", len(set(re.findall(r'data-t="([^"]+)"', hs))), "script ids", re.findall(r'<script[^>]*id="([^"]+)"', hs))
# six langues, trois pages
e = json.load(open(S + "etude-six-langues.json"))
for p in e["pages"]:
    if p["page"] in ("regles-de-course.html", "stages.html", "lexique.html"):
        print(p["page"], json.dumps({k: p[k] for k in ("data_t_elements", "data_t_cles_uniques", "tables", "entrees_plurilingues", "data_l", "selecteur_langue", "detecte_langue", "sans_js", "en_ligne")}, ensure_ascii=False)[:900])
        print("  sans table:", p["data_t_sans_table"][:30], len(p["data_t_sans_table"]))
