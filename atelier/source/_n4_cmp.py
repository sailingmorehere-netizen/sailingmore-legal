import json
import shutil
import sys
from pathlib import Path

J = Path('projets/sailingmore/chants-de-marin.json')
B = Path('cache/chants/avant_n4.json')
if sys.argv[1] == 'sauve':
    shutil.copy(J, B)
    print('sauvegarde', B)
else:
    a = {c['id']: c for c in json.loads(B.read_text())['chants']}
    n = json.loads(J.read_text())['chants']
    b = {c['id']: c for c in n}
    print('avant', len(a), 'apres', len(b))
    print('modifies parmi les anciens :', [k for k in a if k in b and a[k] != b[k]])
    print('disparus :', [k for k in a if k not in b])
    for k in b:
        if k not in a:
            c = b[k]
            print('=' * 70)
            print(k, '|', c['titre'], '|', c['type'], '|', c['lg'], '|', c.get('partiel'), '|', c['source'])
            print(c['paroles'])
