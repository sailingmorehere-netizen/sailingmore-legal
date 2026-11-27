#!/usr/bin/env python3
"""Usage: verifie_champ_stages.py <champ> <max_manquant> [ecole_slug]
Sort 0 si le nombre d'offres de stages.json dont <champ> est vide est <= max_manquant.
Lit stages.json relatif à la racine du projet (copie de travail ou /opt/data)."""
import json, os, sys
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
champ, maxi = sys.argv[1], int(sys.argv[2])
slug = sys.argv[3] if len(sys.argv) > 3 else None
offres = json.load(open(os.path.join(R, 'projets/sailingmore/stages.json')))['offres']
if slug:
    offres = [e for e in offres if e.get('ecole_slug') == slug]
m = sum(1 for e in offres if e.get(champ) in (None, '', [], 0))
print(f'{champ}: {m} manquants sur {len(offres)} (seuil {maxi})')
sys.exit(0 if m <= maxi else 1)
