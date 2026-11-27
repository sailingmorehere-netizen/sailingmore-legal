import re, sys, html, json, urllib.request, collections
o = json.load(open('projets/sailingmore/stages.json'))['offres']
pat = re.compile(r'beginner|débutant|niveau|level|intermedi|gevorderd|beginners|anf[aä]nger|fortgeschritten|principiante|livello|nivel|advanced|confirm', re.I)
liens = collections.OrderedDict()
for e in o:
    if not e.get('niveau') and e['ecole_slug'] not in ('cnv-versoix',):
        liens.setdefault(e['ecole_slug'], collections.Counter())[e['lien']] += 1
for s in sys.argv[1:]:
    for u, n in liens[s].most_common(4):
        try:
            t = urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'}), timeout=25).read().decode('utf8', 'ignore')
        except Exception as ex:
            print(s, n, u, 'ERR', ex)
            continue
        t = re.sub(r'<(script|style)[\s\S]*?</\1>', ' ', t)
        t = re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', t)))
        hits = [t[max(0, m.start() - 60):m.end() + 60] for m in pat.finditer(t)]
        print('##', s, n, u, len(t), len(hits))
        for h in hits[:4]:
            print('   ', h)
