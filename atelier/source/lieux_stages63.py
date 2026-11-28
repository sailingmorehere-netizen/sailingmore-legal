# © 2026 Sailing More — tous droits réservés. All rights reserved.
"""Tâche 63 : renseigne `lieu` des offres de stages sans lieu quand la page du lien (titre, URL, <title>, <h1>,
meta description) nomme un port ou une ville connus. Jamais la ville de l'école par défaut.
Usage : python3 scripts/lieux_stages63.py [--ecrit]   (sans --ecrit : simulation)"""
import json, os, re, sys, urllib.request, concurrent.futures as cf, html, unicodedata

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(R, 'projets/sailingmore/stages.json')

# nom affiché -> motifs (sans accents, minuscules)
LIEUX = {
 'Poltu Quatu': ['poltu quatu'], 'Porto Cervo': ['porto cervo'], 'Argentario': ['argentario'],
 'Ibiza': ['ibiza'], 'Formentera': ['formentera'], 'Palma de Mallorca': ['palma de mallorca', 'palma de majorque'],
 'Mallorca': ['mallorca', 'majorque'], 'Menorca': ['menorca'], 'Barcelone': ['barcelona', 'barcelone'],
 'Valence': ['valencia'], 'Alicante': ['alicante'], 'Huelva': ['huelva'], 'Cadix': ['cadiz'], 'Malaga': ['malaga'],
 'Weymouth': ['weymouth'], 'Portland': ['portland'], 'Poole': ['poole'], 'Southampton': ['southampton'],
 'Hamble': ['hamble'], 'Gosport': ['gosport'], 'Portsmouth': ['portsmouth'], 'Plymouth': ['plymouth'],
 'Falmouth': ['falmouth'], 'Cowes': ['cowes'], 'Lymington': ['lymington'], 'Brighton': ['brighton'],
 'Torquay': ['torquay'], 'Dartmouth': ['dartmouth'], 'Largs': ['largs'], 'Oban': ['oban'], 'Pwllheli': ['pwllheli'],
 'Neyland': ['neyland'], 'Milford Haven': ['milford haven'], 'Gibraltar': ['gibraltar'],
 'Lefkas': ['lefkas', 'lefkada'], 'Athènes': ['athens', 'athenes', 'athen'], 'Corfou': ['corfu', 'corfou'],
 'Rhodes': ['rhodes', 'rodos'], 'Kos': [r'\bkos\b'], 'Athens Alimos': ['alimos'], 'Preveza': ['preveza'],
 'Vouliagmeni': ['vouliagmeni'], 'Sporades': ['sporades'], 'Cyclades': ['cyclades', 'kykladen'],
 'Skiathos': ['skiathos'], 'Paros': [r'\bparos\b'], 'Naxos': [r'\bnaxos\b'], 'Mykonos': ['mykonos'],
 'Split': [r'\bsplit\b'], 'Dubrovnik': ['dubrovnik'], 'Zadar': ['zadar'], 'Šibenik': ['sibenik'],
 'Trogir': ['trogir'], 'Pula': [r'\bpula\b'], 'Biograd': ['biograd'], 'Kornati': ['kornati'], 'Murter': ['murter'],
 'Marina Kremik': ['kremik'], 'Primošten': ['primosten'],
 'Hellevoetsluis': ['hellevoetsluis'], 'Scheveningen': ['scheveningen'], 'Medemblik': ['medemblik'],
 'Lelystad': ['lelystad'], 'Enkhuizen': ['enkhuizen'], 'Harlingen': ['harlingen'], 'Lemmer': [r'\blemmer\b'],
 'Loosdrecht': ['loosdrecht'], 'Kaag': [r'kagerplassen', r'\bkaag\b'], 'Veere': [r'\bveere\b'], 'Zierikzee': ['zierikzee'],
 'Kamperland': ['kamperland'], 'Veerse Meer': ['veerse meer'], 'Grevelingen': ['grevelingen'], 'Brouwersdam': ['brouwersdam'],
 'IJsselmeer': ['ijsselmeer'], 'Wiesbaden': ['wiesbaden'],
 'Berlin': [r'\bberlin\b'], 'Wannsee': ['wannsee'], 'Hamburg': [r'\bhamburg\b'], 'Kiel': [r'\bkiel\b'],
 'Flensburg': ['flensburg'], 'Warnemünde': ['warnemunde'], 'Bodensee': ['bodensee'], 'Überlingen': ['uberlingen'],
 'Konstanz': ['konstanz'], 'Reichenau': ['reichenau'], 'Schluchsee': ['schluchsee'], 'Zürichsee': ['zurichsee', 'zuerichsee'],
 'Zurich': [r'\bzurich\b', r'\bzuerich\b'], 'Genf': [r'\bgenf\b', 'geneve'], 'Neuenburgersee': ['neuenburgersee'],
 'Starnberger See': ['starnberger'], 'Chiemsee': ['chiemsee'], 'Ammersee': ['ammersee'], 'Steinhuder Meer': ['steinhuder'],
 'Müritz': ['muritz'], 'Plau am See': ['plau am see'], 'Rehbach': [],
 'Marseille': ['marseille'], 'La Rochelle': ['la rochelle'], 'Lorient': ['lorient'], 'Brest': [r'\bbrest\b'],
 'Les Glénans': ['glenan'], 'Saint-Malo': ['saint-malo', 'st malo'], 'Cherbourg': ['cherbourg'], 'Hyères': ['hyeres'],
 'Toulon': [r'\btoulon\b'], 'Antibes': ['antibes'], 'Nice': [r'\bnice\b'], 'Ajaccio': ['ajaccio'], 'Bastia': ['bastia'],
 'Port-Camargue': ['port camargue', 'port-camargue'], 'Arcachon': ['arcachon'], 'Carnac': ['carnac'], 'Quiberon': ['quiberon'],
 'Martinique': ['martinique'], 'Guadeloupe': ['guadeloupe'], 'Antilles': ['antilles'], 'Canaries': ['canaries', 'canary'],
 'Tenerife': ['tenerife'], 'Lanzarote': ['lanzarote'], 'Madère': ['madeira'], 'Açores': ['acores', 'azores'],
 'Sardaigne': ['sardinia', 'sardegna', 'sardaigne'], 'Sicile': ['sicilia', 'sicily', 'sicile'], 'Eolie': ['eolie', 'aeolian'],
 'Gênes': ['genova', 'genoa'], 'Naples': ['napoli', 'naples'], 'Rome': [r'\broma\b'], 'Lerici': ['lerici'], 'Portofino': ['portofino'],
 'La Spezia': ['la spezia'], 'Livourne': ['livorno'], 'Venise': ['venezia', 'venice'], 'Lac de Garde': ['lago di garda', 'gardasee'],
 'Lac Majeur': ['lago maggiore'], 'Lac de Côme': ['lago di como'], 'Sardegna Olbia': ['olbia'], 'Cagliari': ['cagliari'],
 'Lisbonne': ['lisboa', 'lisbon', 'lisbonne'], 'Cascais': ['cascais'], 'Algarve': ['algarve'], 'Lagos': [r'\blagos\b'],
 'Malte': [r'\bmalta\b', r'\bmalte\b'], 'Antigua': ['antigua'], 'Grenade': ['grenada'], 'Tortola': ['tortola'],
 'Newport': [r'\bnewport\b'], 'Annapolis': ['annapolis'], 'San Diego': ['san diego'], 'Vancouver': ['vancouver'],
 'Toronto': ['toronto'], 'Kingston': [r'\bkingston\b'], 'Miami': [r'\bmiami\b'], 'Key West': ['key west'],
 'Sydney': [r'\bsydney\b'], 'Phuket': ['phuket'], 'Istanbul': ['istanbul'], 'Marmaris': ['marmaris'], 'Göcek': ['gocek'], 'Bodrum': ['bodrum'],
 'Fethiye': ['fethiye'], 'Pagasétique': [], 'Tallinn': ['tallinn'], 'Stockholm': ['stockholm'], 'Copenhague': ['copenhagen', 'kobenhavn'],
}
PAT = {n: re.compile('|'.join(p), re.I) for n, p in LIEUX.items() if p}


def norm(s):
    s = html.unescape(s)
    return unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode().lower()


def lire(url):
    try:
        rq = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (lecture; sailingmore)'})
        with urllib.request.urlopen(rq, timeout=15) as r:
            b = r.read(400000)
        return b.decode('utf-8', 'ignore')
    except Exception:
        return ''


def zones(page):
    t = re.search(r'<title[^>]*>(.*?)</title>', page, re.S | re.I)
    h = re.findall(r'<h1[^>]*>(.*?)</h1>', page, re.S | re.I)
    m = re.search(r'<meta[^>]+name=["\']description["\'][^>]+content=["\']([^"\']*)', page, re.I)
    z = [t.group(1) if t else ''] + h[:2] + [m.group(1) if m else '']
    return norm(re.sub(r'<[^>]+>', ' ', ' | '.join(z)))


def trouve(txt):
    """lieu unique nommé dans txt, sinon None (deux lieux = ambigu)."""
    hits = [n for n, p in PAT.items() if p.search(txt)]
    # un nom englobé par un autre (Mallorca / Palma de Mallorca) ne compte qu'une fois
    hits = [h for h in hits if not any(h != o and norm(h) in norm(o) for o in hits)]
    return hits[0] if len(hits) == 1 else None


REJET = {('Seven Seas School of Yachting', 'Athènes'), ('Blue Spirit', 'Valence'), ('Solent Boat Training', 'Split'),
         ('Lagoo Segelschule Zürich', 'Split'), ('Ultra Sailing', 'Split'), ('Sailing Xperience', 'Athènes'),
         ('Sailing Virgins', 'Athènes'), ('La Scuola della Vela', 'Poltu Quatu'), ('Seafarer Sailing', 'Cyclades'),
         ('Aquavitesse', 'Grevelingen')}


def un(e):
    n, s = un0(e)
    return (None, '') if (e['ecole'], n) in REJET else (n, s)


def un0(e):
    base =norm(e['titre'] + ' ' + e['lien'].split('/', 3)[-1].replace('-', ' ').replace('/', ' '))
    n = trouve(base)
    if n:
        return n, 'titre/url'
    n = trouve(zones(lire(e['lien'])))
    return (n, 'page') if n else (None, '')


def main():
    d = json.load(open(P, encoding='utf-8'))
    L = d['offres']
    m = [e for e in L if not e.get('lieu')]
    with cf.ThreadPoolExecutor(12) as ex:
        res = list(ex.map(un, m))
    n = 0
    for e, (lieu, src) in zip(m, res):
        if lieu:
            n += 1
            print(f"{e['ecole'][:22]:22} | {e['titre'][:48]:48} -> {lieu} ({src})")
            if '--ecrit' in sys.argv:
                e['lieu'] = lieu
    print('remplis', n, 'sur', len(m), '-> restent', len(m) - n)
    if '--ecrit' in sys.argv:
        json.dump(d, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)


if __name__ == '__main__':
    main()
