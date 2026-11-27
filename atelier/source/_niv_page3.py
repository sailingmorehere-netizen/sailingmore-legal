import sys, re, urllib.request, html
url = sys.argv[1]
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
t = urllib.request.urlopen(req, timeout=30).read().decode('utf-8', 'replace')
t = re.sub(r'(?s)<(script|style).*?</\1>', ' ', t)
t = html.unescape(re.sub(r'<[^>]+>', ' ', t))
t = re.sub(r'\s+', ' ', t)
i = t.find('Ados') if 'ado' in url.split('/')[-1] else 0
j = t.find('Water-skiing', 700)
print(t[900:3600])
