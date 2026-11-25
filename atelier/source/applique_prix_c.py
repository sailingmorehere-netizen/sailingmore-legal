import json, os
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
F = os.path.join(R, 'projets/sailingmore/site/stages-proches.json')
raw = open(F, encoding='utf-8').read()
d = json.loads(raw)
cands = [dict(separators=(',', ':'), ensure_ascii=False), dict(separators=(',', ':'), ensure_ascii=True),
         dict(ensure_ascii=False), dict(ensure_ascii=True)]
kw = next((k for k in cands if json.dumps(d, **k) in (raw, raw.rstrip('\n'))), None)
print('format reproductible:', kw)
# indice -> (prix « à partir de », devise), relevés sur les pages des écoles le 25/11/2026 (lecture seule).
# Black Friday Oltremare : prix de liste (avant remise -20 %).
P = {
 # Segelschule Weber — page /Preise
 390: (390, 'EUR'), 391: (80, 'EUR'), 392: (240, 'EUR'), 393: (150, 'EUR'), 394: (150, 'EUR'),
 395: (150, 'EUR'), 396: (150, 'EUR'), 397: (540, 'EUR'),
 # Neilson
 125: (538, 'GBP'), 126: (600, 'GBP'), 127: (982, 'GBP'), 130: (199, 'GBP'), 131: (499, 'GBP'), 132: (499, 'GBP'),
 # Oltremare Vela
 134: (250, 'EUR'), 135: (220, 'EUR'), 136: (350, 'EUR'), 137: (300, 'EUR'), 138: (190, 'EUR'), 139: (220, 'EUR'),
 141: (440, 'EUR'), 143: (110, 'EUR'), 144: (400, 'EUR'), 145: (250, 'EUR'), 146: (880, 'EUR'),
 # PlymSail
 154: (310, 'GBP'),
 # Club Nàutic Portitxol (tarif socio, le plus bas affiché)
 156: (70, 'EUR'), 159: (150, 'EUR'), 160: (60, 'EUR'),
 # Sailway
 198: (125, 'EUR'), 199: (65, 'EUR'), 200: (55, 'EUR'), 202: (135, 'EUR'), 203: (65, 'EUR'),
 # Seafarer Sailing
 218: (795, 'GBP'), 219: (370, 'GBP'),
}
if kw:
    for i, (p, c) in P.items():
        o = d['o'][i]
        assert not o[8], i
        o[8] = float(p); o[9] = c
    out = json.dumps(d, **kw) + ('\n' if raw.endswith('\n') else '')
    open(F, 'w', encoding='utf-8').write(out)
    print('écrit', len(P))
