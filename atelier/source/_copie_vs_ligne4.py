import re, hashlib
D = "/opt/data/cache/claude-nuit/travail/"
for p in ["regles-de-course", "stages", "lexique"]:
    a = open(D + "projets/sailingmore/site/" + p + ".html", encoding="utf-8").read()
    b = open(D + "sortie-test/enligne-" + p + ".html", encoding="utf-8").read()
    print("==", p, "copie", len(a), "ligne", len(b), "identiques", a == b)
    for nom, h in (("copie", a), ("ligne", b)):
        d = re.findall(r'name="description" content="([^"]*)"', h)
        print(" ", nom, "desc", len(d[0]) if d else None, d[0] if d else "")
        print(" ", nom, "main", len(re.findall(r"<main", h)), "nav", len(re.findall(r"<nav", h)),
              "skip", len(re.findall(r'class="skip', h)), "noscript", len(re.findall(r"<noscript", h)),
              "jsonld", re.findall(r'"@type":\s*"(\w+)"', h)[:4], "hreflang", len(re.findall("hreflang", h)))
        print(" ", nom, "og:image", re.findall(r'og:image" content="([^"]+)"', h)[:1], "html lang", re.findall(r'<html[^>]*>', h)[:1])
# accueil: lien sur chaque page vers les trois autres
for p in ["regles-de-course", "stages", "lexique"]:
    h = open(D + "projets/sailingmore/site/" + p + ".html", encoding="utf-8").read()
    print(p, "liens internes", sorted(set(re.findall(r'href="([a-z\-]+\.html)', h))))
