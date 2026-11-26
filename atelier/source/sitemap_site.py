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
         "carte.html", "ports.html", "simulateur.html", "bateaux.html", "bateaux/index.html", "chants-de-marin.html",
         "equivalences.html", "securite-obligatoire.html", "jeux.html", "annonceurs.html",
         "bourse-equipiers.html", "qui-sommes-nous.html"]
# Pages légales : indexables et déclarées comme le reste (26/11/2026 — elles avaient été oubliées, et
# une correction faite la veille sur le sitemap publié s'était perdue à la reconstruction suivante :
# c'est l'écrivain qu'il faut corriger, pas sa sortie).
LEGALES = ["mentions-legales.html", "confidentialite.html", "delete.html"]
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
    # Une page par école (25/11/2026) : découvertes sur le disque, jamais dans une liste fermée.
    noms = (list(PAGES) + LEGALES + sorted(x.name for x in site.glob("ecole-*.html"))
            if site.is_dir() else list(PAGES) + LEGALES)
    # Une page par chant de marin (26/11/2026) : découvertes sur le disque, comme les pages d'école.
    if site.is_dir():
        noms += sorted(x.name for x in site.glob("chant-*.html"))
    # Une page par mot du lexique (25/11/2026) : 505 fichiers dans `lexique/`, avec leur dossier.
    mot = sorted(x.relative_to(site).as_posix() for x in (site / "lexique").glob("*.html"))
    # Les stories publiées (26/11/2026) : `stories/AAAA-MM-JJ.html`, indexables et avec canonical,
    # mais jamais déclarées — la correction de la veille n'avait porté que sur le sitemap publié,
    # pas sur son écrivain, donc la reconstruction suivante l'avait effacée.
    story = sorted(x.relative_to(site).as_posix() for x in (site / "stories").glob("*.html"))
    for nom in dict.fromkeys(list(noms) + mot + story):
        p = site / nom
        if not _indexable(p):
            continue
        loc = f"{URL}/" if nom == "index.html" else (f"{URL}/{nom[:-10]}" if nom == "bateaux/index.html" else f"{URL}/{nom}")
        lm = datetime.fromtimestamp(p.stat().st_mtime).date().isoformat()
        lignes.append(f"<url><loc>{loc}</loc><lastmod>{lm}</lastmod>{images.get(loc, '')}</url>")
    f.write_text('<?xml version="1.0" encoding="UTF-8"?>\n' + NS + "\n" + "\n".join(lignes) + "\n</urlset>\n",
                 encoding="utf-8")
    return len(lignes)


def fusionner_ports(site: Path) -> int:
    """Les 15 000 fiches de ports ont leur propre sitemap : le sitemap principal reste la liste
    courte des pages du site (règle 7, un seul écrivain par fichier). Au-delà de 50 000 adresses,
    la norme impose de découper — d'où un fichier par tranche de 45 000, prévu dès maintenant."""
    dossier = site / "ports"
    fiches = sorted(dossier.glob("*.html")) if dossier.is_dir() else []
    if not fiches:
        return 0
    urls = []
    for p in fiches:
        try:
            tete = p.read_text(encoding="utf-8")[:4000]
            m = re.search(r'<link rel="canonical" href="([^"]+)"', tete)
            loc = m.group(1) if m else f"{URL}/ports/{p.name}"
            if not _indexable(p):
                continue
            lm = datetime.fromtimestamp(p.stat().st_mtime).date().isoformat()
        except (OSError, UnicodeDecodeError):
            continue
        urls.append(f"<url><loc>{loc}</loc><lastmod>{lm}</lastmod></url>")
    tranche = 45000
    ecrits = 0
    for i in range(0, len(urls), tranche):
        nom = "sitemap-ports.xml" if i == 0 else f"sitemap-ports-{i // tranche + 1}.xml"
        (site / nom).write_text('<?xml version="1.0" encoding="UTF-8"?>\n' + NS + "\n"
                                + "\n".join(urls[i:i + tranche]) + "\n</urlset>\n", encoding="utf-8")
        ecrits += 1
    return ecrits


if __name__ == "__main__":
    here = Path(__file__).resolve().parent.parent / "projets" / "sailingmore" / "site"
    if "--ports" in sys.argv:
        print(f"sitemap-ports.xml : {fusionner_ports(here)} fichier(s)")
        sys.exit(0)
    print(f"sitemap.xml : {fusionner(here)} adresse(s)")
    sys.exit(0)
