#!/usr/bin/env python3
"""Seul écrivain de site/sitemap.xml (règle 7, 25/11/2026).

Appelé par `accueil_site.sortir_le_site` (construction) puis par `publier_atelier.publier` sur le
miroir `cache/rhum/site`, une fois les fichiers fusionnés : le sitemap décrit ce qui est publié, et
certaines pages (`carte.html`, `stories/`) ne naissent pas dans l'atelier. Même fonction, même
écrivain ; aucun autre script n'écrit le sitemap.
- une page est déclarée dès que le fichier existe et ne porte pas `noindex` — y compris les pages
  datées (`stories/`) et les pages légales ; aucune liste fermée, sinon le sitemap retarde sur le site ;
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
# Ordre du sitemap (l'ordre seul, pas le droit d'y figurer : c'est `noindex` qui exclut).
PAGES = ["index.html", "cours.html", "lexique.html", "regles-de-course.html", "regates.html", "stages.html",
         "carte.html", "ports.html", "simulateur.html", "bateaux.html", "chants-de-marin.html",
         "equivalences.html", "securite-obligatoire.html", "jeux.html", "annonceurs.html"]
NS = ('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
      'xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">')


def _indexable(f: Path) -> bool:
    return f.exists() and not re.search(r'<meta[^>]+name=["\']robots["\'][^>]*noindex', f.read_text(encoding="utf-8"), re.I)


def _declarees(site: Path) -> list[str]:
    """Toute page indexable du dossier, `PAGES` d'abord puis les autres (stories datées, pages légales).

    Une page absente du sitemap alors qu'elle est indexable est un signal contradictoire : le 25/11/2026,
    neuf pages (cinq stories, trois pages légales, un aperçu) étaient dans ce cas parce que la liste
    ci-dessus était fermée. La liste ne sert plus qu'à l'ordre ; c'est `noindex` qui exclut.
    """
    vues = [n for n in PAGES if _indexable(site / n)]
    for p in sorted(site.rglob("*.html")):
        nom = p.relative_to(site).as_posix()
        if nom not in PAGES and _indexable(p):
            vues.append(nom)
    return vues


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
    for nom in _declarees(site):
        p = site / nom
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
