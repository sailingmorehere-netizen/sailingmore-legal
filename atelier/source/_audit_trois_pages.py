import re, json, urllib.request, urllib.parse, gzip, time
D = "/opt/data/cache/claude-nuit/travail/sortie-test/"
B = "https://sailingmore.fr/"
def head(u):
    r = urllib.request.Request(u, method="HEAD", headers={"User-Agent": "mesure-lecture"})
    try:
        with urllib.request.urlopen(r, timeout=20) as f:
            return f.status, int(f.headers.get("Content-Length") or 0)
    except Exception as e:
        return getattr(e, "code", "ERR"), 0
out = {}
for p in ["regles-de-course", "stages", "lexique"]:
    h = open(D + "enligne-" + p + ".html", encoding="utf-8").read()
    o = {}
    g = lambda rx: re.findall(rx, h, re.S | re.I)
    o["title"] = g(r"<title[^>]*>(.*?)</title>")[:2]
    o["desc"] = [x[:160] for x in g(r'<meta name="description" content="(.*?)"')]
    o["canonical"] = g(r'<link rel="canonical" href="(.*?)"')
    o["hreflang"] = g(r'<link rel="alternate" hreflang="(.*?)" href="(.*?)"')[:8]
    o["og"] = len(g(r'property="og:'))
    o["html_lang"] = g(r"<html[^>]*lang=\"(.*?)\"")
    o["h1"] = [re.sub(r"<[^>]+>", "", x)[:80] for x in g(r"<h1[^>]*>(.*?)</h1>")]
    o["nb_h1"] = len(o["h1"])
    o["h2"] = len(g(r"<h2[\s>]")); o["h3"] = len(g(r"<h3[\s>]")); o["h4"] = len(g(r"<h4[\s>]"))
    jl = g(r'<script type="application/ld\+json"[^>]*>(.*?)</script>')
    types = []
    for j in jl:
        try:
            d = json.loads(j)
            for x in (d if isinstance(d, list) else d.get("@graph", [d])):
                types.append(x.get("@type"))
        except Exception as e:
            types.append("INVALIDE")
    o["jsonld_types"] = types
    o["imgs"] = len(g(r"<img\b"))
    o["img_sans_alt"] = len([x for x in g(r"<img\b[^>]*>") if "alt=" not in x])
    o["img_alt_vide"] = len([x for x in g(r"<img\b[^>]*>") if re.search(r'alt=""', x)])
    o["img_lazy"] = len([x for x in g(r"<img\b[^>]*>") if "loading=" in x])
    o["img_sans_wh"] = len([x for x in g(r"<img\b[^>]*>") if "width=" not in x])
    o["scripts_inline"] = len(g(r"<script(?![^>]*src)[^>]*>"))
    o["scripts_ext"] = g(r'<script[^>]*src="(.*?)"')
    o["css_ext"] = g(r'<link[^>]*rel="stylesheet"[^>]*href="(.*?)"')
    o["style_inline_bytes"] = sum(len(x) for x in g(r"<style[^>]*>(.*?)</style>"))
    o["script_inline_bytes"] = sum(len(x) for x in re.findall(r"<script(?![^>]*src)[^>]*>(.*?)</script>", h, re.S))
    o["viewport"] = bool(g(r'name="viewport"'))
    o["noscript"] = len(g(r"<noscript"))
    o["skip_link"] = bool(g(r'href="#(main|contenu|content)'))
    o["aria_label"] = len(g(r"aria-label="))
    o["btn_sans_type"] = 0
    o["tabindex"] = len(g(r"tabindex="))
    o["inputs"] = len(g(r"<input\b")); o["input_sans_label"] = len([x for x in g(r"<input\b[^>]*>") if "aria-label" not in x and "id=" not in x])
    o["main"] = len(g(r"<main"))
    o["nav"] = len(g(r"<nav"))
    o["breadcrumb"] = len(g(r"BreadcrumbList|aria-label=\"[^\"]*(Ariane|breadcrumb)"))
    o["data_lang_blocs"] = {l: len(g(r'data-lang="%s"' % l)) + len(g(r'lang="%s"' % l)) for l in ["fr", "de", "en", "it", "es", "pt"]}
    o["liens_internes"] = sorted(set(g(r'href="([a-z0-9\-]+\.html)[#"]')))
    o["liens_ext"] = len(set(g(r'href="(https?://[^"]+)"')))
    o["small_fonts_px"] = sorted(set(g(r"font-size:\s*(\d+(?:\.\d+)?)px")), key=float)[:8]
    out[p] = o
# images/ressources sur disque en ligne : tailles
res = {}
for p in out:
    h = open(D + "enligne-" + p + ".html", encoding="utf-8").read()
    srcs = set(re.findall(r'(?:src|href)="((?!https?:|#|mailto|tel|data:|javascript)[^"]+\.(?:png|jpe?g|webp|svg|js|css|woff2?|json|gif))"', h))
    tot = 0; det = []
    for s in sorted(srcs):
        c, l = head(B + s)
        det.append((s, c, l)); tot += l
    res[p] = dict(n=len(srcs), octets=tot, plus_gros=sorted(det, key=lambda x: -x[2])[:6], non200=[d for d in det if d[1] != 200])
out["ressources"] = res
# liens depuis l'accueil
ih = open(D + "enligne-index.html", encoding="utf-8").read()
out["accueil_liens"] = {p: len(re.findall(p + r"\.html", ih)) for p in ["regles-de-course", "stages", "lexique", "cours", "regates"]}
json.dump(out, open(D + "audit-trois-pages.json", "w"), ensure_ascii=False, indent=1)
print(json.dumps(out, ensure_ascii=False, indent=1)[:12000])
