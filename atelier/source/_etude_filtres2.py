"""Mesures sur la page produite (épreuves embarquées). Lecture seule."""
import json, re, collections, itertools
from pathlib import Path
C = collections.Counter
h = Path('projets/sailingmore/site/regates.html').read_text(encoding='utf-8')
d = json.loads(re.search(r'id="donnees">(.*?)</script>', h, re.S).group(1))
E = d['epreuves']; n = len(E)
print('embarquées', n, '| JSON embarqué octets', len(json.dumps(E, ensure_ascii=False)))
print('SUI par région', C(e['region'] for e in E if e['pays'] == 'SUI'))
print('région Suisse par pays', C(e['pays'] for e in E if e['region'] == 'Suisse'))
print('pays distincts', len(C(e['pays'] for e in E if e['pays'])), C(e['pays'] for e in E).most_common(8))
print('sans pays', sum(1 for e in E if not e['pays']), 'sans classe', sum(1 for e in E if not e['classes']),
      'annulées', sum(1 for e in E if e['annulee']), 'sans lien', sum(1 for e in E if not e['lien']))
cl = C(c for e in E for c in set(e['classes']))
print('classes distinctes', len(cl), '| à 1 épreuve', sum(1 for v in cl.values() if v == 1), '| à <=2', sum(1 for v in cl.values() if v <= 2))
print('types', C(e['type'] for e in E))
# Suisse en décembre : mois prochain
for m in ('2026-12', '2027-01'):
    print(m, 'SUI', sum(1 for e in E if e['pays'] == 'SUI' and e['debut'][:7] == m), '| région Suisse', sum(1 for e in E if e['region'] == 'Suisse' and e['debut'][:7] == m))
# combinaisons à zéro (région x type x pays)
regs = sorted({e['region'] for e in E}); typs = sorted({e['type'] for e in E}); pays = sorted({e['pays'] for e in E if e['pays']})
z = sum(1 for a, t in itertools.product(regs, typs) if not any(e['region'] == a and e['type'] == t for e in E))
print('région x type : combinaisons', len(regs) * len(typs), 'vides', z)
z = sum(1 for a, p in itertools.product(regs, pays) if not any(e['region'] == a and e['pays'] == p for e in E))
print('région x pays : combinaisons', len(regs) * len(pays), 'vides', z)
print('hors-regate résiduel', sum(1 for e in E if e['type'] == 'hors-regate'))
print('lat absent', sum(1 for e in E if 'lat' not in e))
print('épreuves qui incluent un samedi/dimanche', end=' ')
from datetime import date, timedelta
def we(e):
    a = date.fromisoformat(e['debut']); b = date.fromisoformat(e['fin'])
    return any((a + timedelta(i)).weekday() >= 5 for i in range((b - a).days + 1))
print(sum(1 for e in E if we(e)), 'sur', n)
