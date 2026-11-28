#!/usr/bin/env python3
# © 2026 Sailing More — tous droits réservés. All rights reserved.
"""Migration unique : projets/sailingmore/examens/*.json -> simulateur/permis/<cle>.json,
avec source par matière, langue de question, et les permis à venir en matières vides.
Les anciens fichiers ne sont pas supprimés ici (à retirer à la main : ils ne sont plus lus)."""
import json
from pathlib import Path

R = Path(__file__).resolve().parent.parent
ANC = R / "projets/sailingmore/examens"
NEW = R / "simulateur/permis"
NEW.mkdir(parents=True, exist_ok=True)

OFCOM = {"ref": "OFCOM — Prescriptions d'examen SRC", "version": "éd. 3 (2024)",
         "url": "https://www.bakom.admin.ch/dam/fr/sd-web/FtwzNYTaUqLX/pruefungsvorschriften_src_2024.pdf"}
SOURCES = {
    ("src", "reglementation"): OFCOM, ("src", "procedures"): OFCOM, ("src", "alphabet"): OFCOM, ("src", "oral"): OFCOM,
    ("src", "pratique"): {"ref": "Notice ICOM IC-M330 + OFCOM, Prescriptions d'examen SRC", "version": "éd. 3 (2024)", "url": OFCOM["url"]},
    ("permis-cotier", "balisage"): {"ref": "Permis plaisance, option côtière — référentiel du ministère de la Mer", "version": "à préciser", "url": ""},
    ("permis-cotier", "regles"): {"ref": "RIPAM (règlement international pour prévenir les abordages)", "version": "à préciser", "url": ""},
    ("permis-cotier", "reglementation"): {"ref": "Permis plaisance, option côtière — référentiel du ministère de la Mer", "version": "à préciser", "url": ""},
}

for f in sorted(ANC.glob("*.json")):
    d = json.loads(f.read_text(encoding="utf-8"))
    d["pays"] = "CH" if d["id"] == "src" else "FR"
    for m in d["matieres"]:
        m["source"] = SOURCES[(d["id"], m["id"])]
        m["verifie"] = False  # source citée au niveau de la matière, question par question à relire
        for q in m["questions"]:
            q["langue"] = "en" if m["id"] == "oral" else "fr"
    (NEW / f.name).write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")

A_VENIR = {
    "permis-hauturier": ("Permis hauturier — calcul et cartographie", "FR", 60, 75,
        [("calcul-maree", "Calcul de marée", "FR"), ("cartographie", "Cartographie et estime", "FR"), ("meteo", "Météorologie", "FR")]),
    "crr": ("CRR — certificat restreint de radiotéléphonie (ANFR)", "FR", 30, 75,
        [("reglementation", "Réglementation", "FR"), ("procedures", "Procédures", "FR"), ("pratique", "Pratique simulée", "FR"), ("oral", "Oral", "FR")]),
    "rya-day-skipper": ("RYA Day Skipper", "GB", 60, 70,
        [("navigation", "Navigation", "GB"), ("colregs", "Collision regulations", "GB"), ("meteorology", "Meteorology", "GB")]),
    "rya-coastal": ("RYA Coastal Skipper / Yachtmaster Coastal", "GB", 90, 70,
        [("navigation", "Navigation", "GB"), ("tides", "Tides and tidal streams", "GB"), ("meteorology", "Meteorology", "GB")]),
    "sbf-see": ("SBF See (Allemagne)", "DE", 60, 75,
        [("navigation", "Navigation", "DE"), ("schifffahrtsrecht", "Schifffahrtsrecht", "DE"), ("seemannschaft", "Seemannschaft", "DE")]),
    "sbf-binnen": ("SBF Binnen (Allemagne)", "DE", 60, 75,
        [("schifffahrtsrecht", "Schifffahrtsrecht", "DE"), ("seemannschaft", "Seemannschaft", "DE")]),
}
for cle, (titre, pays, duree, seuil, mats) in A_VENIR.items():
    d = {"id": cle, "titre": titre, "pays": pays, "materiel": "", "duree_min": duree, "seuil_pct": seuil,
         "note": "En préparation : aucune question publiée tant que la source officielle n'est pas rattachée.",
         "matieres": [{"id": i, "titre": t, "type": "qcm", "source": None, "verifie": False, "questions": []} for i, t, _ in mats]}
    (NEW / f"{cle}.json").write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
print("écrit", sorted(p.name for p in NEW.glob("*.json")))
