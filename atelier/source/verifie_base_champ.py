#!/usr/bin/env python3
# © 2026 Sailing More — tous droits réservés. All rights reserved.
"""Critere des taches 'remplir un champ'. Usage :
  verifie_base_champ.py <base.json> <champ> <max_manque>   -> 0 si le nombre d'entrees SANS le champ est <= max_manque
  verifie_base_champ.py stages.json titre-hors-offre 0      -> 0 si aucune non-offre sans drapeau hors_offre
La base est cherchee dans /opt/data/projets/sailingmore/ puis .../site/."""
import json, os, re, sys

RACINES = [os.environ.get('NUIT_TRAVAIL', '').rstrip('/') or '/opt/data/projets/sailingmore',
           '/opt/data/projets/sailingmore', '/opt/data/projets/sailingmore/site']
# La copie de travail de Claude passe en tête : un critère juge ce que la tâche a produit, pas
# l'original qu'elle n'a pas le droit de toucher (27/11/2026 : deux tâches justes jugées en échec).
if os.path.isdir('/opt/data/cache/claude-nuit/travail/projets/sailingmore'):
    RACINES.insert(0, '/opt/data/cache/claude-nuit/travail/projets/sailingmore')
HORS_OFFRE = re.compile(r'galer[ií]a|galer.a de im|informatie|offerte aanvragen|erkenningen|cenizas al mar|bono regalo|'
                        r'^le sedi$|our sailing areas|sailing distance calculator|rya training centres|zeilschool gezocht|'
                        r'campeonato del mundo|abre inscripciones|thema.s seizoen|locatie van de zeilschool|'
                        r'^information$|^sailing holidays$', re.I)


def charge(nom):
    for r in RACINES:
        p = os.path.join(r, nom)
        if os.path.exists(p):
            d = json.load(open(p, encoding='utf-8'))
            if isinstance(d, dict):
                listes = [v for v in d.values() if isinstance(v, list)]
                d = max(listes, key=len) if listes else []
            return d
    sys.exit('base introuvable : ' + nom)


def main():
    if len(sys.argv) != 4:
        sys.exit(__doc__)
    nom, champ, seuil = sys.argv[1], sys.argv[2], int(sys.argv[3])
    L = charge(nom)
    if champ == 'titre-hors-offre':
        manque = sum(1 for e in L if HORS_OFFRE.search(e.get('titre') or '') and not e.get('hors_offre'))
    else:
        manque = sum(1 for e in L if e.get(champ) in (None, '', []))
    print(f'{nom} {champ}: manque {manque}/{len(L)} (seuil {seuil})')
    sys.exit(0 if manque <= seuil else 1)


main()
