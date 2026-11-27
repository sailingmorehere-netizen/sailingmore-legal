import re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import verifie_langue as v
S = v.SITE
for p in sorted(S.glob('*.html')):
    if p.name.startswith('pavillon') and not v.COPIE.search(p.name):
        t = p.read_text(errors='replace')
        if 'data-lang="fr"' in t and 'data-lang="de"' not in t:
            print('PAV sans de', p.name, re.findall(r'data-lang="(\w+)"', t)); break
for p in sorted(S.glob('*.html')):
    if v.COPIE.search(p.name):
        continue
    t = p.read_text(errors='replace')
    if (S / (p.stem + '-de.html')).exists() and 'hreflang="de"' not in t:
        print('hreflang manque', p.name)
print(sum(1 for p in S.glob('pavillon*.html')), [p.name for p in list(S.glob('pavillon*.html'))[:3]])
