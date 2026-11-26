import re, sys, urllib.request, html
for u in sys.argv[1:]:
    try:
        t = urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'}), timeout=25).read().decode('utf-8', 'replace')
    except Exception as x:
        print('ERR', u, x)
        continue
    t = re.sub(r'(?s)<(script|style)[^>]*>.*?</\1>', ' ', t)
    t = html.unescape(re.sub(r'<[^>]+>', ' ', t))
    t = re.sub(r'\s+', ' ', t)
    ms = [m.start() for m in re.finditer(r'(?i)\b(next (course|date)|start date|dates?|202[67])\b', t)][:4]
    print('##', u, len(t))
    for s in ms:
        print('  ', t[max(0, s - 60):s + 160])
