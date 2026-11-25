"""Données structurées (JSON-LD) : une seule source pour toutes les pages générées.

Règle : un seul bloc <script type="application/ld+json"> par page, un seul objet {"@context", "@graph": [...]}.
Chaque générateur appelle `bloc(page, nom_fil, *autres_noeuds)` et colle la chaîne dans le <head>.
Rien d'inventé : pas de note, pas d'avis, pas de prix.
"""
from __future__ import annotations

import json

SITE = "https://sailingmore.fr"
NOM = "Sailing More"
LANGUE = "fr"
ORG_ID = f"{SITE}/#organisation"
SITE_ID = f"{SITE}/#site"


# Profils officiels, ceux que la page d'accueil lie déjà. Relevé 25/11/2026 : Facebook, Telegram et X
# répondent 200 avec le nom « Sailing More » ; YouTube répond 200 sans titre lisible ; Instagram
# répond 429 (mesure impossible) — à revérifier à la main avant publication.
SAME_AS = [
    "https://www.facebook.com/SailingMore",
    "https://www.instagram.com/sailingmorehere/",
    "https://www.youtube.com/@SailingMore",
    "https://t.me/sailingmorehere",
    "https://x.com/SailingMore",
]


def organisation() -> dict:
    return {"@type": "Organization", "@id": ORG_ID, "name": NOM, "url": f"{SITE}/",
            "logo": f"{SITE}/icon-512.png", "sameAs": list(SAME_AS)}


def site_web() -> dict:
    return {"@type": "WebSite", "@id": SITE_ID, "name": NOM, "url": f"{SITE}/",
            "inLanguage": LANGUE, "publisher": {"@id": ORG_ID}}


def fil(page: str, nom: str) -> dict:
    """BreadcrumbList « Accueil > page ». `page` = nom de fichier (« cours.html »)."""
    return {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Accueil", "item": f"{SITE}/"},
        {"@type": "ListItem", "position": 2, "name": nom, "item": f"{SITE}/{page}"}]}


def bloc(*noeuds: dict) -> str:
    """La balise <script> complète. `</` est échappé pour ne jamais fermer le script."""
    brut = json.dumps({"@context": "https://schema.org", "@graph": list(noeuds)},
                      ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    return f'<script type="application/ld+json">{brut}</script>'


def social(page: str, titre: str, description: str) -> str:
    """Balises Open Graph / Twitter, mêmes valeurs d'image que l'accueil (og-image.jpg 1200x630)."""
    from html import escape as e
    t, d, u = e(titre, quote=True), e(description, quote=True), f"{SITE}/{page}"
    img = f"{SITE}/og-image.jpg"
    return (f'<meta property="og:title" content="{t}"><meta property="og:description" content="{d}">'
            f'<meta property="og:url" content="{u}"><meta property="og:type" content="website">'
            f'<meta property="og:locale" content="fr_FR"><meta property="og:site_name" content="{NOM}">'
            f'<meta property="og:image" content="{img}"><meta property="og:image:width" content="1200">'
            f'<meta property="og:image:height" content="630">'
            f'<meta name="twitter:card" content="summary_large_image"><meta name="twitter:image" content="{img}">')


def page_simple(page: str, nom: str) -> str:
    return bloc(fil(page, nom))
