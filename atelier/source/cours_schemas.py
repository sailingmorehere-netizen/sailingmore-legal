#!/usr/bin/env python3
"""Pose en tête de `cours.html` les schémas déjà dessinés, un par bloc dépliant.

Les images sont les planches annotées du 23/11/2026 (`cache/scratch/plans` et
`cache/scratch/laser`), copiées telles quelles dans `images/schemas/` : rien n'est redessiné ici, et
le bloc se remplace lui-même à chaque passage (aucun empilement).

La page des cours appartient à Claude : je ne touche pas à son script, j'ajoute le bloc dans la page
déjà construite, comme `regles_schemas.py` sur la page des règles.

- Un schéma par bloc, `<details name="…">` : un seul ouvert à la fois, sans une ligne de JS.
- Les planches sont annotées en français ; les autres langues le disent en une ligne.
"""
from __future__ import annotations

import html as _html
import re
import sys
from pathlib import Path

ATELIER = Path("/opt/data/cache/atelier/source")
RACINE = Path("/opt/data")
LANGUES = ("fr", "en", "it", "es", "pt", "de")

TEXTES = {
    "fr": ("Les schémas des bateaux",
           "Dix planches annotées, déjà dessinées pour le cours. Touchez-en une : elle s'ouvre, une seule à la fois.",
           ""),
    "en": ("The boat diagrams",
           "Ten annotated plates, already drawn for the course. Touch one: it opens, one at a time.",
           "Plates are labelled in French."),
    "it": ("Gli schemi delle barche",
           "Dieci tavole annotate, già disegnate per il corso. Toccane una: si apre, una alla volta.",
           "Le tavole sono annotate in francese."),
    "es": ("Los esquemas de los barcos",
           "Diez láminas anotadas, ya dibujadas para el curso. Toca una: se abre, de una en una.",
           "Las láminas están anotadas en francés."),
    "pt": ("Os esquemas dos barcos",
           "Dez pranchas anotadas, já desenhadas para o curso. Toque numa: abre-se, uma de cada vez.",
           "As pranchas estão anotadas em francês."),
    "de": ("Die Bootsschemata",
           "Zehn beschriftete Tafeln, bereits für den Kurs gezeichnet. Tippen Sie eine an: sie öffnet sich, immer nur eine.",
           "Die Tafeln sind auf Französisch beschriftet."),
}

# Les deux planches qui ne sont pas des bateaux.
TITRES = {
    "allures": {"fr": "Les allures", "en": "Points of sail", "it": "Le andature",
                "es": "Los rumbos", "pt": "As andaduras", "de": "Kurse zum Wind"},
    "portance": {"fr": "La portance d'un foil", "en": "How a foil lifts", "it": "La portanza di un foil",
                 "es": "La sustentación de un foil", "pt": "A sustentação de um foil",
                 "de": "Der Auftrieb eines Foils"},
}
SOUS = {
    "allures": {"fr": "Six allures, et la zone morte",
                "en": "Six points of sail, and the no-go zone",
                "it": "Sei andature, e la zona morta",
                "es": "Seis rumbos, y la zona muerta",
                "pt": "Seis andaduras, e a zona morta",
                "de": "Sechs Kurse, und der Totwinkel"},
    "portance": {"fr": "Coupe d'une aile : incidence et pressions",
                 "en": "Wing section: angle of attack and pressures",
                 "it": "Sezione di un'ala: incidenza e pressioni",
                 "es": "Sección de un ala: incidencia y presiones",
                 "pt": "Secção de uma asa: incidência e pressões",
                 "de": "Flügelprofil: Anstellwinkel und Drücke"},
}

# Ordre d'affichage, celui du cours : (fichier, fiche de bateau, nom affiché).
PLANCHES = (
    ("allures", None, None),
    ("surprise", "surprise", "Surprise"),
    ("x35", "x35", "X-35"),
    ("hobie-16", "hobie16", "Hobie 16"),
    ("laser", "laser", "Laser"),
    ("49er", "49er", "49er"),
    ("planche-a-voile", "iqfoil", "iQFOiL"),
    ("formula-kite", "kite", "Formula Kite"),
    ("wingfoil", "wing", "Wingfoil"),
    # IMOCA et Ultim retirés le 24/11/2026, à la demande de Nicolas : les dessins ne tiennent pas le
    # niveau. Les fichiers restent sur disque (site/images/schemas/imoca.webp, ultim.webp), non liés.
    ("portance", None, None),
)

CSS = """/* Les schémas des bateaux, en tête de page : un schéma par bloc, un seul ouvert */
.schemas-bateaux{background:var(--panneau);border-left:3px solid var(--rouge);padding:1rem 1.15rem;margin:1.3rem 0 1.6rem;border-radius:3px}
.schemas-bateaux h2{font-size:1.02rem;margin:0 0 .25rem;text-transform:none;letter-spacing:0}
.schemas-bateaux .sb-intro{font-size:.86rem;color:var(--gris);margin:.1rem 0 .5rem}
.schemas-bateaux .sb-note{font-size:.78rem;color:var(--gris);margin:.4rem 0 0}
.schemas-bateaux details{margin:0}
.schemas-bateaux summary{display:flex;align-items:center;justify-content:space-between;gap:.8rem;padding:.6rem 0;border-top:1px solid rgba(157,178,198,.22);cursor:pointer;color:var(--ivoire);font-weight:600;list-style:none;font-size:.95rem}
.schemas-bateaux summary::-webkit-details-marker{display:none}
.schemas-bateaux summary small{display:block;font-weight:400;font-size:.76rem;color:var(--gris);letter-spacing:.02em}
.schemas-bateaux .bs-fleche{color:var(--gris);font-size:.8rem;transition:transform .15s}
.schemas-bateaux details[open] .bs-fleche{transform:rotate(90deg)}
.schemas-bateaux figure{margin:.1rem 0 .9rem}
.schemas-bateaux img{width:100%;height:auto;display:block;background:#0b2340;border-radius:2px}
.schemas-bateaux figcaption{font-size:.78rem;color:var(--gris);padding-top:.35rem}
.schemas-bateaux figcaption a{color:var(--ivoire)}"""


def _bateaux_page():
    """Le module qui construit la page des bateaux : celui de l'atelier s'il est là, sinon le mien.

    Prendre le même que la page publiée garantit les mêmes noms et les mêmes fiches.
    """
    for base in (ATELIER, RACINE / "scripts"):
        if (base / "bateaux_page.py").exists():
            sys.path.insert(0, str(base))
            break
    import bateaux_page  # noqa: PLC0415

    return bateaux_page


def fiches():
    """(fichier, titre par langue, sous-titre par langue, lien) pour chaque planche."""
    bp = _bateaux_page()
    par_id = {b["id"]: b for b in bp.BATEAUX}
    sortie = []
    for fichier, bid, nom in PLANCHES:
        if bid is None:  # les deux planches qui ne sont pas des bateaux
            sortie.append((fichier, TITRES[fichier], SOUS[fichier], "bateaux.html"))
            continue
        b = par_id.get(bid)
        if not b:
            continue
        titres = {lg: nom for lg in LANGUES}
        sous = {}
        for lg in LANGUES:
            fin = bp.UI[lg].get(b["cat"], "")
            if b["fiche"].get("long"):
                fin = f"{fin} · {b['fiche']['long']} m"
            sous[lg] = fin
        sortie.append((fichier, titres, sous, f'bateaux.html#{b["id"]}'))
    return sortie


def bloc(lang: str) -> str:
    e = lambda s: _html.escape(str(s), quote=False)  # noqa: E731
    titre, intro, note = TEXTES[lang]
    morceaux = []
    for slug, titres, sous, lien in fiches():
        t, s = titres[lang], sous[lang]
        alt = f"{t} — {s}"
        morceaux.append(
            f'<details name="schemas-{lang}"><summary><span>{e(t)}<small>{e(s)}</small></span>'
            f'<span class="bs-fleche" aria-hidden="true">▸</span></summary>'
            f'<figure><a href="{lien}">'
            f'<img src="images/schemas/{slug}.webp" loading="lazy" '
            f'alt="{_html.escape(alt, quote=True)}"></a>'
            f'<figcaption><a href="{lien}">{e(t)} — {e(s)}</a></figcaption>'
            f"</figure></details>")
    fin = f'<p class="sb-note">{e(note)}</p>' if note else ""
    return (f'<section class="schemas-bateaux"><h2>{e(titre)}</h2>'
            f'<p class="sb-intro">{e(intro)}</p>{"".join(morceaux)}{fin}</section>')


def injecter(page: Path) -> int:
    """Pose (ou repose) le bloc dans `page`. Rend le nombre de langues servies."""
    h = page.read_text(encoding="utf-8")
    # Le bloc se remplace lui-même : on retire la version précédente, où qu'elle soit.
    h = re.sub(r'<section class="schemas-bateaux">.*?</section>', "", h, flags=re.S)
    h = re.sub(r'<style id="sb-css">.*?</style>', "", h, flags=re.S)
    if "</head>" in h:
        h = h.replace("</head>", f'<style id="sb-css">{CSS}</style>\n</head>', 1)
    n = 0
    for lang in LANGUES:
        ancre = f'<nav class="sommaire" id="sommaire-{lang}"'
        if ancre in h:
            h = h.replace(ancre, bloc(lang) + ancre, 1)
            n += 1
    page.write_text(h, encoding="utf-8")
    return n


def main() -> int:
    page = Path(sys.argv[1]) if len(sys.argv) > 1 else RACINE / "projets/sailingmore/site/cours.html"
    print(f"{page} · {injecter(page)} langues")
    return 0


if __name__ == "__main__":
    sys.exit(main())
