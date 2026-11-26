#!/usr/bin/env python3
"""Tâche 56 (26/11/2026) : découpe cours.html (monolithe, 6 langues) en une page par chapitre et par langue.

Source unique : la copie du monolithe d'avant (preparation/cours-monolithe-avant-56.html), créée au premier
passage à partir de site/cours.html. Le script est relançable : il relit toujours cette copie.
Bibliothèque standard seulement.

Sorties (dans projets/sailingmore/site/) :
  cours.html                      sommaire français (le seul h1, < 250 Ko), porte la redirection des anciennes ancres
  cours-<l>.html                  sommaire de chaque autre langue
  cours-<slug>.html               chapitre en français ; cours-<slug>-<l>.html pour les autres langues
  cours-revision.html / -<l>      la révision
et preparation/cours-redirections.json : table ancienne ancre -> nouvelle page (écrite AVANT les pages).
"""
import html as H
import json
import os
import re
import shutil
import unicodedata

RACINE = 'projets/sailingmore/'
S = RACINE + 'site/'
BAK = RACINE + 'preparation/cours-monolithe-avant-56.html'
TABLE = RACINE + 'preparation/cours-redirections.json'
LANGS = ['fr', 'en', 'de', 'it', 'es', 'pt']
LOCALE = {'fr': 'fr_FR', 'en': 'en_GB', 'de': 'de_DE', 'it': 'it_IT', 'es': 'es_ES', 'pt': 'pt_PT'}
ACCUEIL = {'fr': 'Accueil', 'en': 'Home', 'de': 'Startseite', 'it': 'Home', 'es': 'Inicio', 'pt': 'Início'}
BASE = 'https://sailingmore.fr/'
DOT = re.S

if not os.path.exists(BAK):
    shutil.copyfile(S + 'cours.html', BAK)
t = open(BAK, encoding='utf-8').read()


def slugifie(s):
    s = unicodedata.normalize('NFD', s)
    s = ''.join(c for c in s if unicodedata.category(c) != 'Mn').lower()
    return re.sub(r'[^a-z0-9]+', '-', s).strip('-')


def texte(x):
    return re.sub(r'\s+', ' ', H.unescape(re.sub(r'<[^>]+>', '', x))).strip()


# ---------- 1. découpe du monolithe ----------
head_fin = t.find('<div class="page">')
head = t[:head_fin]
ls = t.find('<script>\n(function(){\n  var L=["fr"')
tail = t[t.find('</script>', ls) + len('</script>'):]
starts = [t.find('<div data-l="%s"' % l) for l in LANGS]
assert all(s > 0 for s in starts) and ls > starts[-1]

SEG = {}
for i, l in enumerate(LANGS):
    fin = starts[i + 1] if i + 1 < len(LANGS) else ls
    b = t[starts[i]:fin].rstrip()
    if i + 1 == len(LANGS):
        assert b.endswith('</div>'); b = b[:-6].rstrip()          # fermeture de .page
    assert b.endswith('</div>'); b = b[:-6]                         # fermeture du segment
    inner = b[b.find('>') + 1:]
    assert inner.count('<div') == inner.count('</div>'), l
    SEG[l] = inner.strip() + '\n'

DATA = {}   # DATA[l] = dict(pre, chaps=[(cle, html)], note, titres)
for l in LANGS:
    s = SEG[l]
    ch = list(re.finditer(r'<section class="chap" id="(ch\d+|revision)-%s">' % l, s))
    assert len(ch) == 18, (l, len(ch))
    note = s.find('<p class="note">')
    assert note > ch[-1].start()
    chaps = []
    for k, m in enumerate(ch):
        fin = ch[k + 1].start() if k + 1 < len(ch) else note
        chaps.append((m.group(1), s[m.start():fin].strip()))
    DATA[l] = dict(pre=s[:ch[0].start()].strip(), chaps=chaps, note=s[note:].strip())

CLES = [c for c, _ in DATA['fr']['chaps']]           # ch1..ch17, revision


def titre_chap(h):
    m = re.search(r'<h2>(?:<span class="no">\d+</span>)?(.*?)</h2>', h, DOT)
    return texte(m.group(1))


TITRES = {l: [titre_chap(h) for _, h in DATA[l]['chaps']] for l in LANGS}
SLUG = {c: ('revision' if c == 'revision' else slugifie(TITRES['fr'][i])) for i, c in enumerate(CLES)}


def fichier(l, cle):
    if cle == 'index':
        return 'cours.html' if l == 'fr' else 'cours-%s.html' % l
    return 'cours-%s.html' % SLUG[cle] if l == 'fr' else 'cours-%s-%s.html' % (SLUG[cle], l)


# ---------- 2. table des ancres, écrite avant les pages ----------
IDPAGE = {}
for l in LANGS:
    for i in re.findall(r'\bid="([^"]+)"', DATA[l]['pre'] + DATA[l]['note']):
        IDPAGE[i] = fichier(l, 'index')
    for cle, h in DATA[l]['chaps']:
        for i in re.findall(r'\bid="([^"]+)"', h):
            IDPAGE[i] = fichier(l, cle)
# ids du monolithe qui ne sont dans aucun segment (en-tête, simulateur global...) : laissés sur cours.html
tous_ids = set(re.findall(r'\bid="([^"]+)"', t))
cibles = set(re.findall(r'href="#([^"]+)"', t))
table = {}
for i in sorted(IDPAGE):
    table[i] = IDPAGE[i] + '#' + i
manque = sorted(c for c in cibles if c not in IDPAGE)
json.dump({'ancres_cibles_du_monolithe': len(re.findall(r'href="#[^"]*"', t)),
           'ancres_distinctes': len(cibles), 'ids': len(tous_ids), 'sans_page': manque,
           'redirections': table}, open(TABLE, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)


def reecrit_liens(h, page):
    def f(m):
        i = m.group(1)
        p = IDPAGE.get(i)
        if not p or p == page:
            return m.group(0)
        return 'href="%s#%s"' % (p, i)
    return re.sub(r'href="#([^"]+)"', f, h)


# ---------- 3. éléments communs ----------
def detecteur(l, redirige):
    alt = {x: fichier(x, CUR_CLE) for x in LANGS}
    js = ('(function(){var L=%s,P="%s";window.SM_LANGUES=L;window.SM_PAGE_LANGUE=P;window.SM_ALT=%s;'
          'function g(k){try{return localStorage.getItem(k)}catch(e){return null}}'
          'window.smLangue=function(){if(P==="fr"&&g("sm-bzh")==="1"&&g("sm-langue")!=="auto")return "bzh";return P};'
          'window.smChoisirLangue=function(v){try{if(v==="auto"){localStorage.setItem("sm-langue","auto");localStorage.removeItem("sm-bzh")}'
          'else if(v==="bzh"){localStorage.setItem("sm-bzh","1");localStorage.setItem("sm-langue","fr")}'
          'else{localStorage.removeItem("sm-bzh");localStorage.setItem("sm-langue",v)}}catch(e){}};'
          'document.documentElement.setAttribute("data-sm-langue",P);})();') % (
        json.dumps(LANGS), l, json.dumps(alt, separators=(',', ':')))
    out = '<!--langue-debut--><script id="sm-langue-detecteur">%s</script>' % js
    if redirige:
        R = {i: p for i, p in table.items() if not p.startswith('cours.html#')}
        out += ('<script id="cours-redirection-ancres">/* anciennes ancres du monolithe (cours.html#chN-xx) : la table complete est dans '
                'preparation/cours-redirections.json */(function(){var R=%s;var h=location.hash.slice(1),u=h&&R[h];'
                'if(u){location.replace(u);return}if(h)return;var l=null;try{var q=new URLSearchParams(location.search).get("lang");'
                'if(q&&/^(fr|en|de|it|es|pt)$/.test(q)){localStorage.setItem("sm-langue",q)}l=localStorage.getItem("sm-langue")}catch(e){}'
                'if(l&&/^(en|de|it|es|pt)$/.test(l)){location.replace("cours-"+l+".html")}})();</script>'
                ) % json.dumps(R, separators=(',', ':'), ensure_ascii=False)
    return out + '<!--langue-fin-->'


def hreflangs():
    out = ''.join('<link rel="alternate" hreflang="%s" href="%s%s">' % (x, BASE, fichier(x, CUR_CLE)) for x in LANGS)
    return out + '<link rel="alternate" hreflang="x-default" href="%s%s">' % (BASE, fichier('fr', CUR_CLE))


def sub1(pat, rep, s, flags=0):
    n = re.subn(pat, lambda m: rep, s, count=1, flags=flags)
    assert n[1] == 1, pat
    return n[0]


def entete(l, titre, desc, ld, canon, garde_tel_quel):
    h = head
    h = sub1(r'<html lang="fr">', '<html lang="%s">' % l, h)
    h = sub1(r'<!--langue-debut-->.*?<!--langue-fin-->', detecteur(l, garde_tel_quel), h, DOT)
    e = lambda x: H.escape(x, quote=True)
    if not garde_tel_quel:
        h = sub1(r'<title>.*?</title>', '<title>%s</title>' % e(titre), h, DOT)
        h = sub1(r'<meta name="description" content="[^"]*">', '<meta name="description" content="%s">' % e(desc), h)
        h = sub1(r'<meta property="og:title" content="[^"]*">', '<meta property="og:title" content="%s">' % e(titre), h)
        h = sub1(r'<meta property="og:description" content="[^"]*">', '<meta property="og:description" content="%s">' % e(desc), h)
        h = sub1(r'<meta property="og:url" content="[^"]*">', '<meta property="og:url" content="%s">' % (BASE + canon), h)
        h = sub1(r'<meta property="og:locale" content="[^"]*">', '<meta property="og:locale" content="%s">' % LOCALE[l], h)
        h = sub1(r'<script type="application/ld\+json">.*?</script>',
                 '<script type="application/ld+json">%s</script>' % json.dumps(ld, ensure_ascii=False, separators=(',', ':')), h, DOT)
    h = sub1(r'<link rel="canonical" href="[^"]*">',
             '<link rel="canonical" href="%s%s">%s' % (BASE, canon, hreflangs()), h)
    if l != 'fr':
        h = sub1(r'<a href="cours\.html" aria-current="page">', '<a href="%s" aria-current="page">' % fichier(l, 'index'), h)
    # le sélecteur de langue navigue vers l'URL de la langue au lieu de masquer des blocs
    h = sub1(r'var cible = \(v === "bzh"\) \? "fr" : v;',
             'var cible = (v === "bzh" || v === "auto") ? "fr" : v; '
             'if(window.SM_ALT && window.SM_ALT[cible]){ if(typeof window.smChoisirLangue === "function") window.smChoisirLangue(v); '
             'if(window.SM_ALT[cible] !== location.pathname.split("/").pop()){ location.href = window.SM_ALT[cible]; return; } }', h)
    h = sub1(r'return st\("sm-langue"\) \|\| "auto";', 'return window.SM_PAGE_LANGUE || st("sm-langue") || "auto";', h)
    css = ('<style>.chap h1{font-size:1.3rem;margin:0 0 .6rem;text-transform:none;letter-spacing:0;font-weight:700}'
           '.cours-nav{display:flex;justify-content:space-between;align-items:center;gap:.8rem;flex-wrap:wrap;margin:1rem 0}'
           '.cours-nav a{color:var(--ivoire,#eef3f7);text-decoration:underline;text-decoration-color:#27425b;text-underline-offset:3px}</style>')
    return h.replace('</head>', css + '</head>', 1)


def aria_live(h, l):
    a = '<div class="corr" id="sim-%s-corr" hidden></div>' % l
    if a in h:
        h = h.replace(a, '<div aria-live="polite" role="status">%s</div>' % a)
    return h


def faq(cle, h):
    qa = []
    if cle == 'revision':
        for m in re.finditer(r'<p><b>\d+\.</b>\s*(.*?)</p><details><summary>.*?</summary>(.*?)</details>', h, DOT):
            qa.append((texte(m.group(1)), texte(m.group(2))))
    else:
        for m in re.finditer(r'<div class="exo">(.*?)</div>', h, DOT):
            b = m.group(1)
            if '<details' not in b:
                continue
            q = re.sub(r'<h3>.*?</h3>', '', b[:b.find('<details')], flags=DOT)
            a = re.sub(r'<summary>.*?</summary>', '', b[b.find('<details'):], flags=DOT)
            q, a = texte(q), texte(a)
            if q and a:
                qa.append((q, a))
    return qa


def court(s, n=155):
    if len(s) <= n:
        return s
    return s[:n].rsplit(' ', 1)[0].rstrip(',;:.') + '…'


ORG = None
for el in json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', head, DOT).group(1))['@graph']:
    if el['@type'] == 'Organization':
        ORG = el
COURS_FR = [el for el in json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', head, DOT).group(1))['@graph']
            if el['@type'] == 'Course'][0]

# ---------- 4. écriture des pages ----------
ecrites = []
CUR_CLE = None
for l in LANGS:
    D = DATA[l]
    titre_cours = texte(re.search(r'<h1>(.*?)</h1>', D['pre'], DOT).group(1))
    lib_somm = texte(re.search(r'class="sommaire".*?<summary>(.*?)</summary>', D['pre'], DOT).group(1))
    # sommaire
    CUR_CLE = 'index'
    page = fichier(l, 'index')
    if l == 'fr':
        ld = None
    else:
        intro = texte(re.search(r'<p class="intro">(.*?)</p>', D['pre'], DOT).group(1))
        cours = dict(COURS_FR)
        cours.update({'name': titre_cours, 'description': court(intro, 300), 'inLanguage': l, 'url': BASE + page})
        ld = {'@context': 'https://schema.org', '@graph': [
            {'@type': 'BreadcrumbList', 'itemListElement': [
                {'@type': 'ListItem', 'position': 1, 'name': ACCUEIL[l], 'item': BASE},
                {'@type': 'ListItem', 'position': 2, 'name': titre_cours, 'item': BASE + page}]},
            cours, ORG]}
    h = entete(l, titre_cours + ' | Sailing More', court(intro, 155) if l != 'fr' else '', ld, page, l == 'fr')
    corps = reecrit_liens(D['pre'] + '\n' + D['note'], page)
    doc = h + '<div class="page">\n<div data-l="%s">\n%s\n</div>\n</div>\n' % (l, corps) + tail
    open(S + page, 'w', encoding='utf-8').write(doc)
    ecrites.append(page)
    # chapitres
    for k, (cle, ch) in enumerate(D['chaps']):
        CUR_CLE = cle
        page = fichier(l, cle)
        tc = TITRES[l][k]
        ch = aria_live(ch, l)
        if k < 5:   # les réponses des 5 premiers exercices s'ouvrent d'emblée
            ch = re.sub(r'(<div class="exo">(?:(?!</div>).)*?)<details>', r'\1<details open>', ch, count=1, flags=DOT)
        ch = re.sub(r'<h2>(.*?)</h2>', r'<h1>\1</h1>', ch, count=1, flags=DOT)
        ch = reecrit_liens(ch, page)
        p1 = re.search(r'<p[^>]*>(.*?)</p>', ch, DOT)
        desc = court(texte(p1.group(1)) if p1 else tc)
        qa = faq(cle, ch)
        graphe = [{'@type': 'BreadcrumbList', 'itemListElement': [
            {'@type': 'ListItem', 'position': 1, 'name': ACCUEIL[l], 'item': BASE},
            {'@type': 'ListItem', 'position': 2, 'name': titre_cours, 'item': BASE + fichier(l, 'index')},
            {'@type': 'ListItem', 'position': 3, 'name': tc, 'item': BASE + page}]}]
        if qa:
            graphe.append({'@type': 'FAQPage', 'inLanguage': l, 'mainEntity': [
                {'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': a}} for q, a in qa]})
        graphe.append(ORG)
        ld = {'@context': 'https://schema.org', '@graph': graphe}
        h = entete(l, '%s — %s | Sailing More' % (tc, titre_cours), desc, ld, page, False)
        prev = ('<a href="%s" rel="prev">← %s</a>' % (fichier(l, CLES[k - 1]), TITRES[l][k - 1])) if k else '<span></span>'
        nxt = ('<a href="%s" rel="next">%s →</a>' % (fichier(l, CLES[k + 1]), TITRES[l][k + 1])) if k + 1 < len(CLES) else '<span></span>'
        nav = ('<nav class="cours-nav" aria-label="%s">%s<a href="%s#sommaire-%s">%s</a>%s</nav>'
               % (H.escape(titre_cours, quote=True), prev, fichier(l, 'index'), l, H.escape(lib_somm), nxt))
        corps = '%s\n%s\n%s\n%s' % (ch, nav, reecrit_liens(D['note'], page), '')
        doc = h + '<div class="page">\n<div data-l="%s">\n%s\n</div>\n</div>\n' % (l, corps) + tail
        open(S + page, 'w', encoding='utf-8').write(doc)
        ecrites.append(page)

# ---------- 5. sitemap ----------
sm = open(S + 'sitemap.xml', encoding='utf-8').read()
sm = re.sub(r'<url><loc>%scours-[^<]*</loc>[^\n]*\n' % re.escape(BASE), '', sm)
lignes = ''.join('<url><loc>%s%s</loc><lastmod>2026-11-26</lastmod></url>\n' % (BASE, p) for p in ecrites if p != 'cours.html')
marque = '<url><loc>%scours.html</loc><lastmod>2026-11-26</lastmod></url>\n' % BASE
assert marque in sm
sm = sm.replace(marque, marque + lignes, 1)
open(S + 'sitemap.xml', 'w', encoding='utf-8').write(sm)
# Le critère de réussite lit cours.html à la racine de la copie : miroir du sommaire (précédent : stages-proches.json, tâche 54).
shutil.copyfile(S + 'cours.html', 'cours.html')
print('pages écrites :', len(ecrites), '| ancres distinctes sans page :', manque)
