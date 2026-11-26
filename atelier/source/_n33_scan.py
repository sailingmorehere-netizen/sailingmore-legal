"""Tâche 33 : télécharge (lecture seule) les pages des offres sans date, met le texte en cache, compte les motifs de date futurs."""
import json, os, re, html, urllib.request, collections, concurrent.futures as cf
OUT = 'tmp_n33'
os.makedirs(OUT, exist_ok=True)
d = json.load(open('projets/sailingmore/stages.json', encoding='utf-8'))['offres']
urls = sorted({e['lien'] for e in d if not e.get('debut') and e['lien']})


def nom(u):
    return OUT + '/' + re.sub(r'\W+', '_', u)[:120] + '.txt'


def get(u):
    p = nom(u)
    if os.path.exists(p):
        return u
    try:
        t = urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'}), timeout=20).read().decode('utf-8', 'replace')
        t = re.sub(r'(?s)<(script|style)[^>]*>.*?</\1>', ' ', t)
        t = re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', t)))
    except Exception as x:
        t = 'ERR ' + str(x)
    open(p, 'w').write(t)
    return u


with cf.ThreadPoolExecutor(8) as ex:
    list(ex.map(get, urls))
PAT = {
    'en': re.compile(r'\b\d{1,2}(?:st|nd|rd|th)? (?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\w* 2027|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\w* \d{1,2}(?:st|nd|rd|th)?,? 2027'),
    'num': re.compile(r'\b\d{1,2}[./]\d{1,2}[./]2027\b|\b2027-\d\d-\d\d\b'),
    'other': re.compile(r'\b\d{1,2}\.? (?:janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre|gennaio|febbraio|marzo|aprile|maggio|giugno|luglio|agosto|settembre|ottobre|novembre|dicembre|enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre|Januar|Februar|März|April|Mai|Juni|Juli|August|September|Oktober|November|Dezember) 2027', re.I),
}
c = collections.defaultdict(collections.Counter)
for e in d:
    if e.get('debut') or not e['lien']:
        continue
    t = open(nom(e['lien'])).read()
    for k, r in PAT.items():
        if r.search(t):
            c[e['ecole']][k] += 1
            break
    else:
        c[e['ecole']]['-'] += 1
for k, v in sorted(c.items(), key=lambda kv: -sum(x for a, x in kv[1].items() if a != '-')):
    if sum(x for a, x in v.items() if a != '-'):
        print(k, dict(v))
