import gzip, re, json
p = open("projets/sailingmore/site/chants-de-marin.html", encoding="utf-8").read()
print("octets", len(p.encode()), "gzip", len(gzip.compress(p.encode(), 9)))
print("fiches", p.count('class="fiche"'), "groupes", len(re.findall(r'class="groupe"', p)), "sommaire", 'id="sommaire"' in p)
print("liens sommaire", re.findall(r'href="#g-(\w+)"', p))
d = json.load(open("projets/sailingmore/chants-de-marin.json", encoding="utf-8"))
c = d["chants"]
from collections import Counter
print(Counter(x["type"] for x in c), Counter(x["lg"] for x in c))
print("paroles non vides", sum(1 for x in c if x["paroles"]), "complètes", sum(1 for x in c if x["paroles"] and not x.get("partiel")), "audio", sum(1 for x in c if x["audio"]))
print("hreflang", p.count('hreflang='), "jsonld", p.count("application/ld+json"), "canonical", p.count('rel="canonical"'))
