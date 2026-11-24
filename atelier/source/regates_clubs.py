#!/usr/bin/env python3
"""Moisson des régates hors fédérations et hors Manage2Sail (tâche 62, 24/11/2026) — source n°1 : YCM.

    python3 scripts/regates_clubs.py [--reseau] [--ecrire]

Source : https://yacht-club-monaco.mc/en/event/calendar/ (EventON, WordPress). robots.txt du site :
seul /wp-admin/ est interdit. Une seule page lue, 3 s de pause, aucun crawl.
Sans --reseau : relit cache/moisson62/ycm_events.html. Sans --ecrire : compte seulement.

Écrit projets/sailingmore/regates-clubs.json ({URL source: [épreuves]}) que `regates_collecte.py`
relit à chaque collecte, et ajoute les épreuves nouvelles à `regates.json` (même format, `lu` daté).
Doublon = même nom normalisé et même début, OU (Monaco/même pays, début à ±1 jour, un mot
significatif en commun). Les stages et les courses de bateaux à moteur n'entrent pas.
"""
from __future__ import annotations

import html
import json
import re
import sys
import time
import unicodedata
import urllib.request
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

ICI = Path(__file__).resolve().parent.parent
SRC = "https://yacht-club-monaco.mc/en/event/calendar/"
CACHE = ICI / "cache/moisson62/ycm_events.html"
UA = {"User-Agent": "Mozilla/5.0 (compatible; SailingMore/1.0; +https://sailingmore.fr)"}
HORS = ("stage", "stages", "energy boat", "brunch", "dinner", "tasting")  # pas des régates à voile
GENERIQUE = {"monaco", "trophy", "trophee", "cup", "challenge", "yacht", "club", "regate", "act"}


def cle(t: str) -> str:
    t = "".join(c for c in unicodedata.normalize("NFKD", t or "") if not unicodedata.combining(c))
    return re.sub(r"[\W_]+", "", t.lower())


def mots(t: str) -> set[str]:
    t = "".join(c for c in unicodedata.normalize("NFKD", t or "") if not unicodedata.combining(c))
    return {m for m in re.findall(r"[a-z]{4,}", t.lower())} - GENERIQUE


def lire_page(reseau: bool) -> str:
    if reseau:
        r = urllib.request.urlopen(urllib.request.Request(SRC, headers=UA), timeout=40)
        h = r.read().decode("utf-8", "ignore")
        CACHE.parent.mkdir(parents=True, exist_ok=True)
        CACHE.write_text(h, encoding="utf-8")
        time.sleep(3)
        return h
    return CACHE.read_text(encoding="utf-8", errors="ignore")


def ycm(h: str) -> list[dict]:
    tz = timezone(timedelta(hours=1))
    out, vus = [], set()
    for p in re.split(r'(?=<div id="event_\d+_\d+" class="eventon_list_event)', h)[1:]:
        p = p[:6000]
        t = re.search(r'data-time="(\d+)-(\d+)"', p)
        l = re.search(r'evo_event_schema[^>]*><a href="([^"]+)"', p)
        n = re.search(r'evcal_event_title[^>]*>([^<]+)<', p)
        if not (t and l and n):
            continue
        nom = html.unescape(n.group(1)).replace("–", "-").strip()
        deb = datetime.fromtimestamp(int(t.group(1)), tz).date().isoformat()
        fin = datetime.fromtimestamp(int(t.group(2)), tz).date().isoformat()
        if any(k in nom.lower() for k in HORS) or (cle(nom), deb[:4]) in vus:
            continue
        vus.add((cle(nom), deb[:4]))
        lien = re.sub(r"/var/ri-.*$", "/", l.group(1))
        out.append({
            "nom": nom, "debut": deb, "fin": max(fin, deb), "ville": "Monaco", "pays": "MON",
            "club": "Yacht Club de Monaco", "classes": [], "lien": lien, "resultats": "",
            "niveau": "", "connue": "", "annulee": False, "ocean": False, "departement": "",
            "ligue": "", "sources": [SRC], "region_repliee": "", "region": "Monde",
            "type": "régate", "lu": date.today().isoformat(),
        })
    return out


def doublon(n: dict, base: list[dict]) -> dict | None:
    d = date.fromisoformat(n["debut"])
    for x in base:
        if cle(x["nom"]) == cle(n["nom"]) and x["debut"] == n["debut"]:
            return x
        try:
            ecart = abs((date.fromisoformat(x["debut"]) - d).days)
        except ValueError:
            continue
        if ecart <= 1 and (x["pays"] == n["pays"] or "monaco" in (x.get("club") or "").lower()) \
                and mots(x["nom"]) & mots(n["nom"]):
            return x
    return None


def main() -> int:
    h = lire_page("--reseau" in sys.argv)
    lignes = ycm(h)
    f = ICI / "projets/sailingmore/regates.json"
    d = json.loads(f.read_text(encoding="utf-8"))
    base = d["regates"]
    neuves, dups = [], []
    for n in lignes:
        g = doublon(n, base)
        if g:
            dups.append((n["nom"], n["debut"], g["nom"], g["debut"]))
            if SRC not in g["sources"]:
                g["sources"].append(SRC)
        else:
            neuves.append(n)
    print(f"YCM : {len(lignes)} épreuves lues · {len(neuves)} ajoutées · {len(dups)} déjà en base "
          f"(taux de doublons {100 * len(dups) // max(1, len(lignes))} %)")
    for a in dups:
        print("  doublon :", a)
    for n in neuves:
        print("  nouvelle :", n["debut"], n["fin"], n["nom"])
    if "--ecrire" in sys.argv:
        base.extend(neuves)
        base.sort(key=lambda x: (x["debut"], cle(x["nom"])))
        d.update({"total": len(base), "a_venir": len([x for x in base if x["debut"] >= date.today().isoformat()])})
        f.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
        # fichier relu par la collecte : toutes les épreuves lues, doublons compris (la fusion s'en charge)
        (ICI / "projets/sailingmore/regates-clubs.json").write_text(
            json.dumps({SRC: lignes}, ensure_ascii=False, indent=1), encoding="utf-8")
        print("écrit :", len(base), "épreuves")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
