import re, urllib.request
URLS = ['https://www.oltremare.it/calendario-corsi-e-allenamenti/',
        'https://www.oltremare.it/campus-vela-ragazzi-2027/',
        'https://www.oltremare.it/leffetto-che-fa-weekend-vela-adriatico-2027/',
        'https://tiptopsailing.nl/zeilvakanties/flottielje-zeilen/',
        'https://www.zeilschoolup.nl/zeilkampen',
        'https://www.compagniadellavela.org/events/la-scuola-vela-ragazzi-adulti/']
MOIS = r'(gennaio|febbraio|marzo|aprile|maggio|giugno|luglio|agosto|settembre|ottobre|novembre|dicembre|januari|februari|maart|mei|juni|juli|augustus|oktober|december)'
for u in URLS:
    print('=====', u)
    try:
        h = urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'}), timeout=20).read().decode('utf-8', 'replace')
    except Exception as ex:
        print('ERR', ex); continue
    t = re.sub(r'<(script|style).*?</\1>', ' ', h, flags=re.S)
    t = re.sub(r'<[^>]+>', '\n', t)
    for l in dict.fromkeys(x.strip() for x in t.split('\n')):
        if re.search(MOIS, l, re.I) and re.search(r'\d', l):
            print(l[:200])
