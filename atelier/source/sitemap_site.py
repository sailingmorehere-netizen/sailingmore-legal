#!/usr/bin/env python3
"""Seul écrivain de site/sitemap.xml (règle 7, 25/11/2026).

Appelé par `accueil_site.sortir_le_site` (construction) puis par `publier_atelier.publier` sur le
miroir `cache/rhum/site`, une fois les fichiers fusionnés : le sitemap décrit ce qui est publié, et
certaines pages (`carte.html`, `stories/`) ne naissent pas dans l'atelier. Même fonction, même
écrivain ; aucun autre script n'écrit le sitemap.
- une page est déclarée dès que le fichier existe et ne porte pas `noindex` — y compris les pages
  datées (`stories/`) et les pages légales ; aucune liste fermée, sinon le sitemap retarde sur le site ;
- `lastmod` = le jour où le contenu de la page a **changé pour de bon** : l'empreinte de chaque page
  est gardée dans `cache/rhum/sitemap-dates.json`, une reconstruction à l'identique ne change pas la
  date. Un fichier reconstruit chaque matin portait sinon partout la date du matin, et Google apprend
  à ne plus lire `lastmod` ;
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
ETAT = Path(__file__).resolve().parent.parent / "cache" / "rhum" / "sitemap-dates.json"
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


def _dates(site: Path, noms: list[str]) -> dict[str, str]:
    """La date annoncée pour chaque page : le jour de son dernier vrai changement.

    On compare l'empreinte du fichier à celle de la construction précédente, et on garde la date
    d'avant quand rien n'a bougé. Une entrée par dossier : la copie de travail et le miroir publié
    n'ont pas le même contenu au même moment, et leurs dates ne doivent pas se marcher dessus.
    """
    import hashlib
    import json

    cle = str(site.resolve())
    etat: dict = {}
    try:
        etat = json.loads(ETAT.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001 — un état illisible vaut un état vide, jamais une panne
        etat = {}
    ici = etat.get(cle) if isinstance(etat.get(cle), dict) else {}
    aujourd_hui = datetime.now().date().isoformat()
    dates, neuf = {}, {}
    for nom in noms:
        sha = hashlib.sha1((site / nom).read_bytes()).hexdigest()
        avant = ici.get(nom) if isinstance(ici.get(nom), dict) else {}
        if avant.get("sha") == sha and avant.get("date"):
            dates[nom] = avant["date"]
        else:
            dates[nom] = aujourd_hui
        neuf[nom] = {"sha": sha, "date": dates[nom]}
    etat[cle] = neuf
    ETAT.parent.mkdir(parents=True, exist_ok=True)
    ETAT.write_text(json.dumps(etat, ensure_ascii=False, indent=0, sort_keys=True), encoding="utf-8")
    return dates


def fusionner(site: Path) -> int:
    f = site / "sitemap.xml"
    images = _images(f.read_text(encoding="utf-8")) if f.exists() else {}
    noms = _declarees(site)
    dates = _dates(site, noms)
    lignes = []
    for nom in noms:
        loc = f"{URL}/" if nom == "index.html" else f"{URL}/{nom}"
        lignes.append(f"<url><loc>{loc}</loc><lastmod>{dates[nom]}</lastmod>{images.get(loc, '')}</url>")
    f.write_text('<?xml version="1.0" encoding="UTF-8"?>\n' + NS + "\n" + "\n".join(lignes) + "\n</urlset>\n",
                 encoding="utf-8")
    return len(lignes)


if __name__ == "__main__":
    here = Path(__file__).resolve().parent.parent / "projets" / "sailingmore" / "site"
    print(f"sitemap.xml : {fusionner(here)} adresse(s)")
    sys.exit(0)
