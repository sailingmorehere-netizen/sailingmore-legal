import re, os
d = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "projets/sailingmore/site/")
r = open(d + "regates.html", encoding="utf-8").read()
b = re.search(r'<script[^>]*ld\+json[^>]*>(.*?)</script>', r, re.S).group(1)
for m in re.finditer(r'Monde Dragon', b):
    print(b[max(0, m.start() - 60):m.start() + 500])
print(len(b), b.count('"SportsEvent"'))
for m in re.finditer(r'"name":"([^"]*)","startDate":"[^"]*","endDate":"[^"]*","location":\{"@type":"Place","name":"[^"]*","address":\{"@type":"PostalAddress","addressLocality":"[^"]*","addressCountry":"(FR|)"', b):
    pass
