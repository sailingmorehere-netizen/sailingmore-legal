# © 2026 Sailing More — tous droits réservés. All rights reserved.
"""Tâche 30 : lieu des offres de stages. À défaut du lieu trouvé sur la page (voir lieux_stages63.py), le port
d'attache de l'école — seulement pour les écoles à UN site de formation, vérifié sur leur page contact
(23-26/11/2026). Écoles multi-destinations (charters, flottilles) : jamais de repli. Offre située dans un autre
pays que l'école : jamais de repli. Écrit stages.json (source) ET stages-proches.json (sortie, mêmes lignes).
Usage : python3 scripts/lieu_stages30.py [--ecrit]"""
import json, os, sys

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
S = R + '/projets/sailingmore/stages.json'
P = R + '/projets/sailingmore/site/stages-proches.json'
# école -> (port d'attache, pays ISO3 de l'école)
PORTS = {
    'UKSA': ('Cowes', 'GBR'), 'Solent Boat Training': ('Southampton', 'GBR'), 'Urban Truant': ('Hamble', 'GBR'),
    'Plas Menai': ('Caernarfon', 'GBR'), 'Segelschule Rückenwind': ('Wolgast', 'DEU'),
    'Aquavitesse': ('Bruinisse', 'NLD'), 'Oltremare Vela': ('Lido degli Estensi', 'ITA'),
    'Club Nàutic Portitxol': ('Jávea', 'ESP'), 'Real Club de Mar': ('Palma de Mallorca', 'ESP'),
    'La Scuola della Vela': ('Porto Cervo', 'ITA'), 'Happy Sailing': ('Picton', 'CAN'),
    'Segelschule Grosse Freiheit': ('Berlin', 'DEU'), 'Segelschule Schluchsee': ('Schluchsee', 'DEU'),
    'Lagoo Segelschule Zürich': ('Zürichsee', 'CHE'), 'Segelschule Insel Reichenau': ('Reichenau', 'DEU'),
    'Zeilschool iSail': ('Hellevoetsluis', 'NLD'), 'Compagnia della Vela': ('Venise', 'ITA'),
    'De Bird': ('Heeg', 'NLD'), 'Zeilschool Ûp': ('Balk', 'NLD'), 'EZS Zeilschool': ('Enkhuizen', 'NLD'),
    'Segelschule Rehbach': ('Edersee', 'DEU'), 'Soleil Scuola Nautica': ('Santo Stefano al Mare', 'ITA'),
    'Sailway': ('Vigo', 'ESP'), 'Seven Seas School of Yachting': ('Palaio Faliro', 'GRC'),
    # sites uniques vérifiés le 26/11/2026 (page contact / page du cours) :
    'BH Marine': ('Weymouth', 'GBR'),  # adresse unique : Granby Industrial Estate, Weymouth
}
# école -> (port, pays, fragments d'URL) : repli seulement pour les pages de COURS à site unique ;
# les pages vacances / flottille / mer du Nord de ces écoles restent sans lieu.
PORTS_URL = {
    'Tip Top Sailing': ('Willemstad', 'NLD', ('/zeilschool/', '/inschrijven-zeilschool/')),  # Jachthaven de Batterij
    'Solent Sail': ('Gosport', 'GBR', ('/information/', '/sailing_trips/')),  # « Where we are » : Premier Marina, Gosport
    'Ultra Sailing': ('Split', 'HRV', ('/course/', '/ultra-sailing-school/', '/ispa-sailing-courses',
                                               '/family-sailing-program', '/regatta-schedule')),  # départ ACI Marina Split
}


def repli(ecole, pays, lien):
    p = PORTS.get(ecole)
    if p and pays == p[1]:
        return p[0]
    u = PORTS_URL.get(ecole)
    if u and pays == u[1] and any(f in (lien or '') for f in u[2]):
        return u[0]


def main():
    s = json.load(open(S, encoding='utf-8'))
    n1 = 0
    for o in s['offres']:
        v = None if o.get('lieu') else repli(o['ecole'], o.get('pays'), o.get('lien'))
        if v:
            o['lieu'] = v; n1 += 1
    lien = {}
    for o in s['offres']:  # clé (école, titre, pays) ; le lien le plus spécifique gagne si doublon
        lien.setdefault((o['ecole'], o['titre'], o.get('pays')), []).append(o.get('lien') or '')
    d = json.load(open(P, encoding='utf-8'))
    n2 = 0
    for r in d['o']:
        if r[5]:
            continue
        vs = {repli(r[4], r[12], l) for l in lien.get((r[4], r[3], r[12]), [''])}
        v = vs.pop() if len(vs) == 1 else None  # doublon de titre à liens différents : pas de repli
        if v:
            r[5] = v; n2 += 1
    ok = sum(1 for r in d['o'] if r[5])
    print(f'stages.json +{n1} ; stages-proches.json +{n2} -> {ok}/{len(d["o"])} ({ok/len(d["o"]):.0%})')
    if '--ecrit' in sys.argv:
        json.dump(s, open(S, 'w', encoding='utf-8'), ensure_ascii=False, separators=(', ', ': '))
        json.dump(d, open(P, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))


main()
