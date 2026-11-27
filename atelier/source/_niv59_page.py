import re, sys, html, urllib.request
u = sys.argv[1]
pat = sys.argv[2] if len(sys.argv) > 2 else r'beginner|débutant|niveau|level|intermedi|gevorderd|beginners|anf[aä]nger|fortgeschritten|principiante|livello'
t = urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'}), timeout=30).read().decode('utf8', 'ignore')
t = re.sub(r'<(script|style)[\s\S]*?</\1>', ' ', t)
t = re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', t)))
print(len(t))
n = 0
for m in re.finditer(pat, t, re.I):
    print('...', t[max(0, m.start() - 100):m.end() + 100])
    n += 1
    if n > 12:
        break
