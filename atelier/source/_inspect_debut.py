import json, os, re, hashlib, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
o = json.load(open(os.path.join(R, 'projets/sailingmore/stages.json')))['offres']
for s in ['ultra', 'tiptop', '7seas', 'uksa', 'sailway', 'glenans']:
    m = [e for e in o if e['ecole_slug'] == s and not e.get('debut') and e.get('lien')][:2]
    for e in m:
        f = '/tmp/stages_pages/' + hashlib.md5(e['lien'].encode()).hexdigest()
        t = open(f, encoding='utf-8', errors='replace').read()
        t = re.sub(r'(?is)<(script|style)[^>]*>.*?</\1>', ' ', t)
        t = re.sub(r'<[^>]+>', ' ', t)
        t = re.sub(r'\s+', ' ', t)
        print('==', s, e['titre'][:40], e['lien'])
        for k in list(re.finditer(r'20(?:26|27)', t))[:4]:
            print('   ...', t[max(0, k.start() - 70):k.end() + 40])
