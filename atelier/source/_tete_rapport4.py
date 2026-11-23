import re
D = "/opt/data/cache/claude-nuit/travail/"
for nom, f in (("nouvelle", D + "projets/sailingmore/site/lexique.html"), ("ligne", D + "sortie-test/enligne-lexique.html")):
    h = open(f, encoding="utf-8").read()
    i = h.index("<body")
    b = h[i:i + 60000]
    print(nom, "classes de barre:", re.findall(r'<(?:header|nav|div)[^>]*class="(?:entete|barre|site-bar|topbar)[^"]*"', b)[:5])
    print(nom, "id langues:", h.count('id="langues"'), h.count('id="lng-sel"'), "nav:", h.count("<nav"), "header:", h.count("<header"))
    print(nom, re.sub(r"\s+", " ", h[i:i + 700]))
    print()
