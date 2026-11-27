"""Tâche 47 : niveau annoncé sur la page de l'école (lecture seule). Cache : _niveau47_cache.json.
Usage: _niveau47.py sonde [n]   -> affiche les extraits trouvés pour n offres sans niveau
       _niveau47.py applique    -> écrit niveau dans stages.json pour les extraits sans ambiguïté"""
import json, os, re, sys, urllib.request, html
from concurrent.futures import ThreadPoolExecutor
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SJ = os.path.join(R, 'projets/sailingmore/stages.json')
CA = os.path.join(R, 'scripts/_niveau47_cache.json')
cache = json.load(open(CA)) if os.path.exists(CA) else {}

def fetch(u):
    if u in cache:
        return cache[u]
    try:
        rq = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0 (lecture)'})
        t = urllib.request.urlopen(rq, timeout=20).read(400000).decode('utf-8', 'ignore')
        t = re.sub(r'(?s)<(script|style|nav|footer|header)\b.*?</\1>', ' ', t)
        t = html.unescape(re.sub(r'<[^>]+>', ' ', t))
        t = re.sub(r'\s+', ' ', t)
    except Exception as e:
        t = 'ERR ' + str(e)[:80]
    cache[u] = t
    return t

# Étiquette explicite de niveau : « Level/Niveau/Level: X »
LAB = re.compile(r'(?:niveau|level|livello|nivel|nível|niveaus?|stufe|poziom|skill level|experience|ervaring)\s*(?:requis|required)?\s*[:\-–]\s*'
                 r'([A-Za-zÀ-ÿ ,/&\-]{3,60})', re.I)
MAP = [('debutant', r'd[ée]butant|beginner|principiant|anf[äa]nger|iniciaci|initiant|novice|starter|beginners|no experience|geen ervaring|ohne vorkenntnisse|nessuna esperienza|nivel b[áa]sico|livello base|basic'),
       ('confirme', r'confirm|advanced|expert|avanzat|fortgeschritten|avan[cç]ado|zaawansowan|experienced|gevorderd|professional'),
       ('intermediaire', r'interm[ée]diaire|intermediate|improver|mittel|intermedi|medio|gemiddeld|[śs]redni|progress')]

def classe(txt):
    m = LAB.search(txt)
    if not m:
        return None, None
    s = m.group(1)
    got = {k for k, p in MAP if re.search(p, s, re.I)}
    return (got.pop() if len(got) == 1 else None), m.group(0)

if __name__ == '__main__':
    d = json.load(open(SJ))
    offs = d['offres']
    todo = [e for e in offs if not e.get('niveau') and e.get('lien')]
    if sys.argv[1] == 'sonde':
        todo = todo[:int(sys.argv[2])]
    urls = sorted({e['lien'] for e in todo})
    with ThreadPoolExecutor(8) as ex:
        list(ex.map(fetch, urls))
    json.dump(cache, open(CA, 'w'))
    n = 0
    stats = {}
    for e in todo:
        nv, ex_ = classe(cache.get(e['lien'], ''))
        stats[e['ecole_slug']] = stats.get(e['ecole_slug'], [0, 0])
        stats[e['ecole_slug']][0] += 1
        if nv:
            stats[e['ecole_slug']][1] += 1
            n += 1
            if sys.argv[1] == 'applique':
                e['niveau'] = nv
                e['niveau_src'] = 'page ecole'
            else:
                print(e['ecole_slug'], '|', e['titre'][:40], '|', ex_, '->', nv)
    print('trouvés', n, 'sur', len(todo))
    print(stats)
    errs = sum(1 for u in urls if cache[u].startswith('ERR'))
    print('erreurs réseau', errs, 'sur', len(urls))
    if sys.argv[1] == 'applique':
        json.dump(d, open(SJ, 'w'), ensure_ascii=False, indent=1)
