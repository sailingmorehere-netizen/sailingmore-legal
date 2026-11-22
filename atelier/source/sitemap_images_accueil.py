#!/usr/bin/env python3
"""Déclare dans sitemap.xml les images de la page d'accueil (xmlns:image déjà posé par bateaux_page.maj_sitemap). Idempotent."""
import re
from pathlib import Path

SITE = Path(__file__).resolve().parent.parent / "projets" / "sailingmore" / "site"
CREDIT = "SailingMore.fr — École de voile en ligne"
f = SITE / "sitemap.xml"
x = f.read_text(encoding="utf-8")
html = (SITE / "index.html").read_text(encoding="utf-8")
imgs = []
for src, alt in re.findall(r'<img src="((?:stories/|carte-monde)[^"]+)" alt="([^"]+)"', html):
    if src not in [i[0] for i in imgs]:
        imgs.append((src, alt))
if "xmlns:image" not in x:
    x = x.replace('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
                  '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">')
bloc = "".join(f"<image:image><image:loc>https://sailingmore.fr/{s}</image:loc><image:title>{a.split(' : ')[0]}</image:title>"
               f"<image:caption>{CREDIT} — {a}</image:caption></image:image>" for s, a in imgs)
def _accueil(m):
    corps = re.sub(r"<image:image>.*?</image:image>", "", m.group(2), flags=re.S)  # borné à CETTE <url>
    return m.group(1) + corps + bloc + "</url>"


x = re.sub(r"(<url><loc>https://sailingmore\.fr/</loc>)(.*?)</url>", _accueil, x, count=1, flags=re.S)
f.write_text(x, encoding="utf-8")
print(len(imgs), "images déclarées pour l'accueil")
