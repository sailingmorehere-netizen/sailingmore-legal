"""Relève les origines externes réellement utilisées par le site (base de la CSP). Lecture seule."""
import re, os, collections
root = "projets/sailingmore/site"
c = collections.defaultdict(collections.Counter)
pat = re.compile(r'(<script[^>]+src|<iframe[^>]+src|<link[^>]+href|<img[^>]+src|<form[^>]+action|fetch\(|import\(|url\(|src|href)\s*=?\s*\(?["\']?(https?://[^"\')\s>]+)')
for d, _, fs in os.walk(root):
    for f in fs:
        if not f.endswith((".html", ".js", ".css", ".php")):
            continue
        t = open(os.path.join(d, f), errors="ignore").read()
        for m in pat.finditer(t):
            h = re.match(r'https?://([^/]+)', m.group(2)).group(1)
            if h == "sailingmore.fr":
                continue
            c[h][m.group(1)[:14]] += 1
        if re.search(r'<script(?![^>]*\bsrc)[^>]*>', t): c["__inline_script"][f.rsplit(".", 1)[-1]] += 1
        if re.search(r'\son[a-z]+="', t): c["__inline_handler"][f.rsplit(".", 1)[-1]] += 1
        if re.search(r'\sstyle="', t): c["__inline_style"][f.rsplit(".", 1)[-1]] += 1
        if "<style" in t: c["__style_tag"][f.rsplit(".", 1)[-1]] += 1
for h, v in sorted(c.items()):
    print(h, dict(v))
