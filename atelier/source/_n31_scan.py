"""Lecture seule : cherche des dates (2026-11-26 -> 2027) dans la page de chaque offre sans debut."""
import json, re, sys, urllib.request, concurrent.futures as cf
S = json.load(open('projets/sailingmore/stages.json', encoding='utf-8'))['offres']
MOIS = {}
for i, ms in enumerate(['jan|janv|january|januari|janvier|januar|enero|gennaio', 'feb|fév|fev|february|februari|février|februar|febrero|febbraio',
    'mar|march|maart|mars|märz|marzo', 'apr|april|avril|abril|aprile', 'may|mei|mai|mayo|maggio', 'jun|june|juni|juin|junio|giugno',
    'jul|july|juli|juillet|julio|luglio', 'aug|august|augustus|août|agosto', 'sep|sept|september|septembre|septiembre|settembre',
    'oct|october|oktober|octobre|octubre|ottobre', 'nov|november|novembre|noviembre', 'dec|december|décembre|dezember|diciembre|dicembre'], 1):
    for m in ms.split('|'):
        MOIS[m] = i
RX_ISO = re.compile(r'(?<!\d)(202[67])-(\d\d)-(\d\d)(?!\d)')
RX_TXT = re.compile(r'(?<!\d)(\d{1,2})(?:st|nd|rd|th|er)?\.?\s+([A-Za-zéûä]{3,10})\.?,?\s+(202[67])', re.I)
RX_FR = re.compile(r'(?<!\d)(\d{1,2})[/.](\d{1,2})[/.](202[67])(?!\d)')


def dates(html):
    t = re.sub(r'<script.*?</script>|<style.*?</style>', ' ', html, flags=re.S)
    t = re.sub(r'<[^>]+>', ' ', t)
    out = set()
    for m in RX_ISO.finditer(html):
        out.add(m.group(0))
    for d, mo, y in RX_TXT.findall(t):
        k = MOIS.get(mo.lower())
        if k:
            out.add('%s-%02d-%02d' % (y, k, int(d)))
    for d, mo, y in RX_FR.findall(t):
        if 1 <= int(mo) <= 12 and 1 <= int(d) <= 31:
            out.add('%s-%02d-%02d' % (y, int(mo), int(d)))
    return sorted(x for x in out if '2026-11-26' <= x <= '2027-12-31')


def get(e):
    try:
        r = urllib.request.Request(e['lien'], headers={'User-Agent': 'Mozilla/5.0'})
        h = urllib.request.urlopen(r, timeout=15).read(600000).decode('utf-8', 'ignore')
        return e, dates(h)
    except Exception as x:
        return e, 'ERR'


todo = [e for e in S if not e.get('debut')]
res = {}
with cf.ThreadPoolExecutor(12) as ex:
    for e, d in ex.map(get, todo):
        res[(e['ecole'], e['titre'])] = d
json.dump({'|'.join(k): v for k, v in res.items()}, open('scripts/_n31_scan.json', 'w'), ensure_ascii=False, indent=0)
import collections
c = collections.Counter(k[0] for k, v in res.items() if v and v != 'ERR')
print(sum(c.values()), c.most_common())
print('ERR', sum(1 for v in res.values() if v == 'ERR'))
