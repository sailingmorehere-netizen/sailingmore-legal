"""Sonde (lecture seule) : pour chaque école sans lieu, lit la page d'accueil et affiche titre, meta et lignes d'adresse."""
import json, os, re, html, urllib.request, urllib.parse, concurrent.futures as cf
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
L = json.load(open(R + '/projets/sailingmore/stages.json'))['offres']
H = {}
for o in L:
    if not o.get('lieu'):
        u = urllib.parse.urlparse(o['lien'])
        H.setdefault(o['ecole'], u.scheme + '://' + u.netloc + '/')
AD = re.compile(r'(address|adres|adresse|indirizzo|direcci|anschrift|stra(ß|ss)e|straat|marina|harbou?r|haven|hafen|porto|puerto|port de|base)', re.I)


def lire(u):
    try:
        with urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0 (lecture)'}), timeout=15) as r:
            return r.read(300000).decode('utf-8', 'ignore')
    except Exception as e:
        return 'ERR ' + str(e)


def un(it):
    e, u = it
    p = lire(u)
    t = re.sub(r'\s+', ' ', html.unescape(re.sub(r'<(script|style)[^>]*>.*?</\1>', ' ', p, flags=re.S | re.I)))
    t = re.sub(r'<[^>]+>', ' ', t)
    t = re.sub(r'\s+', ' ', t)
    m = re.findall(r'.{0,60}(?:address|adres|adresse|indirizzo|direcci[oó]n|anschrift|marina|harbou?r|haven|hafen|porto |puerto|base ).{0,80}', t, re.I)
    return e, u, p[:60] if p.startswith('ERR') else '', m[:4]


with cf.ThreadPoolExecutor(8) as ex:
    for e, u, err, m in ex.map(un, H.items()):
        print('##', e, u, err)
        for x in m:
            print('   ', x)
