# © 2026 Sailing More — tous droits réservés. All rights reserved.
"""Tâche 52 : niveau des sessions du Club Nautique de Versoix, lu sur la page du club.
Le niveau n'est écrit que si la page l'affiche pour la session (étiquette de la liste).
Débutant -> debutant ; Perfectionnement -> intermediaire ; « Tous niveaux / Perfectionnement »
-> tous_niveaux (la page ne tranche pas : on ne choisit pas un niveau à sa place)."""
import json, re, subprocess, sys

FICH = 'projets/sailingmore/stages.json'
MOIS = 'Janvier|Février|Mars|Avril|Mai|Juin|Juillet|Août|Septembre|Octobre|Novembre|Décembre'
ETIQ = {'Débutant': 'debutant', 'Perfectionnement': 'intermediaire',
        'Tous niveaux / Perfectionnement': 'tous_niveaux', 'Tous niveaux': 'tous_niveaux'}
STOP = {'du', 'au', 'des', 'de', 'l', 'le', 'la'}


def toks(s):
    s = s.lower().replace('1er', '1').replace('tuesday', 'mardis').replace('friday', 'vendredis')
    s = s.replace('soirs', 'soir').replace('petite semaine', 'mini-semaine')
    s = re.sub(r'(\d+)h(\d\d)?', lambda m: '%02d:%s' % (int(m[1]), m[2] or '00'), s)
    s = s.replace('’', ' ').replace("'", ' ')
    return {t for t in re.findall(r'\d+:\d+|[a-zéèêûôàç]+|\d+', s)} - STOP


def page(url):
    h = subprocess.run(['curl', '-sL', '-m', '25', url.replace('/fr/', '/')],
                       capture_output=True, text=True).stdout
    h = re.sub(r'<(script|style)[^>]*>.*?</\1>', ' ', h, flags=re.S)
    t = re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', h))
    t = t.replace('&amp;', '&').replace('&nbsp;', ' ')
    i = t.find('Voyez les stages')
    t = t[i:]
    out = []
    rx = re.compile(r'(Débutant|Tous niveaux / Perfectionnement|Perfectionnement|Tous niveaux) (?:' + MOIS +
                    r') 20\d\d (.*?) CHF')
    for m in rx.finditer(t):
        out.append((ETIQ[m[1]], toks(m[2]), m[2]))
    return out


d = json.load(open(FICH, encoding='utf-8'))
L = d if isinstance(d, list) else max([v for v in d.values() if isinstance(v, list)], key=len)
V = [x for x in L if x.get('ecole') == 'Club Nautique de Versoix' and not x.get('hors_offre')]
cache = {}
rempli = rate = 0
for x in V:
    if x.get('niveau') not in (None, '', []):
        continue
    if x['lien'] not in cache:
        cache[x['lien']] = page(x['lien'])
    tail = x['titre'].split(' · ', 1)[1] if ' · ' in x['titre'] else ''
    k = toks(tail)
    c = [e for e in cache[x['lien']] if k <= e[1]]
    c.sort(key=lambda e: len(e[1]))
    if not c:  # repli : horaire du relevé différent de la page -> on apparie sur la date seule
        k = {t for t in k if ':' not in t}
        c = sorted([e for e in cache[x['lien']] if k <= e[1]], key=lambda e: len(e[1]))
    niv = {e[0] for e in c if len(e[1]) == len(c[0][1])} if c else set()
    if len(niv) == 1:
        x['niveau'] = niv.pop()
        rempli += 1
    else:
        rate += 1
        print('non résolu :', x['lien'][-20:], x['titre'], niv)
json.dump(d, open(FICH, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print('remplis', rempli, 'non résolus', rate, {u: len(v) for u, v in cache.items()})
