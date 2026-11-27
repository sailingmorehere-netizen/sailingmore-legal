"""Télécharge (lecture seule) le texte des pages des offres sans niveau -> claude/niv59_cache/<hash>.txt"""
import re, html, json, os, hashlib, urllib.request
from concurrent.futures import ThreadPoolExecutor
o = json.load(open('projets/sailingmore/stages.json'))['offres']
D = 'claude/niv59_cache'
os.makedirs(D, exist_ok=True)
liens = sorted({e['lien'] for e in o if not e.get('niveau') and e['ecole_slug'] != 'cnv-versoix'})
def go(u):
    f = os.path.join(D, hashlib.md5(u.encode()).hexdigest() + '.txt')
    if os.path.exists(f):
        return
    try:
        t = urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'}), timeout=25).read().decode('utf8', 'ignore')
        t = re.sub(r'<(script|style)[\s\S]*?</\1>', ' ', t)
        t = re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', t)))
    except Exception as ex:
        t = 'ERR ' + str(ex)
    open(f, 'w').write(u + '\n' + t)
with ThreadPoolExecutor(8) as p:
    list(p.map(go, liens))
print(len(liens), 'pages')
