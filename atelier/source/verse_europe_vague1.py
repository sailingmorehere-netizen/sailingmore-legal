# © 2026 Sailing More — tous droits réservés. All rights reserved.
"""Tâche 22 : verse les 222 offres Europe vague 1 (AUT SWE DNK NOR CZE POL) dans stages.json et ecoles.json.
Idempotent (clé école+titre+lien), n'écrase rien : ajoute seulement. Prix en devise locale, prix_eur seulement
si EUR (pas de conversion). duree_jours seulement si statut 'ok' (ou absent) ; sinon None + duree_texte.
Aucun prix par jour calculé ici (jamais pour DNK/NOR). Usage : python3 scripts/verse_europe_vague1.py [--ecrit]"""
import json, os, re, sys, unicodedata

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = '/opt/data/projets/sailingmore/1-direction/europe-vague1-222-offres.json'
S = R + '/projets/sailingmore/stages.json'
E = R + '/projets/sailingmore/ecoles.json'
NOMS = {'AUT': ('Autriche', 'de'), 'SWE': ('Suède', 'sv'), 'DNK': ('Danemark', 'da'),
        'NOR': ('Norvège', 'no'), 'CZE': ('Tchéquie', 'cs'), 'POL': ('Pologne', 'pl')}


def slug(n):
    n = unicodedata.normalize('NFKD', n).encode('ascii', 'ignore').decode().lower()
    return re.sub(r'[^a-z0-9]+', '-', n).strip('-')


src = json.load(open(SRC, encoding='utf-8'))
s = json.load(open(S, encoding='utf-8'))
e = json.load(open(E, encoding='utf-8'))
deja = {(o['ecole'], o['titre'], o.get('lien')) for o in s['offres']}
ec = {x['nom'] for x in e}
na = ne = 0
for iso, bloc in src['pays'].items():
    nom, lang = NOMS[iso]
    for o in bloc['offres']:
        if (o['ecole'], o['titre'], o['url']) in deja:
            continue
        st = o.get('duree_statut')
        jours = o.get('duree_jours') if st in (None, 'ok') else None
        r = {'ecole': o['ecole'], 'ecole_slug': slug(o['ecole']), 'ecole_pays': iso, 'ecole_pays_nom': nom,
             'langue': lang, 'langue_src': 'ecole', 'titre': o['titre'], 'lieu': '', 'region': o.get('region') or nom,
             'pays': iso, 'pays_nom': nom, 'niveau': o.get('niveau') or '', 'debut': '', 'fin': '',
             'prix': o['prix'], 'devise': o['devise'], 'prix_eur': round(o['prix']) if o['devise'] == 'EUR' else None,
             'prix_publie': True, 'duree_jours': jours, 'duree_texte': o.get('duree_texte') or '',
             'type': 'apprentissage', 'lien': o['url'], 'verifie': src.get('releve', '2026-11-26'),
             'source': 'europe-vague1'}
        if o.get('controle'):
            r['controle'] = o['controle']
        s['offres'].append(r); na += 1
        if o['ecole'] not in ec:
            e.append({'slug': slug(o['ecole']), 'nom': o['ecole'], 'pays': iso, 'langue': lang,
                      'urls': [o.get('page_ecole') or o['url']]})
            ec.add(o['ecole']); ne += 1
print(f'offres +{na}, écoles +{ne}, total offres {len(s["offres"])}, écoles {len(e)}')
if '--ecrit' in sys.argv:
    json.dump(s, open(S, 'w', encoding='utf-8'), ensure_ascii=False, separators=(', ', ': '))
    json.dump(e, open(E, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
