import os, re
base = 'projets/sailingmore/site'
n_if = {}
for root, d, files in os.walk(base):
    for n in files:
        if not n.endswith('.html'):
            continue
        s = open(os.path.join(root, n), encoding='utf-8', errors='ignore').read()
        fam = os.path.relpath(root, base).split(os.sep)[0]
        if re.search(r'<iframe[^>]*(maps|google)', s) or 'maps/embed' in s or 'maps.googleapis' in s:
            n_if.setdefault(fam, []).append(n)
print({k: (len(v), v[:3]) for k, v in n_if.items()})
# générateurs et sources qui parlent d'iframe / embed
for dp, dn, fn in os.walk('.'):
    if any(x in dp for x in ('/site', 'cache', 'pages42', '__pycache__', 'sortie-test')):
        continue
    for n in fn:
        if n.endswith(('.py', '.js')):
            p = os.path.join(dp, n)
            t = open(p, encoding='utf-8', errors='ignore').read()
            if re.search(r'maps/embed|output=embed|<iframe', t):
                print('src:', p, len(t))
