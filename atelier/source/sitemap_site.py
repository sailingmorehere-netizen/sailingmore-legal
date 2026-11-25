#!/usr/bin/env python3
"""Seul écrivain de site/sitemap.xml (règle 7, 25/11/2026).

Appelé par `accueil_site.sortir_le_site` ; aucun autre script n'écrit le sitemap.
- une page est déclarée si le fichier existe et ne porte pas `noindex` ;
- `lastmod` = date de modification du fichier, jamais la date du jour ;
- ni `changefreq` ni `priority` ;
- les blocs `image:image` déjà posés (accueil, bateaux) sont conservés.

    python3 scripts/sitemap_site.py          # écrit site/sitemap.xml de la copie
"""
from __future__ import annotations

import re
import sys
from datetime import datetime
from pathlib import Path

URL = "https://sailingmore.fr"
# Ordre du sitemap. `index.html` -> « / ». equivalences.html : absente tant qu'elle est noindex (page vide).
PAGES = ["index.html", "cours.html", "lexique.html", "regles-de-course.html", "regates.html", "stages.html", "comparatif-stages.html",
         "carte.html", "ports.html", "simulateur.html", "bateaux.html", "chants-de-marin.html",
         "equivalences.html", "securite-obligatoire.html", "jeux.html", "annonceurs.html"]
NS = ('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
      'xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">')


def _indexable(f: Path) -> bool:
    return f.exists() and not re.search(r'<meta[^>]+name=["\']robots["\'][^>]*noindex', f.read_text(encoding="utf-8"), re.I)


def _images(x: str) -> dict[str, str]:
    out = {}
    for m in re.finditer(r"<url><loc>([^<]+)</loc>(.*?)</url>", x, flags=re.S):
        img = "".join(re.findall(r"<image:image>.*?</image:image>", m.group(2), flags=re.S))
        if img:
            out[m.group(1)] = img
    return out


def fusionner(site: Path) -> int:
    f = site / "sitemap.xml"
    images = _images(f.read_text(encoding="utf-8")) if f.exists() else {}
    lignes = []
    for nom in PAGES:
        p = site / nom
        if not _indexable(p):
            continue
        loc = f"{URL}/" if nom == "index.html" else f"{URL}/{nom}"
        lm = datetime.fromtimestamp(p.stat().st_mtime).date().isoformat()
        lignes.append(f"<url><loc>{loc}</loc><lastmod>{lm}</lastmod>{images.get(loc, '')}</url>")
    f.write_text('<?xml version="1.0" encoding="UTF-8"?>\n' + NS + "\n" + "\n".join(lignes) + "\n</urlset>\n",
                 encoding="utf-8")
    return len(lignes)


if __name__ == "__main__":
    here = Path(__file__).resolve().parent.parent / "projets" / "sailingmore" / "site"
    print(f"sitemap.xml : {fusionner(here)} adresse(s)")
    sys.exit(0)
