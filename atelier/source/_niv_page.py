import sys, re, urllib.request, html
url = sys.argv[1]
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
t = urllib.request.urlopen(req, timeout=30).read().decode('utf-8', 'replace')
t = re.sub(r'(?s)<(script|style).*?</\1>', ' ', t)
t = html.unescape(re.sub(r'<[^>]+>', ' ', t))
t = re.sub(r'\s+', ' ', t)
print(len(t))
for m in re.finditer(r'(?i)niveau|d[ée]butant|confirm|perfection|interm[ée]diaire|beginner|advanced|anf[äa]nger', t):
    print('...', t[max(0, m.start()-100):m.end()+100])
