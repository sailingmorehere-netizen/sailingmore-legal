import os
base = 'projets/sailingmore/site'
stat = {}
for root, d, files in os.walk(base):
    fam = os.path.relpath(root, base).split(os.sep)[0]
    for n in files:
        if not n.endswith('.html'):
            continue
        s = open(os.path.join(root, n), encoding='utf-8', errors='ignore').read()
        k = fam if fam != '.' else 'racine'
        a = stat.setdefault(k, [0, 0, 0])
        a[0] += 1
        if 'google.com/maps' in s or 'maps.google' in s:
            a[1] += 1
        if 'maps/embed' in s or 'maps.googleapis' in s:
            a[2] += 1
for k, v in sorted(stat.items()):
    print(k, 'pages', v[0], 'lien maps', v[1], 'embed', v[2])
