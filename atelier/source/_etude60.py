import json
R = '/opt/data/cache/claude-nuit/travail/projets/sailingmore/stages.json'
raw = open(R, encoding='utf-8').read()
S = json.loads(raw)
for ea in (False, True):
    if json.dumps(S, ensure_ascii=ea, indent=2) == raw:
        print('format identique, ensure_ascii =', ea)
        break
else:
    print('format différent'); raise SystemExit(1)
n = 0
for o in S['offres']:
    if o.get('lieu') == 'Tortola' and o.get('lat') in (None, ''):
        o['lat'], o['lon'], o['precision'] = 18.42, -64.62, 'ville'
        n += 1
open(R, 'w', encoding='utf-8').write(json.dumps(S, ensure_ascii=ea, indent=2))
print('corrigé', n)
