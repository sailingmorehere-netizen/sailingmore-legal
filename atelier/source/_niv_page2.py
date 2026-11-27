import sys, re, urllib.request, html
url = sys.argv[1]
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
t = urllib.request.urlopen(req, timeout=30).read().decode('utf-8', 'replace')
t = re.sub(r'(?s)<(script|style).*?</\1>', ' ', t)
t = html.unescape(re.sub(r'<[^>]+>', ' ', t))
t = re.sub(r'\s+', ' ', t)
i = t.find('Niveau')
print(t[:700]); print('====')
print(t[i:i+2500])
