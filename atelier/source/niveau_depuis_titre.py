#!/usr/bin/env python3
"""Ecrit 'niveau' dans stages.json pour les offres sans niveau des écoles nommées, d'après le TITRE seul.
Rien n'est écrit quand le titre ne le dit pas. Usage : python3 scripts/niveau_depuis_titre.py"""
import json, re

CHEMIN = 'projets/sailingmore/stages.json'
ECOLES = ('UKSA', 'Solent Boat Training', 'Tip Top Sailing', 'Segelschule Rückenwind', 'Ultra Sailing', 'Virgins')
CONFIRME = re.compile(r'yachtmaster|coastal skipper|ocean|offshore|advanced|master|fortgeschritten|expert|racing|regatta', re.I)
INTER = re.compile(r'day skipper|dayskipper|intermediate|improver|level 3|level 4|aufbau|fortbildung|performance|seamanship|navigation', re.I)
DEBUT = re.compile(r'competent crew|beginner|start yachting|start sailing|introduc|taster|discover|first time|level 1|level 2|'
                   r'anf(ä|a)nger|einsteiger|schnupper|grundkurs|sbf|schnuppersegeln|try sailing|stepping', re.I)

d = json.load(open(CHEMIN, encoding='utf-8'))
L = d if isinstance(d, list) else max([v for v in d.values() if isinstance(v, list)], key=len)
n = 0
for e in L:
    if e.get('niveau') or e.get('ecole') not in ECOLES:
        continue
    t = e.get('titre') or ''
    # ordre : le plus élevé d'abord ("Yachtmaster" l'emporte sur "Competent Crew" cité en prérequis)
    for niv, rx in (('confirme', CONFIRME), ('intermediaire', INTER), ('debutant', DEBUT)):
        if rx.search(t):
            e['niveau'] = niv
            n += 1
            break
json.dump(d, open(CHEMIN, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('niveaux écrits :', n)
