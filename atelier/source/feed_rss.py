#!/usr/bin/env python3
"""feed.xml — le flux RSS du site, calculé sur les pages réellement publiées.

Nicolas, 24/11/2026 : « Faut un flux rss qui renvoie sur nous notre info ! » Le flux ne décrit pas
un site idéal : il lit les pages qui partent vraiment, prend leur <title>, leur <meta description>
et leur date de modification, et rien d'autre. Un flux tenu à la main se désynchronise de la
publication ; ici il suit le même chemin que `sitemap_site.py`, qui lit la même liste de pages.

Un seul flux pour tout le site, pas un par page : un lecteur s'abonne à un site, pas à une page.
Chaque page porte en revanche un `<link rel="alternate" type="application/rss+xml">` dans sa tête
(posé par `accueil_site.poser_flux_partout()`), c'est ce qui fait découvrir le flux depuis
n'importe quelle page.

Usage :
    python3 scripts/feed_rss.py            # montre le flux
    python3 scripts/feed_rss.py --ecrire   # écrit projets/sailingmore/site/feed.xml
"""
import html
import re
import sys
from datetime import datetime, timezone
from email.utils import format_datetime
from pathlib import Path

SITE = Path("/opt/data/projets/sailingmore/site")
BASE = "https://sailingmore.fr/"
TITRE = "Sailing More — stages, régates et cours de voile"
DESCRIPTION = ("Stages de voile, calendrier des régates d'Europe, cours théoriques, règles de course : "
               "les pages de Sailing More, mises à jour au fil de l'eau.")
NB_MAX = 20

# Les pages qui entrent dans le flux, dans l'ordre de priorité éditoriale du site (stages, régates,
# cours d'abord). Jamais le juridique, le 404, les aperçus noindex ni les écrans de compte.
PAGES = [
    "index.html", "stages.html", "regates.html", "cours.html", "carte.html",
    "regles-de-course.html", "lexique.html", "bateaux.html", "ports.html",
    "simulateur.html", "jeux.html", "chants-de-marin.html", "annonceurs.html",
]


def _texte(balise: str, source: str) -> str:
    m = re.search(balise, source, re.I | re.S)
    if not m:
        return ""
    return html.unescape(re.sub(r"\s+", " ", m.group(1))).strip()


def _url(nom: str) -> str:
    return BASE if nom == "index.html" else BASE + nom


def elements() -> list[dict]:
    """Une entrée par page présente sur le disque, de la plus récente à la plus ancienne."""
    entrees = []
    for nom in PAGES:
        chemin = SITE / nom
        if not chemin.exists():
            continue
        source = chemin.read_text(encoding="utf-8", errors="ignore")
        if "noindex" in source[:3000]:
            continue
        titre = _texte(r"<title>(.*?)</title>", source) or nom
        description = _texte(r'<meta\s+name="description"\s+content="(.*?)"', source)
        date = datetime.fromtimestamp(chemin.stat().st_mtime, tz=timezone.utc)
        entrees.append({"titre": titre, "description": description, "lien": _url(nom),
                        "date": date, "nom": nom})
    entrees.sort(key=lambda e: e["date"], reverse=True)
    return entrees


def construire() -> str:
    entrees = sorted(_dates_reelles(elements()), key=lambda e: e["date"], reverse=True)[:NB_MAX]
    maintenant = datetime.now(timezone.utc)
    t = [format_datetime(d) for d in (maintenant,)]
    lignes = ['<?xml version="1.0" encoding="UTF-8"?>',
              '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">',
              "<channel>",
              f"  <title>{html.escape(TITRE)}</title>",
              f"  <link>{BASE}</link>",
              f"  <description>{html.escape(DESCRIPTION)}</description>",
              "  <language>fr-fr</language>",
              f"  <lastBuildDate>{t[0]}</lastBuildDate>",
              f'  <atom:link href="{BASE}feed.xml" rel="self" type="application/rss+xml"/>',
              "  <ttl>720</ttl>",
              "  <copyright>Sailing More</copyright>",
              "  <generator>sailingmore.fr/feed_rss.py</generator>"]
    for e in entrees:
        lignes += ["  <item>",
                   f"    <title>{html.escape(e['titre'])}</title>",
                   f"    <link>{e['lien']}</link>",
                   f'    <guid isPermaLink="true">{e["lien"]}</guid>',
                   f"    <pubDate>{format_datetime(e['date'])}</pubDate>"]
        if e["description"]:
            lignes.append(f"    <description>{html.escape(e['description'])}</description>")
        lignes.append("  </item>")
    lignes += ["</channel>", "</rss>"]
    return "\n".join(lignes) + "\n"


def _memoire() -> Path:
    # À côté des pages : le fichier vit avec le site, donc il suit le même dossier dans l'atelier.
    # Il n'est jamais publié (absent de `fichiers_a_publier()`).
    return SITE / ".feed-dates.json"


def _dates_reelles(entrees: list[dict]) -> list[dict]:
    """Une vraie date de parution : la dernière fois que la page a changé de contenu.

    `mtime` seul ne va pas : chaque construction réécrit toutes les pages, donc tout le flux
    afficherait la date du jour à chaque passage et un agrégateur verrait douze nouveautés par jour
    (24/11/2026). On garde donc l'empreinte du contenu : empreinte identique, date conservée ;
    contenu changé, date du jour.
    """
    import hashlib
    import json
    mem, chemin = {}, _memoire()
    if chemin.exists():
        try:
            mem = json.loads(chemin.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            mem = {}
    neuf = {}
    for e in entrees:
        page = SITE / e["nom"]
        empreinte = hashlib.sha1(page.read_bytes()).hexdigest()[:16]
        ancien = mem.get(e["nom"])
        if ancien and ancien.get("h") == empreinte:
            try:
                e["date"] = datetime.fromisoformat(ancien["date"])
            except Exception:  # noqa: BLE001
                pass
        neuf[e["nom"]] = {"h": empreinte, "date": e["date"].isoformat()}
    try:
        chemin.parent.mkdir(parents=True, exist_ok=True)
        chemin.write_text(json.dumps(neuf, ensure_ascii=False, indent=1), encoding="utf-8")
    except Exception as ex:  # noqa: BLE001
        print(f"dates du flux non mémorisées : {ex}")
    return entrees


def ecrire(dossier: Path = SITE) -> int:
    """Écrit `feed.xml` dans `dossier` et rend le nombre d'entrées écrites."""
    xml = construire()
    (dossier / "feed.xml").write_text(xml, encoding="utf-8")
    return xml.count("<item>")


def main() -> int:
    xml = construire()
    print(xml)
    if "--ecrire" in sys.argv:
        n = ecrire()
        print(f"écrit : {SITE / 'feed.xml'} ({n} entrées, {len(xml)} octets)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
