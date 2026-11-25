import re, glob, os
S = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "projets", "sailingmore", "site")
for p in ["index.html", "lexique.html", "cours.html", "mentions-legales.html"]:
    s = open(os.path.join(S, p), encoding="utf-8").read()
    h = s[:s.find("</head>")]
    h = re.sub(r'<script.*?</script>', '<SCRIPT/>', h, flags=re.S)
    h = re.sub(r'<style.*?</style>', '<STYLE/>', h, flags=re.S)
    print("=====", p, len(s)); print(h[:1500])
    print("data-t:", len(re.findall(r'data-t="', s)), "data-l:", len(re.findall(r'data-l="', s)))
print(open(os.path.join(S, "robots.txt")).read())
print(open(os.path.join(S, "sitemap.xml")).read()[:600])
print(sorted(os.listdir(S))[:0], [f for f in os.listdir(S) if f.startswith(".") or f in ("_redirects", "netlify.toml", "vercel.json", "CNAME")])
