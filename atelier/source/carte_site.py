#!/usr/bin/env python3
"""Fabrique la carte du monde en points pour la page d'accueil.

Source : `ne_110m_land.geojson` (Natural Earth, domaine public) rasterisé une fois en 80 × 40
cellules — voir `cache/rhum/carte-monde.json`. On dessine ici un PNG de nuit, et la page ne pose
par-dessus que les six points lumineux des pays : 1 042 cercles en SVG alourdissaient la page de
56 Ko pour un résultat identique.

Usage : python3 scripts/carte_site.py
"""
from __future__ import annotations

import json
import os
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

RACINE = Path(os.environ.get("SITE_ROOT", "/opt/data"))
POINTS = RACINE / "cache/rhum/carte-monde.json"
SORTIE = RACINE / "cache/rhum/site/carte-monde.png"
LARGEUR, HAUTEUR = 1000, 500
NUIT = (8, 22, 42)
POINT = (33, 74, 105)
POINT_CHAUD = (44, 96, 132)


def main() -> None:
    pts = json.loads(POINTS.read_text())
    fond = Image.new("RGB", (LARGEUR, HAUTEUR), NUIT)
    # halo doux au centre pour éviter le fond plat
    halo = Image.new("L", (LARGEUR, HAUTEUR), 0)
    ImageDraw.Draw(halo).ellipse((-200, -260, LARGEUR + 200, HAUTEUR + 120), fill=46)
    halo = halo.filter(ImageFilter.GaussianBlur(120))
    fond = Image.composite(Image.new("RGB", (LARGEUR, HAUTEUR), (14, 42, 68)), fond, halo)

    calque = Image.new("RGB", (LARGEUR, HAUTEUR), (0, 0, 0))
    d = ImageDraw.Draw(calque)
    for i, (x, y) in enumerate(pts):
        # une cellule sur cinq un peu plus claire : la carte respire au lieu d'être un aplat
        r = 2.4
        d.ellipse((x - r, y - r, x + r, y + r), fill=POINT_CHAUD if i % 5 == 0 else POINT)

    fond = Image.blend(fond, Image.blend(fond, calque, 0.9), 0.85)
    fond.save(SORTIE, optimize=True)
    print(f"{SORTIE} — {SORTIE.stat().st_size // 1024} Ko, {len(pts)} points")


if __name__ == "__main__":
    main()
