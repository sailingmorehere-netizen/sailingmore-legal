"""Tâche 33 : Solent Boat Training — première session à venir publiée dans « Dates Available »."""
import json, re, sys, html, urllib.request, datetime as dt
EC = sys.argv[1] if len(sys.argv) > 1 else 'Solent Boat Training'
M = {m: i + 1 for i, m in enumerate('Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec'.split())}
RE = re.compile(r'\b(?:Mon|Tue|Wed|Thu|Fri|Sat|Sun)\w* (\d{1,2})(?:st|nd|rd|th)? (Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\w* (\d{4})'
                r'(?: - (?:Mon|Tue|Wed|Thu|Fri|Sat|Sun)\w* (\d{1,2})(?:st|nd|rd|th)? (Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\w*(?: (\d{4}))?)?')
AUJ = dt.date(2026, 11, 26)


def page(u):
    t = urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'}), timeout=25).read().decode('utf-8', 'replace')
    t = re.sub(r'(?s)<(script|style)[^>]*>.*?</\1>', ' ', t)
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', t)))


def premiere(t):
    i = t.find('Dates Available')
    if i < 0:
        return None
    m = RE.search(t, i)
    if not m:
        return None
    a = dt.date(int(m[3]), M[m[2]], int(m[1]))
    if m[4]:
        y = int(m[6]) if m[6] else a.year
        b = dt.date(y, M[m[5]], int(m[4]))
        if b < a:
            b = dt.date(y + 1, M[m[5]], int(m[4]))
    else:
        b = a
    return (a, b) if a >= AUJ else None


if __name__ == '__main__':
    F = 'projets/sailingmore/stages.json'
    d = json.load(open(F, encoding='utf-8'))
    cache = {}
    n = 0
    for e in d['offres']:
        if e['ecole'] != EC or e.get('debut'):
            continue
        u = e['lien']
        if u not in cache:
            try:
                cache[u] = premiere(page(u))
            except Exception as x:
                print('ERR', u, x)
                cache[u] = None
        r = cache[u]
        if r:
            e['debut'], e['fin'] = r[0].isoformat(), r[1].isoformat()
            e['duree_jours'] = (r[1] - r[0]).days + 1
            n += 1
    print('remplis', n, 'sur pages', sum(1 for v in cache.values() if v), '/', len(cache))
    json.dump(d, open(F, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
