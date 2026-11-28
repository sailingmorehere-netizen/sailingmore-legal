# © 2026 Sailing More — tous droits réservés. All rights reserved.
"""Mesure sitemap / statut / canonical / noindex / hreflang, en ligne (GET seul) et dans la copie.
Usage : python3 scripts/mesure_sitemap.py  -> sortie-test/mesure-sitemap.json + tableau markdown."""
import urllib.request, re, json, os, time, datetime
B = "https://sailingmore.fr/"
W = "/opt/data/cache/claude-nuit/travail/"
S = W + "projets/sailingmore/site/"

def get(u, method="GET"):
    r = urllib.request.Request(u, headers={"User-Agent": "mesure-lecture", "Accept-Encoding": "identity"}, method=method)
    try:
        with urllib.request.urlopen(r, timeout=30) as f:
            return f.status, f.geturl(), f.read().decode("utf-8", "replace"), dict(f.headers)
    except Exception as e:
        return getattr(e, "code", str(e)), u, "", {}

def locs(xml):
    return re.findall(r"<loc>([^<]+)</loc>", xml)

now = datetime.datetime.now().isoformat(timespec="seconds")
out = {"date": now}
st, _, robots, _ = get(B + "robots.txt"); out["robots"] = {"status": st, "texte": robots}
sm = {}
for name in ["sitemap.xml", "sitemap-bateaux.xml"]:
    st, _, x, h = get(B + name)
    sm[name] = {"status": st, "urls": locs(x), "lastmods": re.findall(r"<lastmod>([^<]+)</lastmod>", x), "ct": h.get("Content-Type")}
    lx = open(S + name, encoding="utf-8").read() if os.path.exists(S + name) else ""
    sm[name]["local_urls"] = locs(lx)
    sm[name]["identique_copie"] = (x == lx)
out["sitemaps"] = sm
online = set(u for v in sm.values() for u in v["urls"])
local = set(u for v in sm.values() for u in v["local_urls"])
files = sorted(f for f in os.listdir(S) if f.endswith(".html"))
pages = {}
cand = set(online) | set(local) | {B + (f if f != "index.html" else "") for f in files}
for u in sorted(cand):
    st, final, body, h = get(u)
    can = re.search(r'<link[^>]+rel=["\']canonical["\'][^>]*>', body)
    canu = None
    if can:
        m = re.search(r'href=["\']([^"\']+)', can.group(0)); canu = m.group(1) if m else None
    robots_meta = re.search(r'<meta[^>]+name=["\']robots["\'][^>]*content=["\']([^"\']+)', body)
    pages[u] = {"status": st, "final": final if final != u else None, "canonical": canu,
                "noindex": bool(robots_meta and "noindex" in robots_meta.group(1).lower()),
                "hreflang": len(re.findall(r'hreflang=', body)),
                "dans_sitemap": u in online, "dans_sitemap_copie": u in local,
                "x_robots": h.get("X-Robots-Tag")}
    time.sleep(0.2)
out["pages"] = pages
os.makedirs(W + "sortie-test", exist_ok=True)
json.dump(out, open(W + "sortie-test/mesure-sitemap.json", "w"), indent=1, ensure_ascii=False)
print("mesure", now)
print("robots", st if False else out["robots"]["status"]); print(robots)
for n, v in sm.items():
    print(n, v["status"], "en ligne", len(v["urls"]), "copie", len(v["local_urls"]), "identique", v["identique_copie"], "lastmods", sorted(set(v["lastmods"])))
print("| URL | sitemap | copie | HTTP | canonical | noindex | hreflang |")
for u, p in pages.items():
    ok = (p["canonical"] == u) or (u == B and p["canonical"] in (B, B + "index.html"))
    print(f"| {u.replace(B,'/')} | {'oui' if p['dans_sitemap'] else 'NON'} | {'oui' if p['dans_sitemap_copie'] else 'non'} | {p['status']}{' ->'+p['final'] if p['final'] else ''} | {'ok' if ok else (p['canonical'] or 'ABSENT')} | {p['noindex']} | {p['hreflang']} |")
print("fichiers html copie sans URL:", [f for f in files if (B + (f if f != 'index.html' else '')) not in online])
