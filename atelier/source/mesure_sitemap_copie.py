import re, os
S = "/opt/data/cache/claude-nuit/travail/projets/sailingmore/site/"
B = "https://sailingmore.fr/"
urls = []
for n in ["sitemap.xml", "sitemap-bateaux.xml"]:
    urls += re.findall(r"<url><loc>([^<]+)</loc><lastmod>([^<]*)", open(S + n, encoding="utf-8").read())
print("URL copie:", len(urls))
NI = r'name=["\']robots["\'][^>]*noindex'
for u, lm in urls:
    p = S + (u[len(B):] or "index.html")
    if p.endswith("/"): p += "index.html"
    if not os.path.exists(p):
        print("FICHIER ABSENT", u); continue
    t = open(p, encoding="utf-8", errors="replace").read()
    m = re.search(r'<link[^>]+rel=["\']canonical["\'][^>]*href=["\']([^"\']+)', t) or re.search(r'<link[^>]+href=["\']([^"\']+)["\'][^>]*rel=["\']canonical', t)
    c = m.group(1) if m else None
    ni = bool(re.search(NI, t))
    if (c != u and not (u == B and c in (B, B + "index.html"))) or ni:
        print("ECART", u, lm, c, "noindex" if ni else "")
for f in sorted(os.listdir(S)):
    if f.endswith(".html"):
        t = open(S + f, encoding="utf-8", errors="replace").read()
        print(f, "canon" if 'rel="canonical"' in t else "SANS-canon", "noindex" if re.search(NI, t) else "", "hreflang:%d" % t.count("hreflang"))
