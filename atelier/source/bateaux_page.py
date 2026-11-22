#!/usr/bin/env python3
"""Construit `bateaux.html` : la nomenclature illustrée de neuf bateaux, avec filtre, deux niveaux et renvoi au lexique.

Sources uniques : `bateaux_dessins.py` / `bateaux_dessins2.py` (formes et pièces), `bateaux_mots.py` (44 mots
ajoutés au lexique), `projets/sailingmore/lexique.json` (les noms dans six langues : l'étiquette se traduit
comme le reste du site, rien n'est écrit en double dans le SVG). Rien n'est écrit à la main dans site/.

Sorties :
  · site/bateaux.html          la page (SVG en ligne, étiquettes = liens vers lexique.html#ancre, nouvel onglet) ;
  · site/bateaux.json          la correspondance mot → ancres de la page, lue par `lexique_page.py` ;
  · site/sitemap.xml           la page et ses neuf images (image:loc, image:title, image:caption) ;
  · projets/sailingmore/images-src/bateaux/*.svg   les neuf sources des WebP ;
  · bateaux-images.json (racine) la liste que Hermes lit pour rendre les WebP.

    python3 scripts/bateaux_page.py --lexique   # range les mots manquants dans lexique.json (idempotent)
    python3 scripts/bateaux_page.py --verifier  # contrôles, lecture seule
    python3 scripts/bateaux_page.py --ecrire    # lexique + page + json + sources d'images + sitemap
"""
from __future__ import annotations

import html as _html
import json
import math
import os
import re
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bateaux_mots  # noqa: E402
from bateaux_dessins import BATEAUX_1  # noqa: E402
from bateaux_dessins2 import BATEAUX_2  # noqa: E402

RACINE = Path(os.environ.get("SITE_ROOT") or Path(__file__).resolve().parent.parent)
PROJET = RACINE / "projets" / "sailingmore"
SITE = PROJET / "site"
LEXIQUE = PROJET / "lexique.json"
SRC_IMG = PROJET / "images-src" / "bateaux"
MANIFESTE = RACINE / "bateaux-images.json"
URL = "https://sailingmore.fr"
LANGUES = ["fr", "en", "it", "es", "pt", "de"]
BATEAUX = BATEAUX_1 + BATEAUX_2

W = 480            # largeur du repère local ; le dessin est posé à (260, 40) dans un cadre de 1000
DX, DY = 260, 40
GAP = 30           # écart minimal entre deux étiquettes (police 16)
OBST = {"c", "s", "m", "o", "h"}   # formes pleines : un trait de repère ne les traverse pas
VEDETTE = {"x35": "quille", "hobie16": "spinnaker", "laser": "derive-mobile", "49er": "aile-de-rappel",
           "iqfoil": "foil", "kite": "aile-de-kite", "wing": "aile-de-wing", "imoca": "foil", "ultim": "foil"}

# Seconds noms : uniquement un nom ATTESTÉ encore employé (Nicolas, 22/11/2026).
#   bôme / gui : Larousse (« bôme : synonyme de gui »).
#   spinnaker / spi : « spi » est l'abréviation usuelle de spinnaker (Larousse).
# Écartés faute de source : « tangon / boute-hors » (l'OQLF donne boute-hors comme ancienne orthographe de
# bout-dehors, pas comme synonyme de tangon) et « pataras / bastaque » (la bastaque est un autre hauban).
ANCIEN = {"bome": "gui", "spinnaker": "spi"}

CATS = ["tous", "habitable", "multicoque", "deriveur", "skiff", "planche", "kite", "wing", "large"]
UI = {
    "fr": {"titre": "Nomenclature des bateaux", "chapo": "Neuf supports dessinés de profil, chaque pièce nommée et reliée à sa définition du lexique.",
           "retour": "Lexique", "filtre": "Type de bateau", "niveau": "Niveau de détail", "ne": "Essentiel", "nt": "Tout",
           "tous": "Tous", "habitable": "Habitable", "multicoque": "Multicoque", "deriveur": "Dériveur", "skiff": "Skiff",
           "planche": "Planche", "kite": "Kite", "wing": "Wing", "large": "Course au large",
           "un": "bateau", "n": "bateaux", "liste": "Pièces numérotées", "long": "Longueur", "crew": "Équipage",
           "rig": "Gréement", "serie": "Série", "cours": "Comprendre le vocabulaire et les allures : les cours théoriques de voile",
           "leg": "Image de la nomenclature à partager", "sur": "Sur les schémas", "fermer": "Fermer", "nouv": "s'ouvre dans un nouvel onglet",
           "m": "m", "sch": "Schéma"},
    "en": {"titre": "Boat parts diagrams", "chapo": "Nine craft drawn in profile, every part named and linked to its glossary definition.",
           "retour": "Glossary", "filtre": "Type of boat", "niveau": "Level of detail", "ne": "Essential", "nt": "Everything",
           "tous": "All", "habitable": "Cruiser", "multicoque": "Multihull", "deriveur": "Dinghy", "skiff": "Skiff",
           "planche": "Windsurf", "kite": "Kite", "wing": "Wing", "large": "Offshore racing",
           "un": "boat", "n": "boats", "liste": "Numbered parts", "long": "Length", "crew": "Crew",
           "rig": "Rig", "serie": "Class", "cours": "Learn the vocabulary and the points of sail: the online sailing theory course",
           "leg": "Diagram image to share", "sur": "On the diagrams", "fermer": "Close", "nouv": "opens in a new tab",
           "m": "m", "sch": "Diagram"},
    "it": {"titre": "Nomenclatura delle barche", "chapo": "Nove imbarcazioni disegnate di profilo, ogni parte con il suo nome e il rimando al lessico.",
           "retour": "Lessico", "filtre": "Tipo di barca", "niveau": "Livello di dettaglio", "ne": "Essenziale", "nt": "Tutto",
           "tous": "Tutti", "habitable": "Crociera", "multicoque": "Multiscafo", "deriveur": "Deriva", "skiff": "Skiff",
           "planche": "Windsurf", "kite": "Kite", "wing": "Wing", "large": "Regata oceanica",
           "un": "barca", "n": "barche", "liste": "Parti numerate", "long": "Lunghezza", "crew": "Equipaggio",
           "rig": "Armo", "serie": "Classe", "cours": "Capire il vocabolario e le andature: i corsi teorici di vela",
           "leg": "Immagine della nomenclatura da condividere", "sur": "Negli schemi", "fermer": "Chiudi", "nouv": "si apre in una nuova scheda",
           "m": "m", "sch": "Schema"},
    "es": {"titre": "Nomenclatura de los barcos", "chapo": "Nueve embarcaciones dibujadas de perfil, cada pieza con su nombre y enlazada a su definición del léxico.",
           "retour": "Léxico", "filtre": "Tipo de barco", "niveau": "Nivel de detalle", "ne": "Esencial", "nt": "Todo",
           "tous": "Todos", "habitable": "Crucero", "multicoque": "Multicasco", "deriveur": "Deriva", "skiff": "Skiff",
           "planche": "Windsurf", "kite": "Kite", "wing": "Wing", "large": "Regata oceánica",
           "un": "barco", "n": "barcos", "liste": "Piezas numeradas", "long": "Eslora", "crew": "Tripulación",
           "rig": "Aparejo", "serie": "Clase", "cours": "Entender el vocabulario y los rumbos: los cursos teóricos de vela",
           "leg": "Imagen de la nomenclatura para compartir", "sur": "En los esquemas", "fermer": "Cerrar", "nouv": "se abre en una pestaña nueva",
           "m": "m", "sch": "Esquema"},
    "pt": {"titre": "Nomenclatura dos barcos", "chapo": "Nove embarcações desenhadas de perfil, cada peça com o seu nome e ligada à definição do léxico.",
           "retour": "Léxico", "filtre": "Tipo de barco", "niveau": "Nível de detalhe", "ne": "Essencial", "nt": "Tudo",
           "tous": "Todos", "habitable": "Cruzeiro", "multicoque": "Multicasco", "deriveur": "Dinghy", "skiff": "Skiff",
           "planche": "Windsurf", "kite": "Kite", "wing": "Wing", "large": "Regata oceânica",
           "un": "barco", "n": "barcos", "liste": "Peças numeradas", "long": "Comprimento", "crew": "Tripulação",
           "rig": "Aparelho", "serie": "Classe", "cours": "Perceber o vocabulário e os rumos: os cursos teóricos de vela",
           "leg": "Imagem da nomenclatura para partilhar", "sur": "Nos esquemas", "fermer": "Fechar", "nouv": "abre num novo separador",
           "m": "m", "sch": "Esquema"},
    "de": {"titre": "Bezeichnungen am Boot", "chapo": "Neun Boote im Profil gezeichnet, jedes Teil benannt und mit seiner Erklärung im Lexikon verknüpft.",
           "retour": "Lexikon", "filtre": "Bootstyp", "niveau": "Detailgrad", "ne": "Wesentliches", "nt": "Alles",
           "tous": "Alle", "habitable": "Fahrtenyacht", "multicoque": "Mehrrumpf", "deriveur": "Jolle", "skiff": "Skiff",
           "planche": "Windsurf", "kite": "Kite", "wing": "Wing", "large": "Hochseeregatta",
           "un": "Boot", "n": "Boote", "liste": "Nummerierte Teile", "long": "Länge", "crew": "Crew",
           "rig": "Rigg", "serie": "Klasse", "cours": "Vokabular und Kurse verstehen: die Segeltheorie-Kurse",
           "leg": "Bild der Bezeichnungen zum Teilen", "sur": "In den Skizzen", "fermer": "Schließen", "nouv": "öffnet in einem neuen Tab",
           "m": "m", "sch": "Skizze"},
}
NOMS = {
    "x35": ["Voilier Habitable X35", "X35 cruiser-racer", "Barca da crociera X35", "Velero de crucero X35", "Veleiro de cruzeiro X35", "Fahrtenyacht X35"],
    "hobie16": ["Catamaran Hobie 16 avec spi", "Hobie 16 catamaran with spinnaker", "Catamarano Hobie 16 con spi", "Catamarán Hobie 16 con spi", "Catamarã Hobie 16 com spi", "Katamaran Hobie 16 mit Spi"],
    "laser": ["Dériveur Laser", "Laser dinghy", "Deriva Laser", "Deriva Laser", "Dinghy Laser", "Jolle Laser"],
    "49er": ["Skiff 49er", "49er skiff", "Skiff 49er", "Skiff 49er", "Skiff 49er", "49er-Skiff"],
    "iqfoil": ["Planche à voile iQFOiL", "iQFOiL windsurf board", "Tavola a vela iQFOiL", "Tabla de windsurf iQFOiL", "Prancha de windsurf iQFOiL", "iQFOiL-Windsurfboard"],
    "kite": ["Kite Formula Kite", "Formula Kite", "Formula Kite", "Formula Kite", "Formula Kite", "Formula Kite"],
    "wing": ["Wingfoil", "Wingfoil", "Wingfoil", "Wingfoil", "Wingfoil", "Wingfoil"],
    "imoca": ["IMOCA", "IMOCA", "IMOCA", "IMOCA", "IMOCA", "IMOCA"],
    "ultim": ["Ultim", "Ultim", "Ultim", "Ultim", "Ultim", "Ultim"],
}
COURT = {"x35": "X35", "hobie16": "Hobie 16", "laser": "Laser", "49er": "49er", "iqfoil": "iQFOiL",
         "kite": "Formula Kite", "wing": "Wing", "imoca": "IMOCA", "ultim": "Ultim"}
CREW = {
    "1": ["1 personne", "1 person", "1 persona", "1 persona", "1 pessoa", "1 Person"],
    "2": ["2 équipiers", "2 crew", "2 persone", "2 tripulantes", "2 tripulantes", "2 Personen"],
    "plus": ["plusieurs équipiers, selon le programme", "several crew, depending on the programme", "più persone, secondo il programma",
             "varios tripulantes, según el programa", "vários tripulantes, conforme o programa", "mehrere Personen, je nach Programm"],
    "var": ["en solo ou en équipage, selon la course", "solo or crewed, depending on the race", "in solitario o in equipaggio, secondo la regata",
            "en solitario o en tripulación, según la regata", "a solo ou em tripulação, conforme a regata", "solo oder mit Crew, je nach Regatta"],
}
MARQUE = "SailingMore.fr"
MARQUE2 = "École de voile en ligne"
LEGENDE = f"{MARQUE} — {MARQUE2}"
# Titre : la promesse, jamais un slogan (Hermes, 22/11/2026). L'école se dit dans le H1, la description, la fiche.
TITRE_PROMESSE = "Nomenclature des bateaux : toutes les pièces, du Laser à l'Ultim — SailingMore"
# Licence : décision prise à la place de Nicolas — la page des mentions légales, qui dit les conditions de réutilisation.
LICENCE_URL = "https://sailingmore.fr/mentions-legales.html"


def json_ld_images(mots) -> str:
    """Une ImageObject par dessin : copyrightNotice, creditText, creator, license (même texte que le crédit visible)."""
    objets = []
    for b in BATEAUX:
        objets.append({
            "@context": "https://schema.org", "@type": "ImageObject",
            "contentUrl": f"{URL}/images/bateaux/{_nom_fichier(b)}",
            "name": _alt(b, mots, "fr").split(" : ")[0],
            "description": _alt(b, mots, "fr"),
            "width": 1200, "height": int((b["h"] + 80) * 1.2),
            "encodingFormat": "image/webp",
            "creator": {"@type": "Organization", "name": MARQUE, "url": URL},
            "creditText": LEGENDE,
            "copyrightNotice": f"© {date.today().year} {LEGENDE}",
            "license": LICENCE_URL,
            "acquireLicensePage": LICENCE_URL,
        })
    return json.dumps(objets, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")


# ──────────────────────────────────────────────────────────────────────────── lexique
def _lexique() -> dict:
    return json.loads(LEXIQUE.read_text(encoding="utf-8"))


def mots_lexique(avec_nouveaux: bool = True) -> dict[str, tuple[list[str], list[str]]]:
    """clé → (six mots, six définitions). Les 44 mots de bateaux_mots comptent même avant leur rangement."""
    out: dict[str, tuple[list[str], list[str]]] = {}
    for t in _lexique()["themes"]:
        for x in t.get("termes", []):
            out[x["cle"]] = ([x["mot"][l] for l in LANGUES], [x["def"][l] for l in LANGUES])
    if avec_nouveaux:
        for cle, v in bateaux_mots.T.items():
            out.setdefault(cle, v)
    return out


def ranger_lexique() -> int:
    """Insère dans le thème « bateau » les termes de bateaux_mots absents de lexique.json. Idempotent."""
    texte = LEXIQUE.read_text(encoding="utf-8")
    deja = {x["cle"] for t in json.loads(texte)["themes"] for x in t.get("termes", [])}
    neufs = [(c, v) for c, v in bateaux_mots.T.items() if c not in deja]
    if not neufs:
        return 0
    s = lambda v: json.dumps(v, ensure_ascii=False)  # noqa: E731
    blocs = []
    for cle, (mots, defs) in neufs:
        mot = ", ".join(f'"{l}": {s(m)}' for l, m in zip(LANGUES, mots))
        d = ",\n".join(f'            "{l}": {s(x)}' for l, x in zip(LANGUES, defs))
        blocs.append(f'        {{\n          "cle": {s(cle)},\n          "mot": {{{mot}}},\n          "def": {{\n{d}\n          }}\n        }}')
    suivant = texte.index('"cle": "manoeuvre"')        # le thème qui suit « bateau »
    fin_liste = texte.rfind("]", 0, suivant)
    dernier = texte.rfind("}", 0, fin_liste)
    nouveau = texte[:dernier + 1] + ",\n" + ",\n".join(blocs) + texte[dernier + 1:]
    json.loads(nouveau)                                 # jamais un fichier cassé
    LEXIQUE.write_text(nouveau, encoding="utf-8")
    return len(neufs)


# ──────────────────────────────────────────────────────────────────────────── géométrie
def _poly(sh):
    if sh["k"] == "e":
        cx, cy, rx, ry = sh["ell"]
        return [(cx + rx * math.cos(i * math.pi / 8), cy + ry * math.sin(i * math.pi / 8)) for i in range(16)]
    return sh["subs"][0]


def _segments(sh):
    if sh["k"] in ("p", "e"):
        p = _poly(sh)
        return [(p[i], p[(i + 1) % len(p)]) for i in range(len(p))]
    out = []
    for sub in sh["subs"]:
        out += [(sub[i], sub[i + 1]) for i in range(len(sub) - 1)]
    return out


def _proche(p, a, b):
    ax, ay = a
    bx, by = b
    dx, dy = bx - ax, by - ay
    t = 0.0 if dx == dy == 0 else max(0.0, min(1.0, ((p[0] - ax) * dx + (p[1] - ay) * dy) / (dx * dx + dy * dy)))
    return (ax + t * dx, ay + t * dy)


def _dedans(pt, poly):
    x, y = pt
    r = False
    j = len(poly) - 1
    for i in range(len(poly)):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi) + xi:
            r = not r
        j = i
    return r


def _croise(a, b, c, d):
    def o(p, q, r):
        return (q[0] - p[0]) * (r[1] - p[1]) - (q[1] - p[1]) * (r[0] - p[0])
    return o(a, b, c) * o(a, b, d) < 0 and o(c, d, a) * o(c, d, b) < 0


def _snap(boat, mot, ax, ay):
    """L'ancre est ramenée sur le bord de la pièce elle-même, jamais en l'air."""
    best, bd = (ax, ay), 1e9
    for sh in boat["shapes"]:
        if sh["mot"] != mot:
            continue
        for a, b in _segments(sh):
            q = _proche((ax, ay), a, b)
            d = math.hypot(q[0] - ax, q[1] - ay)
            if d < bd:
                best, bd = q, d
    return best


def _pav(desired, gap):
    z = [d - i * gap for i, d in enumerate(desired)]
    blocs: list[list[float]] = []
    for v in z:
        blocs.append([v, 1])
        while len(blocs) > 1 and blocs[-2][0] / blocs[-2][1] >= blocs[-1][0] / blocs[-1][1]:
            s, c = blocs.pop()
            blocs[-1][0] += s
            blocs[-1][1] += c
    out, i = [], 0
    for s, c in blocs:
        for _ in range(c):
            out.append(s / c + i * gap)
            i += 1
    return out


class Mise:
    """Mise en page d'un bateau : côté de l'étiquette, trait, repli en numéro."""

    def __init__(self, boat):
        self.b = boat
        self.h = boat["h"]
        self.parts = []
        for p in boat["parts"]:
            ax, ay = _snap(boat, p["mot"], p["ax"], p["ay"])
            q = dict(p)
            q.update(ax=ax, ay=ay, id=f'{boat["id"]}-{p["mot"]}')
            self.parts.append(q)
        self.obst = []
        for sh in boat["shapes"]:
            if sh["k"] in ("p", "e") and sh["cls"] in OBST:
                poly = _poly(sh)
                xs, ys = [q[0] for q in poly], [q[1] for q in poly]
                self.obst.append((sh["mot"], (min(xs) - 1, min(ys) - 1, max(xs) + 1, max(ys) + 1), poly))
        self._cache: dict = {}
        self.nu: set[str] = set()

    def _libre(self, own, pts):
        """Le trait ne traverse aucune forme pleine d'une autre pièce (échantillonné tous les 3 unités)."""
        for a, b in zip(pts, pts[1:]):
            n = max(1, int(math.hypot(b[0] - a[0], b[1] - a[1]) / 3))
            for i in range(n + 1):
                t = i / n
                x, y = a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t
                if a is pts[0] and i * math.hypot(b[0] - a[0], b[1] - a[1]) / n < 4:
                    continue
                for mot, (x0, y0, x1, y1), poly in self.obst:
                    if mot == own or not (x0 <= x <= x1 and y0 <= y <= y1):
                        continue
                    if _dedans((x, y), poly):
                        return False
        return True

    def _trait(self, p, side, mode, y):
        ex = -8 if side == "l" else W + 8
        if mode == "e" and abs(y - p["ay"]) > 1:
            return [(p["ax"], p["ay"]), (p["ax"], y), (ex, y)]
        return [(p["ax"], p["ay"]), (ex, y)]

    def evaluer(self, assign):
        """assign : id → (côté, mode, y souhaité). Rend positions, traits, pièces en échec."""
        pos, echec = {}, set()
        par_id = {p["id"]: p for p in self.parts}
        for side in ("l", "r"):
            lot = [par_id[i] for i, c in assign.items() if c[0] == side]
            lot.sort(key=lambda p: (assign[p["id"]][2], p["ax"]))
            ys = _pav([assign[p["id"]][2] for p in lot], GAP) if lot else []
            lo, hi = 14, self.h - 10
            if ys and ys[0] < lo:
                ys = [y + (lo - ys[0]) for y in ys]
            if ys and ys[-1] > hi:
                ys = [y - (ys[-1] - hi) for y in ys]
                if ys[0] < lo - 0.01:
                    echec.update(p["id"] for p in lot)
            for p, y in zip(lot, ys):
                pos[p["id"]] = (side, assign[p["id"]][1], round(y, 1))
        traits = {}
        for pid, (side, mode, y) in pos.items():
            p = par_id[pid]
            cle = (pid, side, mode, y)
            if cle not in self._cache:
                pts = self._trait(p, side, mode, y)
                self._cache[cle] = (pts, self._libre(p["mot"], pts))
            pts, ok = self._cache[cle]
            traits[pid] = pts
            if not ok:
                echec.add(pid)
        ids = list(traits)
        for i, a in enumerate(ids):
            for b in ids[i + 1:]:
                if pos[a][0] != pos[b][0]:
                    continue
                if any(_croise(p1, p2, q1, q2) for p1, p2 in zip(traits[a], traits[a][1:]) for q1, q2 in zip(traits[b], traits[b][1:])):
                    echec.add(a)
                    echec.add(b)
        return pos, traits, echec

    def candidats(self, p):
        """(côté, mode, y souhaité), du plus simple au plus détourné."""
        pref = p.get("side") or ("l" if p["ax"] < W / 2 else "r")
        autre = "r" if pref == "l" else "l"
        out = [(pref, "d", p["ay"]), (autre, "d", p["ay"])]
        for side in (pref, autre):
            n = 0
            for dy in range(10, 200, 10):
                for y in (p["ay"] - dy, p["ay"] + dy):
                    if 14 <= y <= self.h - 10 and n < 4:
                        pts = self._trait(p, side, "e", y)
                        if self._libre(p["mot"], pts):
                            out.append((side, "e", y))
                            n += 1
        return out

    def disposer(self):
        """Pose les essentielles d'abord, puis le reste : une étiquette n'entre que si TOUT reste propre."""
        self.nu = set()
        actifs: dict = {}
        ordre = sorted(self.parts, key=lambda p: p["niv"] != "e")
        for p in ordre:
            for cand in self.candidats(p):
                essai = dict(actifs)
                essai[p["id"]] = cand
                if not self.evaluer(essai)[2]:
                    actifs = essai
                    break
            else:
                self.nu.add(p["id"])
        self.pos, self.traits, _ = self.evaluer(actifs)
        # numéros : les essentiels d'abord (1 à k), puis le reste ; badges sans recouvrement
        ordre = sorted(self.parts, key=lambda p: (p["niv"] != "e", p["ax"], p["ay"]))
        placees: list[tuple[float, float]] = []
        for n, p in enumerate(ordre, 1):
            p["n"] = n
            cands = [(0, 0)] + [(r * math.cos(k * math.pi / 4), r * math.sin(k * math.pi / 4))
                                for r in (26, 38, 52) for k in (6, 7, 5, 0, 4, 1, 3, 2)]
            choix = cands[-1]
            for dx, dy in cands:
                x, y = p["ax"] + dx, p["ay"] + dy
                if 12 <= x <= W - 12 and 12 <= y <= self.h - 12 and all(math.hypot(x - u, y - v) >= 34 for u, v in placees):
                    choix = (dx, dy)
                    break
            p["bx"], p["by"] = round(p["ax"] + choix[0], 1), round(p["ay"] + choix[1], 1)
            placees.append((p["bx"], p["by"]))
            p["nu"] = p["id"] in self.nu
        return self


# ──────────────────────────────────────────────────────────────────────────── SVG
def _n(v):
    v = round(v, 1)
    return str(int(v)) if v == int(v) else str(v)


def _pts(pts):
    return " ".join(f"{_n(x)},{_n(y)}" for x, y in pts)


def _forme(sh, niv_mot, ved):
    cls = {"e": "g"}.get(sh["cls"], sh["cls"])
    mot = sh["mot"]
    if mot and ved == mot:
        cls += " v"
    if mot and niv_mot.get(mot) == "t":
        cls += " nt"
    dm = f' data-mot="{mot}"' if mot else ""
    if sh["k"] == "e":
        cx, cy, rx, ry = sh["ell"]
        return f'<ellipse class="{cls}"{dm} cx="{_n(cx)}" cy="{_n(cy)}" rx="{_n(rx)}" ry="{_n(ry)}"/>'
    if sh["k"] == "p":
        return f'<polygon class="{cls}"{dm} points="{_pts(sh["subs"][0])}"/>'
    if len(sh["subs"]) == 1:
        return f'<polyline class="{cls}"{dm} points="{_pts(sh["subs"][0])}"/>'
    d = "".join("M" + "L".join(f"{_n(x)} {_n(y)}" for x, y in s) for s in sh["subs"])
    return f'<path class="{cls}"{dm} d="{d}"/>'


def _texte_label(mot, mots, lang="fr"):
    nom = mots[mot][0][LANGUES.index(lang)]
    return nom


def _inscriptions(b):
    x, y, t = b["ins"]
    vx, vy, *rot = b["vs"]
    coque = (f'<text class="ins" x="{x}" y="{y}" font-size="{t}">{MARQUE}<tspan class="i2"> {MARQUE2}</tspan></text>')
    if rot and rot[0] == 0:
        voile = f'<text class="vs" x="{vx}" y="{vy}">{MARQUE}</text>'
    else:
        voile = f'<text class="vs" transform="translate({vx} {vy}) rotate(-90)">{MARQUE}</text>'
    return coque + voile


def _vue_tight(b):
    return f"250 20 500 {b['h'] + 40}"


def svg_bateau(b, m: Mise, mots, interactif=True, seulement_essentiel=False):
    niv_mot = {p["mot"]: p["niv"] for p in m.parts}
    ved = VEDETTE.get(b["id"])
    formes = []
    for sh in b["shapes"]:
        if seulement_essentiel and sh["mot"] and niv_mot.get(sh["mot"]) == "t":
            continue
        formes.append(_forme(sh, niv_mot, ved))
    labels = []
    for p in m.parts:
        if p["nu"] or (seulement_essentiel and p["niv"] != "e"):
            continue
        side, mode, y = m.pos[p["id"]]
        tr = m.traits[p["id"]]
        nom = mots[p["mot"]][0][0]
        anc = ANCIEN.get(p["mot"])
        sec = f'<tspan class="an"> / {_html.escape(anc)}</tspan>' if anc else ""
        tx = tr[-1][0] + (-6 if side == "l" else 6)
        fin = ' text-anchor="end"' if side == "l" else ""
        txt = f'<text x="{_n(tx)}" y="{_n(y + 5)}"{fin}>{_html.escape(nom)}{sec}</text>'
        if interactif:
            txt = f'<a href="lexique.html#{p["mot"]}" target="_blank" rel="noopener">{txt}</a>'
        cls = "lb " + ("ne" if p["niv"] == "e" else "nt") + (" v" if p["mot"] == ved else "")
        ident = f' id="{p["id"]}" data-mot="{p["mot"]}"' if interactif else ""
        labels.append(f'<g class="{cls}"{ident}><polyline points="{_pts(tr)}"/><circle cx="{_n(p["ax"])}" cy="{_n(p["ay"])}" r="3.5"/>{txt}</g>')
    return "".join(formes), "".join(labels), _inscriptions(b)


CSS_SVG = (
    ".c{fill:#0f2438;stroke:#eef3f7;stroke-width:2;stroke-linejoin:round}"
    ".s,.sn{fill:rgba(238,243,247,.1);stroke:#eef3f7;stroke-width:1.6;stroke-linejoin:round}"
    ".m{fill:#eef3f7;stroke:#eef3f7}.o{fill:#0a1a2b;stroke:#eef3f7;stroke-width:1.6;stroke-linejoin:round}"
    ".h{fill:#9db2c6;stroke:#eef3f7}.n{fill:rgba(157,178,198,.1);stroke:#9db2c6;stroke-width:1.2;stroke-dasharray:5 4}"
    ".l{fill:none;stroke:#eef3f7;stroke-width:4;stroke-linecap:round;stroke-linejoin:round}"
    ".f{fill:none;stroke:#9db2c6;stroke-width:1.5}.g{fill:none;stroke:#eef3f7;stroke-width:2.4;opacity:.9}"
    ".r{fill:none;stroke:#9db2c6;stroke-width:3;stroke-linecap:round;stroke-linejoin:round;opacity:.8}"
    ".v{stroke:#e23a3e}"
    ".lb polyline{fill:none;stroke:#9db2c6;stroke-width:1.2}.lb circle{fill:#eef3f7}"
    ".lb.v polyline{stroke:#e23a3e}.lb.v circle{fill:#e23a3e}"
    ".lb text{font-size:16px;fill:#eef3f7}.an{font-size:14px;fill:#9db2c6}"
    ".ins{fill:#eef3f7;font-weight:600;letter-spacing:.04em}.i2{font-weight:400}.vs{font-size:16px;fill:#9db2c6;letter-spacing:.06em}"
)


# ──────────────────────────────────────────────────────────────────────────── page
def _alt(b, mots, lang):
    noms = ", ".join(mots[k][0][LANGUES.index(lang)] for k in b["alt_mots"])
    tete = {"fr": "Nomenclature", "en": "Parts of", "it": "Nomenclatura", "es": "Nomenclatura", "pt": "Nomenclatura", "de": "Bezeichnungen"}[lang]
    if lang == "en":
        return f"Parts diagram {b['desc'][lang]}: {noms}"
    if lang == "de":
        return f"Bezeichnungen {b['desc'][lang]}: {noms}"
    return f"{tete} {b['desc'][lang]} : {noms}"


def _nom_fichier(b):
    return f"sailingmore-nomenclature-{b['slug']}.webp"


def _num(v, lang):
    return v.replace(",", ".") if lang == "en" else v


def construire():
    mots = mots_lexique()
    ancres = set(mots)
    mises = [Mise(b).disposer() for b in BATEAUX]
    return mots, ancres, mises


def verifier(mots, mises) -> list[str]:
    pb: list[str] = []
    for b, m in zip(BATEAUX, mises):
        formes = {s["mot"] for s in b["shapes"] if s["mot"]}
        vus = set()
        for p in m.parts:
            if p["mot"] in vus:
                pb.append(f"{b['id']} : {p['mot']} en double")
            vus.add(p["mot"])
            if p["mot"] not in mots:
                pb.append(f"{b['id']} : « {p['mot']} » n'a pas d'entrée de lexique")
            if p["mot"] not in formes:
                pb.append(f"{b['id']} : « {p['mot']} » n'a aucune forme dessinée")
        for mot in formes - vus:
            pb.append(f"{b['id']} : forme « {mot} » sans pièce")
        for k in b["alt_mots"]:
            if k not in vus:
                pb.append(f"{b['id']} : alt cite « {k} » absente du bateau")
        ne = [p for p in m.parts if p["niv"] == "e"]
        nunu = [p["mot"] for p in ne if p["nu"]]
        if nunu:
            pb.append(f"{b['id']} : essentielles numérotées faute de trait propre : {', '.join(nunu)}")
        if not 10 <= len(ne) <= 14:
            pb.append(f"{b['id']} : {len(ne)} pièces essentielles (une douzaine attendue)")
    for l in LANGUES:
        for cle, (ms, ds) in bateaux_mots.T.items():
            if not 12 <= len(ds[LANGUES.index(l)].split()) <= 25:
                pb.append(f"lexique {cle} {l} : {len(ds[LANGUES.index(l)].split())} mots")
    return pb


def diagnostic(mises) -> str:
    """Pour chaque pièce numérotée : ce qui bloque un trait droit à sa hauteur, vers chaque côté."""
    out = []
    for b, m in zip(BATEAUX, mises):
        for p in m.parts:
            if not p["nu"]:
                continue
            res = []
            for side in ("l", "r"):
                pts = m._trait(p, side, "d", p["ay"])
                bloc = None
                for a, c in zip(pts, pts[1:]):
                    n = max(1, int(math.hypot(c[0] - a[0], c[1] - a[1]) / 3))
                    for i in range(n + 1):
                        x, y = a[0] + (c[0] - a[0]) * i / n, a[1] + (c[1] - a[1]) * i / n
                        if i * math.hypot(c[0] - a[0], c[1] - a[1]) / n < 4:
                            continue
                        for mot, (x0, y0, x1, y1), poly in m.obst:
                            if mot != p["mot"] and x0 <= x <= x1 and y0 <= y <= y1 and _dedans((x, y), poly):
                                bloc = bloc or mot
                res.append(f"{side}:{bloc or 'libre'}")
            out.append(f"{b['id']:8} {p['mot']:22} ancre=({p['ax']:.0f},{p['ay']:.0f}) {' '.join(res)}")
    return "\n".join(out)


def stats(mises) -> str:
    out = []
    for b, m in zip(BATEAUX, mises):
        ne = sum(1 for p in m.parts if p["niv"] == "e")
        nu = [p["mot"] for p in m.parts if p["nu"]]
        out.append(f"{b['id']:8} {len(m.parts):2} pièces ({ne} essentielles), {len(nu)} numérotées{(' : ' + ', '.join(nu)) if nu else ''}")
    return "\n".join(out)


def donnees_js(mots, mises) -> dict:
    utiles = sorted({p["mot"] for m in mises for p in m.parts})
    bat = {}
    for b, m in zip(BATEAUX, mises):
        fi = b["fiche"]
        bat[b["id"]] = {
            "cat": b["cat"], "court": COURT[b["id"]], "nom": NOMS[b["id"]],
            "alt": [_alt(b, mots, l) for l in LANGUES],
            "fiche": {"long": [None if not fi["long"] else _num(fi["long"], l) + " m" for l in LANGUES],
                      "crew": CREW[fi["crew"]], "rig": [fi["rig"][l] for l in LANGUES], "serie": [fi["serie"][l] for l in LANGUES]},
            "p": [[p["id"], p["mot"], p["niv"], p["n"], 1 if p["nu"] else 0, round(p["bx"]), round(p["by"]),
                   round(p["ax"]), round(p["ay"])] for p in sorted(m.parts, key=lambda q: q["n"])],
        }
    return {"langues": LANGUES, "ui": UI, "cats": CATS, "ordre": [b["id"] for b in BATEAUX],
            "mots": {k: mots[k][0] for k in utiles}, "anc": ANCIEN, "bateaux": bat}


CSS = """
body{margin:0;background:#0a1a2b;color:#eef3f7;font-family:ui-sans-serif,system-ui,-apple-system,"Helvetica Neue",Arial,sans-serif;line-height:1.6;-webkit-font-smoothing:antialiased}
:root{--nuit:#0a1a2b;--nuit2:#0f2438;--creme:#eef3f7;--gris:#9db2c6;--eau:#e23a3e}
*{box-sizing:border-box}
.page{max-width:68rem;margin:0 auto;padding:1.6rem 1.2rem 4rem}
h1{font-size:clamp(1.8rem,6vw,2.6rem);line-height:1.08;margin:.6rem 0 .4rem;font-weight:300;text-transform:uppercase;letter-spacing:-.01em}
h1::after{content:"";display:block;width:3.4rem;height:3px;background:var(--eau);margin:1rem 0 1.1rem}
.chapo{color:var(--gris);max-width:40rem;margin:0 0 1.4rem}
a{color:var(--creme)}
:focus-visible{outline:2px solid #fff;outline-offset:2px}
.cmd{position:sticky;top:var(--h-entete,3.2rem);z-index:15;background:var(--nuit);padding:.7rem 0 .8rem;margin:0 0 1rem;border-bottom:1px solid rgba(238,243,247,.12)}
.cmd .rang{display:flex;flex-wrap:wrap;gap:.4rem .5rem;align-items:center;margin:0 0 .5rem}
.cmd .et{font-size:.7rem;letter-spacing:.16em;text-transform:uppercase;color:var(--gris);margin-right:.3rem}
.puce{font:inherit;font-size:.95rem;color:var(--gris);background:none;border:1px solid rgba(238,243,247,.25);border-radius:2px;padding:.55rem .9rem;min-height:44px;cursor:pointer}
.puce:hover{color:#fff;border-color:rgba(238,243,247,.55)}
.puce[aria-pressed="true"]{color:#fff;border-color:var(--eau);background:rgba(226,58,62,.16)}
.compte{color:var(--gris);font-size:.85rem;margin:.2rem 0 0}
.bandeau{display:flex;flex-wrap:wrap;align-items:center;gap:.4rem .6rem;background:var(--nuit2);border:1px solid rgba(226,58,62,.55);border-radius:2px;padding:.5rem .8rem;margin:0 0 1rem;font-size:.95rem}
.bandeau .bt{color:var(--creme);font-weight:600}
.bandeau button{font:inherit;font-size:.9rem;color:var(--creme);background:none;border:1px solid rgba(238,243,247,.3);border-radius:2px;padding:.4rem .7rem;min-height:44px;cursor:pointer}
.bandeau button[aria-current="true"]{border-color:var(--eau);background:rgba(226,58,62,.16)}
.bandeau .x{margin-left:auto;color:var(--gris)}
.bat{background:var(--nuit2);border-left:3px solid var(--eau);padding:1rem 1.1rem 1.2rem;margin:0 0 1.6rem}
.bat[hidden]{display:none}
.bat h2{font-size:1.25rem;font-weight:600;margin:0 0 .4rem}
.sch{margin:0}
.sch svg{display:block;width:100%;height:auto;font-family:inherit}
.dsn .lb a{cursor:pointer}
.dsn .lb a:hover text{text-decoration:underline}
.niv-ne .nt{display:none}
.sch.num .lb{display:none}
.bd{cursor:pointer}
.bd circle{fill:var(--nuit);stroke:var(--creme);stroke-width:1.8}
.bd text{font-size:20px;font-weight:700;fill:var(--creme);text-anchor:middle}
.bd line{stroke:var(--gris);stroke-width:1.2}
.bd.v circle{stroke:var(--eau)}
.sch:not(.num) .bd:not(.fb){display:none}
.dsn .ins{font-size:14px}
.sch.num .ins{font-size:20px}.sch.num .i2{display:none}.sch.num .vs{font-size:20px}
.dsn [data-mot].on{stroke:#e23a3e!important;stroke-width:4!important;filter:drop-shadow(0 0 6px #e23a3e)}
.dsn .bd.on circle{stroke:#e23a3e;stroke-width:4;filter:drop-shadow(0 0 6px #e23a3e)}
.dsn .an-r{fill:none;stroke:#e23a3e;stroke-width:2;filter:drop-shadow(0 0 5px #e23a3e)}
.liste{list-style:none;margin:.6rem 0 0;padding:0;columns:2 14rem;column-gap:1.6rem}
.liste li{break-inside:avoid;display:flex;gap:.6rem;align-items:baseline}
.liste li[hidden]{display:none}
.liste .no{min-width:1.9rem;color:var(--gris);font-variant-numeric:tabular-nums}
.liste a{display:inline-block;padding:.5rem 0;min-height:44px;font-size:1rem}
.liste .an{font-size:.85rem;color:var(--gris)}
.ls-t{font-size:.7rem;letter-spacing:.16em;text-transform:uppercase;color:var(--gris);margin:.8rem 0 0}
.bas{display:flex;flex-wrap:wrap;gap:1rem 1.6rem;align-items:flex-start;margin-top:1rem}
.fiche{flex:1 1 20rem;font-size:.95rem}
.fiche p{margin:.15rem 0}
.fiche b{color:var(--gris);font-weight:600;font-size:.72rem;letter-spacing:.14em;text-transform:uppercase;margin-right:.5rem}
.fiche .cours{margin-top:.6rem}
.fiche .cours a{text-decoration-color:var(--eau);text-underline-offset:3px}
.vig{flex:0 0 14rem;margin:0}
.vig img{display:block;width:100%;height:auto;border:1px solid rgba(238,243,247,.18);background:var(--nuit)}
.vig figcaption{font-size:.78rem;color:var(--gris);margin-top:.3rem;line-height:1.4}
.pied{color:var(--gris);font-size:.8rem;margin-top:2rem}
@media(max-width:600px){.page{padding:1rem .8rem 3rem}.bat{padding:.8rem .7rem 1rem}.vig{flex-basis:100%}}
"""

JS = r"""
(function(){
  var D = JSON.parse(document.getElementById('donnees-bateaux').textContent);
  var L = D.langues, UI = D.ui, MOTS = D.mots, ANC = D.anc, B = D.bateaux, ORDRE = D.ordre, CATS = D.cats;
  var NS = 'http://www.w3.org/2000/svg';
  var racine = document.getElementById('bateaux');
  var etat = {cat:'tous', niv:'ne', lang:'fr', mot:'', cible:''};
  var temp = false;

  function stocke(k){ try{ return localStorage.getItem(k); }catch(e){ return null; } }
  function range(k,v){ try{ localStorage.setItem(k,v); }catch(e){} }
  function auto(){ var n = (navigator.language || 'fr').slice(0,2); return L.indexOf(n) >= 0 ? n : 'en'; }
  function esc(s){ return String(s).replace(/[&<>"]/g,function(c){ return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]; }); }
  function idx(){ return L.indexOf(etat.lang); }
  function u(k){ return UI[etat.lang][k]; }
  function nom(mot){ var m = MOTS[mot]; return m ? m[idx()] : mot; }
  function fait(el,svg){ return svg ? document.createElementNS(NS,el) : document.createElement(el); }

  /* ── étiquettes : le nom vient du lexique, dans la langue choisie ── */
  function etiquettes(){
    var gs = racine.querySelectorAll('.lb');
    for(var i=0;i<gs.length;i++){
      var t = gs[i].querySelector('text'), mot = gs[i].getAttribute('data-mot');
      while(t.firstChild){ t.removeChild(t.firstChild); }
      t.appendChild(document.createTextNode(nom(mot)));
      if(etat.lang === 'fr' && ANC[mot]){
        var s = document.createElementNS(NS,'tspan'); s.setAttribute('class','an');
        s.textContent = ' / ' + ANC[mot]; t.appendChild(s);
      }
    }
  }

  /* ── numéros sur le dessin + liste sous le bateau ── */
  function numeros(){
    var secs = racine.querySelectorAll('.bat');
    for(var i=0;i<secs.length;i++){
      var id = secs[i].getAttribute('data-id'), b = B[id];
      var g = secs[i].querySelector('.bds');
      if(!g.firstChild){
        for(var k=0;k<b.p.length;k++){
          var p = b.p[k], e = document.createElementNS(NS,'g');
          e.setAttribute('class','bd ' + (p[2]==='e'?'ne':'nt') + (p[4]?' fb':''));
          e.setAttribute('id', p[4] ? p[0] : p[0] + '-n'); e.setAttribute('data-mot', p[1]);
          var h = '';
          if(Math.abs(p[5]-p[7]) + Math.abs(p[6]-p[8]) > 2){ h += '<line x1="'+p[7]+'" y1="'+p[8]+'" x2="'+p[5]+'" y2="'+p[6]+'"/>'; }
          e.innerHTML = h + '<circle cx="'+p[5]+'" cy="'+p[6]+'" r="15"/><text x="'+p[5]+'" y="'+(p[6]+7)+'">'+p[3]+'</text>';
          e.addEventListener('click', (function(pp){ return function(){
            var a = document.getElementById(pp[0] + '-l'); if(a){ a.focus(); a.scrollIntoView({block:'center'}); } }; })(p));
          g.appendChild(e);
        }
      }
      var ol = secs[i].querySelector('.liste'), h2 = '';
      for(var k2=0;k2<b.p.length;k2++){
        var q = b.p[k2], ancien = (etat.lang==='fr' && ANC[q[1]]) ? ' <span class="an">/ ' + esc(ANC[q[1]]) + '</span>' : '';
        h2 += '<li id="'+q[0]+'-l" class="'+(q[2]==='e'?'ne':'nt')+(q[4]?' fb':'')+'" data-mot="'+q[1]+'"><span class="no">'+q[3]+'</span>'
          + '<a href="lexique.html#'+q[1]+'" target="_blank" rel="noopener" title="'+esc(u('nouv'))+'">'+esc(nom(q[1]))+ancien+'</a></li>';
      }
      ol.innerHTML = h2;
    }
  }

  /* ── textes de la page, fiches, images ── */
  function textes(){
    var U = UI[etat.lang];
    document.documentElement.lang = etat.lang;
    var ts = document.querySelectorAll('[data-t]');
    for(var i=0;i<ts.length;i++){ ts[i].textContent = U[ts[i].getAttribute('data-t')]; }
    document.title = U.titre + ' — Sailing More';
    var bs = document.querySelectorAll('#filtre .puce');
    for(var j=0;j<bs.length;j++){ bs[j].textContent = U[bs[j].getAttribute('data-cat')]; }
    var secs = racine.querySelectorAll('.bat');
    for(var s=0;s<secs.length;s++){
      var id = secs[s].getAttribute('data-id'), b = B[id], n = idx();
      secs[s].querySelector('h2').textContent = b.nom[n];
      var f = '';
      if(b.fiche.long[n]){ f += '<p><b>'+esc(U.long)+'</b>'+esc(b.fiche.long[n])+'</p>'; }
      f += '<p><b>'+esc(U.crew)+'</b>'+esc(b.fiche.crew[n])+'</p><p><b>'+esc(U.rig)+'</b>'+esc(b.fiche.rig[n])+'</p><p><b>'+esc(U.serie)+'</b>'+esc(b.fiche.serie[n])+'</p>';
      f += '<p class="cours"><a href="cours.html">'+esc(U.cours)+'</a></p>';
      secs[s].querySelector('.fiche').innerHTML = f;
      var im = secs[s].querySelector('.vig img'); if(im){ im.alt = b.alt[n]; }
      var cap = secs[s].querySelector('.vig figcaption'); if(cap){ cap.textContent = b.alt[n].split(' : ')[0].split(': ')[0] + ' — SailingMore.fr — École de voile en ligne'; }
      secs[s].querySelector('.ls-t').textContent = U.liste;
      var svg = secs[s].querySelector('svg'); svg.setAttribute('aria-label', b.nom[n]);
    }
    var bl = document.querySelectorAll('.bascule .puce');
    for(var q=0;q<bl.length;q++){ bl[q].textContent = U[bl[q].getAttribute('data-niv')]; }
    document.getElementById('filtre').setAttribute('aria-label', U.filtre);
    document.getElementById('niveau').setAttribute('aria-label', U.niveau);
    var bt = document.querySelectorAll('#langues button');
    var sauve = stocke('sm-langue');
    for(var z=0;z<bt.length;z++){ var d = bt[z].getAttribute('data-lang'); bt[z].setAttribute('aria-pressed', String(sauve ? d===sauve : d==='auto')); }
  }

  /* ── affichage : filtre, niveau, mode étiquettes / numéros ── */
  function mode(){
    var figs = racine.querySelectorAll('.sch');
    for(var i=0;i<figs.length;i++){
      var w = figs[i].getBoundingClientRect().width; if(!w){ continue; }
      var num = w < 880, sec = figs[i].parentNode, svg = figs[i].querySelector('svg');
      if(num !== figs[i].classList.contains('num')){
        figs[i].classList.toggle('num', num);
        svg.setAttribute('viewBox', num ? sec.getAttribute('data-vbn') : sec.getAttribute('data-vbc'));
      }
    }
    var ols = racine.querySelectorAll('.bat');
    for(var j=0;j<ols.length;j++){
      var f = ols[j].querySelector('.sch'), ol = ols[j].querySelector('.liste'), lis = ol.children, vis = 0;
      for(var k=0;k<lis.length;k++){
        var li = lis[k], ok = (f.classList.contains('num') || li.classList.contains('fb')) && !(etat.niv==='ne' && li.classList.contains('nt'));
        li.hidden = !ok; if(ok){ vis++; }
      }
      ol.hidden = !vis; ols[j].querySelector('.ls-t').hidden = !vis;
    }
    anneaux();
  }
  function appliquer(){
    racine.className = 'niv-' + etat.niv;
    var secs = racine.querySelectorAll('.bat'), n = 0;
    for(var i=0;i<secs.length;i++){
      var ok = etat.cat === 'tous' || secs[i].getAttribute('data-cat') === etat.cat;
      secs[i].hidden = !ok; if(ok){ n++; }
    }
    var bs = document.querySelectorAll('#filtre .puce');
    for(var j=0;j<bs.length;j++){ bs[j].setAttribute('aria-pressed', String(bs[j].getAttribute('data-cat') === etat.cat)); }
    var bn = document.querySelectorAll('.bascule .puce');
    for(var k=0;k<bn.length;k++){ bn[k].setAttribute('aria-pressed', String(bn[k].getAttribute('data-niv') === etat.niv)); }
    document.getElementById('compte').textContent = n + ' ' + (n > 1 ? u('n') : u('un'));
    mode();
  }
  function url(){
    var q = new URLSearchParams(location.search);
    if(etat.cat === 'tous'){ q.delete('type'); } else { q.set('type', etat.cat); }
    var s = q.toString();
    try{ history.replaceState(null, '', location.pathname + (s ? '?' + s : '') + location.hash); }catch(e){}
  }

  /* ── ?mot= : brillance de la pièce, de son étiquette et de son numéro ── */
  function anneaux(){
    var olds = racine.querySelectorAll('.an-r');
    for(var i=0;i<olds.length;i++){ olds[i].parentNode.removeChild(olds[i]); }
    if(!etat.mot){ return; }
    var gs = racine.querySelectorAll('.lb.on');
    for(var j=0;j<gs.length;j++){
      try{
        var t = gs[j].querySelector('text'), b = t.getBBox();
        if(!b.width){ continue; }
        var r = document.createElementNS(NS,'rect'); r.setAttribute('class','an-r');
        r.setAttribute('x', b.x-5); r.setAttribute('y', b.y-3); r.setAttribute('width', b.width+10); r.setAttribute('height', b.height+6); r.setAttribute('rx', 5);
        gs[j].insertBefore(r, gs[j].firstChild);
      }catch(e){}
    }
  }
  function briller(mot){
    var ons = racine.querySelectorAll('.on');
    for(var i=0;i<ons.length;i++){ ons[i].classList.remove('on'); }
    etat.mot = mot;
    if(!mot){ anneaux(); return; }
    var tous = racine.querySelectorAll('[data-mot="'+mot+'"]');
    for(var j=0;j<tous.length;j++){ tous[j].classList.add('on'); }
    anneaux();
  }
  function bateauxDe(mot){
    var r = [];
    for(var i=0;i<ORDRE.length;i++){
      var ps = B[ORDRE[i]].p;
      for(var k=0;k<ps.length;k++){ if(ps[k][1] === mot){ r.push([ORDRE[i], ps[k]]); } }
    }
    return r;
  }
  function aller(id, mot){
    var sec = document.getElementById(id), p = null, ps = B[id].p;
    for(var k=0;k<ps.length;k++){ if(ps[k][1] === mot){ p = ps[k]; } }
    if(!p){ return; }
    if(sec.hidden){ etat.cat = 'tous'; }
    if(p[2] === 't' && etat.niv === 'ne'){ etat.niv = 'nt'; temp = true; }
    etat.cible = id; appliquer(); majBandeau();
    var fig = sec.querySelector('.sch'), el = document.getElementById(p[4] ? p[0] : p[0] + (fig.classList.contains('num') ? '-n' : ''));
    if(!el){ el = sec; }
    el.scrollIntoView({block:'center'});
  }
  function majBandeau(){
    var b = document.getElementById('bandeau'); if(!b){ return; }
    var liste = bateauxDe(etat.mot), h = '<span class="bt">' + esc(nom(etat.mot)) + ' —</span>';
    for(var i=0;i<liste.length;i++){
      h += '<button type="button" data-b="'+liste[i][0]+'" aria-current="'+(liste[i][0]===etat.cible)+'">'+esc(B[liste[i][0]].court)+'</button>';
    }
    h += '<button type="button" class="x" aria-label="'+esc(u('fermer'))+'">×</button>';
    b.innerHTML = h;
  }
  function ouvrirMot(mot){
    var liste = bateauxDe(mot); if(!liste.length){ return; }
    var b = document.createElement('div'); b.id = 'bandeau'; b.className = 'bandeau'; b.setAttribute('role','status');
    document.getElementById('cmd').parentNode.insertBefore(b, document.getElementById('cmd'));
    b.addEventListener('click', function(ev){
      var bt = ev.target.closest('button'); if(!bt){ return; }
      if(bt.classList.contains('x')){
        b.parentNode.removeChild(b); briller(''); etat.cible = '';
        var q = new URLSearchParams(location.search); q.delete('mot'); var s = q.toString();
        try{ history.replaceState(null,'',location.pathname + (s ? '?'+s : '') + location.hash); }catch(e){}
        return;
      }
      aller(bt.getAttribute('data-b'), etat.mot);
    });
    etat.mot = mot; etat.cible = liste[0][0];
    briller(mot); majBandeau();
    aller(liste[0][0], mot);
  }

  /* ── branchements ── */
  function langue(l, sauve){
    etat.lang = l; if(sauve === 1){ range('sm-langue', l); }
    etiquettes(); numeros(); textes(); briller(etat.mot); appliquer(); if(etat.mot){ majBandeau(); }
  }
  var langues = document.querySelectorAll('#langues button');
  for(var i=0;i<langues.length;i++){
    langues[i].addEventListener('click', (function(b){ return function(){
      var d = b.getAttribute('data-lang');
      if(d === 'auto'){ try{ localStorage.removeItem('sm-langue'); }catch(e){} langue(auto(), 0); }
      else { langue(d, 1); }
    }; })(langues[i]));
  }
  document.getElementById('filtre').addEventListener('click', function(ev){
    var b = ev.target.closest('.puce'); if(!b){ return; }
    etat.cat = b.getAttribute('data-cat'); appliquer(); url();
  });
  document.getElementById('niveau').addEventListener('click', function(ev){
    var b = ev.target.closest('.puce'); if(!b){ return; }
    etat.niv = b.getAttribute('data-niv'); temp = false; range('sm-bateaux-niveau', etat.niv); appliquer();
  });
  window.addEventListener('resize', mode);
  if(window.ResizeObserver){ var ro = new ResizeObserver(mode); var fs = racine.querySelectorAll('.sch'); for(var f=0;f<fs.length;f++){ ro.observe(fs[f]); } }

  var q0 = new URLSearchParams(location.search);
  var t0 = q0.get('type'); if(t0 && CATS.indexOf(t0) >= 0){ etat.cat = t0; }
  var n0 = stocke('sm-bateaux-niveau'); if(n0 === 'ne' || n0 === 'nt'){ etat.niv = n0; }
  var sauve = stocke('sm-langue');
  etat.lang = (sauve && L.indexOf(sauve) >= 0) ? sauve : auto();
  etiquettes(); numeros(); textes(); appliquer();
  var m0 = q0.get('mot'); if(m0 && MOTS[m0]){ ouvrirMot(m0); }
})();
"""


def _section(b, m, mots):
    formes, labels, ins = svg_bateau(b, m, mots)
    h = b["h"] + 80
    nom = b["nom"]
    fi = b["fiche"]
    fiche = ""
    if fi["long"]:
        fiche += f'<p><b>{UI["fr"]["long"]}</b>{fi["long"]} m</p>'
    fiche += (f'<p><b>{UI["fr"]["crew"]}</b>{CREW[fi["crew"]][0]}</p><p><b>{UI["fr"]["rig"]}</b>{_html.escape(fi["rig"]["fr"])}</p>'
              f'<p><b>{UI["fr"]["serie"]}</b>{_html.escape(fi["serie"]["fr"])}</p>'
              f'<p class="cours"><a href="cours.html">{UI["fr"]["cours"]}</a></p>')
    alt = _html.escape(_alt(b, mots, "fr"), quote=True)
    fichier = _nom_fichier(b)
    return (
        f'<section class="bat" id="{b["id"]}" data-id="{b["id"]}" data-cat="{b["cat"]}" '
        f'data-vbc="0 0 1000 {h}" data-vbn="{_vue_tight(b)}">'
        f'<h2>{_html.escape(nom)}</h2>'
        f'<figure class="sch"><svg class="dsn" viewBox="0 0 1000 {h}" role="img" aria-label="{_html.escape(nom)}">'
        f'<g transform="translate({DX} {DY})"><g class="d">{formes}</g>{ins}<g class="ls">{labels}</g><g class="bds"></g></g></svg></figure>'
        f'<p class="ls-t" hidden></p><ol class="liste" hidden></ol>'
        f'<div class="bas"><div class="fiche">{fiche}</div>'
        f'<figure class="vig"><a href="images/bateaux/{fichier}"><img src="images/bateaux/{fichier}" alt="{alt}" width="1200" height="{int(h * 1.2)}" '
        f'loading="lazy" decoding="async" onerror="this.closest(\'figure\').hidden=true"></a>'
        f'<figcaption>{_html.escape(_alt(b, mots, "fr").split(" : ")[0])} — {LEGENDE}</figcaption></figure></div></section>')


def page(mots, mises) -> str:
    import site_blocks
    donnees = donnees_js(mots, mises)
    brut = json.dumps(donnees, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    corps = "".join(_section(b, m, mots) for b, m in zip(BATEAUX, mises))
    ui = UI["fr"]
    desc = ("Nomenclature illustrée de neuf bateaux de voile — voilier habitable X35, Hobie 16, Laser, 49er, planche iQFOiL, "
            "Formula Kite, wingfoil, IMOCA, Ultim : chaque pièce nommée et reliée à sa définition du lexique.")
    og = f"{URL}/images/bateaux/{_nom_fichier(BATEAUX[0])}"
    filtres = "".join(f'<button type="button" class="puce" data-cat="{c}" aria-pressed="{"true" if c == "tous" else "false"}">{ui[c]}</button>' for c in CATS)
    return (
        '<!doctype html>\n<html lang="fr"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        f'<title>{TITRE_PROMESSE}</title>'
        f'<link rel="canonical" href="{URL}/bateaux.html">'
        f'<meta name="description" content="{_html.escape(desc)}">'
        f'<meta property="og:type" content="website"><meta property="og:site_name" content="Sailing More">'
        f'<meta property="og:title" content="{TITRE_PROMESSE}"><meta property="og:description" content="{_html.escape(desc)}">'
        f'<meta property="og:url" content="{URL}/bateaux.html"><meta property="og:image" content="{og}">'
        f'<meta property="og:image:alt" content="{_html.escape(_alt(BATEAUX[0], mots, "fr"), quote=True)}">'
        f'<meta name="twitter:card" content="summary_large_image"><meta name="twitter:image" content="{og}">'
        f'<script type="application/ld+json">{json_ld_images(mots)}</script>'
        f'<style>{site_blocks.ENTETE_CSS}{CSS}{CSS_SVG}</style></head><body>\n'
        f'{site_blocks.entete_site("bateaux.html", LANGUES)}\n<div class="page">\n'
        f'<h1 data-t="titre">{ui["titre"]}</h1><p class="chapo" data-t="chapo">{ui["chapo"]}</p>\n'
        '<div class="cmd" id="cmd"><div class="rang"><span class="et" data-t="filtre">' + ui["filtre"] + '</span>'
        f'<span id="filtre" role="group" aria-label="{ui["filtre"]}" style="display:contents">{filtres}</span></div>'
        '<div class="rang"><span class="et" data-t="niveau">' + ui["niveau"] + '</span>'
        f'<span id="niveau" class="bascule" role="group" aria-label="{ui["niveau"]}" style="display:contents">'
        f'<button type="button" class="puce" data-niv="ne" aria-pressed="true">{ui["ne"]}</button>'
        f'<button type="button" class="puce" data-niv="nt" aria-pressed="false">{ui["nt"]}</button></span></div>'
        f'<p class="compte" id="compte" role="status" aria-live="polite">{len(BATEAUX)} {ui["n"]}</p></div>\n'
        f'<main id="bateaux" class="niv-ne">{corps}</main>\n'
        f'<p class="pied">{LEGENDE}</p></div>\n'
        f'<script type="application/json" id="donnees-bateaux">{brut}</script>\n<script>{JS}</script>\n</body></html>\n')


def correspondance(mises) -> dict:
    mots: dict[str, list] = {}
    for b, m in zip(BATEAUX, mises):
        for p in sorted(m.parts, key=lambda q: q["n"]):
            mots.setdefault(p["mot"], []).append({"bateau": b["id"], "ancre": p["id"], "niveau": "essentiel" if p["niv"] == "e" else "tout"})
    return {"page": "bateaux.html", "genere_par": "scripts/bateaux_page.py", "bateaux": {b["id"]: NOMS[b["id"]][0] for b in BATEAUX},
            "mots": dict(sorted(mots.items()))}


def image_svg(b, m, mots) -> str:
    formes, labels, ins = svg_bateau(b, m, mots, interactif=False, seulement_essentiel=True)
    h = b["h"] + 80
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="{int(h * 1.2)}" viewBox="0 0 1000 {h}" '
            f'font-family="ui-sans-serif,system-ui,-apple-system,\'Helvetica Neue\',Arial,sans-serif">'
            f'<title>{_html.escape(b["nom"])}</title><style>{CSS_SVG}.ins{{font-size:14px}}</style>'
            f'<rect width="1000" height="{h}" fill="#0a1a2b"/>'
            f'<text x="28" y="34" font-size="22" fill="#eef3f7" font-weight="600">{_html.escape(b["nom"])}</text>'
            f'<g transform="translate({DX} {DY})">{formes}{ins}{labels}</g></svg>\n')


def maj_sitemap(mots) -> None:
    f = SITE / "sitemap.xml"
    if not f.exists():
        return
    x = f.read_text(encoding="utf-8")
    if "xmlns:image" not in x:
        x = x.replace('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
                      '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">')
    x = re.sub(r"\s*<url><loc>https://sailingmore\.fr/bateaux\.html</loc>.*?</url>", "", x, flags=re.S)
    e = lambda s: _html.escape(s, quote=False)  # noqa: E731
    imgs = "".join(
        f'<image:image><image:loc>{URL}/images/bateaux/{_nom_fichier(b)}</image:loc>'
        f'<image:title>{e(_alt(b, mots, "fr").split(" : ")[0])}</image:title>'
        f'<image:caption>{e(LEGENDE + " — " + _alt(b, mots, "fr"))}</image:caption></image:image>' for b in BATEAUX)
    ligne = (f'\n  <url><loc>{URL}/bateaux.html</loc><lastmod>{date.today().isoformat()}</lastmod>'
             f'<changefreq>monthly</changefreq><priority>0.8</priority>{imgs}</url>')
    x = x.replace("</urlset>", ligne + "\n</urlset>")
    f.write_text(x, encoding="utf-8")


def ecrire_page(dossier: Path = SITE) -> str:
    ranger_lexique()
    mots, ancres, mises = construire()
    pb = [p for p in verifier(mots, mises) if "essentielles numérotées" not in p or True]
    dossier.mkdir(parents=True, exist_ok=True)
    (dossier / "bateaux.html").write_text(page(mots, mises), encoding="utf-8")
    (dossier / "bateaux.json").write_text(json.dumps(correspondance(mises), ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    SRC_IMG.mkdir(parents=True, exist_ok=True)
    manif = []
    for b, m in zip(BATEAUX, mises):
        svg = SRC_IMG / f"{b['slug']}.svg"
        svg.write_text(image_svg(b, m, mots), encoding="utf-8")
        manif.append({"id": b["id"], "svg": svg.relative_to(RACINE).as_posix(),
                      "webp": f"images/bateaux/{_nom_fichier(b)}", "largeur": 1200, "fond": "#0a1a2b",
                      "alt": _alt(b, mots, "fr"), "titre": _alt(b, mots, "fr").split(" : ")[0],
                      "legende": f"{LEGENDE} — {_alt(b, mots, 'fr')}"})
    MANIFESTE.write_text(json.dumps(manif, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    maj_sitemap(mots)
    # le lexique se réécrit avec ses nouvelles ancres (même générateur, chemins de cette copie)
    try:
        import lexique_page
        lexique_page.JSON, lexique_page.SITE = LEXIQUE, dossier
        (dossier / "lexique.html").write_text(lexique_page.page_lexique(), encoding="utf-8")
    except Exception as err:  # noqa: BLE001
        print("lexique.html non réécrit :", err)
    for p in pb:
        print("À VOIR ·", p)
    return "bateaux.html"


def main() -> int:
    arg = set(sys.argv[1:])
    if arg & {"--lexique"}:
        print(f"{ranger_lexique()} terme(s) rangé(s) dans {LEXIQUE}")
    if arg & {"--verifier", "--ecrire"}:
        mots, ancres, mises = construire()
        print(stats(mises))
        if "--diag" in arg:
            print(diagnostic(mises))
        pb = verifier(mots, mises)
        for p in pb:
            print("ÉCHEC ·" if "essentielles" not in p else "À VOIR ·", p)
        if "--verifier" in arg:
            return 1 if any("essentielles" not in p for p in pb) else 0
    if "--ecrire" in arg:
        ecrire_page()
        taille = (SITE / "bateaux.html").stat().st_size
        print(f"{SITE / 'bateaux.html'} · {taille / 1024:.1f} Ko")
    if not arg:
        print(__doc__)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
