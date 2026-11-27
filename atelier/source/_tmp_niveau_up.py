import re, urllib.request

h = urllib.request.urlopen(urllib.request.Request('https://www.zeilschoolup.nl/zeilkampen/bootkeuze', headers={'User-Agent': 'Mozilla/5.0'}), timeout=20).read().decode('utf8', 'ignore')
t = re.sub(r'<[^>]+>', ' ', h)
t = re.sub(r'\s+', ' ', t)
for m in re.finditer(r'(Optimist|Laser Pico \dmans|Rs Feva|Rs Neo|Keus22|Polyvalk|Laser Vago)[^.]{0,160}?Zeilervaring: ?([^.]{0,40})', t):
    print(m.group(1), '|', m.group(2))
