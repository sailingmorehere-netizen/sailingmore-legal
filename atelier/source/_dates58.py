"""Tâche 58 : relève debut/fin/duree_jours sur la page de chaque offre sans date (lecture seule, curl).
python3 scripts/_dates58.py sonde    -> télécharge, écrit scripts/_dates58_cache.json, résumé par école
python3 scripts/_dates58.py applique -> écrit debut, fin, duree_jours ENSEMBLE dans stages.json
Seules les PLAGES explicites (début → fin) d'une même page sont retenues ; une date isolée n'est pas un début.
Plusieurs plages sur la page : la plus proche à venir. Aucune plage : fiche laissée vide."""
import json, os, re, sys, html, subprocess, datetime
from concurrent.futures import ThreadPoolExecutor
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
F = os.path.join(R, 'projets/sailingmore/stages.json')
C = os.path.join(R, 'scripts/_dates58_cache.json')
AUJ = datetime.date(2026, 11, 27)
MAXI = datetime.date(2028, 12, 31)
MN = {}
for i, ns in enumerate([
    'january jan januari janvier janv januar gennaio enero janeiro tammikuu',
    'february feb februari février fevrier févr februar febbraio febrero fevereiro helmikuu',
    'march mar maart mars märz marz marzo março maaliskuu',
    'april apr avril aprile abril huhtikuu',
    'may mei mai maggio mayo maio toukokuu',
    'june jun juni juin giugno junio junho kesäkuu',
    'july jul juli juillet juil luglio julio julho heinäkuu',
    'august aug augustus août aout agosto elokuu',
    'september sep sept septembre settembre septiembre setembro syyskuu',
    'october oct okt oktober octobre ottobre octubre outubro lokakuu',
    'november nov novembre noviembre novembro marraskuu',
    'december dec dez décembre decembre dicembre diciembre dezembro joulukuu'], 1):
    for n in ns.split():
        MN[n] = i
NOMS = '|'.join(sorted(MN, key=len, reverse=True))
SEP = r'\s*(?:→|&rarr;|-&gt;|–|—|-|to|bis|au|al|a|till|until)\s*'
D1 = r'(\d{1,2})(?:st|nd|rd|th|er|\.)?\s+(?:of\s+)?(' + NOMS + r')\.?,?\s+(20\d\d)'
RX_FULL = re.compile(D1 + SEP + D1, re.I)                                   # 3 Jan 2027 → 9 Jan 2027
RX_SHORT = re.compile(r'(\d{1,2})(?:st|nd|rd|th|er|\.)?' + SEP + r'(\d{1,2})(?:st|nd|rd|th|er|\.)?\s+(?:of\s+)?(' + NOMS + r')\.?,?\s+(20\d\d)', re.I)  # 3-9 Jan 2027
RX_NUM = re.compile(r'(\d{1,2})[./](\d{1,2})[./](20\d\d)' + SEP + r'(\d{1,2})[./](\d{1,2})[./](20\d\d)')
RX_ISO = re.compile(r'(20\d\d)-(\d\d)-(\d\d)' + SEP + r'(20\d\d)-(\d\d)-(\d\d)')


def texte(u):
    try:
        t = subprocess.run(['curl', '-sL', '-m', '25', '-A', 'Mozilla/5.0', u], capture_output=True).stdout.decode('utf-8', 'replace')
    except Exception:
        return ''
    t = re.sub(r'(?s)<(script|style).*?</\1>', ' ', t)
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', t)))


def plages(t):
    out = set()
    def add(a, b):
        if AUJ <= a <= MAXI and a <= b and (b - a).days <= 120:
            out.add((a.isoformat(), b.isoformat()))
    for m in RX_FULL.finditer(t):
        g = m.groups()
        try: add(datetime.date(int(g[2]), MN[g[1].lower()], int(g[0])), datetime.date(int(g[5]), MN[g[4].lower()], int(g[3])))
        except Exception: pass
    for m in RX_SHORT.finditer(t):
        g = m.groups()
        try: add(datetime.date(int(g[3]), MN[g[2].lower()], int(g[0])), datetime.date(int(g[3]), MN[g[2].lower()], int(g[1])))
        except Exception: pass
    for m in RX_NUM.finditer(t):
        g = [int(x) for x in m.groups()]
        try: add(datetime.date(g[2], g[1], g[0]), datetime.date(g[5], g[4], g[3]))
        except Exception: pass
    for m in RX_ISO.finditer(t):
        g = [int(x) for x in m.groups()]
        try: add(datetime.date(g[0], g[1], g[2]), datetime.date(g[3], g[4], g[5]))
        except Exception: pass
    return sorted(out)


def main():
    d = json.load(open(F, encoding='utf-8'))
    L = d['offres']
    cache = json.load(open(C)) if os.path.exists(C) else {}
    cible = [e for e in L if not e.get('debut') and not e.get('hors_offre') and str(e.get('lien', '')).startswith('http')]
    urls = sorted({e['lien'] for e in cible})
    if sys.argv[1] == 'sonde':
        todo = [u for u in urls if u not in cache]
        with ThreadPoolExecutor(12) as ex:
            for u, t in zip(todo, ex.map(texte, todo)):
                cache[u] = plages(t)
        json.dump(cache, open(C, 'w'))
    import collections
    st = collections.defaultdict(lambda: [0, 0])
    n = 0
    for e in cible:
        p = cache.get(e['lien'], [])
        st[e['ecole_slug']][0] += 1
        if p:
            st[e['ecole_slug']][1] += 1
            if sys.argv[1] == 'applique':
                a, b = (datetime.date.fromisoformat(x) for x in p[0])
                e['debut'], e['fin'] = a.isoformat(), b.isoformat()
                e['duree_jours'] = (b - a).days + 1
                e['verifie'] = AUJ.isoformat()
                n += 1
    if sys.argv[1] == 'applique':
        json.dump(d, open(F, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        print('datées', n)
    print('école: [sans date, avec plage]')
    for k, v in sorted(st.items(), key=lambda x: -x[1][1]):
        if v[1]: print(v, k)
    print('total avec plage', sum(v[1] for v in st.values()))


main()
