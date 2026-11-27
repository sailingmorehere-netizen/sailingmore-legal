import json, os, re, sys
sys.argv = ['x', 'none']
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = open(os.path.join(R, 'scripts/_dates58.py')).read().replace('\nmain()\n', '\n')
exec(compile(src, 'd58', 'exec'))
L = json.load(open(F))['offres']
cible = [e for e in L if not e.get('debut') and not e.get('hors_offre')]
seen = set()
for slug in ['solentboat', 'tiptop', 'ultra', 'debirt', 'sailway', 'rueckenwind', 'virgins', 'urbantruant', 'plasmenai', 'lagoo', 'weber']:
    e = next((x for x in cible if x['ecole_slug'] == slug), None)
    if not e: continue
    t = texte(e['lien'])
    print('==', slug, e['lien'], len(t))
    ms = [m for m in re.finditer(r'(20(?:26|27))|(\b\d{1,2}[./]\d{1,2}[./]\d{2,4})', t)]
    for m in ms[:4]:
        print('   ', t[max(0, m.start() - 60):m.end() + 60])
