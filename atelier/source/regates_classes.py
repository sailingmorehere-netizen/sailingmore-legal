"""Table sigle FFVoile → nom lisible, et liste des jauges « inter-séries » (tout bateau).

Fichier à part, lu par `regates_page.py`. Une seule source :
- NOMS : un sigle absent de la table reste affiché tel quel sur la page (jamais de nom inventé).
  Les noms de classes sont des noms propres : ils sont les mêmes dans les six langues.
- JAUGES : sigles de jauge de handicap qui font courir ensemble des bateaux différents.
  Ajouter un sigle ici suffit pour qu'il rejoigne l'entrée « tout bateau » du filtre.

Clés en MAJUSCULES : la recherche se fait sans tenir compte de la casse (« Class 40 » = « CLASS 40 »).
Seuls les sigles dont le sens est certain sont renseignés. IND, INC, RCB… (fréquents dans les
données) restent bruts tant qu'ils ne sont pas confirmés : voir RAPPORT.md.
"""
from __future__ import annotations

NOMS = {
    "OSIR": "Osiris",
    "IRC": "IRC",
    "WING": "Wing foil",
    "OPTI": "Optimist",
    "B293": "Bic 293",
    "J80": "J/80",
    "J70": "J/70",
    "CLASS 40": "Class40",
    "IMOCA 60": "IMOCA 60",
    "LAS4": "Laser 4.7",
    "TF35": "TF35",
    "420": "420",
    "470": "470",
    "49ER": "49er",
    "29ER": "29er",
    "FINN": "Finn",
    "SNIPE": "Snipe",
    "DRAGON": "Dragon",
    "SOLING": "Soling",
    "ILCA 4": "ILCA 4",
    "ILCA 6": "ILCA 6",
    "ILCA 7": "ILCA 7",
    "OPEN 5.70": "Open 5.70",
    "FIGARO": "Figaro",
    "MINI 6.50": "Mini 6.50",
}

JAUGES = ("OSIR", "IRC")


def nom(sigle: str) -> str:
    """Nom lisible, ou chaîne vide quand le sigle n'est pas dans la table."""
    return NOMS.get(sigle.strip().upper(), "")
