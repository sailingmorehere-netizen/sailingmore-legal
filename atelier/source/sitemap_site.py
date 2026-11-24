#!/usr/bin/env python3
"""sitemap.xml du site — reconstruit depuis les pages réellement publiées.

Pourquoi ce script : au 22/11/2026 le sitemap déclarait 8 adresses et ignorait les trois plus
grosses pages du site (cours, stages, règles de course). Un sitemap tenu à la main se désynchronise
toujours de la publication ; ici il est calculé sur les fichiers qui partent vraiment.

Usage :
    python3 scripts/sitemap_site.py            # montre ce qui serait écrit
    python3 scripts/sitemap_site.py --ecrire   # écrit projets/sailingmore/site/sitemap.xml
"""
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

SITE = Path("/opt/data/projets/sailingmore/site")
BASE = "https://sailingmore.fr/"

# Pages qui méritent d'être déclarées, avec priorité et fréquence de changement.
PAGES = {
    "index.html":            (1.0, "weekly"),
    "cours.html":            (0.9, "monthly"),
    "lexique.html":          (0.9, "monthly"),
    "regles-de-course.html": (0.9, "monthly"),
    "regates.html":          (0.8, "weekly"),
    "stages.html":           (0.8, "monthly"),
    "annonceurs.html":       (0.6, "monthly"),
    "jeux.html":             (0.6, "weekly"),
    "carte.html":            (0.8, "monthly"),
    "bateaux.html":          (0.7, "monthly"),
    "ports.html":            (0.7, "monthly"),
    "simulateur.html":       (0.7, "monthly"),
    "chants-de-marin.html":  (0.6, "monthly"),
}
# Pages exclues volontairement : noindex, ou doublon canonique.
NON_INDEXEES = re.compile(r"/pavillon-[a-z0-9-]+\.html$")
EXCLUES = {"404.html", "merci.html", "apercu-schemas.html", "regles-apercu.html",
           "mentions-legales.html", "confidentialite.html", "delete.html"}


def url_de(nom: str) -> str:
    return BASE if nom == "index.html" else BASE + nom


def construire() -> str:
    lignes = ['<?xml version="1.0" encoding="UTF-8"?>',
              '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    manquantes = []
    for nom, (prio, freq) in PAGES.items():
        chemin = SITE / nom
        if not chemin.exists():
            manquantes.append(nom)
            continue
        # Une page qui se déclare noindex n'a rien à faire dans le sitemap (23/11/2026) :
        # `equivalences.html` est noindex tant qu'aucune correspondance n'est validée.
        if "noindex" in chemin.read_text(encoding="utf-8", errors="ignore")[:3000]:
            continue
        jour = datetime.fromtimestamp(chemin.stat().st_mtime, tz=timezone.utc).strftime("%Y-%m-%d")
        lignes.append(f"  <url><loc>{url_de(nom)}</loc><lastmod>{jour}</lastmod>"
                      f"<changefreq>{freq}</changefreq><priority>{prio}</priority></url>")
    lignes.append("</urlset>")
    if manquantes:
        print("⚠ pages déclarées mais absentes du disque :", ", ".join(manquantes))
    return "\n".join(lignes) + "\n"


def fusionner(dossier: Path = SITE) -> int:
    """Reconstruit le sitemap sans perdre ce que les générateurs y ont ajouté.

    Deux écrivains coexistent : cette liste-ci, et `chants_page`/`bateaux_page`, qui ajoutent leur
    entrée — et, pour `bateaux`, ses neuf images (`image:loc`). Réécrire la liste seule effaçait ces
    images (24/11/2026). Ici : les pages connues sont remises à jour, tout bloc déjà présent pour une
    autre adresse est recopié tel quel, et une adresse n'apparaît qu'une fois.
    Rend le nombre d'adresses écrites.
    """
    chemin = dossier / "sitemap.xml"
    existants = {}
    if chemin.exists():
        for bloc in re.findall(r"\s*<url>.*?</url>", chemin.read_text(encoding="utf-8"), re.S):
            m = re.search(r"<loc>(.*?)</loc>", bloc)
            if m:
                existants[m.group(1)] = bloc.strip()
    blocks = []
    # Les 42 pages des pavillons (24/11/2026) : pages de référence en `noindex` tant que leur fiche n'est
    # pas écrite en entier — une page noindex n'a rien à faire ici. Quand Claude les aura remplies, il
    # suffira de retirer cette exclusion et le noindex ensemble.
    famille = {}
    for nom, (prio, freq) in {**PAGES, **famille}.items():
        f = dossier / nom
        if not f.exists():
            continue
        if "noindex" in f.read_text(encoding="utf-8", errors="ignore")[:3000]:
            continue
        jour = datetime.fromtimestamp(f.stat().st_mtime, tz=timezone.utc).strftime("%Y-%m-%d")
        loc = url_de(nom)
        # Un bloc déjà posé par un générateur est plus riche (images) : on le garde.
        blocks.append(existants.pop(loc, None) or
                      f"  <url><loc>{loc}</loc><lastmod>{jour}</lastmod>"
                      f"<changefreq>{freq}</changefreq><priority>{prio}</priority></url>")
    # Une adresse passée en noindex sort du sitemap : garder son bloc d'hier la remettrait dans l'index.
    blocks += [b for k, b in sorted(existants.items()) if not NON_INDEXEES.search(k)]
    xml = "\n".join(['<?xml version="1.0" encoding="UTF-8"?>',
                     '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
                     'xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">']
                    + blocks + ["</urlset>"]) + "\n"
    chemin.write_text(xml, encoding="utf-8")
    return xml.count("<url>")


def main() -> int:
    xml = construire()
    print(xml)
    if "--ecrire" in sys.argv:
        (SITE / "sitemap.xml").write_text(xml, encoding="utf-8")
        print(f"écrit : {SITE / 'sitemap.xml'} ({len(xml)} octets)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
