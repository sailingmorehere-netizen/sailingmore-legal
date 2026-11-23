"""Remet la feuille d'équilibre (equilibre.css absent de la copie) sur les pages qui l'ont perdue en étant reconstruites,
en reprenant le bloc déjà posé sur les autres pages de la copie — même texte que poser_equilibre()."""
import re
D = "/opt/data/cache/claude-nuit/travail/projets/sailingmore/site/"
pat = re.compile(r'<style id="equilibre">.*?</style>\n?', re.S)
blocs = {}
for p in ("index", "regates", "stages", "jeux", "404"):
    m = pat.search(open(D + p + ".html", encoding="utf-8").read())
    blocs[p] = m.group(0) if m else None
print({k: (len(v) if v else None) for k, v in blocs.items()})
ref = blocs["regates"]
assert ref and all(v == ref for v in blocs.values() if v), "blocs différents : je m'arrête"
for p in ("regles-de-course", "lexique", "cours", "bateaux"):
    f = D + p + ".html"
    h = open(f, encoding="utf-8").read()
    if 'id="equilibre"' in h:
        print(p, "déjà posé"); continue
    h = h.replace("</head>", ref + ("" if ref.endswith("\n") else "\n") + "</head>", 1)
    open(f, "w", encoding="utf-8").write(h)
    print(p, "posé", len(h))
