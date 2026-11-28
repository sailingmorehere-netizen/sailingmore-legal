#!/usr/bin/env python3
# © 2026 Sailing More — tous droits réservés. All rights reserved.
"""Ecrit 'niveau' dans stages.json pour TOUTES les offres sans niveau, d'après le TITRE seul (multilingue).
Rien n'est écrit quand le titre ne le dit pas. Les pages sans prix ni dates (infos, accès...) ne sont pas touchées
par cette règle : seul un mot de niveau explicite dans le titre compte.
Usage : python3 scripts/niveau_titre_toutes.py [--ecrire]   (sans option : compte seulement)"""
import json, re, sys, collections

CHEMIN = 'projets/sailingmore/stages.json'
CONFIRME = re.compile(r'yachtmaster|coastal skipper|ocean|offshore|advanced|fortgeschritten|expert|'
                      r'confirm[ée]|gevorderd|avanzad|avanzato|perfezionamento avanz|hochsee', re.I)
INTER = re.compile(r'day skipper|dayskipper|intermediate|improver|level 3|level 4|aufbau|perfectionnement|perfeccionamiento|'
                   r'perfezionamento|doorstart|vervolg|gevorderden|interm[eé]di|seamanship|niveau 3|niveau 4', re.I)
DEBUT = re.compile(r'competent crew|beginner|start yachting|start sailing|introduc|taster|discover|first time|level 1|level 2|'
                   r'anf(ä|a)nger|einsteiger|schnupper|grundkurs|try sailing|initiation|d[ée]butant|d[ée]couverte|'
                   r'iniciaci[oó]n|principiante|iniziazione|beginners|beginnersles|eerste|kennismak|proefles|opstap|'
                   r'niveau 1|niveau 2', re.I)

ecrire = '--ecrire' in sys.argv
d = json.load(open(CHEMIN, encoding='utf-8'))
L = d['offres']
n = 0
par = collections.Counter()
for e in L:
    if e.get('niveau'):
        continue
    t = e.get('titre') or ''
    for niv, rx in (('confirme', CONFIRME), ('intermediaire', INTER), ('debutant', DEBUT)):
        if rx.search(t):
            if ecrire:
                e['niveau'] = niv
            n += 1
            par[niv] += 1
            break
if ecrire:
    json.dump(d, open(CHEMIN, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
vide = sum(1 for e in L if not e.get('niveau'))
print('niveaux %s : %d %s ; sans niveau restant : %d/%d' % ('écrits' if ecrire else 'écrivables', n, dict(par), vide, len(L)))
