#!/usr/bin/env python3
"""Usage: verifie_champ_stages.py <champ> <max_manquants> [chemin stages.json]
Sort 0 si le nombre d'entrées sans <champ> est <= max_manquants."""
import json, sys
champ, mx = sys.argv[1], int(sys.argv[2])
p = sys.argv[3] if len(sys.argv) > 3 else '/opt/data/projets/sailingmore/stages.json'
d = json.load(open(p, encoding='utf-8'))
L = max([v for v in d.values() if isinstance(v, list)], key=len) if isinstance(d, dict) else d
m = sum(1 for e in L if e.get(champ) in (None, ''))
print(f'{champ}: {m}/{len(L)} manquants (seuil {mx})')
sys.exit(0 if m <= mx else 1)
