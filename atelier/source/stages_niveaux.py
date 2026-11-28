#!/usr/bin/env python3
# © 2026 Sailing More — tous droits réservés. All rights reserved.
"""Niveau et certification d'une offre de stage, lus dans son **titre** — et seulement là.

Utilisé par `stages_page.py` à chaque construction (les deux champs sont recalculés depuis le titre,
donc une règle corrigée ici vaut pour toutes les offres au build suivant). Le relevé
(`stages_releve.py`) peut appeler `classer()` pour écrire les champs dans `stages.json`.

Règle cardinale (sprint 1, 23/11/2026) : **ne pas deviner.** Une valeur fausse est pire qu'une
valeur absente. Donc :
  - on ne lit que des formules explicites (« Day Skipper », « Yachtmaster Offshore », « SKS »…),
    jamais la durée, le prix, le bateau ou le lieu ;
  - si le titre nomme deux niveaux différents (« Day Skipper / Competent Crew », « Coastal Skipper /
    Yachtmaster Offshore Shorebased », « Beginner, Improver, Advanced »), le niveau reste **vide** ;
  - le bateau à moteur, le jet-ski, le kayak, la radio, le secourisme et les brevets professionnels
    (MCA Master, OOW, STCW) n'ont pas de place sur cette échelle de voile : niveau vide ;
  - « Yachtmaster » seul (sans Coastal / Offshore / Ocean) est ambigu : niveau vide.

Échelle `niveau` (courte, ordonnée) :
  decouverte   — premier contact : découverte, initiation, baptême, essai, « beginner », « first time »,
                 RYA Start Yachting, RYA Dinghy Start / Level 1 ;
  equipier     — équipier sur un voilier habitable : RYA Competent Crew, « équipier » ;
  chef-de-bord — conduire un voilier en côtier : RYA Day Skipper, Coastal Skipper, Yachtmaster Coastal,
                 ICC, SKS (Sportküstenschifferschein), ASA 104 Bareboat ;
  hauturier    — au large : Yachtmaster Offshore / Ocean, SSS (Sportseeschifferschein), Hochseeschein,
                 « hauturier » (hors « extension hauturière », qui est un permis moteur) ;
  moniteur     — former les autres : instructor, instructeur, moniteur, istruttore, Ausbilder ;
  ""           — indéterminable depuis le titre.

`certif` : le référentiel **nommé** par le titre — RYA, ICC, FFVoile, DSV, ASA, IYT, MCA, `autre`
(un référentiel est nommé mais hors de cette liste : CWO, ISPA, SKS/SSS/SBF, PER, Patente nautica,
STCW, SRC…), ou "" si le titre n'en nomme aucun. Quand plusieurs sont nommés, le plus précis gagne,
dans l'ordre de `ORDRE_CERTIF` (« RYA ICC Assessment » → ICC ; « RYA / MCA Yachtmaster » → RYA, qui
délivre le cours).

    python3 scripts/stages_niveaux.py            # classe les titres de stages.json et affiche les comptes
"""
from __future__ import annotations

import re

NIVEAUX = ("decouverte", "equipier", "chef-de-bord", "hauturier", "moniteur")
CERTIFS = ("RYA", "ICC", "FFVoile", "DSV", "ASA", "IYT", "MCA", "autre")

_I = re.IGNORECASE

# Ce qui sort une offre de l'échelle de voile, quel que soit le reste du titre.
HORS_ECHELLE = re.compile(
    r"powerboat|motor\s?boat|motorboot|motor cruising|\bmotor\b|\bPWC\b|jet ?ski|kayak|caiac|"
    r"extension hauturi|permis (option )?c[oô]ti|\bSRC\b|\bVHF\b|GMDSS|first aid|STCW|"
    r"officer of the watch|\bOOW\b|\bmaster\s*\(|chief mate|workboat|engine|diesel", _I)

REGLES_NIVEAU: list[tuple[str, re.Pattern]] = [
    ("moniteur", re.compile(r"instruct(or|eur)|moniteur|istruttore|ausbilder", _I)),
    ("hauturier", re.compile(
        r"yachtmaster.*\b(offshore|ocean)\b|\boffshore\b.*yachtmaster|\bSSS\b|sport-?see-?schiffer|"
        r"hochsee(schein)?|hauturi|\bd'altura\b|\bde altura\b", _I)),
    ("chef-de-bord", re.compile(
        r"day\s?skipper|coastal skipper|yachtmaster\W*coastal|\bICC\b|\bSKS\b|sport-?k[üu]sten-?schiffer|"
        r"ASA\s*104|bareboat cruising", _I)),
    ("equipier", re.compile(r"competent crew|[ée]quipi[eè]r", _I)),
    ("decouverte", re.compile(
        r"d[ée]couverte|initiation|iniciaci[oó]n|bapt[eê]me|bautismo|schnupper|prova la vela|proefles|"
        r"intro(duction)? to sailing|first time|try sailing|\bbeginners?\b|d[ée]butants?|\banf[äa]nger\b|"
        r"principiant|start yachting|dinghy start|dinghy level 1", _I)),
]
# « Beginner, Improver, Advanced » : un titre qui vise aussi un niveau confirmé n'est pas « découverte ».
CONTRE_DECOUVERTE = re.compile(r"advanced|improver|avanzat|fortgeschritten|perfezionamento|"
                               r"faux-d[ée]butant", _I)

ORDRE_CERTIF: list[tuple[str, re.Pattern]] = [
    ("ICC", re.compile(r"\bICC\b", _I)),
    ("IYT", re.compile(r"\bIYT\b", _I)),
    ("ASA", re.compile(r"\bASA\b")),                       # majuscules : « asa » existe en espagnol
    ("FFVoile", re.compile(r"\bFFV(oile)?\b|f[ée]d[ée]ration fran[cç]aise de voile", _I)),
    ("DSV", re.compile(r"\bDSV\b|deutscher segler", _I)),
    ("RYA", re.compile(r"\bRYA\b", _I)),
    ("MCA", re.compile(r"\bMCA\b", _I)),
    ("autre", re.compile(
        r"\bCWO\b|\bISPA\b|\bSKS\b|\bSSS\b|\bSBF\b|sportbootf[üu]hrerschein|sport-?k[üu]sten-?schiffer|"
        r"sport-?see-?schiffer|hochseeschein|bodenseeschifferpatent|hochrheinpatent|vaarbewijs|"
        r"\bPER\b|\bPNB\b|capit[aá]n de yate|patent(e|ino) nautic|\bSTCW\b|\bSRC\b|\bGMDSS\b|"
        r"certificat restreint|sail canada|\bUBI\b|\bFKN\b", _I)),
]


# Niveaux posés à la main (tâche 44, nuit du 24/11/2026) pour des titres sans formule explicite mais sans
# ambiguïté (cours « de base », classes Optimist, « Instructor »…). Début de titre, casse ignorée ; une
# ligne retirée rend le titre à la règle. Les cours moteur « Day/Coastal Skipper », « Yachtmaster » et les
# cours d'instructeur y sont classés malgré HORS_ECHELLE : décision prise à la place de Nicolas, à confirmer.
NIVEAU_PAR_TITRE: list[tuple[str, str]] = [
    ("basic sailing course", "decouverte"), ("corso di vela base", "decouverte"),
    ("grundkurs", "decouverte"), ("segelkurs basic i dein", "decouverte"),
    ("optimist 8 - 12", "decouverte"), ("zeilkamp optimist", "decouverte"),
    ("kindersegelkurs berlin opti", "decouverte"), ("dinghy minis", "decouverte"),
    ("private discover sailing", "decouverte"), ("asa 101", "decouverte"),
    ("cwo i 5-daagse", "decouverte"), ("cwo i-weekend", "decouverte"),
    ("segeln lernen zürichsee", "decouverte"),
    ("asa 106", "chef-de-bord"), ("rya day skipper motor", "chef-de-bord"),
    ("rya coastal skipper motor", "chef-de-bord"), ("rya motor boat coastal skipper", "chef-de-bord"),
    ("rya day skipper motorboat", "chef-de-bord"), ("sbt yachtmaster coastal coc prep for motor", "chef-de-bord"),
    ("sbt yachtmaster offshore coc prep for motor", "hauturier"),
    ("rya powerboat instructors course", "moniteur"), ("powerboat instructor skills", "moniteur"),
    ("rya pwc instructor course", "moniteur"),
    # « RYA Powerboat Instructor » (uksa.org) retiré le 24/11/2026 : la page répond 403, rien ne prouve le niveau.
]


def niveau(titre: str) -> str:
    t = titre or ""
    for debut, nv in NIVEAU_PAR_TITRE:
        if t.casefold().startswith(debut):
            return nv
    if HORS_ECHELLE.search(t) and not re.search(r"instruct|moniteur", t, _I):
        # Le moteur, la radio, le pro : pas d'échelle de voile. Un moniteur moteur reste « moniteur »
        # seulement si le titre ne parle pas de moteur — d'où le second test ci-dessous.
        return ""
    trouves = []
    for nom, motif in REGLES_NIVEAU:
        if motif.search(t):
            trouves.append(nom)
    if "moniteur" in trouves:
        # Un cours de moniteur moteur ou jet-ski n'est pas un moniteur de voile.
        return "" if HORS_ECHELLE.search(t) else "moniteur"
    if "decouverte" in trouves and CONTRE_DECOUVERTE.search(t):
        trouves.remove("decouverte")
    return trouves[0] if len(trouves) == 1 else ""


def certif(titre: str) -> str:
    t = titre or ""
    for nom, motif in ORDRE_CERTIF:
        if motif.search(t):
            return nom
    return ""


def classer(titre: str) -> dict:
    return {"niveau": niveau(titre), "certif": certif(titre)}


def comptes(offres: list[dict]) -> dict:
    n = len(offres)
    avec_niveau = sum(1 for o in offres if o.get("niveau") in NIVEAUX)
    avec_certif = sum(1 for o in offres if o.get("certif"))
    vides = sum(1 for o in offres if not o.get("niveau") and not o.get("certif"))
    return {"offres": n, "niveau": avec_niveau, "certif": avec_certif, "vides": vides}


if __name__ == "__main__":
    import json
    import os
    import sys
    from collections import Counter
    from pathlib import Path

    racine = Path(os.environ.get("SAILINGMORE_RACINE", "/opt/data"))
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    chemin = Path(args[0]) if args else racine / "projets/sailingmore/stages.json"
    offres = json.loads(chemin.read_text(encoding="utf-8")).get("offres", [])
    classees = [{**o, **classer(o.get("titre", ""))} for o in offres]
    c = comptes(classees)
    print(f"{c['offres']} offres · {c['niveau']} avec un niveau · {c['certif']} avec une certification · "
          f"{c['vides']} sans l'un ni l'autre")
    print("niveaux :", dict(Counter(o["niveau"] or "—" for o in classees).most_common()))
    print("certifs :", dict(Counter(o["certif"] or "—" for o in classees).most_common()))
    if "--detail" in sys.argv:
        for o in classees:
            if o["niveau"] or o["certif"]:
                print(f"  {o['niveau'] or '—':13} {o['certif'] or '—':8} {o['titre']}")
