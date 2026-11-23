#!/usr/bin/env python3
"""Vérifie que les images à nous s'ouvrent encore, et portent Artist/Copyright (EXIF), Credit (IPTC) ou Copyright (PNG)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import marque_fichier
from PIL import Image, IptcImagePlugin

mal = 0
for p in marque_fichier.images_a_nous():
    with Image.open(p) as im:
        im.load()
        if p.suffix.lower() == ".png":
            ok = "Copyright" in im.text and "Credit" in im.text
            detail = im.text.get("Credit", "")
        elif p.suffix.lower() == ".webp":
            ex = im.getexif()
            ok = bool(ex.get(315)) and bool(ex.get(33432))
            detail = ex.get(315, "")
        else:
            ex = im.getexif()
            ip = IptcImagePlugin.getiptcinfo(im) or {}
            cred = ip.get((2, 110), b"")
            ok = bool(ex.get(315)) and bool(ex.get(33432)) and cred.decode("utf-8", "ignore") == marque_fichier.CREDIT
            detail = cred.decode("utf-8", "ignore")
    if not ok:
        mal += 1
        print("MANQUE", p)
print("images vérifiées, manquantes :", mal, "· exemple credit :", detail)
