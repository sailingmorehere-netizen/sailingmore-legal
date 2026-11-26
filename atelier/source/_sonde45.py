import re, glob, os
S = '/opt/data/cache/claude-nuit/travail/projets/sailingmore/site/'
for f in ['stages.html', 'regates.html', 'ports.html', 'bateaux.html', 'lexique.html', 'ports/escale.html', 'carte.html']:
    p = S + f
    if not os.path.exists(p):
        print(f, 'ABSENT'); continue
    t = open(p, encoding='utf-8').read()
    print(f, len(t), 'smGeo', t.count('smGeo'), 'geo-accueil', t.count('geo-accueil'),
          'googleapis', t.count('googleapis'), 'selects', re.findall(r'<select[^>]*id="([^"]*)"', t)[:12])
ec = glob.glob(S + 'ecole-*.html')
print('ecoles', len(ec), 'avec geo-accueil', sum('geo-accueil' in open(x, encoding='utf-8').read() for x in ec))
print('googleapis dans le site:', [os.path.basename(x) for x in glob.glob(S + '*.html') + glob.glob(S + '*.js') if 'googleapis' in open(x, encoding='utf-8', errors='ignore').read()][:10])
t = open(S + 'stages.html', encoding='utf-8').read()
for m in re.finditer(r'smGeo', t):
    print('stages>', t[max(0, m.start() - 80):m.start() + 220].replace('\n', ' '))
    break
