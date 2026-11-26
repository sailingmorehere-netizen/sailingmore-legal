import json, os, re, sys, time, urllib.request, urllib.parse, urllib.error

UA = "SailingMore-chants-illustrations/1.0 (usage editorial, lecture seule; site sailingmore.fr)"
API = "https://commons.wikimedia.org/w/api.php"


def get(url, binary=False):
    for _ in range(3):
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                data = r.read()
            time.sleep(2)
            return data if binary else data.decode("utf-8", "replace")
        except urllib.error.HTTPError as e:
            if e.code == 429:
                print("429 -> attente 60 s", file=sys.stderr)
                time.sleep(60)
                continue
            raise
    raise RuntimeError("429 repete: " + url)


def recherche(q, n=6):
    p = {"action": "query", "format": "json", "generator": "search", "gsrsearch": q + " filetype:bitmap",
         "gsrnamespace": "6", "gsrlimit": str(n), "prop": "imageinfo", "iiprop": "url|size|extmetadata",
         "iiurlwidth": "1000"}
    j = json.loads(get(API + "?" + urllib.parse.urlencode(p)))
    out = []
    for pg in j.get("query", {}).get("pages", {}).values():
        ii = pg["imageinfo"][0]
        m = ii.get("extmetadata", {})
        out.append((pg["title"], ii["width"], ii["height"], m.get("LicenseShortName", {}).get("value"),
                    re.sub("<[^>]+>", "", m.get("Artist", {}).get("value", ""))[:50]))
    return out


if __name__ == "__main__":
    if sys.argv[1] == "whall":
        os.makedirs("cache_dl/whall", exist_ok=True)
        t = get("https://archive.org/download/seasongsshanties00whal/seasongsshanties00whal_djvu.txt")
        open("cache_dl/whall/whall.txt", "w").write(t)
        for i, l in enumerate(t.splitlines()):
            if re.search(r"illustration|frontispiece|\bplate\b", l, re.I):
                print(i, l[:120])
    else:
        for q in sys.argv[1:]:
            print("##", q)
            try:
                for r in recherche(q):
                    print("  ", r)
            except Exception as e:
                print("  ERR", e)
