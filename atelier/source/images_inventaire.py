#!/usr/bin/env python3
"""Inventaire des images du site + titres. Écrit images-inventaire.md à la racine de la copie."""
import os, re, glob, sys
RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(RACINE, "projets", "sailingmore", "site")
try:
    from PIL import Image
except Exception:
    Image = None
EXT = (".jpg", ".jpeg", ".png", ".webp", ".gif", ".svg")
out = ["# Inventaire des images du site (copie de travail)", ""]
out.append(f"PIL disponible : {bool(Image)}")
tot = {}
for dossier, _, fichiers in os.walk(SITE):
    for f in sorted(fichiers):
        if f.lower().endswith(EXT):
            p = os.path.join(dossier, f)
            rel = os.path.relpath(p, SITE)
            d = rel.split(os.sep)[0] if os.sep in rel else "(racine)"
            t = tot.setdefault(d, [0, 0, []])
            t[0] += 1
            t[1] += os.path.getsize(p)
            dim = ""
            if Image:
                try:
                    with Image.open(p) as im:
                        dim = f"{im.size[0]}x{im.size[1]}"
                        ex = im.getexif() if hasattr(im, "getexif") else {}
                        cop = ex.get(33432, "") if ex else ""
                except Exception:
                    dim = "?"
                    cop = ""
            else:
                cop = ""
            if d != "stages-img" and d != "drapeaux":
                out.append(f"- {rel} — {os.path.getsize(p)} o {dim} copyright={'oui' if cop else 'non'}")
out.append("")
out.append("## Totaux par dossier")
for d, (n, s, _) in sorted(tot.items()):
    out.append(f"- {d} : {n} fichiers, {s//1024} Ko")
out.append("")
out.append("## Titres")
for p in sorted(glob.glob(SITE + "/*.html") + glob.glob(SITE + "/stories/*.html")):
    h = open(p, encoding="utf-8", errors="ignore").read()
    m = re.search(r"<title>(.*?)</title>", h, re.S)
    out.append(f"- {os.path.relpath(p, SITE)} : {m.group(1).strip() if m else 'AUCUN'} ({len(m.group(1).strip()) if m else 0} car.) ImageObject={h.count('ImageObject')}")
open(os.path.join(RACINE, "images-inventaire.md"), "w", encoding="utf-8").write("\n".join(out) + "\n")
print("\n".join(out))
