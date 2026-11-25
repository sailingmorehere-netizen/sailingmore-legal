"""Tâche 47 : lit (GET seulement) la page de chaque offre sans date et relève les dates publiées.
python3 scripts/_dates47.py sonde   -> télécharge + écrit scripts/_dates47_cache.json, résumé par école
python3 scripts/_dates47.py applique -> écrit debut (col 7) dans stages-proches.json"""
import json, os, re, sys, html, subprocess, datetime
from concurrent.futures import ThreadPoolExecutor
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
F = os.path.join(R, 'projets/sailingmore/site/stages-proches.json')
C = os.path.join(R, 'scripts/_dates47_cache.json')
AUJ = datetime.date(2026, 11, 25)
MOIS = {}
for i, ns in enumerate([
    'january jan januari janvier janv januar gennaio enero janeiro',
    'february feb februari février fevrier févr februar febbraio febrero fevereiro',
    'march mar maart mars märz marz marzo marzo março',
    'april apr avril aprile abril',
    'may mei mai maggio mayo maio',
    'june jun juni juin giugno junio junho',
    'july jul juli juillet juil luglio julio julho',
    'august aug augustus août aout agosto',
    'september sep sept septembre settembre septiembre setembro',
    'october oct okt oktober octobre ottobre octubre outubro',
    'november nov novembre noviembre novembro',
    'december dec dez december décembre decembre dicembre diciembre dezembro'], 1):
    for n in ns.split():
        MOIS[n] = i
NOMS = '|'.join(sorted(MOIS, key=len, reverse=True))
RX = [
    (re.compile(r'\b(20\d\d)-(\d\d)-(\d\d)\b'), 'ymd'),
    (re.compile(r'\b(\d{1,2})(?:st|nd|rd|th|er|\.)?\s+(?:of\s+)?(' + NOMS + r')\.?,?\s+(20\d\d)\b', re.I), 'dmy'),
    (re.compile(r'\b(' + NOMS + r')\.?\s+(\d{1,2})(?:st|nd|rd|th)?,?\s+(20\d\d)\b', re.I), 'mdy'),
    (re.compile(r'\b(\d{1,2})[./](\d{1,2})[./](20\d\d)\b'), 'dmyn'),
]


def texte(u):
    try:
        t = subprocess.run(['curl', '-sL', '-m', '20', '-A', 'Mozilla/5.0', u], capture_output=True).stdout.decode('utf-8', 'replace')
    except Exception:
        return ''
    t = re.sub(r'(?s)<(script|style).*?</\1>', ' ', t)
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', t)))


def dates(t, u):
    out = set()
    for rx, k in RX:
        for m in rx.finditer(t + ' ' + u):
            g = m.groups()
            try:
                if k == 'ymd': d = datetime.date(int(g[0]), int(g[1]), int(g[2]))
                elif k == 'dmy': d = datetime.date(int(g[2]), MOIS[g[1].lower()], int(g[0]))
                elif k == 'mdy': d = datetime.date(int(g[2]), MOIS[g[0].lower()], int(g[1]))
                else: d = datetime.date(int(g[2]), int(g[1]), int(g[0]))
            except Exception:
                continue
            if AUJ <= d <= datetime.date(2028, 12, 31):
                out.add(d.isoformat())
    return sorted(out)


def main():
    d = json.load(open(F))
    cache = json.load(open(C)) if os.path.exists(C) else {}
    cible = sorted({o[10] for o in d['o'] if not o[7] and o[10].startswith('http')})
    if sys.argv[1] == 'sonde':
        todo = [u for u in cible if u not in cache]
        with ThreadPoolExecutor(12) as ex:
            for u, t in zip(todo, ex.map(texte, todo)):
                cache[u] = dates(t, u)
        json.dump(cache, open(C, 'w'))
    import collections
    st = collections.defaultdict(lambda: [0, 0, 0])
    n = 0
    for o in d['o']:
        if o[7]: continue
        ds = cache.get(o[10], [])
        st[o[4]][0] += 1
        if len(ds) == 1: st[o[4]][1] += 1
        elif ds: st[o[4]][2] += 1
        if sys.argv[1] == 'applique' and len(ds) == 1:
            o[7] = ds[0]; n += 1
    if sys.argv[1] == 'applique':
        json.dump(d, open(F, 'w'), ensure_ascii=False, separators=(',', ':'))
        print('écrit', n)
    for e, v in sorted(st.items(), key=lambda x: -x[1][0]):
        print(v, e)


main()
