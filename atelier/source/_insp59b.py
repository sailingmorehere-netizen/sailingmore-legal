import json, re, os, collections
o = json.load(open('projets/sailingmore/stages.json'))['offres']
DEB = re.compile(r"(?i)no (previous |prior )?(sailing )?experience|complete beginners?|for beginners|beginners? (welcome|course)|aucune exp[ée]rience|sans exp[ée]rience|pour d[ée]butants|ouvert aux d[ée]butants|keine (Vor)?kenntnisse|keine Erfahrung|für Anfänger|geen ervaring|voor beginners|sin experiencia|para principiantes|nessuna esperienza|per principianti|sem experi[êe]ncia")
CON = re.compile(r"(?i)experienced sailors?|prior (sailing )?experience (is )?(required|essential|needed)|previous experience (is )?(required|essential|needed)|advanced (sailors?|course|level)|for experienced|exp[ée]riment[ée]s? requis|navigateurs? confirm[ée]s|niveau confirm[ée]|erfahrene Segler|Segelerfahrung (ist )?erforderlich|ervaren zeilers|con experiencia previa|navegantes? experimentados|velisti esperti|esperienza pregressa")
def txt(u):
    p = 'tmp_n59/' + re.sub(r'\W+', '_', u)[:150] + '.txt'
    return open(p).read() if os.path.exists(p) else ''
par = collections.defaultdict(list)
for e in o:
    if not e.get('niveau') and e['ecole_slug'] != 'cnv-versoix':
        t = txt(e['lien'])
        d, c = bool(DEB.search(t)), bool(CON.search(t))
        v = 'debutant' if d and not c else 'confirme' if c and not d else ''
        par[e['ecole_slug']].append((v, e['lien'], e['titre']))
tot = 0
for s, l in par.items():
    n = sum(1 for x in l if x[0])
    tot += n
    print(s, n, '/', len(l), [x[2][:40] + '→' + x[0] for x in l if x[0]][:3])
print('total', tot)
