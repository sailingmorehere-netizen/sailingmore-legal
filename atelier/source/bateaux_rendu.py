#!/usr/bin/env python3
"""Rend les SVG de nomenclature en WebP, sans autre dépendance que Pillow.

Chaîne unique (une seule source, un seul chemin) :
  bateaux_page.py --ecrire  →  images-src/bateaux/*.svg + bateaux-images.json (manifeste)
                            →  ce module lit le manifeste, rend chaque SVG, pose le WebP au chemin
                               du manifeste (`site/images/bateaux/…webp`) — celui du HTML, du JSON-LD
                               et du sitemap.

Il ne sait lire que le SVG que `bateaux_page.image_svg` écrit : g/translate, rect, polygon, polyline,
path (M/L), ellipse, circle, text/tspan (rotate(-90) compris), feuille de style à sélecteurs de classes.
Rendu en 3× puis réduit (anticrénelage). Police : Inter, déjà dans site/fonts.

    python3 scripts/bateaux_rendu.py            # rend les neuf images depuis le manifeste
"""
from __future__ import annotations

import json
import math
import os
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

from PIL import Image, ImageColor, ImageDraw, ImageFont

RACINE = Path(os.environ.get("SITE_ROOT") or Path(__file__).resolve().parent.parent)
SITE = RACINE / "projets" / "sailingmore" / "site"
SS = 3                      # sur-échantillonnage
NS = "{http://www.w3.org/2000/svg}"
POLICES = {400: "inter-regular.woff", 600: "inter-semibold.woff", 300: "inter-light.woff"}
_cache_police: dict = {}


def _police(taille: float, poids: int, dossier_site: Path):
    poids = 600 if poids >= 600 else 400
    cle = (round(taille * SS), poids)
    if cle not in _cache_police:
        _cache_police[cle] = ImageFont.truetype(str(dossier_site / "fonts" / POLICES[poids]), cle[0])
    return _cache_police[cle]


# ───────────────────────────────────────────────────────────── styles
def _regles(css: str):
    out = []
    for i, (sel, corps) in enumerate(re.findall(r"([^{}]+)\{([^{}]*)\}", css)):
        decl = dict((k.strip(), v.strip()) for k, v in (d.split(":", 1) for d in corps.split(";") if ":" in d))
        for s in sel.split(","):
            parts = s.split()
            spec = sum(1 + p.count(".") for p in parts)
            out.append((spec, i, parts, decl))
    return sorted(out, key=lambda r: (r[0], r[1]))


def _match(part: str, el) -> bool:
    tag, *classes = part.split(".")
    if tag and el.tag.replace(NS, "") != tag:
        return False
    have = (el.get("class") or "").split()
    return all(c in have for c in classes)


def _style(el, chaine, regles) -> dict:
    """Style calculé : héritage de fill/stroke exclu (les classes les posent), font/texte hérités."""
    st: dict = {}
    for spec, _, parts, decl in regles:
        if not _match(parts[-1], el):
            continue
        reste = parts[:-1]
        anc = list(reversed(chaine))
        ok, k = True, 0
        for p in reversed(reste):
            while k < len(anc) and not _match(p, anc[k]):
                k += 1
            if k >= len(anc):
                ok = False
                break
            k += 1
        if ok:
            st.update(decl)
    for a in ("fill", "stroke", "stroke-width", "font-size", "font-weight", "opacity", "letter-spacing"):
        if el.get(a) is not None:
            st.setdefault(a, el.get(a))
    return st


def _couleur(v, opacite=1.0):
    if not v or v == "none":
        return None
    m = re.match(r"rgba\(([^)]*)\)", v)
    if m:
        r, g, b, a = [float(x) for x in m.group(1).split(",")]
        return (int(r), int(g), int(b), int(255 * a * opacite))
    r, g, b = ImageColor.getrgb(v)[:3]
    return (r, g, b, int(255 * opacite))


# ───────────────────────────────────────────────────────────── dessin
def _trait(draw, pts, coul, larg, ferme=False, tirets=None):
    if not coul or not pts:
        return
    w = max(1, round(larg * SS))
    if ferme:
        pts = pts + [pts[0]]
    if tirets:
        on, off = tirets[0] * SS, tirets[1] * SS
        for a, b in zip(pts, pts[1:]):
            d = math.hypot(b[0] - a[0], b[1] - a[1])
            t = 0.0
            while t < d:
                t2 = min(d, t + on)
                p = (a[0] + (b[0] - a[0]) * t / d, a[1] + (b[1] - a[1]) * t / d)
                q = (a[0] + (b[0] - a[0]) * t2 / d, a[1] + (b[1] - a[1]) * t2 / d)
                draw.line([p, q], fill=coul, width=w)
                t += on + off
        return
    draw.line(pts, fill=coul, width=w, joint="curve")
    r = w / 2                       # bouts arrondis : un disque à chaque sommet, sinon les angles s'ébrèchent
    for x, y in pts:
        draw.ellipse([x - r, y - r, x + r, y + r], fill=coul)


def _nombres(s):
    return [float(x) for x in re.findall(r"-?\d+(?:\.\d+)?", s)]


def _sous_chemins(d: str):
    subs = []
    for seg in re.findall(r"M[^M]*", d):
        n = _nombres(seg)
        subs.append([(n[i], n[i + 1]) for i in range(0, len(n) - 1, 2)])
    return subs


def _texte(img, el, st, ox, oy, dossier_site, chaine, regles, ech):
    """Un <text> (et ses <tspan>) : posé sur sa ligne de base, ancre start/end, rotation -90 possible.
    `ech` : rapport viewBox → pixels (1,2) ; tailles et positions en sont multipliées."""
    taille = float(re.sub("px", "", st.get("font-size", "16"))) * ech
    poids = int(st.get("font-weight", "400"))
    fill = _couleur(st.get("fill", "#eef3f7"))
    esp = st.get("letter-spacing")
    esp = float(esp[:-2]) * taille if esp and esp.endswith("em") else float(esp or 0) * ech
    morceaux = [(el.text or "", taille, poids, fill, esp)]
    for ts in el:
        sts = _style(ts, chaine + [el], regles)
        t2 = float(re.sub("px", "", sts["font-size"])) * ech if "font-size" in sts else taille
        e2 = sts.get("letter-spacing")
        e2 = float(e2[:-2]) * t2 if e2 and e2.endswith("em") else (esp if e2 is None else float(e2) * ech)
        morceaux.append((ts.text or "", t2, int(sts.get("font-weight", poids)), _couleur(sts.get("fill")) or fill, e2))
        if ts.tail:
            morceaux.append((ts.tail, taille, poids, fill, esp))
    largeur = 0.0
    for t, tz, pd, _, e in morceaux:
        f = _police(tz, pd, dossier_site)
        largeur += f.getlength(t) + e * SS * len(t)
    x0, y0 = float(el.get("x", 0)), float(el.get("y", 0))
    rot = 0
    tr = el.get("transform", "")
    m = re.search(r"translate\(([-\d. ]+)\)", tr)
    if m:
        x0, y0 = _nombres(m.group(1))[:2]
    if "rotate(-90)" in tr:
        rot = 90
    cadre = Image.new("RGBA", (int(largeur) + 8 * SS, int(taille * 2 * SS)), (0, 0, 0, 0))
    d = ImageDraw.Draw(cadre)
    base = int(taille * 1.4 * SS)
    fin = el.get("text-anchor") == "end"
    x = 4.0 * SS
    for t, tz, pd, col, e in morceaux:
        f = _police(tz, pd, dossier_site)
        for ch in t:
            d.text((x, base), ch, font=f, fill=col, anchor="ls")
            x += f.getlength(ch) + e * SS
    if rot:
        cadre = cadre.rotate(rot, expand=True)
        # après rotation de +90° (sens inverse des aiguilles) le départ du texte est en bas à gauche
        px = (ox + x0) * SS * ech - base
        py = (oy + y0) * SS * ech - (cadre.height - 4 * SS)
    else:
        px = (ox + x0) * SS * ech - 4 * SS - (largeur if fin else 0)
        py = (oy + y0) * SS * ech - base
    img.alpha_composite(cadre, (int(round(px)), int(round(py))))


def rendre_svg(svg_texte: str, dossier_site: Path) -> Image.Image:
    racine = ET.fromstring(svg_texte)
    vb = [float(v) for v in racine.get("viewBox").split()]
    larg, haut = float(racine.get("width")), float(racine.get("height"))
    echelle = larg / vb[2]
    css = "".join(s.text or "" for s in racine.iter(NS + "style"))
    regles = _regles(css)
    k = echelle * SS
    img = Image.new("RGBA", (round(larg * SS), round(haut * SS)), (0, 0, 0, 0))

    def parcours(el, chaine, ox, oy):
        tag = el.tag.replace(NS, "")
        if tag in ("title", "style"):
            return
        if tag == "g":
            m = re.search(r"translate\(([-\d. ]+)\)", el.get("transform", ""))
            if m:
                dx, dy = _nombres(m.group(1))[:2]
                ox, oy = ox + dx, oy + dy
            for c in el:
                parcours(c, chaine + [el], ox, oy)
            return
        if tag == "a":                       # lien d'étiquette : ne dessine rien lui-même
            for c in el:
                parcours(c, chaine + [el], ox, oy)
            return
        st = _style(el, chaine, regles)
        op = float(st.get("opacity", 1))
        fill, stroke = _couleur(st.get("fill", "black" if tag not in ("polyline",) else "none"), op), _couleur(st.get("stroke"), op)
        sw = float(re.sub("px", "", st.get("stroke-width", "1")))
        tirets = [float(x) for x in st["stroke-dasharray"].split()] if "stroke-dasharray" in st else None
        # chaque élément est dessiné sur sa propre couche : les alphas se composent comme en SVG
        couche = Image.new("RGBA", img.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(couche)
        P = lambda pts: [((ox + x) * k, (oy + y) * k) for x, y in pts]  # noqa: E731
        if tag == "rect":
            fc = _couleur(el.get("fill"))
            d.rectangle([(ox + float(el.get("x", 0))) * k, (oy + float(el.get("y", 0))) * k,
                         (ox + float(el.get("x", 0)) + float(el.get("width"))) * k - 1,
                         (oy + float(el.get("y", 0)) + float(el.get("height"))) * k - 1], fill=fc)
        elif tag in ("polygon", "polyline"):
            n = _nombres(el.get("points"))
            pts = P([(n[i], n[i + 1]) for i in range(0, len(n) - 1, 2)])
            if tag == "polygon" and fill:
                d.polygon(pts, fill=fill)
            _trait(d, pts, stroke, sw * echelle, ferme=tag == "polygon", tirets=[t * echelle for t in tirets] if tirets else None)
        elif tag == "path":
            for sub in _sous_chemins(el.get("d")):
                _trait(d, P(sub), stroke, sw * echelle)
        elif tag in ("ellipse", "circle"):
            cx, cy = float(el.get("cx")), float(el.get("cy"))
            rx = float(el.get("rx", el.get("r", 0)))
            ry = float(el.get("ry", el.get("r", 0)))
            box = [(ox + cx - rx) * k, (oy + cy - ry) * k, (ox + cx + rx) * k, (oy + cy + ry) * k]
            d.ellipse(box, fill=fill)
            if stroke:
                d.ellipse(box, outline=stroke, width=max(1, round(sw * k)))
        elif tag == "text":
            _texte(couche, el, st, ox, oy, dossier_site, chaine, regles, echelle)
        else:
            return
        if tag != "rect" or True:
            img.alpha_composite(couche)

    # le texte de titre (hors <g>) et le reste : parcours simple
    for c in racine:
        parcours(c, [racine], 0.0, 0.0)
    fond = Image.new("RGB", img.size, (10, 26, 43))
    fond.paste(img, mask=img.split()[3])
    return fond.resize((round(larg), round(haut)), Image.LANCZOS)


def rendre_manifeste(manifeste: Path = RACINE / "bateaux-images.json", dossier_site: Path = SITE) -> list[str]:
    """Lit le manifeste, rend chaque SVG, pose chaque WebP à son chemin. Rend la liste des fichiers posés."""
    posees = []
    for e in json.loads(manifeste.read_text(encoding="utf-8")):
        svg = RACINE / e["svg"]
        cible = dossier_site / e["webp"]
        cible.parent.mkdir(parents=True, exist_ok=True)
        im = rendre_svg(svg.read_text(encoding="utf-8"), dossier_site)
        if im.width != e["largeur"]:
            raise SystemExit(f"{svg.name} : largeur {im.width} ≠ {e['largeur']} du manifeste")
        im.save(cible, "WEBP", quality=88, method=6)
        posees.append(cible.relative_to(dossier_site).as_posix())
    return posees


if __name__ == "__main__":
    for p in rendre_manifeste():
        print("posée :", p, f"{(SITE / p).stat().st_size / 1024:.0f} Ko")
