#!/usr/bin/env python3
# © 2026 Sailing More — tous droits réservés. All rights reserved.
"""Niveau des offres Tip Top Sailing dont la page annonce l'étendue des niveaux CWO.

Relevé en ligne le 27/11/2026 :
  - /zeilschool/cwo-jachtzeilen-non-tidal/ : « Jachtzeilen niveau I » ... IV, tous niveaux sur une page ;
  - /zeezeilen/zeezeilprogramma/ : « CWO zeezeilprogramma, Tidal niveau I t/m IV ».
Une page qui annonce I à IV -> tous_niveaux (valeur déjà utilisée). Aucune autre page Tip Top n'est touchée.
    python3 scripts/niveau_tiptop.py
"""
import json, os

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
F = os.path.join(R, 'projets/sailingmore/stages.json')
LIENS = {
    'https://tiptopsailing.nl/zeilschool/cwo-jachtzeilen-non-tidal/',
    'https://tiptopsailing.nl/zeezeilen/zeezeilprogramma/',
}
d = json.load(open(F))
n = 0
for e in d['offres']:
    if e.get('ecole_slug') == 'tiptop' and not e.get('niveau') and e.get('lien') in LIENS:
        e['niveau'] = 'tous_niveaux'
        n += 1
json.dump(d, open(F, 'w'), ensure_ascii=False, indent=1)
print(n, 'offres renseignées')
