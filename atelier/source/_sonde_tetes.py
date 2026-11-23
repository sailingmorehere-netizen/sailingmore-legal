import re, glob, os, urllib.request
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
S = os.path.join(R, "projets", "sailingmore", "site")
def get(u):
    try:
        with urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "mesure-site"}), timeout=20) as f:
            return f.status, f.read().decode("utf-8", "replace")
    except Exception as e:
        return str(e)[:40], ""
def visible(s):
    s = re.sub(r"<(script|style)\b.*?</\1>", " ", s, flags=re.S)
    return len(re.sub(r"<[^>]+>", " ", s).split())
print("page | titre | desc(car) | og(t+d) | canonical | alternate | document.title JS | statut ligne | mots visibles copie/ligne | ?lang=de identique")
for p in sorted(glob.glob(S + "/*.html")):
    n = os.path.basename(p)
    s = open(p, encoding="utf-8").read()
    t = re.search(r"<title>(.*?)</title>", s, re.S)
    d = re.search(r'name="description"\s+content="([^"]*)"', s)
    og = len(re.findall(r'property="og:(?:title|description)"', s))
    can = bool(re.search(r'rel="canonical"', s))
    alt = len(re.findall(r'rel="alternate"', s))
    js = len(re.findall(r"document\.title\s*=", s))
    u = "https://sailingmore.fr/" + ("" if n == "index.html" else n)
    st, live = get(u)
    st2, live2 = get(u + "?lang=de") if st == 200 else ("-", "")
    print(n, "|", (t.group(1).strip() if t else None), "|", len(d.group(1)) if d else None, "|", og, "|", can, "|", alt, "|", js, "|", st,
          "|", visible(s), "/", visible(live) if live else "-", "|", (live2 == live) if live2 else "-")
