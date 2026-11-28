#!/usr/bin/env python3
"""Tâche 50 : si debut et fin existent et duree_jours est vide, poser fin-debut+1. Sinon rien.
Usage: deduit_duree_jours.py [chemin stages.json]"""
import json, sys
from datetime import date

p = sys.argv[1] if len(sys.argv) > 1 else 'projets/sailingmore/stages.json'
txt = open(p, encoding='utf-8').read()
d = json.loads(txt)
# format d'origine : on le reproduit pour ne changer que les champs posés
ea = '\\u' in txt
L = d['offres'] if isinstance(d, dict) else d
posees = ignores = 0
for e in L:
    if e.get('duree_jours') not in (None, ''):
        continue
    a, b = e.get('debut'), e.get('fin')
    if not a or not b:
        continue
    try:
        n = (date.fromisoformat(b[:10]) - date.fromisoformat(a[:10])).days + 1
    except ValueError:
        ignores += 1
        continue
    if n < 1:
        ignores += 1
        continue
    e['duree_jours'] = n
    posees += 1
out = json.dumps(d, indent=1, ensure_ascii=ea)
if txt.endswith('\n'):
    out += '\n'
open(p, 'w', encoding='utf-8').write(out)
print(f'posées: {posees}, ignorées (date invalide ou fin<debut): {ignores}')
