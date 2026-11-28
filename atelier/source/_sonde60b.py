import json, collections, urllib.request, concurrent.futures as cf
d = json.load(open('projets/sailingmore/stages.json'))
n = collections.Counter(e['lien'] for e in d['offres'])
c = [e for e in d['offres'] if not e.get('debut') and not e.get('hors_offre') and n[e['lien']] == 1]
def t(e):
    try:
        urllib.request.urlopen(urllib.request.Request(e['lien'], headers={'User-Agent': 'Mozilla/5.0'}), timeout=15).read(); return None
    except Exception as ex:
        return e['ecole_slug'], str(ex)[:50]
with cf.ThreadPoolExecutor(8) as ex:
    r = [x for x in ex.map(t, c) if x]
print(collections.Counter(r).most_common(15))
print(collections.Counter(e['ecole_slug'] for e in d['offres'] if not e.get('debut') and not e.get('hors_offre') and n[e['lien']] > 1).most_common(8))
