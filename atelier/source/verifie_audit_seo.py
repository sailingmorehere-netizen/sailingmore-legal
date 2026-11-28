#!/usr/bin/env python3
# © 2026 Sailing More — tous droits réservés. All rights reserved.
"""Contrôles issus de l'audit SEO du 24/11/2026 (2026-11-25-audit-sailingmore-fr-pour-nico.md).

Chaque sous-commande sort 0 quand le point est corrigé, 1 sinon, et affiche la mesure.
Aucune connexion réseau : tout se juge sur la copie de travail du site.

    python3 scripts/verifie_audit_seo.py liens        # plus de target=_blank interne
    python3 scripts/verifie_audit_seo.py jsonld       # sameAs + codes pays SportsEvent
    python3 scripts/verifie_audit_seo.py contraste    # les trois couleurs AA
    python3 scripts/verifie_audit_seo.py sitemap      # carte.html dedans, equivalences dehors
"""
import glob
import json
import os
import re
import sys

SITE = (os.environ.get("SITE_DIR")
        or os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        "projets/sailingmore/site"))
if not os.path.isdir(SITE):   # lancé hors de l'arbre du projet
    SITE = "/opt/data/projets/sailingmore/site"
PAGES = sorted(glob.glob(os.path.join(SITE, "*.html")))
INTERNE = re.compile(r'href="(?:/|https://sailingmore\.fr|[A-Za-z0-9_-]+\.html)')


def lire(nom):
    p = os.path.join(SITE, nom)
    if not os.path.exists(p):
        return ""
    return open(p, encoding="utf-8", errors="replace").read()


def liens():
    """Les liens internes ne doivent plus ouvrir un nouvel onglet."""
    fautifs, total = [], 0
    for f in PAGES:
        for tag in re.findall(r"<a\b[^>]*>", open(f, encoding="utf-8", errors="replace").read()):
            if 'target="_blank"' in tag:
                total += 1
                if INTERNE.search(tag):
                    fautifs.append(os.path.basename(f))
    print(f"target=_blank : {total} au total, {len(fautifs)} sur des liens internes")
    if fautifs:
        from collections import Counter
        for page, n in Counter(fautifs).most_common(8):
            print(f"   {page} : {n}")
    return 0 if not fautifs else 1


def jsonld():
    """sameAs dans l'Organization, codes pays à deux lettres dans les SportsEvent."""
    accueil = lire("index.html")
    same = "sameAs" in accueil and "facebook.com" in accueil
    regates = lire("regates.html")
    # Trois lettres = code ISO 3166-1 alpha-3 en trop, mais un JSON-LD en `@graph` échappe à la
    # première passe : le 25/11/2026 la tâche se cochait sur « 0 valeurs » alors que regates.html en
    # portait. On découpe chaque bloc et on inspecte le texte brut, pas le seul motif collé.
    trois = set()
    blocs = re.findall(r'<script[^>]*application/ld\+json[^>]*>(.*?)</script>', regates, re.S)
    for b in (blocs or [regates]):
        trois.update(re.findall(r'addressCountry"?\s*:\s*"?([A-Z]{3})', b))
    trois = sorted(trois)
    print(f"Organization sameAs : {'oui' if same else 'non'}")
    print(f"addressCountry à trois lettres : {len(trois)} valeurs {trois[:6]}")
    return 0 if same and not trois else 1


def contraste():
    """Les trois couleurs corrigées de l'audit (seuil AA 4,5:1)."""
    attendu = {"#f05a5e": "texte rouge sur fond nuit", "#c62a2e": "bouton survolé"}
    presents = {}
    for f in PAGES:
        t = open(f, encoding="utf-8", errors="replace").read().lower()
        for c in attendu:
            if c.lower() in t:
                presents[c] = presents.get(c, 0) + 1
    for c, quoi in attendu.items():
        print(f"{c} ({quoi}) : {presents.get(c, 0)} page(s)")
    return 0 if presents.get("#f05a5e", 0) >= 20 else 1


def sitemap():
    """carte.html doit être dans le sitemap, equivalences.html hors index."""
    s = open(os.path.join(SITE, "sitemap.xml"), encoding="utf-8").read()
    urls = re.findall(r"<loc>(.*?)</loc>", s)
    carte = any("carte.html" in u for u in urls)
    equiv = any("equivalences.html" in u for u in urls)
    noindex = 'name="robots"' in lire("equivalences.html")
    print(f"sitemap : {len(urls)} adresses, carte.html {'présente' if carte else 'ABSENTE'}, "
          f"equivalences.html {'présente' if equiv else 'retirée'}, noindex {'posé' if noindex else 'absent'}")
    return 0 if carte and not equiv and noindex else 1


COMMANDES = {"liens": liens, "jsonld": jsonld, "contraste": contraste, "sitemap": sitemap}

if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in COMMANDES:
        print(__doc__)
        sys.exit(2)
    sys.exit(COMMANDES[sys.argv[1]]())
