#!/usr/bin/env python3
"""Critère des tâches « remplir un champ de projets/sailingmore/stages.json » (offres hors `hors_offre`).
Usage : python3 /opt/data/scripts/verifie_stages_trou.py <champ> [<seuil>] [<école>]
  champ  : prix_eur, debut, fin, duree_jours, niveau, lieu, image, lat
  seuil  : taux minimal de remplissage (0-1) ; défaut ci-dessous
  école  : restreint aux offres de cette école (nom exact) — sans elle, toutes les écoles
Sort 0 si le taux de remplissage >= seuil. Sans argument : affiche l'état de tous les champs (sort 0)."""
import json, os, sys

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
F = os.path.join(RACINE, 'projets/sailingmore/stages.json')
CHAMPS = ('prix_eur', 'debut', 'fin', 'duree_jours', 'niveau', 'lieu', 'image', 'lat')
DEFAUT = {'prix_eur': 0.9, 'debut': 0.5, 'fin': 0.5, 'duree_jours': 0.6, 'niveau': 0.6,
          'lieu': 0.95, 'image': 0.8, 'lat': 1.0}


def taux(L, champ):
    ok = sum(1 for o in L if o.get(champ) not in (None, '', 0))
    return ok, len(L)


def main():
    L = [o for o in json.load(open(F, encoding='utf-8'))['offres'] if not o.get('hors_offre')]
    a = sys.argv[1:]
    if not a:
        for c in CHAMPS:
            ok, n = taux(L, c)
            print(f'{c}: {ok}/{n} ({ok / n:.0%})')
        return 0
    champ = a[0]
    if champ not in CHAMPS:
        print('champ inconnu :', champ); return 2
    seuil = float(a[1]) if len(a) > 1 else DEFAUT[champ]
    if len(a) > 2:
        L = [o for o in L if o.get('ecole') == a[2]]
    ok, n = taux(L, champ)
    t = ok / n if n else 0
    print(f'{champ}: {ok}/{n} ({t:.0%}), seuil {seuil:.0%}')
    return 0 if t >= seuil else 1


sys.exit(main())
