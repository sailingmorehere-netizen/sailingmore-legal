# © 2026 Sailing More — tous droits réservés. All rights reserved.
import re, urllib.request, html, sys
U = open('scripts/lire_pages.py').read().split('"""')[1].split()
for u in U[3:9] + U[9:10] + U[0:3]:
    print("=====", u)
    try:
        h = urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"}), timeout=25).read().decode("utf-8", "replace")
    except Exception as e:
        print("ERREUR", e); continue
    h = re.sub(r"(?is)<(script|style|noscript|nav|footer|header).*?</\1>", " ", h)
    t = html.unescape(re.sub(r"<[^>]+>", "\n", h))
    ls = [re.sub(r"\s+", " ", l).strip() for l in t.split("\n")]
    ls = [l for l in ls if len(l) > 50 and "cookie" not in l.lower()]
    for l in ls[:14]:
        print("-", l[:350])
