import json, re, urllib.request, html, collections
base = 'https://www.cnv.ch/fr/stages-voile/'
o = json.load(open('projets/sailingmore/stages.json'))['offres']
for slug in ['ado', 'adultes', 'optimist', 'rs-feva', 'parents-enfants', 'optimist-decouverte']:
    req = urllib.request.Request(base + slug, headers={'User-Agent': 'Mozilla/5.0'})
    t = urllib.request.urlopen(req, timeout=30).read().decode('utf-8', 'replace')
    t = re.sub(r'(?s)<(script|style).*?</\1>', ' ', t)
    t = html.unescape(re.sub(r'<[^>]+>', ' ', t))
    t = re.sub(r'\s+', ' ', t)
    i = t.find('Members: log in')
    seg = t[i:]
    rows = re.findall(r'(Beginner|Intermediate|Advanced|All levels / Advanced|All levels)\s+(\w+ 20\d\d)\s+(.*?)\s+CHF (\d+)', seg)
    print('#####', slug, len(rows), collections.Counter(r[0] for r in rows))
    for r in rows[:4]:
        print('   ', r)
    off = [e for e in o if e['lien'].endswith('/' + slug) and e['ecole_slug'] == 'cnv-versoix']
    print('  offres', len(off), collections.Counter(e.get('niveau') for e in off))
    for e in off[:3]:
        print('   ', e['titre'], e['debut'], e['fin'], e['prix'], e.get('niveau'))
