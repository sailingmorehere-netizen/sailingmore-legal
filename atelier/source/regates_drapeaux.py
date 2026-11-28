# © 2026 Sailing More — tous droits réservés. All rights reserved.
"""Drapeaux de pays en SVG local (jamais d'emoji : Windows ne les affiche pas) et noms de pays
dans les six langues. Lu par `regates_page.py`, qui émet une seule fois un « sprite » dans la page ;
chaque carte n'y renvoie que par `<use>`, donc le rendu de 1 000 cartes reste léger.

Clé = code pays du JSON (FFVoile/World Sailing). Un code absent de cette table : pas de drapeau,
rien à la place. Pour ajouter un pays : un viewBox, les formes, et ses six noms.
"""
from __future__ import annotations

import math


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


def _etoile(cx: float, cy: float, r: float, couleur: str = "#FFFFFF",
            angle: float = -90.0) -> str:
    """Une étoile à cinq branches en polygone — un SVG n'a pas de police pour en dessiner."""
    pts = []
    for i in range(10):
        a = math.radians(angle + i * 36)
        rr = r if i % 2 == 0 else r * 0.42
        pts.append(f"{cx + rr * math.cos(a):.2f},{cy + rr * math.sin(a):.2f}")
    return f'<polygon points="{" ".join(pts)}" fill="{couleur}"/>'


def _jack(x: float, y: float, w: float, h: float) -> str:
    """L'Union Jack réduit : diagonales, puis croix — pour le Royaume-Uni et les cantons."""
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#012169"/>'
            f'<path d="M{x},{y} L{x + w},{y + h} M{x},{y + h} L{x + w},{y}" stroke="#FFFFFF"'
            f' stroke-width="{h / 3:.2f}"/>'
            f'<path d="M{x},{y} L{x + w},{y + h} M{x},{y + h} L{x + w},{y}" stroke="#C8102E"'
            f' stroke-width="{h / 6:.2f}"/>'
            f'<rect x="{x + w / 2 - h / 6:.2f}" y="{y}" width="{h / 3:.2f}" height="{h}" fill="#FFFFFF"/>'
            f'<rect x="{x}" y="{y + h / 2 - h / 6:.2f}" width="{w}" height="{h / 3:.2f}" fill="#FFFFFF"/>'
            f'<rect x="{x + w / 2 - h / 12:.2f}" y="{y}" width="{h / 6:.2f}" height="{h}" fill="#C8102E"/>'
            f'<rect x="{x}" y="{y + h / 2 - h / 12:.2f}" width="{w}" height="{h / 6:.2f}" fill="#C8102E"/>')


def _grece() -> tuple[str, str]:
    s = ""
    for i in range(9):
        s += f'<rect y="{i * 2}" width="27" height="2" fill="{"#0D5EAF" if i % 2 == 0 else "#FFFFFF"}"/>'
    s += ('<rect width="10" height="10" fill="#0D5EAF"/>'
          '<rect x="4" width="2" height="10" fill="#FFFFFF"/>'
          '<rect y="4" width="10" height="2" fill="#FFFFFF"/>')
    return ("0 0 27 18", s)


def _usa() -> tuple[str, str]:
    s = '<rect width="13" height="13" fill="#FFFFFF"/>'
    for i in range(0, 13, 2):
        s += f'<rect y="{i}" width="13" height="1" fill="#B22234"/>'
    s += '<rect width="5.2" height="7" fill="#3C3B6E"/>'
    for ligne in range(5):
        decale = 0.5 if ligne % 2 == 0 else 1.0
        for col in range(4 if ligne % 2 else 5):
            s += f'<circle cx="{decale + col * 1.05:.2f}" cy="{0.8 + ligne * 1.35:.2f}" r="0.16" fill="#FFFFFF"/>'
    return ("0 0 13 13", s)


def _australie() -> tuple[str, str]:
    return ("0 0 6 3", '<rect width="6" height="3" fill="#012169"/>' + _jack(0, 0, 3, 1.5)
            + _etoile(1.5, 2.25, 0.38) + _etoile(4.2, 0.55, 0.18) + _etoile(4.85, 1.25, 0.18)
            + _etoile(4.2, 1.95, 0.18) + _etoile(4.45, 1.3, 0.09) + _etoile(3.75, 1.25, 0.13))


def _nouvelle_zelande() -> tuple[str, str]:
    return ("0 0 6 3", '<rect width="6" height="3" fill="#012169"/>' + _jack(0, 0, 3, 1.5)
            + _etoile(4.15, 0.6, 0.2, "#CC142B") + _etoile(4.95, 1.45, 0.2, "#CC142B")
            + _etoile(4.15, 2.3, 0.2, "#CC142B") + _etoile(4.5, 1.45, 0.13, "#CC142B"))


def _hong_kong() -> tuple[str, str]:
    """Le champ rouge et la fleur blanche : cinq pétales lus comme une fleur à 20 px."""
    s = '<rect width="3" height="2" fill="#DE2910"/>'
    for i in range(5):
        a = math.radians(-90 + i * 72)
        s += f'<circle cx="{1.5 + 0.26 * math.cos(a):.2f}" cy="{1 + 0.26 * math.sin(a):.2f}" r="0.2" fill="#FFFFFF"/>'
    s += '<circle cx="1.5" cy="1" r="0.13" fill="#DE2910"/>'
    return ("0 0 3 2", s)


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
    "GBR": ("0 0 6 3", _jack(0, 0, 6, 3)),
    "HKG": _hong_kong(),
    "MON": ("0 0 5 4", '<rect width="5" height="4" fill="#FFFFFF"/><rect y="2" width="5" height="2" fill="#CE1126"/>'),
    "JPN": ("0 0 3 2", '<rect width="3" height="2" fill="#FFFFFF"/><circle cx="1.5" cy="1" r="0.6" fill="#BC002D"/>'),
    "POL": _bandes_h("#FFFFFF", "#DC143C"),
    "AUT": _bandes_h("#ED2939", "#FFFFFF", "#ED2939"),
    "HUN": _bandes_h("#CE2939", "#FFFFFF", "#477050"),
    "IRL": _bandes_v("#169B62", "#FFFFFF", "#FF883E"),
    "THA": ("0 0 3 3", '<rect width="3" height="3" fill="#A51931"/>'
                       '<rect y="0.5" width="3" height="2" fill="#F4F5F8"/>'
                       '<rect y="1" width="3" height="1" fill="#2D2A4A"/>'),
    "CHI": ("0 0 3 2", '<rect width="3" height="2" fill="#FFFFFF"/>'
                       '<rect y="1" width="3" height="1" fill="#D52B1E"/>'
                       '<rect width="1" height="1" fill="#0039A6"/>' + _etoile(0.5, 0.5, 0.3)),
    "GRE": _grece(),
    "USA": _usa(),
    "BRA": ("0 0 10 7", '<rect width="10" height="7" fill="#009C3B"/>'
                        '<polygon points="5,0.5 9.5,3.5 5,6.5 0.5,3.5" fill="#FFDF00"/>'
                        '<circle cx="5" cy="3.5" r="1.5" fill="#002776"/>'),
    "TUR": ("0 0 3 2", '<rect width="3" height="2" fill="#E30A17"/>'
                       '<circle cx="1.15" cy="1" r="0.55" fill="#FFFFFF"/>'
                       '<circle cx="1.32" cy="1" r="0.44" fill="#E30A17"/>' + _etoile(1.95, 1, 0.22)),
    "UAE": ("0 0 3 2", '<rect width="3" height="0.67" fill="#00732F"/>'
                       '<rect y="0.67" width="3" height="0.67" fill="#FFFFFF"/>'
                       '<rect y="1.34" width="3" height="0.66" fill="#000000"/>'
                       '<rect width="0.75" height="2" fill="#FF0000"/>'),
    "CHN": ("0 0 3 2", '<rect width="3" height="2" fill="#DE2910"/>'
                       + _etoile(0.55, 0.5, 0.42, "#FFDE00") + _etoile(1.05, 0.25, 0.14, "#FFDE00")
                       + _etoile(1.28, 0.55, 0.14, "#FFDE00") + _etoile(1.28, 0.9, 0.14, "#FFDE00")
                       + _etoile(1.05, 1.2, 0.14, "#FFDE00")),
    "SGP": ("0 0 3 2", '<rect width="3" height="2" fill="#FFFFFF"/>'
                       '<rect width="3" height="1" fill="#EF3340"/>'
                       '<circle cx="0.72" cy="0.5" r="0.3" fill="#FFFFFF"/>'
                       '<circle cx="0.85" cy="0.5" r="0.25" fill="#EF3340"/>'
                       + "".join(_etoile(0.95 + 0.16 * math.cos(math.radians(-90 + i * 72)),
                                         0.5 + 0.16 * math.sin(math.radians(-90 + i * 72)),
                                         0.06, "#FFFFFF") for i in range(5))),
    "AUS": _australie(),
    "NZL": _nouvelle_zelande(),
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
    "GBR": ("Royaume-Uni", "Vereinigtes Königreich", "United Kingdom", "Regno Unito", "Reino Unido", "Reino Unido"),
    "HKG": ("Hong Kong", "Hongkong", "Hong Kong", "Hong Kong", "Hong Kong", "Hong Kong"),
    "MON": ("Monaco", "Monaco", "Monaco", "Monaco", "Mónaco", "Mónaco"),
    "JPN": ("Japon", "Japan", "Japan", "Giappone", "Japón", "Japão"),
    "POL": ("Pologne", "Polen", "Poland", "Polonia", "Polonia", "Polónia"),
    "AUT": ("Autriche", "Österreich", "Austria", "Austria", "Austria", "Áustria"),
    "HUN": ("Hongrie", "Ungarn", "Hungary", "Ungheria", "Hungría", "Hungria"),
    "IRL": ("Irlande", "Irland", "Ireland", "Irlanda", "Irlanda", "Irlanda"),
    "THA": ("Thaïlande", "Thailand", "Thailand", "Thailandia", "Tailandia", "Tailândia"),
    "CHI": ("Chili", "Chile", "Chile", "Cile", "Chile", "Chile"),
    "GRE": ("Grèce", "Griechenland", "Greece", "Grecia", "Grecia", "Grécia"),
    "USA": ("États-Unis", "USA", "United States", "Stati Uniti", "Estados Unidos", "Estados Unidos"),
    "BRA": ("Brésil", "Brasilien", "Brazil", "Brasile", "Brasil", "Brasil"),
    "TUR": ("Turquie", "Türkei", "Türkiye", "Turchia", "Turquía", "Turquia"),
    "UAE": ("Émirats arabes unis", "VAE", "United Arab Emirates", "Emirati Arabi Uniti",
            "Emiratos Árabes Unidos", "Emirados Árabes Unidos"),
    "CHN": ("Chine", "China", "China", "Cina", "China", "China"),
    "SGP": ("Singapour", "Singapur", "Singapore", "Singapore", "Singapur", "Singapura"),
    "AUS": ("Australie", "Australien", "Australia", "Australia", "Australia", "Austrália"),
    "NZL": ("Nouvelle-Zélande", "Neuseeland", "New Zealand", "Nuova Zelanda", "Nueva Zelanda", "Nova Zelândia"),
}
NOMS_PAYS = {code: dict(zip(LANGUES, noms)) for code, noms in _PAYS.items()}


def sprite(codes) -> str:
    """Les `<symbol>` des seuls pays présents dans la page."""
    return "".join(f'<symbol id="f-{c}" viewBox="{DRAPEAUX[c][0]}">{DRAPEAUX[c][1]}</symbol>'
                   for c in sorted(set(codes)) if c in DRAPEAUX)
