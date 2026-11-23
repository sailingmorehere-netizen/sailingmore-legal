#!/usr/bin/env python3
# Génère projets/sailingmore/site/simulateur.html (page autonome, six langues) et lance les tests.
# Usage : python3 scripts/simulateur_priorites.py   (depuis la copie de travail)
import json, math, os, re, shutil, subprocess, sys

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ICI)
import simulateur_donnees as D

RACINE = os.path.dirname(ICI)
SITE = os.path.join(RACINE, "projets", "sailingmore", "site")

# ------------------------------------------------------------------ tests
def vis(o, v):
    """Feux de o vus depuis v — même logique que le JS."""
    b = math.degrees(math.atan2(v["x"] - o["x"], -(v["y"] - o["y"])))
    r = b - o["h"]
    while r > 180: r -= 360
    while r <= -180: r += 360
    a = abs(r)
    if o["k"] == "n": return {"R2"}
    out = set()
    if o["k"] == "f": out.add("RW")
    if o["k"] in ("m", "g", "u") and a <= 112.5: out.add("M")
    if a <= 112.5:
        if a <= 5: out |= {"R", "G"}
        else: out.add("G" if r > 0 else "R")
    else: out.add("S")
    return out

def rel(o, v):
    r = math.degrees(math.atan2(v["x"] - o["x"], -(v["y"] - o["y"]))) - o["h"]
    while r > 180: r -= 360
    while r <= -180: r += 360
    return r

def tack(h):  # vent du nord
    return "port" if 0 < h % 360 < 180 else "star"

def along(b):
    r = math.radians(b["h"]); return b["x"] * math.sin(r) - b["y"] * math.cos(r)

def closest(a, b):
    best = 1e9
    for i in range(0, 2001):
        t = i / 20
        pa = (a["x"] + t * math.sin(math.radians(a["h"])), a["y"] - t * math.cos(math.radians(a["h"])))
        pb = (b["x"] + t * math.sin(math.radians(b["h"])), b["y"] - t * math.cos(math.radians(b["h"])))
        best = min(best, math.dist(pa, pb))
    return best

def tester():
    err = []
    sc = D.SC
    if len(sc) != 50: err.append("il faut 50 scénarios, %d trouvés" % len(sc))
    if [s["id"] for s in sc] != list(range(1, 51)): err.append("identifiants non consécutifs")
    n = {f: sum(1 for s in sc if s["fam"] == f) for f in ("rrs", "col", "luc")}
    if n != {"rrs": 30, "col": 13, "luc": 7}: err.append("répartition %s" % n)
    for l in D.LANGS:
        for k, v in D.T.items():
            if len(v) != 6: err.append("raison %s : %d langues" % (k, len(v)))
    for k, v in D.T.items():
        for i, x in enumerate(v):
            if not x.strip() or len(x) > 220: err.append("raison %s langue %d vide ou trop longue" % (k, i))
            if x.count(".") > 1 and "(" not in x: err.append("raison %s langue %d : plus d'une phrase ?" % (k, i))
    for k, v in D.UI.items():
        if len(v) != 6 or not all(x.strip() for x in v): err.append("ui %s incomplet" % k)
    for s in sc:
        i = s["id"]
        if s["reason"] not in D.T: err.append("%d raison inconnue" % i)
        if s["ans"] not in ("A", "B", "AB"): err.append("%d réponse" % i)
        ids = [b["id"] for b in s["boats"]]
        if ids != ["A", "B"]: err.append("%d bateaux A/B" % i)
        for b in s["boats"]:
            if not (0 <= b["x"] <= 100 and 0 <= b["y"] <= 100): err.append("%d %s hors cadre" % (i, b["id"]))
        A, Bt = s["boats"]
        by = {"A": A, "B": Bt}
        r = s["reason"]
        if r in ("r10", "r10b", "c12a"):
            win = "B" if s["ans"] == "A" else "A"
            if s["ans"] == "AB": err.append("%d bord" % i); continue
            if tack(by[s["ans"]]["h"]) != "port" or tack(by[win]["h"]) != "star":
                err.append("%d : celui qui s'écarte n'est pas bâbord amures" % i)
            if closest(A, Bt) > 6: err.append("%d : pas de route de collision (%.1f)" % (i, closest(A, Bt)))
        if r in ("r11", "c12b"):
            o = by[s["ans"]]; p = by["B" if s["ans"] == "A" else "A"]
            if not (o["y"] < p["y"]): err.append("%d : le bateau désigné n'est pas au vent" % i)
            if o["h"] != p["h"] or abs(along(o) - along(p)) > 8: err.append("%d : pas de recouvrement" % i)
        if r in ("r12", "c13"):
            o = by[s["ans"]]; p = by["B" if s["ans"] == "A" else "A"]
            if o["h"] != p["h"] and not (r == "c13" and abs(o["h"] - p["h"]) <= 10): err.append("%d : caps différents" % i)
            if not (along(o) < along(p) - (8 if r == "r12" else 0) + (0 if r == "r12" else 0)):
                err.append("%d : le bateau désigné n'est pas derrière" % i)
            if r == "r12" and along(p) - along(o) <= 8: err.append("%d : recouvrement" % i)
        if r in ("r18o", "r18b"):
            m = s["marks"][0]; o = by[s["ans"]]; p = by["B" if s["ans"] == "A" else "A"]
            ov = abs(along(o) - along(p)) <= 8
            if r == "r18o":
                if not ov: err.append("%d : pas de recouvrement" % i)
                if math.dist((o["x"], o["y"]), m) < math.dist((p["x"], p["y"]), m): err.append("%d : le désigné est intérieur" % i)
            else:
                if ov: err.append("%d : recouvrement" % i)
                if not along(o) < along(p): err.append("%d : le désigné n'est pas derrière" % i)
        if r == "c15":
            if not 0 < rel(A, Bt) < 112.5: err.append("%d : B n'est pas sur la droite de A" % i)
        if s["fam"] == "luc":
            v = vis(Bt, A)
            att = {"lred": ({"R"}, "A"), "lgreen": ({"G"}, "B"), "lhead": ({"R", "G", "M"}, "AB"),
                   "lstern": ({"S"}, "A"), "lsailpow": (None, "A"), "lfish": (None, "A"), "lnuc": ({"R2"}, "A")}[r]
            if att[0] is not None and not att[0] <= v: err.append("%d : feux vus %s attendus %s" % (i, v, att[0]))
            if r == "lstern" and "S" not in v: err.append("%d : pas de feu de poupe" % i)
            if r == "lred" and ("G" in v or "S" in v): err.append("%d : feux mélangés %s" % (i, v))
            if r == "lgreen" and "R" in v: err.append("%d : feux mélangés %s" % (i, v))
            if r == "lsailpow" and ("M" in v or not v & {"R", "G"}): err.append("%d : voilier non reconnaissable %s" % (i, v))
            if r == "lfish" and "RW" not in v: err.append("%d : pêche" % i)
            if s["ans"] != att[1]: err.append("%d : réponse feux" % i)
    return err

# ------------------------------------------------------------------ page
GABARIT = open(os.path.join(ICI, "simulateur_gabarit.html"), encoding="utf8").read()

def construire():
    data = D.export()
    js = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    html = GABARIT.replace("__DATA__", js)
    sortie = os.path.join(SITE, "simulateur.html")
    open(sortie, "w", encoding="utf8").write(html)
    return sortie, len(html.encode("utf8"))

def test_js(chemin):
    nd = shutil.which("node")
    if not nd: return "node absent : syntaxe JS non vérifiée"
    h = open(chemin, encoding="utf8").read()
    m = re.search(r"<script>(.*?)</script>", h, re.S)
    tmp = os.path.join(RACINE, "_simu_test.js")
    open(tmp, "w", encoding="utf8").write(m.group(1))
    p = subprocess.run([nd, "--check", tmp], capture_output=True, text=True)
    os.remove(tmp) if os.path.exists(tmp) else None
    return "node --check OK" if p.returncode == 0 else "node --check ÉCHEC : " + p.stderr[:400]

if __name__ == "__main__":
    e = tester()
    if e:
        print("TESTS ÉCHEC"); [print(" -", x) for x in e]; sys.exit(1)
    print("tests données : OK (50 scénarios, 30/13/7, six langues, géométrie et feux cohérents)")
    ch, taille = construire()
    print("écrit", ch, taille, "octets")
    print(test_js(ch))
