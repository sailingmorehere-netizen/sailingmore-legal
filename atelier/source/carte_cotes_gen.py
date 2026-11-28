# © 2026 Sailing More — tous droits réservés. All rights reserved.
"""Fabrique `carte_cotes.txt` (le tracé des côtes de la carte) depuis un GeoJSON de terres émergées.

Usage : python3 scripts/carte_cotes_gen.py <ne_110m_land.geojson> [tolérance en degrés, 0.35 par défaut]

Source prévue : Natural Earth « 110m land » (domaine public, naturalearthdata.com) ; une copie existe
dans /opt/data/assets/cartes/ne_110m_land.geojson. Le tracé est simplifié (Douglas-Peucker) puis
arrondi au dixième de degré, dans le repère de la carte : x = lon + 180, y = 90 - lat.
Sortie : une chaîne `d` de <path>, visée sous 12 Ko. Aucun appel réseau.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

SORTIE = Path(__file__).resolve().parent / "carte_cotes.txt"


def _dist(p, a, b) -> float:
    (x, y), (x1, y1), (x2, y2) = p, a, b
    dx, dy = x2 - x1, y2 - y1
    if dx == 0 and dy == 0:
        return ((x - x1) ** 2 + (y - y1) ** 2) ** 0.5
    t = max(0.0, min(1.0, ((x - x1) * dx + (y - y1) * dy) / (dx * dx + dy * dy)))
    return ((x - (x1 + t * dx)) ** 2 + (y - (y1 + t * dy)) ** 2) ** 0.5


def simplifier(pts: list, tol: float) -> list:
    if len(pts) < 3:
        return pts
    imax, dmax = 0, 0.0
    for i in range(1, len(pts) - 1):
        d = _dist(pts[i], pts[0], pts[-1])
        if d > dmax:
            imax, dmax = i, d
    if dmax <= tol:
        return [pts[0], pts[-1]]
    return simplifier(pts[: imax + 1], tol)[:-1] + simplifier(pts[imax:], tol)


def anneaux(geo: dict):
    for f in geo.get("features", [geo]):
        g = f.get("geometry", f)
        polys = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
        for poly in polys:
            yield poly[0]  # anneau extérieur seulement (les lacs intérieurs ne se lisent pas à cette échelle)


def main(chemin: str, tol: float = 0.35) -> int:
    geo = json.loads(Path(chemin).read_text(encoding="utf-8"))
    morceaux = []
    for an in anneaux(geo):
        pts = simplifier([(lon, lat) for lon, lat in an], tol)
        if len(pts) < 4:
            continue
        s = "M" + " L".join(f"{lon + 180:.1f} {90 - lat:.1f}" for lon, lat in pts) + "Z"
        morceaux.append(s)
    d = "".join(morceaux)
    SORTIE.write_text(d, encoding="utf-8")
    print(f"{len(morceaux)} masses de terre, {len(d)} caractères → {SORTIE}")
    return 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    sys.exit(main(sys.argv[1], float(sys.argv[2]) if len(sys.argv) > 2 else 0.35))
