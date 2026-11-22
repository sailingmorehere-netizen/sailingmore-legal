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


def organisation() -> dict:
    return {"@type": "Organization", "@id": ORG_ID, "name": NOM, "url": f"{SITE}/",
            "logo": f"{SITE}/icon-512.png"}


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


def page_simple(page: str, nom: str) -> str:
    return bloc(fil(page, nom))
