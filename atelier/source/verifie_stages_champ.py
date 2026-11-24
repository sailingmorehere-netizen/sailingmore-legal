#!/usr/bin/env python3
"""Critère des tâches « remplir un champ des stages ». Sort 0 si le lot est rempli.
Usage : python3 verifie_stages_champ.py <lot>   (prix_a, prix_b, prix_c, prix_d, lieu, debut, image)
Lit projets/sailingmore/site/stages-proches.json (colonnes : 5 lieu, 7 debut, 8 prix, 11 image, 4 école)
relatif à la racine du projet (/opt/data ou la copie de travail)."""
import json, os, sys

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
F = os.path.join(RACINE, 'projets/sailingmore/site/stages-proches.json')
LOTS = {
    'prix_a': ['Solent Boat Training', 'Tip Top Sailing', 'Seven Seas School of Yachting', 'Ultra Sailing'],
    'prix_b': ['De Bird', 'UKSA', 'Segelschule Rückenwind', 'Zeilschool Ûp', 'BH Marine'],
    'prix_c': ['Oltremare Vela', 'Sailway', 'Sailing Virgins', 'Segelschule Weber', 'Seafarer Sailing',
               'Neilson', 'Club Nàutic Portitxol', 'Aquavitesse', 'PlymSail'],
    'prix_d': ['Segelschule Insel Reichenau', 'Compagnia della Vela', 'École de croisière Slowlife',
               'Urban Truant', 'Segelschule Grosse Freiheit', 'La Scuola della Vela', 'Soleil Scuola Nautica',
               'Segelschule Überlingen', 'EZS Zeilschool', 'Real Club de Mar', 'Blue Spirit', 'Solent Sail',
               'Vent du Large', 'Lagoo Segelschule Zürich', 'Segelschule Rehbach', 'Segelschule Schluchsee', 'Windzone'],
}
COL = {'prix': 8, 'lieu': 5, 'debut': 7, 'image': 11}
SEUIL = {'lieu': 0.9, 'debut': 0.4, 'image': 0.95}


def main():
    lot = sys.argv[1] if len(sys.argv) > 1 else ''
    L = json.load(open(F))['o']
    if lot in LOTS:
        champ, seuil = 'prix', 0.9
        sel = [o for o in L if o[4] in LOTS[lot]]
    elif lot in SEUIL:
        champ, seuil, sel = lot, SEUIL[lot], L
    else:
        print('lot inconnu :', lot); return 2
    ok = sum(1 for o in sel if o[COL[champ]] not in (None, '', 0))
    taux = ok / len(sel) if sel else 0
    print(f'{lot}: {champ} rempli {ok}/{len(sel)} ({taux:.0%}), seuil {seuil:.0%}')
    return 0 if taux >= seuil else 1


sys.exit(main())
