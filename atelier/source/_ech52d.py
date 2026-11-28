import re, html, urllib.request, sys
for u in sys.argv[1:]:
    r = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'})
    t = urllib.request.urlopen(r, timeout=20).read().decode('utf8', 'ignore')
    t = re.sub(r'<(script|style)[\s\S]*?</\1>', ' ', t)
    t = re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', t)))
    print('==', u, len(t))
    for mm in list(re.finditer(r'.{60}20(26|27).{80}', t))[:6]:
        print('   ', mm.group(0))
