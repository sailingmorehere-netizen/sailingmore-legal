import re
S = '/opt/data/cache/claude-nuit/travail/projets/sailingmore/site/'
for f in ['ports.html', 'regates.html', 'stages.html']:
    t = open(S + f, encoding='utf-8').read()
    print('=====', f)
    for m in re.finditer(r'smGeo', t):
        print('  >', t[max(0, m.start() - 150):m.start() + 350].replace('\n', ' '))
        print()
e = open(S + 'ecole-' + sorted(__import__('os').listdir(S))[0][:0] + 'x', 'w') if False else None
import glob
f = sorted(glob.glob(S + 'ecole-*.html'))[0]
t = open(f, encoding='utf-8').read()
print(f, 'carte' in t, re.findall(r'<(?:div|svg|iframe)[^>]*(?:carte|map)[^>]*>', t)[:3])
