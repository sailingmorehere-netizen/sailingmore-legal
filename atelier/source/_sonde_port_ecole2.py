"""Sonde 2 (lecture seule) : cherche un code postal + ville sur l'accueil et /contact des écoles restantes."""
import re, html, urllib.request, concurrent.futures as cf
E = {'De Bird': 'https://www.debird.nl/', 'Zeilschool Ûp': 'https://www.zeilschoolup.nl/', 'EZS': 'https://www.ezs.nl/',
     'Soleil': 'https://www.soleil-scuola-nautica.it/', 'Sailway': 'https://sailway.es/', 'Rehbach': 'https://segelschule-rehbach.de/',
     'BH Marine': 'https://www.bhmarine.co.uk/', 'Tip Top': 'https://tiptopsailing.nl/', 'Slowlife': 'https://ecoledecroisiereslowlife.com/',
     'Reichenau': 'https://segelschule-insel-reichenau.de/', 'Solent Sail': 'https://solentsail.com/', 'SevenSeas': 'https://7seassailing.com/',
     'Blue Spirit': 'http://bluespirit.es/', 'Compagnia': 'https://www.compagniadellavela.org/', 'Plas Menai': 'https://plasmenai.wales/',
     'UKSA': 'https://uksa.org/', 'SBT': 'https://www.solentboattraining.co.uk/'}
PC = re.compile(r'.{0,50}(?:\b\d{4} ?[A-Z]{2}\b|\b\d{5}\b|\b[A-Z]{1,2}\d{1,2}[A-Z]? ?\d[A-Z]{2}\b).{0,40}')


def lire(u):
    try:
        with urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0 (lecture)'}), timeout=15) as r:
            return r.read(300000).decode('utf-8', 'ignore')
    except Exception as e:
        return ''


def un(it):
    n, u = it
    out = []
    for suf in ('', 'contact', 'contact/', 'contacto', 'contatti', 'kontakt'):
        p = lire(u + suf)
        t = re.sub(r'<(script|style)[^>]*>.*?</\1>', ' ', p, flags=re.S | re.I)
        t = re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', t)))
        out += PC.findall(t)[:3]
        if len(out) >= 3:
            break
    return n, out[:3]


with cf.ThreadPoolExecutor(8) as ex:
    for n, o in ex.map(un, E.items()):
        print('##', n)
        for x in o:
            print('   ', x)
