#!/usr/bin/env python3
"""Critère des tâches « remplir les bases » (tâche 50, 27/11/2026).

Usage : verifie_trou_site.py <base> <champ> <max> [ecole]
  base  : stages | regates | bourses
  champ : champ qui doit être rempli (vide, null, "" = manquant)
  max   : nombre maximal d'entrées encore vides pour sortir en 0
  ecole : (stages seulement) ne compter que cette école ; "-" = toutes
Les entrées stages marquées hors_offre sont ignorées.
Sort en 0 si manquants <= max, sinon 1, en affichant le compte.
"""
import glob
import json
import sys

RACINE = '/opt/data/projets/sailingmore/'


def liste(d):
    if isinstance(d, list):
        return d
    return max([v for v in d.values() if isinstance(v, list)], key=len)


def main(a):
    if len(a) < 3:
        print(__doc__)
        return 2
    base, champ, mx = a[0], a[1], int(a[2])
    ecole = a[3] if len(a) > 3 and a[3] != '-' else None
    if base == 'stages':
        fich = RACINE + 'stages.json'
    elif base == 'regates':
        fich = RACINE + 'regates.json'
    else:
        fs = glob.glob(RACINE + '**/bourses*.json', recursive=True)
        if not fs:
            print('bourses*.json introuvable sous', RACINE)
            return 2
        fich = fs[0]
    L = liste(json.load(open(fich, encoding='utf-8')))
    if base == 'stages':
        L = [x for x in L if not x.get('hors_offre')]
        if ecole:
            L = [x for x in L if x.get('ecole') == ecole]
    n = sum(1 for x in L if x.get(champ) in (None, '', []))
    print(f'{base}.{champ}' + (f' [{ecole}]' if ecole else '') + f': {n} manquants sur {len(L)} (max {mx})')
    return 0 if n <= mx else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
