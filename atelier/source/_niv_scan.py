import json, re, urllib.request, html, collections, concurrent.futures as cf
o = json.load(open('projets/sailingmore/stages.json'))['offres']
m = [e for e in o if not e.get('niveau')]
liens = collections.Counter(e['lien'] for e in m)
KW = re.compile(r'(?i)\b(beginners?|d[ée]butants?|anf[äa]nger|principiant\w*|principiantes?|beginner|intermediate|interm[ée]diaire|fortgeschritten\w*|advanced|avanzad\w*|confirm[ée]s?|experienced|improver|niveau|level|stufe|livello|nivel)\b')
def f(u):
    try:
        req = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'})
        t = urllib.request.urlopen(req, timeout=20).read().decode('utf-8', 'replace')
        t = re.sub(r'(?s)<(script|style).*?</\1>', ' ', t)
        t = re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', t)))
        return u, collections.Counter(x.lower() for x in KW.findall(t))
    except Exception as ex:
        return u, str(ex)[:50]
print(len(liens))
with cf.ThreadPoolExecutor(8) as ex:
    for u, c in ex.map(f, list(liens)):
        print(liens[u], u, dict(c) if isinstance(c, collections.Counter) else c)
