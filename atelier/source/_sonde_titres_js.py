import re, os
S = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "projets", "sailingmore", "site")
for n in ["stages.html", "regates.html", "cours.html", "equivalences.html", "jeux.html", "carte.html", "confidentialite.html", "mentions-legales.html"]:
    s = open(os.path.join(S, n), encoding="utf-8").read()
    print("==", n, "noscript:", len(re.findall(r"<noscript", s)), "robots:", re.findall(r'name="robots"\s+content="([^"]*)"', s))
    for m in list(re.finditer(r"(?:document\.title|\.title\s*=|setAttribute\(\s*[\"']content|meta\[name=)[^\n]{0,140}", s))[:4]:
        print("   ", m.group(0)[:170])
    for m in list(re.finditer(r"[\"'](?:titre|title|meta_title|seo_t\w*|page_t\w*|desc|meta_desc\w*)[\"']\s*:\s*[\"'][^\"']{0,80}", s))[:4]:
        print("   cle:", m.group(0)[:110])
