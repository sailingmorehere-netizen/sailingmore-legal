#!/usr/bin/env python3
# © 2026 Sailing More — tous droits réservés. All rights reserved.
"""Contrôle de la découpe du cours (tâche 56). Bibliothèque standard seulement. Sortie 0 si tout passe."""
import glob
import json
import os
import re

S = 'projets/sailingmore/site/'
LANGS = ['fr', 'en', 'de', 'it', 'es', 'pt']
mal = []
pages = sorted(glob.glob(S + 'cours.html') + glob.glob(S + 'cours-*.html'))
cache = {p: open(p, encoding='utf-8').read() for p in pages}
base = {os.path.basename(p): t for p, t in cache.items()}

# critère de Nicolas, appliqué à site/cours.html
t = cache[S + 'cours.html']
h = len(re.findall(r'<h1', t)); k = os.path.getsize(S + 'cours.html') // 1024
print('critère : h1', h, 'Ko', k)
if not (h == 1 and k < 250):
    mal.append('critère cours.html')

n_faq = n_open = n_live = 0
for nom, t in base.items():
    if len(re.findall(r'<h1', t)) != 1:
        mal.append('%s : h1 != 1' % nom)
    m = re.search(r'<html lang="(\w+)"', t)
    lang = m.group(1) if m else None
    if lang not in LANGS:
        mal.append('%s : lang' % nom)
    can = re.search(r'<link rel="canonical" href="https://sailingmore.fr/([^"]+)"', t)
    if not can or can.group(1) != nom:
        mal.append('%s : canonical' % nom)
    alts = dict(re.findall(r'<link rel="alternate" hreflang="([\w-]+)" href="https://sailingmore.fr/([^"]+)"', t))
    if set(alts) != set(LANGS) | {'x-default'} or alts.get(lang) != nom:
        mal.append('%s : hreflang' % nom)
    for lg, f in alts.items():
        if f not in base:
            mal.append('%s : hreflang vers fichier absent %s' % (nom, f))
        elif not re.search(r'hreflang="%s" href="https://sailingmore.fr/%s"' % (lang, re.escape(nom)), base[f]):
            mal.append('%s : hreflang non réciproque avec %s' % (nom, f))
    for blob in re.findall(r'<script type="application/ld\+json">(.*?)</script>', t, re.S):
        try:
            d = json.loads(blob)
            if any(e.get('@type') == 'FAQPage' for e in d['@graph']):
                n_faq += 1
        except Exception as e:
            mal.append('%s : JSON-LD %s' % (nom, e))
    # liens locaux : fichier et ancre
    for href in re.findall(r'href="(cours[^"#]*\.html)(?:#([^"]*))?"', t):
        f, a = href
        if f not in base:
            mal.append('%s : lien mort %s' % (nom, f))
        elif a and ('id="%s"' % a) not in base[f]:
            mal.append('%s : ancre absente %s#%s' % (nom, f, a))
    for a in re.findall(r'href="#([^"]+)"', t):
        if ('id="%s"' % a) not in t:
            mal.append('%s : ancre locale absente #%s' % (nom, a))
    if re.search(r'<div class="exo"><h3>[^<]*</h3>(?:(?!</div>).)*<details open>', t, re.S):
        n_open += 1
    if 'aria-live="polite"' in t:
        n_live += 1
    if ' hidden>' in t[t.find('<div class="page">'):] and 'data-l="' in t and re.search(r'<div data-l="\w+" hidden', t):
        mal.append('%s : segment masqué' % nom)

# la table des redirections
tab = json.load(open('projets/sailingmore/preparation/cours-redirections.json', encoding='utf-8'))
for i, v in tab['redirections'].items():
    f = v.split('#')[0]
    if f not in base or ('id="%s"' % i) not in base[f]:
        mal.append('redirection cassée %s -> %s' % (i, v))
if tab['sans_page']:
    mal.append('ancres sans page : %s' % tab['sans_page'])

sm = open(S + 'sitemap.xml', encoding='utf-8').read()
for nom in base:
    if ('https://sailingmore.fr/%s<' % nom) not in sm:
        mal.append('sitemap : %s absent' % nom)
print('pages', len(base), '| avec FAQPage', n_faq, '| avec 1re réponse ouverte', n_open, '| avec aria-live', n_live,
      '| ancres redirigées', len(tab['redirections']))
print('taille max', max((len(t) // 1024, n) for n, t in base.items()))
print('PROBLÈMES :' if mal else 'TOUT PASSE', *mal[:40], sep='\n')
raise SystemExit(1 if mal else 0)
