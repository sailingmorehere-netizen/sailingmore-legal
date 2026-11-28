#!/usr/bin/env python3
# © 2026 Sailing More — tous droits réservés. All rights reserved.
"""Geocode les bourses sans lat via la ville du port dans ports.sqlite. Usage: geocode_bourses.py [--ecrire]"""
import json, sqlite3, sys, os
R = '/opt/data/cache/claude-nuit/travail/projets/sailingmore'
p = os.path.join(R, 'bourses.json')
d = json.load(open(p, encoding='utf-8'))
L = d if isinstance(d, list) else max([v for v in d.values() if isinstance(v, list)], key=len)
print('cles:', list(L[0].keys()))
db = sqlite3.connect(os.path.join(R, 'ports.sqlite'))
for t, in db.execute("select name from sqlite_master where type='table'"):
    print(t, [c[1] for c in db.execute('pragma table_info(%s)' % t)])
for e in L:
    if e.get('lat') in (None, '', []):
        print('SANS LAT:', json.dumps(e, ensure_ascii=False))
