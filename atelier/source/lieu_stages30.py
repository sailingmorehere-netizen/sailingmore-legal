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
}


def main():
    s = json.load(open(S, encoding='utf-8'))
    n1 = 0
    for o in s['offres']:
        p = PORTS.get(o['ecole'])
        if p and not o.get('lieu') and o.get('pays') == p[1]:
            o['lieu'] = p[0]; n1 += 1
    d = json.load(open(P, encoding='utf-8'))
    n2 = 0
    for r in d['o']:
        p = PORTS.get(r[4])
        if p and not r[5] and r[12] == p[1]:
            r[5] = p[0]; n2 += 1
    ok = sum(1 for r in d['o'] if r[5])
    print(f'stages.json +{n1} ; stages-proches.json +{n2} -> {ok}/{len(d["o"])} ({ok/len(d["o"]):.0%})')
    if '--ecrit' in sys.argv:
        json.dump(s, open(S, 'w', encoding='utf-8'), ensure_ascii=False, separators=(', ', ': '))
        json.dump(d, open(P, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))


main()
