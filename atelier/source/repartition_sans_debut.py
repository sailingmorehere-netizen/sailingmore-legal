#!/usr/bin/env python3
# © 2026 Sailing More — tous droits réservés. All rights reserved.
"""Répartition par école des offres sans debut (lecture seule)."""
import json, collections
o = json.load(open('projets/sailingmore/stages.json'))['offres']
m = [e for e in o if not e.get('debut')]
c = collections.Counter(e['ecole_slug'] for e in m)
liens = collections.Counter(e['lien'] for e in m)
for s, n in c.most_common(30):
    ex = next(e for e in m if e['ecole_slug'] == s)
    nl = len({e['lien'] for e in m if e['ecole_slug'] == s})
    print(s, n, 'liens distincts', nl, 'hors_offre', sum(1 for e in m if e['ecole_slug'] == s and e.get('hors_offre')), ex['titre'][:40], ex['lien'][:70])
print(len(m), 'sans debut ;', sum(1 for e in m if e.get('hors_offre')), 'hors_offre')
