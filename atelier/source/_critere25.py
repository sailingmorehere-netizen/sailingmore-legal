import re, os
for f in ('cours.html', 'projets/sailingmore/site/cours.html'):
    t = open(f, encoding='utf-8').read()
    h = len(re.findall(r'<h1', t)); k = os.path.getsize(f) // 1024
    print(f, 'h1', h, 'Ko', k)
    assert h == 1 and k < 250
