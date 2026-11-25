"""Tache 61 : ecrit debut/fin/duree_jours depuis les calendriers publies (premiere session a venir, date lue telle quelle)."""
import json, re, datetime as dt
F = 'projets/sailingmore/stages.json'
d = json.load(open(F, encoding='utf-8'))
MOIS = {'januari': 1, 'februari': 2, 'maart': 3, 'april': 4, 'mei': 5, 'juni': 6, 'juli': 7, 'augustus': 8, 'september': 9}


def txt(url):
    n = re.sub(r'\W+', '_', url)[:100]
    return open(f'tmp_n61/{n}.txt').read()


def D(y, m, j):
    return dt.date(y, m, j)


val = {}  # lien -> (debut, fin)
# Zeilschool Up : premiere session listee "2027 <nom> (J mois t/m J mois)"
for e in d['offres']:
    if e['ecole'] == 'Zeilschool Ûp' and not e.get('debut') and ('/product/' in e['lien'] or e['lien'].endswith('-jaar')):
        t = txt(e['lien'])
        m = re.search(r'2027 [^()]{3,30}\((\d+) (\w+) t/m (\d+) (\w+)\)', t)
        if m:
            val[e['lien']] = (D(2027, MOIS[m[2]], int(m[1])), D(2027, MOIS[m[4]], int(m[3])))
val['https://www.zeilschoolup.nl/zeilkampen/instructeursopleiding'] = (D(2027, 3, 5), D(2027, 3, 7))  # Methodiekweekend 5 - 7 maart 2027
# Oltremare
val['https://www.oltremare.it/apnea-a-vela-luglio-2027/'] = (D(2027, 7, 3), D(2027, 7, 10))
val['https://www.oltremare.it/corso-apnea-life-style-open-water-1-livello-freediver/'] = (D(2027, 3, 18), D(2027, 4, 15))
for u in ('https://www.oltremare.it/corso-di-manutenzione-del-motore-diesel/',
          'https://www.oltremare.it/prodotto/corso-manutenzione-motore-diesel-e-gestione-delle-avarie/'):
    val[u] = (D(2027, 1, 30), D(2027, 1, 31))
val['https://www.oltremare.it/corso-regata-2/'] = (D(2026, 11, 28), D(2026, 11, 29))
# Compagnia, Zeezeilschool, Tip Top
val['https://www.compagniadellavela.org/open-day-scuola-vela-2-giugno/'] = (D(2027, 6, 2), D(2027, 6, 2))
val['https://zeezeilschool.nl/cwo/cwo-i-weekend/'] = (D(2027, 3, 26), D(2027, 3, 28))
val['https://tiptopsailing.nl/zeezeilen/zeezeilprogramma/'] = (D(2027, 4, 19), D(2027, 4, 27))  # tableau "Zeezeil programma 2027" 19-Apr -> 27-Apr
val['https://tiptopsailing.nl/zeilvakanties/flottielje-zeilen/flottielje-zeilen-lefkas/'] = (D(2027, 4, 24), D(2027, 5, 1))  # "seizoen 2027" 17 24/04 01/05

n = 0
for e in d['offres']:
    if not e.get('debut') and e['lien'] in val:
        a, b = val[e['lien']]
        assert b >= a
        e['debut'], e['fin'] = a.isoformat(), b.isoformat()
        calc = (b - a).days + 1
        if e.get('duree_jours') not in (None, calc):
            print('duree publiee differente', e['lien'], e['duree_jours'], calc)
        e['duree_jours'] = calc
        n += 1
        print(e['debut'], e['fin'], calc, e['titre'][:40])
json.dump(d, open(F, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('remplis', n)
