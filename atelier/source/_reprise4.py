import re, json, urllib.request
D = "/opt/data/cache/claude-nuit/travail/"
live = urllib.request.urlopen("https://sailingmore.fr/sitemap.xml").read().decode()
loc = lambda s: re.findall(r"<loc>([^<]+)", s)
cp = open(D + "projets/sailingmore/site/sitemap.xml").read()
print("en ligne:", loc(live))
print("copie  :", loc(cp))
print("robots :", urllib.request.urlopen("https://sailingmore.fr/robots.txt").read().decode())
e = json.load(open(D + "sortie-test/etude-six-langues.json"))
print(list(e.keys()))
for p in e["pages"]:
    if p["page"] in ("regles-de-course.html", "stages.html", "lexique.html"):
        print({k: v for k, v in p.items() if k != "data_t_sans_table"})
a = json.load(open(D + "sortie-test/audit-trois-pages.json"))
for k in ("stages", "lexique"):
    print(k, {x: a[k][x] for x in ("title", "desc", "h1", "h2", "h3", "jsonld_types", "imgs", "img_sans_alt", "skip_link", "noscript", "main", "nav", "hreflang", "og")})
for p in ("regles-de-course", "stages", "lexique"):
    h = open(D + "sortie-test/enligne-" + p + ".html", encoding="utf-8").read()
    t = re.sub(r"<(script|style)[\s\S]*?</\1>", "", h)
    t = re.sub(r"<[^>]+>", " ", t)
    print(p, "mots visibles sans JS:", len(t.split()))
