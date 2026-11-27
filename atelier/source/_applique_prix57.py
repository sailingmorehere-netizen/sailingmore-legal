"""Tâche 57 : prix lus le 27/11/2026 sur la page de l'offre (champ lien), aucun inventé.
(ecole_slug, début du titre) -> (prix publié, devise)."""
import json
F = 'projets/sailingmore/stages.json'
d = json.load(open(F, encoding='utf-8'))
taux = d['taux']
print('taux', taux)
P = [
 ('marjaniemen-purjehtijat', 'Alkeiskurssi', 120, 'EUR'),
 ('marjaniemen-purjehtijat', 'Viiden päivän', 390, 'EUR'),
 ('marjaniemen-purjehtijat', 'Neljän päivän', 320, 'EUR'),
 ('espoon-merenkavijat-emk', 'Purjehduksen alkeiskurssi', 290, 'EUR'),
 ('espoon-pursiseura', 'Aikuisten ja nuorten jollakurssi – alkeiskurssi', 240, 'EUR'),
 ('espoon-pursiseura', 'Aikuisten ja nuorten jollakurssi – jatkokurssi', 240, 'EUR'),
 ('naantalin-pursiseura-nps', 'Aikuisten purjehduskoulu', 350, 'EUR'),
 ('turun-pursiseura', 'Purjehtijakurssi kevät 2026', 450, 'EUR'),
 ('quovadis-sailing', 'Purjehtijakurssi (Helsinki)', 490, 'EUR'),
 ('abrego', 'Purjehtijakurssi', 520, 'EUR'),
 ('abrego', 'Saaristopäällikkökurssi', 520, 'EUR'),
 ('abrego', 'Rannikkopäällikkökurssi', 520, 'EUR'),
 ('tampereen-pursiseura-taps', 'Retkipurjehduksen perusteet', 300, 'EUR'),
 ('tampereen-pursiseura-taps', 'Junnujen alkeiskurssi 7', 230, 'EUR'),
 ('tampereen-pursiseura-taps', 'Jollapurjehduksen alkeiskurssi 5', 200, 'EUR'),
 ('borga-segelsallskap-bss', 'Juniorien kesäleiri', 330, 'EUR'),
 ('nemo-sailing', 'Johdatus purjehdukseen 4 h', 122, 'EUR'),
 ('nemo-sailing', 'Yöpurjehduskurssi', 154, 'EUR'),
 ('sola-jadranja-odpluj', 'Tečaj jadranja – 1 dan', 139, 'EUR'),
 ('sola-jadranja-odpluj', 'Tečaj pristajanja', 155, 'EUR'),
 ('sola-jadranja-odpluj', 'Tečaj skiper', 490, 'EUR'),
 ('sola-jadranja-odpluj', 'ODPLUJ SAM', 276, 'EUR'),
 ('sola-jadranja-odpluj', 'Individualni navtični tečaj', 399, 'EUR'),
 ('jadralni-klub-pirat', 'Tečaj Osnove (otroci)', 440, 'EUR'),
 ('navtikon-sola-jadranja', 'Osnovni tečaj jadranja', 315, 'EUR'),
 ('north-adriatic-sailing-academy-na-sa', 'Osnovni tečaj jadranja – maj–september', 420, 'EUR'),
 ('north-adriatic-sailing-academy-na-sa', 'Nadaljevalni tečaj jadranja – oktober–april', 420, 'EUR'),
 ('north-adriatic-sailing-academy-na-sa', 'Nadaljevalni tečaj jadranja – maj–september', 460, 'EUR'),
 ('jadralni-klub-ljubljana', 'Šola jadranja', 440, 'EUR'),
 ('nys-skola-jachtingu', 'Ochutnávka jachtingu', 150, 'EUR'),
 ('good-captain-sailing-school', 'ISSA Yacht Crew Beginner', 499, 'EUR'),
 ('good-captain-sailing-school', 'ISSA Inshore Skipper', 1190, 'EUR'),
 ('good-captain-sailing-school', 'Discover Sailing', 129, 'EUR'),
 ('soleil', 'Corso BLSD', 105, 'EUR'),
 ('holovits-vitorlasiskola', 'Vitorlás elméleti és gyakorlati', 219900, 'HUF'),
 ('holovits-vitorlasiskola', 'Kombinált gyakorlati', 259900, 'HUF'),
 ('lazy-jack-vitorlasiskola', 'Vitorlás tanfolyam (3 napos', 136000, 'HUF'),
 ('hetenyi-hajosiskola', 'Kedvtelési célú vitorlás kishajó', 230000, 'HUF'),
 ('hetenyi-hajosiskola', 'Vitorlás gyakorló hétvége', 165000, 'HUF'),
 ('windworks', 'Egyéni vitorlás tanfolyam', 120000, 'HUF'),
 ('vitorlazas-hu', 'Kezdő tengeri vitorlástanfolyam', 155000, 'HUF'),
]
n = 0
for slug, deb, p, dev in P:
    c = [e for e in d['offres'] if e.get('ecole_slug') == slug and e['titre'].startswith(deb)
         and e.get('prix_eur') in (None, '', 0)]
    if len(c) != 1:
        print('IGNORE', slug, deb, len(c)); continue
    e = c[0]
    e['prix'] = float(p); e['devise'] = dev
    if dev == 'EUR':
        e['prix_eur'] = int(round(p))
    else:
        t = taux[dev]
        e['prix_eur'] = int(round(p / t)) if dev in ('HUF', 'RON') else int(round(p * t))
    e['prix_publie'] = True
    print(slug, deb, p, dev, '->', e['prix_eur']); n += 1
open(F, 'w', encoding='utf-8').write(json.dumps(d, ensure_ascii=False, indent=1))
print(n, 'prix posés')
