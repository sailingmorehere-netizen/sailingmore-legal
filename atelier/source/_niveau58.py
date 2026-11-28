"""Passe 58 : lit la page `lien` (GET seul) et pose niveau seulement si <title>/<h1>/meta description
disent explicitement debutant OU confirme (jamais les deux). Sinon vide. Ne touche pas un niveau present."""
import json, re, os, html, shutil, subprocess, concurrent.futures as cf
P = 'projets/sailingmore/stages.json'
C = 'scripts/_niveau58_cache.json'
if not os.path.exists(P + '.bak-avant-58'):
    shutil.copy(P, P + '.bak-avant-58')
d = json.load(open(P + '.bak-avant-58', encoding='utf-8'))
L = d['offres']
cache = json.load(open(C)) if os.path.exists(C) else {}

def tete(url):
    try:
        b = subprocess.run(['curl', '-sL', '--max-time', '20', '-A', 'Mozilla/5.0', url],
                           capture_output=True, timeout=30).stdout.decode('utf-8', 'ignore')
    except Exception:
        return None
    if not b:
        return None
    out = []
    for rx in (r'<title[^>]*>(.*?)</title>', r'<h1[^>]*>(.*?)</h1>',
               r'<meta[^>]+name=["\']description["\'][^>]+content=["\'](.*?)["\']',
               r'<meta[^>]+property=["\']og:description["\'][^>]+content=["\'](.*?)["\']'):
        for m in re.findall(rx, b, re.I | re.S):
            out.append(html.unescape(re.sub(r'<[^>]+>', ' ', m)))
    return ' | '.join(out)

urls = sorted({e['lien'] for e in L if not e.get('niveau') and e.get('lien') and e['lien'] not in cache})
with cf.ThreadPoolExecutor(8) as ex:
    for u, t in zip(urls, ex.map(tete, urls)):
        cache[u] = t
json.dump(cache, open(C, 'w'), ensure_ascii=False)

DEB = re.compile(r'\bbeginners?\b|for beginners|no (previous |prior )?experience|d[ée]butants?\b|anf[äa]nger|'
                 r'keine vorkenntnisse|voor beginners|principiantes?\b|principianti|iniciaci[óo]n|iniciantes?|pocz[ąa]tkuj', re.I)
CON = re.compile(r'\badvanced\b|experienced sailors|exp[ée]riment[ée]s|confirm[ée]s?\b|fortgeschritten|'
                 r'gevorderd|avanzad[oa]|esperti|zaawansowan', re.I)
nn = 0
for e in L:
    if e.get('niveau'):
        continue
    t = cache.get(e.get('lien') or '') or ''
    a, b = bool(DEB.search(t)), bool(CON.search(t))
    if a != b:
        e['niveau'] = 'debutant' if a else 'confirme'
        nn += 1
print('poses', nn, '; vides', sum(1 for e in L if not e.get('niveau')), '; pages nulles', sum(1 for v in cache.values() if not v))

# --- 2e etape : corps de page, phrases explicites seulement ---
CB = 'scripts/_niveau58_corps.json'
corps = json.load(open(CB)) if os.path.exists(CB) else {}
def texte(url):
    try:
        b = subprocess.run(['curl', '-sL', '--max-time', '20', '-A', 'Mozilla/5.0', url],
                           capture_output=True, timeout=30).stdout.decode('utf-8', 'ignore')
    except Exception:
        return None
    b = re.sub(r'(?is)<(script|style|nav|header|footer|noscript)\b.*?</\1>', ' ', b)
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', b)))[:40000]
urls = sorted({e['lien'] for e in L if not e.get('niveau') and e.get('lien') and e['lien'] not in corps})
with cf.ThreadPoolExecutor(8) as ex:
    for u, t in zip(urls, ex.map(texte, urls)):
        corps[u] = t
json.dump(corps, open(CB, 'w'), ensure_ascii=False)
DEB2 = re.compile(r'(suitable|ideal|perfect|designed|aimed|geared|open) (for|to) (complete |absolute |total )?beginners|'
                  r'no (previous |prior |sailing )?experience (is )?(needed|necessary|required)|(complete|absolute) beginners?|'
                  r'geschikt voor beginners|voor beginners|geen ervaring (nodig|vereist)|f[üu]r anf[äa]nger|ohne vorkenntnisse|keine vorkenntnisse|'
                  r'pour (les )?d[ée]butants|niveau\s*:?\s*d[ée]butant|aucune exp[ée]rience|sin experiencia previa|para principiantes|'
                  r'per principianti|nessuna esperienza|n[ií]vel\s*:?\s*iniciante', re.I)
CON2 = re.compile(r'(for|to) (more )?(experienced|advanced) (sailors|skippers|crew|students)|'
                  r'(prior|previous|solid|good) (sailing )?experience (is )?(required|needed|necessary)|'
                  r'voor gevorderden|f[üu]r fortgeschrittene|pour (les )?(marins )?confirm[ée]s|niveau\s*:?\s*confirm[ée]|'
                  r'para (navegantes )?(avanzados|experimentados)|per esperti', re.I)
n2 = 0
for e in L:
    if e.get('niveau'):
        continue
    t = corps.get(e.get('lien') or '') or ''
    a, b = bool(DEB2.search(t)), bool(CON2.search(t))
    if a != b:
        e['niveau'] = 'debutant' if a else 'confirme'
        n2 += 1
json.dump(d, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('etape 2 poses', n2, '; vides', sum(1 for e in L if not e.get('niveau')))
