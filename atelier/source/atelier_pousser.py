#!/usr/bin/env python3
# © 2026 Sailing More — tous droits réservés. All rights reserved.
"""Pousse un fichier source de `scripts/` dans l'atelier GitHub (branche `claude`).

Le site n'a qu'une source : `atelier/source/` sur la branche `claude`. Quand je corrige un script
ici, je le pousse par cette commande pour que l'atelier reste la vérité — sinon la prochaine
reconstruction repartirait d'une version ancienne et effacerait la correction.

    python3 scripts/atelier_pousser.py mer_louvoyage.py "mer : empreinte du moteur dans l'adresse"
"""
from __future__ import annotations

import base64
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

RACINE = Path("/opt/data")
DEPOT = "sailingmorehere-netizen/sailingmore-legal"
BRANCHE = "claude"
JETON = (RACINE / "credentials/github-token.txt").read_text().strip()
SOURCE = {"accueil_site.py", "site_blocks.py", "mer_louvoyage.py", "carte_site.py", "equilibre.css",
          "marque.py", "regates_page.py",
          # Flux RSS et sitemap (24/11/2026) : `accueil_site` les importe ; sans eux dans l'atelier,
          # la reconstruction du site s'arrête ou publie un flux périmé.
          "feed_rss.py", "sitemap_site.py",
          # Favoris (24/11/2026) : écrit js/favoris*.js, js/config.js et mes-favoris.html ; sans lui
          # dans l'atelier, la reconstruction perd la page.
          "favoris_page.py",
          # Comptes (24/11/2026) : écrans connexion / inscription / mon-compte, inertes en mode « local ».
          "comptes_page.py",
          # Modules importés par regates_page : sans eux dans l'atelier, la reconstruction du site
          # s'arrête sur « No module named regates_classes » et plus rien ne se publie.
          "regates_classes.py", "regates_drapeaux.py",
          # Pavillons (24/11/2026) : cours_page importe ce module pour les chapitres pavillons, signaux de
          # course et VHF ; sans lui dans l'atelier, la reconstruction s'arrête sur ImportError.
          "pavillons_cours.py",
          # Page des règles de course et sa source de données (22/11/2026).
          "regles_page.py", "regles.json",
          # Schémas « avant / pendant / après » et vidéo, sur la page des règles (22/11/2026).
          "regles_schemas.py",
          # Page des stages : le générateur et sa source de données, relevée sur les sites des écoles.
          "stages_page.py", "stages.json",
          # Deux oublis du même genre (24/11/2026) : `accueil_2026.py` est importé par `accueil_site`
          # et porte le corps de l'accueil ; `securite_page.py` pose la page de sécurité. Sans eux
          # dans l'atelier, une correction faite ici n'atteint jamais le site.
          "accueil_2026.py", "securite_page.py",
          # Trois générateurs oubliés dans cette liste : sans eux, une modification faite ici ne
          # pouvait pas entrer dans l'atelier, donc n'était jamais publiée — le 23/11/2026, neuf
          # tâches cochées « faites » n'avaient rien en ligne pour cette seule raison.
          "lexique_page.py", "bateaux_page.py", "cours_page.py", "lexique.json", "bateaux-images.json",
          # Une page par mot du lexique (25/11/2026) : `accueil_site` l'importe ; sans lui dans l'atelier,
          # la reconstruction passe sans erreur mais aucune page de mot n'est écrite, et le sitemap les oublie.
          "lexique_mot_page.py",
          # Traduction automatique du lexique (25/11/2026) : `accueil_site` l'importe ; sans lui, la page
          # ne se traduit pas toute seule pour un visiteur hors des six langues écrites.
          "trad_auto.py",
          # Les 42 pavillons du Code international de signaux (24/11/2026) : cours_page les lit à côté de lui.
          "pavillons.json",
          # Ajouts du 23/11/2026 : sans eux l'atelier reconstruit avec l'ancien code, la page
          # d'accueil perd la section des équivalences et grossit de 30 % de moins que la page en
          # ligne, donc le garde-fou refuse de publier et plus rien ne passe (ni le breton après).
          "equivalences_page.py", "stages_niveaux.py", "bateaux_dessins.py", "equivalences.json",
          # La démonstration d'où sort le moteur WebGL (23/11/2026) : elle est la vraie source du
          # suivi de la souris, et `mer_louvoyage.py` la lit pour régénérer `mer-louvoyage.js`.
          "demo-v3-detaillee.html",
          # L'exercice du simulateur posé dans le chapitre des priorités (25/11/2026) : `cours_page`
          # l'importe ; sans lui dans l'atelier, la reconstruction passe sans erreur, mais le chapitre
          # perd 38 % de son poids, le garde-fou refuse la page et plus rien ne se publie — panne
          # silencieuse trouvée ce matin sur `cours.html` (707 → 442 ko).
          "simulateur_exercice.py",
          # Page des chants de marins (24/11/2026) : le générateur et sa source de données.
          "chants_page.py", "chants-de-marin.json",
          # Deux pages entières écrites par Claude, publiées le 24/11/2026 : le fichier HTML complet
          # voyage tel quel dans `donnees/projets/sailingmore/pages/`, et `accueil_site` le recopie.
          "ports.html", "simulateur.html",
          # Page « bourse aux équipiers » (26/11/2026) : `accueil_site` l'importe ; sans elle dans
          # l'atelier, la reconstruction passe sans erreur mais la page n'est jamais écrite, et
          # l'entrée de menu pointe un 404.
          "bourses_page.py",
          # `accueil_site` la lance à chaque reconstruction pour refaire `go-liens.json` ; sans elle
          # dans l'atelier, la liste blanche reste périmée et les liens sortants tombent en 404.
          "clics_sortants.py"}

# Les fichiers de données voyagent sous `donnees/projets/sailingmore/`, là où le générateur les lit
# quand il tourne dans l'atelier. Sans cette carte, `equivalences.json` arriverait à côté du code et
# la page serait reconstruite vide, squelette à la place du contenu.
DEST = {"equivalences.json": "atelier/donnees/projets/sailingmore/equivalences.json",
        "chants-de-marin.json": "atelier/donnees/projets/sailingmore/chants-de-marin.json",
        # Le moteur WebGL n'est pas écrit dans `mer-louvoyage.js` : `mer_louvoyage.py` l'extrait de
        # cette démonstration (23/11/2026 : le suivi de la souris a été écrit là). Sans elle dans
        # l'atelier, la reconstruction régénère l'ancien moteur et la correction n'atteint jamais
        # le site.
        "demo-v3-detaillee.html": "atelier/donnees/cache/documents/demo-v3-detaillee.html",
        "ports.html": "atelier/donnees/projets/sailingmore/pages/ports.html",
        "simulateur.html": "atelier/donnees/projets/sailingmore/pages/simulateur.html"}
# Et sa source locale ne vit pas dans `scripts/` comme les autres données : ce fichier est né dans
# le projet, pas dans les scripts.
SRC = {"equivalences.json": RACINE / "projets/sailingmore/equivalences.json",
       "chants-de-marin.json": RACINE / "projets/sailingmore/chants-de-marin.json",
       "demo-v3-detaillee.html": RACINE / "cache/documents/demo-v3-detaillee.html",
       "ports.html": RACINE / "projets/sailingmore/pages/ports.html",
       "simulateur.html": RACINE / "projets/sailingmore/pages/simulateur.html"}

# Données que des générateurs lisent et qui n'avaient jamais voyagé (26/11/2026) : sans elles,
# l'atelier reconstruisait des pages plus pauvres que celles en ligne — lexique 195 entrées au lieu
# de 507, stages sans les offres du 25/11 — le garde-fou refusait quatre pages et plus rien ne se
# publiait depuis la veille au soir.
DONNEES = ["ecoles.json", "stages-ajout-2026-11-25.json", "terres-monde.json", "lacs-monde.json",
           "toponymes-monde.json", "bassins.json", "chants-catalogue.json", "chants-menu.json",
           # Les treize groupes de la bourse aux équipiers (26/11/2026) : sans lui, corriger une
           # zone ici ne changeait rien en ligne — la reconstruction relisait la copie de l'atelier.
           "bourses.json"]
SOURCE |= set(DONNEES)
SRC.update({n: RACINE / "projets/sailingmore" / n for n in DONNEES})
DEST.update({n: f"atelier/donnees/projets/sailingmore/{n}" for n in DONNEES})


def appel(chemin: str, methode: str = "GET", corps: dict | None = None):
    r = urllib.request.Request(
        f"https://api.github.com{chemin}",
        data=json.dumps(corps).encode() if corps is not None else None,
        method=methode,
        headers={"Authorization": f"token {JETON}", "Accept": "application/vnd.github+json",
                 "User-Agent": "hermes"})
    try:
        with urllib.request.urlopen(r, timeout=90) as rep:
            brut = rep.read()
            return rep.status, (json.loads(brut) if brut else {})
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()[:300]


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    noms = [n for n in sys.argv[1:] if not n.startswith("-")]
    message = " ".join(a for a in sys.argv[1:] if a.startswith("-") is False)[:0]
    souhaite = [n for n in noms if n in SOURCE]
    if not souhaite:
        print("aucun fichier source reconnu ; attendus :", sorted(SOURCE))
        return 2
    message = f"source : {', '.join(souhaite)}"

    s, ref = appel(f"/repos/{DEPOT}/git/ref/heads/{BRANCHE}")
    if s != 200:
        print("branche", BRANCHE, "illisible :", s)
        return 1
    tete = ref["object"]["sha"]
    s, commit = appel(f"/repos/{DEPOT}/git/commits/{tete}")
    arbre = []
    for nom in souhaite:
        p = SRC.get(nom, RACINE / "scripts" / nom)
        if not p.exists():
            print("absent :", p)
            return 1
        s, blob = appel(f"/repos/{DEPOT}/git/blobs", "POST",
                        {"content": base64.b64encode(p.read_bytes()).decode(), "encoding": "base64"})
        if s not in (200, 201):
            print("blob refusé", nom, s, blob)
            return 1
        arbre.append({"path": DEST.get(nom, f"atelier/source/{nom}"), "mode": "100644",
                      "type": "blob", "sha": blob["sha"]})

    s, t = appel(f"/repos/{DEPOT}/git/trees", "POST",
                 {"base_tree": commit["tree"]["sha"], "tree": arbre})
    if s not in (200, 201):
        print("arbre refusé", s, t)
        return 1
    s, c = appel(f"/repos/{DEPOT}/git/commits", "POST",
                 {"message": message, "tree": t["sha"], "parents": [tete]})
    if s not in (200, 201):
        print("commit refusé", s, c)
        return 1
    s, _ = appel(f"/repos/{DEPOT}/git/refs/heads/{BRANCHE}", "PATCH", {"sha": c["sha"]})
    print(f"poussé sur {BRANCHE} : {', '.join(souhaite)} · commit {c['sha'][:8]} · {s}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
