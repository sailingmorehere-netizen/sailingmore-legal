import re, urllib.request
h = urllib.request.urlopen(urllib.request.Request('https://solentsail.com/sailing_trips/', headers={'User-Agent': 'Mozilla/5.0'}), timeout=20).read().decode('utf8', 'ignore')
t = re.sub(r'<[^>]+>', ' ', re.sub(r'<(script|style).*?</\1>', ' ', h, flags=re.S))
t = ' '.join(t.split())
for m in list(re.finditer(r'(Gosport|Hamble|Lymington|Cowes|Southampton|Portsmouth|Poole|Brighton|France|Cherbourg|depart|leave)', t))[:10]:
    print(t[max(0, m.start() - 70):m.start() + 90])
