import json, re, collections, html, urllib.request, concurrent.futures as cf
d = json.load(open('projets/sailingmore/stages.json'))
n = collections.Counter(e['lien'] for e in d['offres'])
c = [e for e in d['offres'] if not e.get('debut') and not e.get('hors_offre') and n[e['lien']] == 1]
print(collections.Counter(e['ecole_slug'] for e in c).most_common(12))
def t(e):
    try:
        x = urllib.request.urlopen(urllib.request.Request(e['lien'], headers={'User-Agent': 'Mozilla/5.0'}), timeout=15).read().decode('utf8', 'ignore')
        x = re.sub(r'<(script|style)[\s\S]*?</\1>', ' ', x)
        x = re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', x)))
        return e['ecole_slug'], re.findall(r'.{25}(?:20\d\d|\d{1,2}[./]\d{1,2}[./]).{25}', x)[:2]
    except Exception:
        return e['ecole_slug'], 'ERR'
with cf.ThreadPoolExecutor(8) as ex:
    for s, m in list(ex.map(t, c[:90]))[::3]:
        print(s, m)
