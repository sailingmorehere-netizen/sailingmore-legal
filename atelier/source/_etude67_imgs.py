import re
p = "/opt/data/cache/claude-nuit/travail/projets/sailingmore/site/cours.html"
s = open(p, encoding="utf-8").read()
a = s.find('id="entree-h-fr"'); b = s.find('id="entree-h-en"')
fr = s[a:b]
for ch in (9, 10, 13, 14):
    i = fr.find('id="ch%d-fr"' % ch)
    j = fr.find('id="ch%d-fr"' % (ch + 1))
    seg = fr[i:j if j > 0 else None]
    srcs = re.findall(r'<img[^>]*src="([^"]+)"', seg)
    print("ch", ch, len(srcs), srcs[:5], "...", srcs[-2:])
    print("   svg ids/titles:", re.findall(r'<svg[^>]*aria-label="([^"]+)"', seg)[:3])
