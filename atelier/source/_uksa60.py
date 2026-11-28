import json, re, html, urllib.request, concurrent.futures as cf
d = json.load(open('projets/sailingmore/stages.json', encoding='utf-8'))
idx = [i for i, e in enumerate(d['offres']) if e['ecole'] == 'UKSA' and e.get('prix_eur') in (None, '', 0) and not e.get('hors_offre')]

def f(i):
    try:
        rq = urllib.request.Request(d['offres'][i]['lien'], headers={'User-Agent': 'Mozilla/5.0 (lecture)'})
        t = urllib.request.urlopen(rq, timeout=25).read(900000).decode('utf-8', 'replace')
    except Exception as ex:
        return i, str(ex)[:30], []
    t = re.sub(r'(?is)<(script|style|noscript).*?</\1>', ' ', t)
    t = re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', t)))
    return i, '', [(m.group(1), t[max(0, m.start() - 60):m.start()].strip()) for m in re.finditer(r'(?:[Ff]rom|[Pp]rice:?)\s?£\s?([\d,]+)', t)]

with cf.ThreadPoolExecutor(4) as ex:
    for i, err, v in ex.map(f, idx):
        if v or err:
            print(i, d['offres'][i]['titre'][:60], err, len(v))
            for p, c in v[:3]:
                print('      £', p, '<-', c[-60:])
