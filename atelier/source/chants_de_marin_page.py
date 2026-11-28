# © 2026 Sailing More — tous droits réservés. All rights reserved.
"""Génère site/chants-de-marin.html : sommaire des pages chant-*.html existantes.
Brouillon de cadrage (tâche 8) : texte seul, aucune balise audio, aucun enregistrement."""
import glob, html, os, re

RACINE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "projets", "sailingmore", "site")
lignes = []
for f in sorted(glob.glob(os.path.join(RACINE, "chant-*.html"))):
    t = re.search(r"<title>([^<]*)", open(f, encoding="utf-8").read())
    titre = t.group(1).split(" · ")[0].split(" | ")[0] if t else os.path.basename(f)
    lignes.append('<li><a href="%s">%s</a></li>' % (os.path.basename(f), html.escape(titre)))

page = """<!doctype html><html lang="fr"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Chants de marin | Sailing More</title>
<meta name="description" content="Les chants de marin de Sailing More : textes, origine et usage à bord.">
<meta name="robots" content="noindex"><!-- brouillon : à retirer après validation du cadrage -->
</head><body><main>
<h1>Chants de marin</h1>
<p>Les chants qui rythmaient les manœuvres à bord : %d fiches, en texte seul (ni audio ni enregistrement).</p>
<ul>
%s
</ul>
</main></body></html>
""" % (len(lignes), "\n".join(lignes))
open(os.path.join(RACINE, "chants-de-marin.html"), "w", encoding="utf-8").write(page)
print(len(lignes), "chants")
