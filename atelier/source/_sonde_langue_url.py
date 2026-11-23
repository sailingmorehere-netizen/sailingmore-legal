import re, os, urllib.request
S = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "projets", "sailingmore", "site")
src = open(os.path.join(S, "index.html"), encoding="utf-8").read()
for pat in [r"<title>.*?</title>", r'<meta name="description"[^>]*>', r'<link rel="alternate"[^>]*>', r"document\.title.{0,200}",
            r"URLSearchParams.{0,160}", r"sm-langue.{0,120}", r"history\.(replace|push)State.{0,120}", r"location\.(search|hash).{0,100}"]:
    for m in list(re.finditer(pat, src, re.S))[:3]:
        print(pat[:25], "=>", m.group(0)[:260].replace("\n", " "))
sm = open(os.path.join(S, "sitemap.xml"), encoding="utf-8").read()
print("sitemap hreflang:", sm.count("hreflang"), "urls:", sm.count("<loc>"))
print(sm[:600])
def get(u):
    r = urllib.request.Request(u, headers={"User-Agent": "mesure-site"})
    try:
        with urllib.request.urlopen(r, timeout=20) as f:
            return f.status, f.read()
    except Exception as e:
        return str(e), b""
for u in ["https://sailingmore.fr/?lang=de", "https://sailingmore.fr/de/", "https://sailingmore.fr/sitemap.xml", "https://sailingmore.fr/robots.txt"]:
    s, b = get(u)
    print(u, s, len(b), b.count(b"hreflang"), b.count(b"<loc>"))
