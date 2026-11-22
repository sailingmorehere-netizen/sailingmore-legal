"""Drapeaux de pays en SVG local (jamais d'emoji : Windows ne les affiche pas) et noms de pays
dans les six langues. Lu par `regates_page.py`, qui émet une seule fois un « sprite » dans la page ;
chaque carte n'y renvoie que par `<use>`, donc le rendu de 1 000 cartes reste léger.

Clé = code pays du JSON (FFVoile/World Sailing). Un code absent de cette table : pas de drapeau,
rien à la place. Pour ajouter un pays : un viewBox, les formes, et ses six noms.
"""
from __future__ import annotations


def _bandes_v(*couleurs: str) -> tuple[str, str]:
    n = len(couleurs)
    return (f"0 0 {n} 2", "".join(f'<rect x="{i}" width="1" height="2" fill="{c}"/>' for i, c in enumerate(couleurs)))


def _bandes_h(*couleurs: str) -> tuple[str, str]:
    n = len(couleurs)
    return (f"0 0 3 {n}", "".join(f'<rect y="{i}" width="3" height="1" fill="{c}"/>' for i, c in enumerate(couleurs)))


def _croix(w: int, h: int, fond: str, croix: str, x: int, e: int, interne: str = "", e2: int = 0) -> tuple[str, str]:
    y = (h - e) // 2 if (h - e) % 2 == 0 else (h - e) / 2
    s = (f'<rect width="{w}" height="{h}" fill="{fond}"/>'
         f'<rect x="{x}" width="{e}" height="{h}" fill="{croix}"/>'
         f'<rect y="{y}" width="{w}" height="{e}" fill="{croix}"/>')
    if interne:
        s += (f'<rect x="{x + (e - e2) / 2}" width="{e2}" height="{h}" fill="{interne}"/>'
              f'<rect y="{y + (e - e2) / 2}" width="{w}" height="{e2}" fill="{interne}"/>')
    return (f"0 0 {w} {h}", s)


DRAPEAUX = {
    "FRA": _bandes_v("#0055A4", "#FFFFFF", "#EF4135"),
    "BEL": _bandes_v("#000000", "#FDDA24", "#EF3340"),
    "ITA": _bandes_v("#009246", "#FFFFFF", "#CE2B37"),
    "GER": _bandes_h("#000000", "#DD0000", "#FFCE00"),
    "NED": _bandes_h("#AE1C28", "#FFFFFF", "#21468B"),
    "LTU": _bandes_h("#FDB913", "#006A44", "#C1272D"),
    "EST": _bandes_h("#0072CE", "#000000", "#FFFFFF"),
    "ESP": ("0 0 4 4", '<rect width="4" height="4" fill="#AA151B"/><rect y="1" width="4" height="2" fill="#F1BF00"/>'),
    "SUI": ("0 0 5 5", '<rect width="5" height="5" fill="#DA291C"/><rect x="2" y="1" width="1" height="3" fill="#FFFFFF"/>'
                       '<rect x="1" y="2" width="3" height="1" fill="#FFFFFF"/>'),
    "FIN": _croix(18, 11, "#FFFFFF", "#003580", 5, 3),
    "DEN": _croix(37, 28, "#C8102E", "#FFFFFF", 12, 4),
    "SWE": _croix(16, 10, "#006AA7", "#FECC00", 5, 2),
    "NOR": _croix(22, 16, "#BA0C2F", "#FFFFFF", 6, 4, "#00205B", 2),
}

LANGUES = ("fr", "de", "en", "it", "es", "pt")

_PAYS = {
    "FRA": ("France", "Frankreich", "France", "Francia", "Francia", "França"),
    "GER": ("Allemagne", "Deutschland", "Germany", "Germania", "Alemania", "Alemanha"),
    "FIN": ("Finlande", "Finnland", "Finland", "Finlandia", "Finlandia", "Finlândia"),
    "SUI": ("Suisse", "Schweiz", "Switzerland", "Svizzera", "Suiza", "Suíça"),
    "DEN": ("Danemark", "Dänemark", "Denmark", "Danimarca", "Dinamarca", "Dinamarca"),
    "BEL": ("Belgique", "Belgien", "Belgium", "Belgio", "Bélgica", "Bélgica"),
    "NED": ("Pays-Bas", "Niederlande", "Netherlands", "Paesi Bassi", "Países Bajos", "Países Baixos"),
    "NOR": ("Norvège", "Norwegen", "Norway", "Norvegia", "Noruega", "Noruega"),
    "SWE": ("Suède", "Schweden", "Sweden", "Svezia", "Suecia", "Suécia"),
    "ITA": ("Italie", "Italien", "Italy", "Italia", "Italia", "Itália"),
    "ESP": ("Espagne", "Spanien", "Spain", "Spagna", "España", "Espanha"),
    "LTU": ("Lituanie", "Litauen", "Lithuania", "Lituania", "Lituania", "Lituânia"),
    "EST": ("Estonie", "Estland", "Estonia", "Estonia", "Estonia", "Estónia"),
}
NOMS_PAYS = {code: dict(zip(LANGUES, noms)) for code, noms in _PAYS.items()}


def sprite(codes) -> str:
    """Les `<symbol>` des seuls pays présents dans la page."""
    return "".join(f'<symbol id="f-{c}" viewBox="{DRAPEAUX[c][0]}">{DRAPEAUX[c][1]}</symbol>'
                   for c in sorted(set(codes)) if c in DRAPEAUX)
