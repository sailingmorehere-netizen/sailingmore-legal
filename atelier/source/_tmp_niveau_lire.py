import sys, re, urllib.request

for u in sys.argv[1:]:
    try:
        req = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'})
        h = urllib.request.urlopen(req, timeout=20).read().decode('utf8', 'ignore')
    except Exception as x:
        print('==', u, 'ERREUR', x)
        h = None
    if h is None:
        pass
    else:
        t = re.sub(r'<(script|style).*?</\1>', ' ', h, flags=re.S)
        t = re.sub(r'<[^>]+>', ' ', t)
        t = re.sub(r'\s+', ' ', t)
        print('==', u, len(t))
        for m in list(re.finditer(r'.{90}(niveau|beginner|gevorderd|ervaring|beginners|vanaf).{90}', t, re.I))[:4]:
            print('  ', m.group(0))
