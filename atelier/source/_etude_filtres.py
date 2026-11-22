"""Mesures de l'étude des filtres (tâche 46). Lecture seule."""
import json, collections, re, sys
from datetime import date, timedelta
C = collections.Counter
d = json.load(open('projets/sailingmore/regates.json'))
r = d['regates']
print('clés racine', list(d.keys()))
print('épreuves', len(r)); print('exemple', r[0])
print('clés', C(k for e in r for k in e).most_common())
for k in ['pays', 'type', 'region', 'ligue']:
    c = C(e.get(k) for e in r)
    print(k, 'valeurs distinctes', len(c), c.most_common(15))
print('sans debut', sum(1 for e in r if not e.get('debut')),
      'sans fin', sum(1 for e in r if not e.get('fin')),
      'fin<debut', sum(1 for e in r if e.get('fin') and e.get('debut') and e['fin'] < e['debut']),
      'sans classes', sum(1 for e in r if not e.get('classes')),
      'sans pays', sum(1 for e in r if not e.get('pays')),
      'sans region', sum(1 for e in r if not e.get('region')),
      'sans lieu', sum(1 for e in r if not (e.get('ville') or e.get('club'))),
      'sans lien', sum(1 for e in r if not e.get('lien')),
      'annulees', sum(1 for e in r if e.get('annulee')),
      'avec lat', sum(1 for e in r if e.get('lat') is not None))
today = date.today().isoformat()
print('à venir (fin>=today)', sum(1 for e in r if (e.get('fin') or e.get('debut') or '') >= today))
cl = C(c.strip() for e in r for c in (e.get('classes') or []) if c and c.strip())
print('classes distinctes', len(cl), 'top', cl.most_common(12))
print('classes avec 1 seule épreuve', sum(1 for v in cl.values() if v == 1), ' <=2:', sum(1 for v in cl.values() if v <= 2))
# couples (pays,mois) pour « Suisse le mois prochain »
mois = C((e.get('pays'), (e.get('debut') or '')[:7]) for e in r)
print('SUI par mois', sorted((m, n) for (p, m), n in mois.items() if p == 'SUI')[:16])
reg_pays = collections.defaultdict(set)
for e in r:
    reg_pays[e.get('region')].add(e.get('pays'))
print('regions->pays', {k: sorted(map(str, v)) for k, v in reg_pays.items()})
# combinaisons de deux filtres qui ne renvoient rien (à venir)
av = [e for e in r if (e.get('fin') or e.get('debut') or '') >= today]
vide = 0; tot = 0
regs = sorted({str(e.get('region')) for e in av}); typs = sorted({str(e.get('type')) for e in av})
for a in regs:
    for t in typs:
        tot += 1
        if not any(str(e.get('region')) == a and str(e.get('type')) == t for e in av): vide += 1
print('région×type à venir : combinaisons', tot, 'vides', vide)
# week-end
def we(e):
    try:
        a = date.fromisoformat(e['debut']); b = date.fromisoformat(e.get('fin') or e['debut'])
    except Exception:
        return False
    x = a
    while x <= b:
        if x.weekday() >= 5: return True
        x += timedelta(days=1)
    return False
print('épreuves touchant un week-end', sum(1 for e in av if we(e)), 'sur', len(av))
print('durée>14 j', sum(1 for e in r if e.get('fin') and e.get('debut') and (date.fromisoformat(e['fin']) - date.fromisoformat(e['debut'])).days > 14))
