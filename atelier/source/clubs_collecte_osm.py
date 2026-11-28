# © 2026 Sailing More — tous droits réservés. All rights reserved.
"""Collecte les clubs de voile d'OpenStreetMap (lecture seule, GET Overpass) -> projets/clubs-monde/osm.json.
Lancer depuis la racine de la copie : python3 scripts/clubs_collecte_osm.py
"""
import json, os, time, urllib.parse, urllib.request

OUT = 'projets/clubs-monde/osm.json'
Q = ('[out:json][timeout:180];('
     'nwr["club"="sailing"];nwr["sport"="sailing"]["name"];nwr["club"="yacht"];nwr["sport"="yachting"]["name"];'
     ');out tags center;')
SERVEURS = ['https://overpass-api.de/api/interpreter', 'https://overpass.kumi.systems/api/interpreter']

def main():
    os.makedirs('projets/clubs-monde', exist_ok=True)
    err = []
    for s in SERVEURS:
        try:
            req = urllib.request.Request(s + '?data=' + urllib.parse.quote(Q), headers={'User-Agent': 'sailingmore-annuaire/1.0'})
            with urllib.request.urlopen(req, timeout=200) as r:
                d = json.load(r)
            els = d.get('elements', [])
            json.dump({'source': s, 'releve': time.strftime('%Y-%m-%d'), 'elements': els}, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False)
            print('ok', s, len(els), 'objets')
            return
        except Exception as e:
            err.append('%s : %r' % (s, e)); print('échec', err[-1])
    open('projets/clubs-monde/osm-erreur.txt', 'w').write('\n'.join(err))

main()
