import json, re, urllib.request, html, sys
o = json.load(open('projets/sailingmore/stages.json'))['offres']
for e in o:
    if e['ecole_slug'] == sys.argv[1] and not e.get('niveau'):
        print(e['titre'][:90], '|', e['lien'])
u = sys.argv[2]
t = urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'}), timeout=30).read().decode('utf8', 'ignore')
t = re.sub(r'(?s)<(script|style).*?</\1>', ' ', t)
t = re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', t)))
for m in re.finditer(r'(?i)beginner|intermediate|advanced|improver|principiants|anf[äa]nger|fortgeschritten', t):
    print('..', t[max(0, m.start()-120):m.end()+120])
