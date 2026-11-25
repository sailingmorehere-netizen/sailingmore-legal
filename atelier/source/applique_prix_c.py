import json, os
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
F = os.path.join(R, 'projets/sailingmore/site/stages-proches.json')
raw = open(F, encoding='utf-8').read()
d = json.loads(raw)
cands = [dict(separators=(',', ':'), ensure_ascii=False), dict(separators=(',', ':'), ensure_ascii=True),
         dict(ensure_ascii=False), dict(ensure_ascii=True)]
kw = next((k for k in cands if json.dumps(d, **k) in (raw, raw.rstrip('\n'))), None)
print('format reproductible:', kw)
# indice -> (prix « à partir de », devise), lus sur la page de l'offre le 25/11/2026 (lecture seule).
# Oltremare : prix de liste avant remise Black Friday -20 %. Portitxol : tarif socio. Indices vérifiés par titre.
P = {
 # Neilson
 123: (538, 'GBP'), 124: (600, 'GBP'), 125: (982, 'GBP'), 127: (538, 'GBP'), 128: (199, 'GBP'),
 129: (499, 'GBP'), 130: (499, 'GBP'),
 # Oltremare Vela
 131: (220, 'EUR'), 132: (250, 'EUR'), 133: (220, 'EUR'), 134: (350, 'EUR'), 135: (300, 'EUR'),
 136: (190, 'EUR'), 137: (220, 'EUR'), 139: (440, 'EUR'), 141: (110, 'EUR'), 142: (400, 'EUR'),
 143: (250, 'EUR'), 144: (880, 'EUR'),
 # PlymSail
 152: (310, 'GBP'),
 # Club Nàutic Portitxol
 154: (70, 'EUR'), 157: (150, 'EUR'), 158: (60, 'EUR'),
 # Sailway
 196: (125, 'EUR'), 197: (65, 'EUR'), 198: (55, 'EUR'), 199: (125, 'EUR'), 200: (135, 'EUR'),
 201: (65, 'EUR'), 207: (400, 'EUR'),
 # Seafarer Sailing
 216: (795, 'GBP'), 217: (370, 'GBP'),
 # Segelschule Weber
 388: (390, 'EUR'), 389: (80, 'EUR'), 390: (80, 'EUR'), 391: (150, 'EUR'), 392: (150, 'EUR'),
 393: (150, 'EUR'), 394: (150, 'EUR'), 395: (540, 'EUR'), 396: (200, 'EUR'),
}
if kw:
    for i, (p, c) in P.items():
        o = d['o'][i]
        assert not o[8], i
        o[8] = float(p); o[9] = c
    out = json.dumps(d, **kw) + ('\n' if raw.endswith('\n') else '')
    open(F, 'w', encoding='utf-8').write(out)
    print('écrit', len(P))
