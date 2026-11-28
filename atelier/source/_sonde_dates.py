import sys, re, urllib.request, html
url = sys.argv[1]
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (lecture)'})
try:
    t = urllib.request.urlopen(req, timeout=20).read().decode('utf-8', 'replace')
except Exception as e:
    print('ERR', e); sys.exit(0)
t = re.sub(r'(?s)<(script|style).*?</\1>', ' ', t)
t = html.unescape(re.sub(r'<[^>]+>', ' ', t))
t = re.sub(r'\s+', ' ', t)
print(len(t))
for m in re.finditer(r'(20(26|27)-\d\d-\d\d|\d{1,2}[./]\d{1,2}[./]20(26|27)|\d{1,2}(st|nd|rd|th)? (of )?(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*( 20(26|27))?)', t):
    s = max(0, m.start() - 60)
    print('..', t[s:m.end() + 60])
