# © 2026 Sailing More — tous droits réservés. All rights reserved.
"""Tâche 60 : prix lus le 28/11/2026 sur la page `lien` de l'offre (relevés : releve_prix_lien60*.py).
Règle : prix affiché en toutes lettres pour cette offre ; tarif horaire, acompte, frais d'inscription,
remise conditionnelle exclus ; devise d'origine gardée, prix_eur converti avec d['taux'] (HUF/RON divisés,
GBP/CHF multipliés, comme _applique_prix57.py). Offre inconnue ou titre différent -> ignorée. Rejouable."""
import json
F = 'projets/sailingmore/stages.json'
raw = open(F, encoding='utf-8').read()
d = json.loads(raw)
for ea in (False, True):
    for ind in (2, 1):
        if json.dumps(d, ensure_ascii=ea, indent=ind) == raw:
            FMT = (ea, ind); break
    else:
        continue
    break
else:
    raise SystemExit('format non reproductible, je n ecris rien')
taux = d['taux']
# indice dans d['offres'] : (début du titre, prix, devise)
P = {
 81: ('Junior Sailing', 250, 'EUR'), 111: ('STCW', 600, 'EUR'), 112: ('Kombikurse', 560, 'EUR'),
 142: ('Corso APNEA', 440, 'EUR'), 174: ('Angebote für Studenten', 340, 'EUR'),
 188: ('Zum Reinschnuppern', 75, 'EUR'), 230: ('Corso BLSD', 105, 'EUR'),
 312: ('Vollausgerüstete', 550, 'EUR'), 376: ('Adhésion', 10, 'EUR'),
 801: ('Alkeiskurssi', 120, 'EUR'), 802: ('Viiden', 390, 'EUR'), 803: ('Neljän', 320, 'EUR'),
 805: ('Purjehtijakurssi (alkaen)', 270, 'EUR'), 806: ('Aikuisten purjehduskoulu', 350, 'EUR'),
 807: ('Purjehduksen alkeiskurssi', 290, 'EUR'), 808: ('Aikuisten ja nuorten', 240, 'EUR'),
 809: ('Aikuisten ja nuorten', 240, 'EUR'), 810: ('Purjehtijakurssi', 450, 'EUR'),
 811: ('Päällikkökurssi', 450, 'EUR'), 812: ('Jollapurjehduksen alkeiskurssi', 250, 'EUR'),
 813: ('Jollapurjehduksen peruskurssi', 250, 'EUR'), 817: ('Johdatus', 122, 'EUR'),
 820: ('Yöpurjehduskurssi', 154, 'EUR'), 821: ('Purjehtijakurssi', 490, 'EUR'),
 822: ('Saaristopäällikkökurssi', 490, 'EUR'), 823: ('Purjehtijakurssi', 520, 'EUR'),
 824: ('Saaristopäällikkökurssi', 520, 'EUR'), 825: ('Rannikkopäällikkökurssi', 520, 'EUR'),
 826: ('Junnujen alkeiskurssi', 230, 'EUR'), 828: ('Retkipurjehduksen', 300, 'EUR'),
 829: ('Juniorien', 330, 'EUR'), 830: ('Seglingsskola 1', 370, 'EUR'), 831: ('Seglingsskola 3', 310, 'EUR'),
 832: ('Začetni', 230, 'EUR'), 834: ('Race Sailing', 890, 'EUR'), 835: ('Barcolana', 590, 'EUR'),
 837: ('Tečaj jadranja – 1', 139, 'EUR'), 839: ('Tečaj pristajanja', 155, 'EUR'),
 840: ('Tečaj skiper', 490, 'EUR'), 841: ('ODPLUJ SAM', 276, 'EUR'), 842: ('Individualni', 399, 'EUR'),
 843: ('Tečaj Osnove', 440, 'EUR'), 844: ('Tečaj Napredujem', 440, 'EUR'), 845: ('Tečaj Mladostniki', 440, 'EUR'),
 849: ('Osnovni', 315, 'EUR'), 850: ('Regatni', 330, 'EUR'),
 852: ('Osnovni', 420, 'EUR'), 853: ('Nadaljevalni', 420, 'EUR'), 854: ('Nadaljevalni', 460, 'EUR'),
 855: ('Šola jadranja', 440, 'EUR'), 856: ('Ochutnávka', 150, 'EUR'), 861: ('Kurz Vodca', 400, 'EUR'),
 864: ('Kapitánsky', 460, 'EUR'), 895: ('ISSA Yacht', 499, 'EUR'), 896: ('ISSA Inshore', 1190, 'EUR'),
 897: ('Discover', 129, 'EUR'),
 117: ('Segelkurse', 680, 'CHF'), 316: ('Superyacht', 22500, 'GBP'),
 865: ('Kezdő 1 hetes', 245000, 'HUF'), 866: ('Kezdő 2 hétvégés', 245000, 'HUF'),
 867: ('Kezdő Extra', 367500, 'HUF'), 868: ('Expressz', 158000, 'HUF'), 869: ('Hétvégi', 200000, 'HUF'),
 871: ('Vitorlás tanfolyam tengeri', 150000, 'HUF'), 873: ('Kombinált', 180000, 'HUF'),
 874: ('Vitorlás elméleti', 219900, 'HUF'), 876: ('Kombinált gyakorlati', 259900, 'HUF'),
 880: ('Vitorlás tanfolyam (3', 136000, 'HUF'), 881: ('Kedvtelési', 230000, 'HUF'),
 883: ('Vitorlás gyakorló hétvége', 165000, 'HUF'), 884: ('Egyéni', 120000, 'HUF'),
 885: ('Kezdő tengeri', 155000, 'HUF'),
 886: ('Certificat Clasa S', 1500, 'RON'), 891: ('Curs Sailing', 1950, 'RON'),
 # relevé complémentaire (pages relues en contexte)
 827: ('Jollapurjehduksen alkeiskurssi', 200, 'EUR'), 173: ('Sportbootführerschein See', 228, 'EUR'),
 838: ('Tečaj jadranja – 2', 269, 'EUR'), 890: ('Curs C+S', 2250, 'RON'),
 902: ('Капитански', 500, 'EUR'), 894: ('Curs motor CD', 1750, 'RON'),
 399: ('Personal Training', 500, 'EUR'),  # plus bas prix de cours affiché (Funkkurs SRC/UBI)
}
CORRIGE = {886, 891}  # posés une première fois à 1350 / 1750 : corrigés (1350 = tarif remisé, 1950 = prix de la page)
n = 0
for i, (deb, p, dev) in P.items():
    e = d['offres'][i]
    if not e['titre'].startswith(deb):
        print('IGNORE', i, deb, '!=', e['titre'][:40]); continue
    if e.get('prix_eur') not in (None, '', 0) and i not in CORRIGE:
        continue
    e['prix'] = float(p); e['devise'] = dev
    t = taux[dev]
    e['prix_eur'] = int(round(p / t)) if dev in ('HUF', 'RON') else int(round(p * t))
    e['prix_publie'] = True
    n += 1
open(F, 'w', encoding='utf-8').write(json.dumps(d, ensure_ascii=FMT[0], indent=FMT[1]))
print(n, 'prix posés')
