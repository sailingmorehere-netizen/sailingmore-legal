# © 2026 Sailing More — tous droits réservés. All rights reserved.
"""La marque Sailing More : une seule source pour tout ce qui est partagé.

Nicolas, 21/11/2026 : « tout ce qu'on fait sur le site doit être lié à nos publications story etc ».
Le site (`accueil_site.py`) et les feuilles (`feuille_promo.py`) lisent ici les mêmes réseaux, les
mêmes couleurs, les mêmes prix. Un prix change : il change ici, et nulle part ailleurs.

Le module ne dessine rien, n'écrit rien et ne lit aucun fichier à l'import : ce ne sont que des données.
"""
from __future__ import annotations

MARQUE = "SAILING MORE"
HEURE_PUBLICATION = "18:00"
FUSEAU = "Europe/Paris"

# Couleurs telles que dessinées dans le code : feuille_promo.py (OR, ROUGE, CREME, EAU, GRIS, BLANC)
# et regates_page.py pour le fond #0a1f33.
COULEURS = {
    "fond": "#0a1f33",
    "or": "#e23a3e",
    "rouge": "#ff6048",
    "creme": "#f0eada",
    "eau": "#9db2c6",
    "gris": "#a8b6c4",
    "blanc": "#ffffff",
}


def rgb(nom: str) -> tuple[int, int, int]:
    """Une couleur nommée en triplet (r, g, b), pour PIL."""
    h = COULEURS[nom].lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


POLICES = {
    "dossier": "/opt/data/assets/fonts",
    "titre": "Anton-Regular.ttf",
    "texte": "SpaceGrotesk.ttf",
    "rond": "ArchivoBlack-Regular.ttf",
}

# Dans l'ordre d'affichage des feuilles. Le site en tire sa propre liste (Telegram à gauche d'Instagram).
RESEAUX = [
    {
        "nom": "Facebook",
        "pseudo": "facebook.com/SailingMore",
        "cle": "facebook",
        "url": "https://www.facebook.com/SailingMore",
        "svg": (
            '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="#1877f2" d="M22 12a10 10 0 1 0-11.6 9.9v-7H7.9V12h2.5V9.8c0-2.5 1.5-3.9 3.7-3.9 1.1 0 2.2.2 2.2.2v2.4h-1.2c-1.2 0-1.6.8-1.6 1.6V12h2.7l-.4 2.9h-2.3v7A10 10 0 0 0 22 12z"/></svg>'
        ),
        "logo": "/opt/data/assets/reseaux/facebook.png",
    },
    {
        "nom": "Instagram",
        "pseudo": "@sailingmorehere",
        "cle": "instagram",
        "url": "https://www.instagram.com/sailingmorehere/",
        "svg": (
            '<svg viewBox="0 0 24 24" aria-hidden="true"><defs><linearGradient id="ig" x1="0" y1="1" x2="1" y2="0">'
            '<stop offset="0" stop-color="#feda75"/><stop offset=".35" stop-color="#fa7e1e"/>'
            '<stop offset=".65" stop-color="#d62976"/><stop offset="1" stop-color="#962fbf"/></linearGradient></defs>'
            '<path fill="url(#ig)" fill-rule="evenodd" d="M12 2.2c3.2 0 3.6 0 4.9.1 1.2.1 1.9.3 2.4.5.6.2 1 .5 1.5 1 .5.5.8.9 1 1.5.2.5.4 1.2.5 2.4.1 1.3.1 1.7.1 4.9s0 3.6-.1 4.9c-.1 1.2-.3 1.9-.5 2.4-.2.6-.5 1-1 1.5-.5.5-.9.8-1.5 1-.5.2-1.2.4-2.4.5-1.3.1-1.7.1-4.9.1s-3.6 0-4.9-.1c-1.2-.1-1.9-.3-2.4-.5-.6-.2-1-.5-1.5-1-.5-.5-.8-.9-1-1.5-.2-.5-.4-1.2-.5-2.4C2.2 15.6 2.2 15.2 2.2 12s0-3.6.1-4.9c.1-1.2.3-1.9.5-2.4.2-.6.5-1 1-1.5.5-.5.9-.8 1.5-1 .5-.2 1.2-.4 2.4-.5 1.3-.1 1.7-.1 4.9-.1zm0 3.2c-3.1 0-3.5 0-4.7.1-1 .1-1.4.2-1.7.4-.4.2-.7.4-1 .7-.3.3-.5.6-.7 1-.2.3-.3.7-.4 1.7-.1 1.2-.1 1.6-.1 4.7s0 3.5.1 4.7c.1 1 .2 1.4.4 1.7.2.4.4.7.7 1 .3.3.6.5 1 .7.3.2.7.3 1.7.4 1.2.1 1.6.1 4.7.1s3.5 0 4.7-.1c1-.1 1.4-.2 1.7-.4.4-.2.7-.4 1-.7.3-.3.5-.6.7-1 .2-.3.3-.7.4-1.7.1-1.2.1-1.6.1-4.7s0-3.5-.1-4.7c-.1-1-.2-1.4-.4-1.7-.2-.4-.4-.7-.7-1-.3-.3-.6-.5-1-.7-.3-.2-.7-.3-1.7-.4-1.2-.1-1.6-.1-4.7-.1zm0 3.1a5.5 5.5 0 1 1 0 11 5.5 5.5 0 0 1 0-11zm0 3.2a2.3 2.3 0 1 0 0 4.6 2.3 2.3 0 0 0 0-4.6zm5.7-3.5a1.3 1.3 0 1 1 0 2.6 1.3 1.3 0 0 1 0-2.6z"/></svg>'
        ),
        "logo": "/opt/data/assets/reseaux/instagram.png",
    },
    {
        "nom": "YouTube",
        "pseudo": "@sailingmore",
        "cle": "youtube",
        "url": "https://www.youtube.com/@SailingMore",
        "svg": (
            '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="#ff0000" d="M23 7.5a3 3 0 0 0-2.1-2.1C19 4.9 12 4.9 12 4.9s-7 0-8.9.5A3 3 0 0 0 1 7.5 31 31 0 0 0 .5 12 31 31 0 0 0 1 16.5a3 3 0 0 0 2.1 2.1c1.9.5 8.9.5 8.9.5s7 0 8.9-.5a3 3 0 0 0 2.1-2.1A31 31 0 0 0 23.5 12 31 31 0 0 0 23 7.5zM9.8 15.4V8.6L15.7 12z"/></svg>'
        ),
        "logo": "/opt/data/assets/reseaux/youtube.png",
    },
    {
        "nom": "Telegram",
        "pseudo": "t.me/sailingmorehere",
        "cle": "telegram",
        "url": "https://t.me/sailingmorehere",
        "svg": (
            '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="#29a9eb" d="M12 2a10 10 0 1 0 0 20 10 10 0 0 0 0-20zm4.6 6.6-1.6 7.6c-.1.5-.4.6-.8.4l-2.3-1.7-1.1 1.1c-.1.1-.2.2-.4.2l.2-2.5 4.6-4.1c.2-.2 0-.3-.3-.1l-5.7 3.6-2.4-.8c-.5-.2-.5-.5.1-.7l9.4-3.6c.4-.2.8 0 .6.6z"/></svg>'
        ),
        "logo": "/opt/data/assets/reseaux/telegram.png",
    },
    {
        "nom": "X",
        "pseudo": "@SailingMore",
        "cle": "x",
        "url": "https://x.com/SailingMore",
        "svg": (
            '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="#ffffff" d="M18.9 2H22l-6.8 7.8L23 22h-6.3l-4.9-6.4L6.2 22H3l7.3-8.3L2.4 2h6.4l4.5 5.9L18.9 2zm-1.1 18h1.7L7.4 3.7H5.6L17.8 20z"/></svg>'
        ),
        "logo": "/opt/data/assets/reseaux/x.png",
    },
]

# Les quatre formules du site, reprises de site_blocks.PACKS (blocs-parite-2026-11-20.md).
FORMULES = [
    {"cle": "p1", "nom": "Essai une semaine", "prix": 440, "prix_affiche": "440 €",
     "comprend": "2 publications · 1 concours", "duree": "7 j", "publications": 2, "concours": 1},
    {"cle": "p2", "nom": "Présence un mois", "prix": 890, "prix_affiche": "890 €",
     "comprend": "4 publications · 2 concours", "duree": "30 j", "publications": 4, "concours": 2},
    {"cle": "p3", "nom": "Parité un mois", "prix": 1390, "prix_affiche": "1 390 €",
     "comprend": "5 publications · 2 concours", "duree": "30 j", "publications": 5, "concours": 2},
    {"cle": "p4", "nom": "Trimestre", "prix": 3900, "prix_affiche": "3 900 €",
     "comprend": "12 publications · 6 concours", "duree": "90 j", "publications": 12, "concours": 6},
]

PRIX_MIN = min(f["prix"] for f in FORMULES)
PRIX_MAX = max(f["prix"] for f in FORMULES)
