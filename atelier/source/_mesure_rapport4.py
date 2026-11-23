import re, gzip, json, os
D = "/opt/data/cache/claude-nuit/travail/"
S = D + "sortie-test/"
SITE = D + "projets/sailingmore/"
out = {}
for p in ["regles-de-course", "stages", "lexique", "index"]:
    h = open(S + "enligne-" + p + ".html", encoding="utf-8").read()
    raw = h.encode()
    o = dict(octets=len(raw), gzip_est=len(gzip.compress(raw, 6)))
    o["hreflang"] = len(re.findall(r'hreflang=', h))
    o["og"] = len(re.findall(r'property="og:', h))
    o["twitter"] = len(re.findall(r'name="twitter:', h))
    o["canonical"] = re.findall(r'rel="canonical" href="([^"]+)"', h)
    o["title"] = re.findall(r'<title>(.*?)</title>', h)
    o["desc_len"] = [len(x) for x in re.findall(r'name="description" content="([^"]*)"', h)]
    o["lang_attr"] = re.findall(r'<html[^>]*lang="(\w+)"', h)
    o["h1"] = len(re.findall(r'<h1[ >]', h))
    heads = [(m.group(1)) for m in re.finditer(r'<h([1-6])[ >]', h)]
    o["saut_titres"] = sum(1 for a, b in zip(heads, heads[1:]) if int(b) - int(a) > 1)
    o["premier_titre_apres_h1"] = heads[:4]
    o["liens_ancre_vides"] = len(re.findall(r'<a [^>]*href="#"', h))
    o["a_sans_texte_ni_aria"] = len(re.findall(r'<a [^>]*></a>', h))
    o["img"] = len(re.findall(r'<img ', h))
    o["svg"] = len(re.findall(r'<svg', h))
    o["button"] = len(re.findall(r'<button', h))
    o["outline_none"] = len(re.findall(r'outline:\s*none|outline:\s*0', h))
    o["focus_visible"] = len(re.findall(r':focus', h))
    o["prefers_reduced"] = len(re.findall(r'prefers-reduced-motion', h))
    o["min_height_44"] = len(re.findall(r'min-height:\s*44px|height:\s*44px', h))
    o["media_max_width"] = sorted(set(re.findall(r'@media[^{]*max-width:\s*(\d+)px', h)))
    o["font_px_lt12"] = sorted(set(float(x) for x in re.findall(r'font-size:\s*(\d+(?:\.\d+)?)px', h) if float(x) < 12))
    o["analytics"] = len(re.findall(r'google-analytics|gtag|plausible|matomo|umami|_paq', h))
    o["ressources_ext"] = sorted(set(re.findall(r'(?:src|href)="((?:https?:)?//[^"]+|/[^"#]+\.(?:js|css|png|jpg|webp))"', h)))[:12]
    # ancre vers le contenu / skip link
    o["skip"] = len(re.findall(r'skip|aller au contenu', h, re.I))
    o["noscript"] = len(re.findall(r'<noscript', h))
    # texte visible sans JS (hors script/style)
    t = re.sub(r'<script.*?</script>|<style.*?</style>', ' ', h, flags=re.S)
    t = re.sub(r'<[^>]+>', ' ', t)
    o["mots_sans_js"] = len(t.split())
    out[p] = o
# accueil -> trois pages
for p in ["regles-de-course", "stages", "lexique", "cours", "regates"]:
    out["index"].setdefault("liens", {})[p] = len(re.findall(p + r'\.html', open(S + "enligne-index.html", encoding="utf-8").read()))
# JSON sources
st = json.load(open(SITE + "stages.json"))
lx = json.load(open(SITE + "lexique.json"))
def shape(x, d=0):
    if isinstance(x, dict):
        return {k: (shape(v, d + 1) if d < 1 else type(v).__name__ + str(len(v) if hasattr(v, '__len__') else '')) for k, v in list(x.items())[:12]}
    if isinstance(x, list):
        return "list%d" % len(x) + (":" + json.dumps(shape(x[0], d + 1), ensure_ascii=False)[:400] if x else "")
    return type(x).__name__
out["stages_json"] = shape(st)
out["lexique_json"] = shape(lx)
print(json.dumps(out, ensure_ascii=False, indent=1))
