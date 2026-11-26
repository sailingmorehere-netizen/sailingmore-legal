"""Lot D (prix_d) : prix relevés sur les pages des offres (lecture seule, 26/11/2026).
Plus bas prix de cours affiché ; tarifs horaires, frais d'inscription seuls et minimums légaux exclus."""
import json, os
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
F = os.path.join(R, 'projets/sailingmore/site/stages-proches.json')
raw = open(F, encoding='utf8').read()
d = json.loads(raw)
for sep, asc in (((',', ':'), False), ((', ', ': '), False), ((',', ':'), True)):
    if json.dumps(d, separators=sep, ensure_ascii=asc) == raw.rstrip('\n'):
        break
else:
    raise SystemExit('format non reproductible, je n ecris rien')
P = {
    76: (250, 'EUR', 'Compagnia della Vela'),        # Junior : inscription 1re semaine 250 EUR
    100: (600, 'EUR', 'EZS Zeilschool'),             # STCW : Basic Safety 600 EUR (autre cours 845)
    106: (253, 'CHF', 'Lagoo Segelschule Zürich'),   # cours d'initiation 253 CHF (leçons à l'heure exclues)
    211: (105, 'EUR', 'Soleil Scuola Nautica'),      # Corso BLSD : « Costo del corso 105€ »
    291: (300, 'EUR', 'Segelschule Überlingen'),     # yacht 4 pers. : week-end 300 EUR (basse saison)
    355: (10, 'EUR', 'Vent du Large'),               # adhésion annuelle 10 EUR
}
n = 0
for i, (p, c, ecole) in P.items():
    o = d['o'][i]
    assert o[4] == ecole and o[8] in (None, '', 0), i
    o[8], o[9] = float(p), c
    n += 1
open(F, 'w', encoding='utf8').write(json.dumps(d, separators=sep, ensure_ascii=asc) + ('\n' if raw.endswith('\n') else ''))
print('ok', n)
