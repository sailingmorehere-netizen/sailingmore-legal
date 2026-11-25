"""Tâche 76 : retire target/rel des liens internes d'accueil_2026.py, index.html -> / dans les générateurs."""
import re
from pathlib import Path

S = Path(__file__).parent
p = S / "accueil_2026.py"
t = p.read_text(encoding="utf-8")
n0 = t.count('target="_blank"')
t = t.replace('<a class="{cls}" href="{href}" target="_blank" rel="noopener">', '<a class="{cls}" href="{href}">')
t = t.replace('<a href="{h}" target="_blank" rel="noopener" data-t="{k}">', '<a href="{h}" data-t="{k}">')
t = re.sub(r'(<a href="[a-z\-]+\.html")(?: data-t="cook_l")? target="_blank" rel="noopener"',
           lambda m: m.group(0).replace(' target="_blank" rel="noopener"', ''), t)
p.write_text(t, encoding="utf-8")
print("accueil_2026 : target", n0, "->", t.count('target="_blank"'))

for nom in ["accueil_site.py", "regates_page.py", "comptes_page.py", "favoris_page.py"]:
    q = S / nom
    s = q.read_text(encoding="utf-8")
    a = s.count('href="index.html"') + s.count('href=\\"index.html\\"')
    s = s.replace('href="index.html"', 'href="/"').replace('href=\\"index.html\\"', 'href=\\"/\\"')
    s = s.replace('href="index.html#', 'href="/#').replace('href=\\"index.html#', 'href=\\"/#')
    q.write_text(s, encoding="utf-8")
    print(nom, a)
