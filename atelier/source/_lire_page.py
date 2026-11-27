import re, sys, urllib.request
for u in sys.argv[1:]:
    print('===', u)
    try:
        t = urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'}), timeout=25).read().decode('utf-8', 'replace')
    except Exception as e:
        print('ERREUR', e)
        continue
    t = re.sub(r'<(script|style)[^>]*>.*?</\1>', '', t, flags=re.S)
    t = re.sub(r'<[^>]+>', ' ', t)
    t = re.sub(r'\s+', ' ', t)
    print(len(t))
    for m in re.findall(r'.{0,150}(?:Dauer|Termin|Tage|Uhr|duration|[Dd]ays?\b|hours|Datum).{0,200}', t)[:10]:
        print('-', m)
