import re, html
p = "/opt/data/cache/claude-nuit/travail/projets/sailingmore/site/cours.html"
s = open(p, encoding="utf-8").read()
# bloc français : de entree-h-fr jusqu'à entree-h-en
a = s.find('id="entree-h-fr"')
b = s.find('id="entree-h-en"')
fr = s[a:b]
print("octets bloc fr:", len(fr))
txt = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", fr, flags=re.S)
txt = html.unescape(re.sub(r"<[^>]+>", " ", txt))
print("mots bloc fr:", len(txt.split()))
# titres h2/h3 hors génériques + attributs id de sections
for m in re.finditer(r'<h2[^>]*>(.*?)</h2>', fr, flags=re.S):
    print("H2:", re.sub(r"<[^>]+>", "", m.group(1)).strip()[:90])
ids = re.findall(r'<(?:section|div|article)[^>]*id="([^"]*(?:chap|cours|ch)[^"]*)"', fr)
print("ids:", ids[:60])
print("schemas svg:", len(re.findall(r"<svg", fr)), "img:", len(re.findall(r"<img", fr)))
print("exercices:", len(re.findall(r"<h3>Exercice", fr)))
