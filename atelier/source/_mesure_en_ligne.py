import urllib.request, time, re, gzip, json, os, sys
B = "https://sailingmore.fr/"
OUT = "/opt/data/cache/claude-nuit/travail/sortie-test/"
def get(u):
    t = time.time()
    r = urllib.request.Request(u, headers={"Accept-Encoding": "gzip", "User-Agent": "mesure-lecture"})
    try:
        with urllib.request.urlopen(r, timeout=30) as f:
            raw = f.read(); h = dict(f.headers); code = f.status
    except Exception as e:
        return getattr(e, "code", str(e)), {}, b"", b"", time.time() - t
    body = gzip.decompress(raw) if h.get("Content-Encoding") == "gzip" else raw
    return code, h, raw, body, time.time() - t
res = {}
for p in ["regles-de-course", "stages", "lexique", "index", "sitemap.xml", "robots.txt"]:
    u = B + (p if "." in p else p + ".html")
    code, h, raw, body, t = get(u)
    res[p] = dict(code=code, wire=len(raw), body=len(body), t=round(t, 2),
                  enc=h.get("Content-Encoding"), cache=h.get("Cache-Control"), srv=h.get("Server"))
    if code == 200:
        open(OUT + "enligne-" + p.replace(".html", "") + (".html" if "." not in p else ""), "wb").write(body)
print(json.dumps(res, indent=1))
