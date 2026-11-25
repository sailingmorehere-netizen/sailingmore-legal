import re, html
p = "/opt/data/cache/claude-nuit/travail/projets/sailingmore/site/cours.html"
s = open(p, encoding="utf-8").read()
a = s.find('id="entree-h-fr"')
b = s.find('id="entree-h-en"')
fr = s[a:b]
parts = re.split(r'(?=<[a-z]+[^>]*id="ch\d+-fr")', fr)
for part in parts:
    m = re.match(r'<[a-z]+[^>]*id="(ch\d+-fr)"', part)
    if not m:
        continue
    t = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", part, flags=re.S)
    t = html.unescape(re.sub(r"<[^>]+>", " ", t))
    print(m.group(1), "mots", len(t.split()), "svg", part.count("<svg"), "img", part.count("<img"), "exo", part.count("Exercice"))
