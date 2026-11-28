#!/usr/bin/env python3
"""Usage: verifie_trou_base.py <base.json> <champ> <max_vides> [--avec CHAMP]
Sort 0 si le nombre d'entrées dont <champ> est vide (parmi celles dont CHAMP est rempli, si --avec)
est <= max_vides. Base cherchée dans /opt/data/projets/sailingmore/, sinon projets/sailingmore/."""
import json, os, sys

def charge(nom):
    for racine in ('/opt/data/projets/sailingmore', 'projets/sailingmore'):
        p = os.path.join(racine, nom)
        if os.path.exists(p):
            return json.load(open(p, encoding='utf-8'))
    sys.exit('base introuvable: ' + nom)

def liste(d):
    if isinstance(d, list):
        return d
    return max((v for v in d.values() if isinstance(v, list)), key=len)

def rempli(e, k):
    return e.get(k) not in (None, '', [])

a = sys.argv[1:]
if len(a) < 3:
    sys.exit(__doc__)
base, champ, mx = a[0], a[1], int(a[2])
avec = a[a.index('--avec') + 1] if '--avec' in a else None
L = liste(charge(base))
if avec:
    L = [e for e in L if rempli(e, avec)]
vides = sum(1 for e in L if not rempli(e, champ))
print(f'{base} {champ}: {vides} vides sur {len(L)} (max {mx})')
sys.exit(0 if vides <= mx else 1)
