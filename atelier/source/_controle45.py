"""Contrôle tâche 45 : syntaxe JS de stages.html (node --check) + unicité de la clé de stockage (lien)."""
import re, json, subprocess, tempfile, os, collections
s = open('projets/sailingmore/site/stages.html', encoding='utf-8').read()
blocs = re.findall(r'<script(?![^>]*src)[^>]*>(.*?)</script>', s, re.S)
code = [b for b in blocs if 'cmpSauve' in b][0]
d = tempfile.mkdtemp()
f = os.path.join(d, 'a.js')
open(f, 'w', encoding='utf-8').write(code)
r = subprocess.run(['/opt/hermes/tools/node-26.12.1-linux-x64/bin/node', '--check', f], capture_output=True, text=True)
print('syntaxe code', r.returncode, r.stderr[:500])
for b in blocs:
    if b.lstrip().startswith('{"ui"'):
        D = json.loads(b)
        of = D['offres']
        c = collections.Counter(o.get('lien') for o in of)
        print('offres', len(of), 'liens uniques', len(c), 'sans lien', c.get(None, 0))
        dup = [(k, v) for k, v in c.items() if v > 1][:5]
        print('doublons', dup)
        o = of[0]
        print({k: o[k] for k in list(o)[:12]})
        break
