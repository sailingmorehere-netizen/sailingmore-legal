"""Empreintes des fichiers du site : python3 _empreintes_site.py avant|apres|comparer"""
import hashlib, json, os, sys, shutil
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
S = os.path.join(R, "projets", "sailingmore", "site")
AV = os.path.join(R, "sortie-test", "avant-etude")
J = os.path.join(R, "sortie-test", "empreintes.json")
def h():
    return {n: hashlib.sha256(open(os.path.join(S, n), "rb").read()).hexdigest()[:12] for n in sorted(os.listdir(S)) if n.endswith((".html", ".js", ".xml", ".txt", ".json"))}
a = sys.argv[1]
if a == "avant":
    os.makedirs(AV, exist_ok=True)
    for n in h(): shutil.copy2(os.path.join(S, n), os.path.join(AV, n))
    json.dump(h(), open(J, "w")); print(len(h()), "fichiers sauvegardés dans", AV)
else:
    av = json.load(open(J)); ap = h()
    for n in sorted(set(av) | set(ap)):
        if av.get(n) != ap.get(n):
            t = lambda p: os.path.getsize(p) if os.path.exists(p) else None
            print("CHANGÉ" if n in av and n in ap else "AJOUTÉ/SUPPRIMÉ", n, t(os.path.join(AV, n)), "->", t(os.path.join(S, n)))
    print("comparaison terminée")
