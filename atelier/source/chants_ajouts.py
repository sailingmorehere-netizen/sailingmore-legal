#!/usr/bin/env python3
# © 2026 Sailing More — tous droits réservés. All rights reserved.
"""Prépare les ajouts de chants moissonnés hors spécifications (cache/chants/moisson/*.json).

Contrôle dur avant d'accepter un chant :
  - au moins 4 vers et 70 % des vers retrouvés mot pour mot dans le fichier du livre ;
  - type connu, langue connue, note et résumés fr/en non vides ;
  - titre non déjà présent dans chants-de-marin.json ni dans les ajouts.
Écrit cache/chants/ajouts.json, que `chants_construire.py` ajoute ensuite (seul écrivain du JSON).
"""
import json
import re
import unicodedata
from pathlib import Path

BASE = Path("/opt/data")
MOISSON = BASE / "cache/chants/moisson"
SRC = BASE / "cache/chants/src"
CIBLE = BASE / "cache/chants/ajouts.json"
JSON_F = BASE / "projets/sailingmore/chants-de-marin.json"

LIVRES = {
    "whall": ("seasongsshanties00whal.txt", "Whall, Sea Songs and Shanties (4e éd., 1920)", "1920"),
    "terry1": ("shantybooksailor00terr.txt", "Terry, The Shanty Book, Part I (1921)", "1921"),
    "terry2": ("terry2.txt", "Terry, The Shanty Book, Part II (1926)", "1926"),
    "smith": ("musicofwaterscol00smituoft.txt", "Smith, The Music of the Waters (1888)", "1888"),
}
TYPES = {"hisser", "virer", "pompe", "festif", "melancolique"}
LANGS = {"en", "fr", "nl", "gd", "br", "no", "it", "es", "pt", "de", "ja"}
# Un chant dont les paroles portent une insulte raciale d'époque n'est pas publié sur la page :
# le texte est recopié du livre, mais la page est publique et familiale. On l'écarte et on le dit.
MOTS_ECARTES = re.compile(r"\bn[iy]gg(er|ah|a)\b|\bdark(ie|y)\b|\bcoon\b", re.I)
# Coquilles d'OCR repérées dans les chants français de Smith : lettres et ponctuation seulement,
# aucun mot n'est changé. Les accents perdus par le scan ne sont pas rétablis à l'aveugle.
FR_OCR = [(re.compile(r"\bII\b"), "Il"), (re.compile(r"\bUs\b"), "Ils"),
          (re.compile(r"\b1['’](?=\w)"), "l'"), (re.compile(r"\b1a\b"), "la"),
          (re.compile(r"\b1e\b"), "le"), (re.compile(r"\b1es\b"), "les"),
          (re.compile(r"\bdone\b"), "donc"), (re.compile(r"E\^coutez"), "Écoutez"),
          (re.compile(r"\s+&c\.$"), ".")]
BRUIT = re.compile(r"^\(?\s*(repeat|chorus|solo|verse|1st|2nd|3rd)\b.*\)?$", re.I)


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = re.sub(r"[^a-z0-9 ]+", " ", s.lower())
    return re.sub(r"\s+", " ", s).strip()


def cle(t: str) -> str:
    t = norm(t)
    for a in ("the ", "a ", "o ", "oh ", "ye "):
        if t.startswith(a):
            t = t[len(a):]
    return t.replace(" ", "")


def slug(t: str) -> str:
    return norm(t).replace(" ", "-")[:40].strip("-") or "chant"


def _shingles(t: str, k: int = 4):
    mots = norm(t).split()
    if len(mots) < k:
        return {" ".join(mots)} if mots else set()
    return {" ".join(mots[i:i + k]) for i in range(len(mots) - k + 1)}


def verifie(paroles: str, src_plat: str):
    """Rend (vers gardés, vers lus, pire taux). Le livre est de l'OCR : les lignes y sont coupées
    n'importe où, donc on vérifie par groupes de 4 mots et non ligne à ligne. Un couplet n'est
    gardé que si ses groupes de mots se retrouvent dans le livre."""
    garde, tot, pire = [], 0, 1.0
    for bloc in re.split(r"\n\s*\n", (paroles or "").strip()):
        vers = [l.strip() for l in bloc.split("\n") if l.strip()]
        if not vers:
            continue
        tot += len(vers)
        sh = _shingles(" ".join(vers))
        if not sh:
            continue
        taux = sum(1 for g in sh if g in src_plat) / len(sh)
        if taux >= 0.75 and sum(1 for g in sh if g in src_plat) >= 3:
            garde.append(vers)
        else:
            pire = min(pire, taux)
    return garde, tot, pire


def main() -> int:
    d = json.loads(JSON_F.read_text(encoding="utf-8"))
    # Les ajouts déjà retenus une fois restent acquis : sans ça, chaque nouvelle moisson écraserait
    # la précédente et la construction repartirait avec moins de chants qu'avant.
    anciens = []
    if CIBLE.exists():
        anciens = json.loads(CIBLE.read_text(encoding="utf-8"))
    anciens_ids = {c["id"] for c in anciens}
    titres = {cle(c["titre"]) for c in d["chants"] if c["id"] not in anciens_ids}
    ids = {c["id"] for c in d["chants"] if c["id"] not in anciens_ids}
    retenus, vus, ecartes = list(anciens), {cle(c["titre"]) for c in anciens}, []
    a_jamais = {}

    for livre, (fichier, nom, annee) in LIVRES.items():
        f = MOISSON / f"{livre}.json"
        if not f.exists():
            print(f"pas de moisson pour {livre}")
            continue
        src = re.sub(r"\s+", " ", norm((SRC / fichier).read_text(encoding="utf-8", errors="replace")))
        for c in json.loads(f.read_text(encoding="utf-8")).get("chants", []):
            titre = (c.get("titre") or "").strip()
            k = cle(titre)
            motif = None
            if not titre:
                motif = "sans titre"
            elif c.get("type") not in TYPES:
                motif = f"type inconnu ({c.get('type')})"
            elif (c.get("lg") or "") not in LANGS:
                motif = f"langue hors liste ({c.get('lg')})"
            elif not (c.get("note") or "").strip() or not (c.get("resume_fr") or "").strip() or not (c.get("resume_en") or "").strip():
                motif = "note ou résumés vides"
            elif k in titres or k in vus:
                motif = "déjà présent"
            if motif:
                ecartes.append((livre, titre or "?", motif))
                continue
            garde, tot, pire = verifie(c.get("paroles", ""), src)
            if MOTS_ECARTES.search("\n".join("\n".join(b) for b in garde)):
                ecartes.append((livre, titre, "insulte raciale dans le texte d'origine"))
                continue
            gardees = sum(len(b) for b in garde)
            if gardees < 6 or (tot and gardees / tot < 0.6):
                ecartes.append((livre, titre, f"texte non vérifié ({gardees}/{tot} vers, pire {pire:.0%})"))
                continue
            i = slug(titre)
            base, n = i, 2
            while i in ids:
                i = f"{base}-{n}"
                n += 1
            ids.add(i)
            vus.add(k)
            page = c.get("page")
            ref = f"{nom}" + (f", p. {page}" if isinstance(page, int) else "")
            if (c.get("lg") or "") == "fr":
                c["paroles"] = c["paroles"]
                for rgx, rep in FR_OCR:
                    c["paroles"] = rgx.sub(rep, c["paroles"])
            blocs = []  # couples entiers validés par `verifie` ; les didascalies tombent
            for b in garde:
                vers = [l for l in b if not BRUIT.match(l)]
                if vers:
                    blocs.append("\n".join(vers))
            e = {
                "id": i, "type": c["type"], "lg": c["lg"], "titre": titre,
                "annees": "≤" + annee, "livre": livre,
                "resume": {"fr": c["resume_fr"].strip(), "en": c["resume_en"].strip()},
                "paroles": "\n\n".join(blocs),
                "accords": "", "audio": None, "video": None,
                "source": ref + " — " + c["note"].strip(),
            }
            # un chant qui commence au couplet 2 ou tient en moins de six vers est partiel
            premier = (blocs[0].split("\n")[0] if blocs else "")
            if not c.get("complet") or re.match(r"^\d{1,2}[\.\)]\s", premier) or gardees < 8:
                e["partiel"] = True
            retenus.append(e)
            a_jamais[livre] = a_jamais.get(livre, 0) + 1

    retenus.sort(key=lambda c: (c["type"], norm(c["titre"])))
    CIBLE.write_text(json.dumps(retenus, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"ajouts retenus : {len(retenus)} {a_jamais}")
    print(f"écartés : {len(ecartes)}")
    for e in ecartes[:40]:
        print("   ", e)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
