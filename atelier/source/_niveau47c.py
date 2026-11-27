"""Tâche 47, cnv-versoix : niveau par session lu dans la liste de la page (cache). 'applique' écrit."""
import json, os, re, sys, collections
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SJ = os.path.join(R, 'projets/sailingmore/stages.json')
c = json.load(open(os.path.join(R, 'scripts/_niveau47_cache.json')))
D = json.load(open(SJ)); d = D['offres']
MOIS = ['January','February','March','April','May','June','July','August','September','October','November','December']
LV = {'Beginner': 'debutant', 'Advanced': 'confirme', 'Intermediate': 'intermediaire'}
SESS = re.compile(r'(All levels / Advanced|Beginner|Intermediate|Advanced) (' + '|'.join(MOIS) + r') (\d{4}) (.*?) · (\d\d:\d\d)[–-](\d\d:\d\d)')
def table(t):
    out = collections.defaultdict(set)
    for m in SESS.finditer(t):
        lab, mo, an, rest, h1, h2 = m.groups()
        nums = re.findall(r'\d+', rest)
        # premier jour : premier nombre qui n'est pas un compteur « 4 Saturday » (suivi d'un mot)
        mm = re.search(r'(?:of |, |^|Ascension, |Whitsun, )(\d{1,2})(?=[–\- ])', rest)
        if not mm: continue
        out[(int(an), MOIS.index(mo) + 1, int(mm.group(1)), h1)].add(lab)
    return out
n = 0; amb = 0; tous = 0; sans = 0
for e in d:
    if e['ecole_slug'] != 'cnv-versoix' or e.get('niveau'): continue
    t = c.get(e['lien'], '')
    tb = table(t)
    y, mo, dd = map(int, e['debut'].split('-'))
    h = re.search(r'(\d\d:\d\d)-\d\d:\d\d', e['titre'])
    labs = tb.get((y, mo, dd, h.group(1))) if h else None
    if not labs: sans += 1; continue
    if len(labs) != 1: amb += 1; continue
    lab = next(iter(labs))
    if lab not in LV: tous += 1; continue
    e['niveau'] = LV[lab]; e['niveau_src'] = 'page ecole'; n += 1
print('posés', n, 'tous niveaux', tous, 'ambigus', amb, 'sans correspondance', sans)
if len(sys.argv) > 1 and sys.argv[1] == 'applique':
    json.dump(D, open(SJ, 'w'), ensure_ascii=False, indent=1)
