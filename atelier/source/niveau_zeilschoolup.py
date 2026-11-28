#!/usr/bin/env python3
# © 2026 Sailing More — tous droits réservés. All rights reserved.
"""Niveau des offres Zeilschool Ûp, lu sur la page « Bootkeuze » de l'école (champ « Zeilervaring »).

Relevé en ligne le 27/11/2026 : Optimist, Laser Pico 1/2 mans, Polyvalk, Keus22 = « geen » (aucune
expérience) -> debutant ; RS Feva = CWO I, RS Neo = CWO I ZB ou CWO II JZ, Laser Vago = CWO II ZB
-> intermediaire. Les pages génériques (Zeilkampen, Bootkeuze, Instructeursopleiding) ne portent
pas de niveau : laissées vides.
    python3 scripts/niveau_zeilschoolup.py
"""
import json, os, re

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
F = os.path.join(R, 'projets/sailingmore/stages.json')

# motif sur le lien ou le titre -> niveau annoncé par l'école
REGLES = [
    (r'optimist', 'debutant'),
    (r'pico', 'debutant'),
    (r'polyvalk', 'debutant'),
    (r'keus22', 'debutant'),
    (r'feva', 'intermediaire'),
    (r'rs-neo|rs neo', 'intermediaire'),
    (r'vago', 'intermediaire'),
]

d = json.load(open(F))
n = 0
for e in d['offres']:
    if e.get('ecole_slug') != 'zeilschoolup' or e.get('niveau'):
        continue
    cle = (e.get('lien', '') + ' ' + e.get('titre', '')).lower()
    if 'instructeur' in cle:
        continue
    for motif, niv in REGLES:
        if re.search(motif, cle):
            e['niveau'] = niv
            n += 1
            break
json.dump(d, open(F, 'w'), ensure_ascii=False, indent=1)
print(n, 'offres renseignées')
