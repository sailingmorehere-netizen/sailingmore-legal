#!/usr/bin/env python3
# © 2026 Sailing More — tous droits réservés. All rights reserved.
"""Garde-fou SEO : mesure les 9 défauts de gabarit sur les pages HTML du site.

Usage : python3 scripts/seo_garde_fou.py [--exemples N]
Sortie : un compteur par défaut, hors pages « noindex ». Code retour 0 si tous
les compteurs sont à zéro, 1 sinon. Lecture seule : rien n'est écrit.

Défauts mesurés (tâche n°46) :
  og_image, og_image_alt, og_title, og_description, og_url,
  title_longueur (15-65), description_longueur (60-165),
  maillage_absent (aucun lien interne <a href> dans le HTML brut),
  jsonld_absent, jsonld_fil_ariane_seul, date_modified_absente,
  og_image_relative, hors_sitemap.
"""
import glob
import json
import os
import re
import sys
from collections import defaultdict

RACINE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
SITE = os.path.join(RACINE, 'projets', 'sailingmore', 'site')
DOMAINE = 'https://sailingmore.fr'

RE_META = r'<meta\s+[^>]*?(?:property|name)="%s"[^>]*?>'


def meta(t, nom):
    m = re.search(RE_META % re.escape(nom), t, re.I)
    if not m:
        return None
    c = re.search(r'content="([^"]*)"', m.group(0))
    return c.group(1) if c else ''


def charge_sitemaps():
    urls = set()
    for f in glob.glob(os.path.join(SITE, 'sitemap*.xml')):
        s = open(f, encoding='utf-8', errors='replace').read()
        urls.update(re.findall(r'<loc>\s*([^<\s]+)\s*</loc>', s))
    return urls


def url_page(chemin):
    rel = os.path.relpath(chemin, SITE).replace(os.sep, '/')
    return DOMAINE + '/' + rel


def jsonld(t):
    blocs = []
    for m in re.finditer(r'<script[^>]*application/ld\+json[^>]*>(.*?)</script>', t, re.S | re.I):
        try:
            blocs.append(json.loads(m.group(1)))
        except ValueError:
            blocs.append(None)
    return blocs


def types(bloc):
    out = []
    if isinstance(bloc, list):
        for b in bloc:
            out += types(b)
    elif isinstance(bloc, dict):
        if '@graph' in bloc:
            out += types(bloc['@graph'])
        ty = bloc.get('@type')
        out += ty if isinstance(ty, list) else [ty]
    return [x for x in out if x]


def main():
    n_ex = 3
    if '--exemples' in sys.argv:
        n_ex = int(sys.argv[sys.argv.index('--exemples') + 1])
    sitemap = charge_sitemaps()
    cpt = defaultdict(int)
    ex = defaultdict(list)
    total = noindex = 0

    def note(cle, chemin):
        cpt[cle] += 1
        if len(ex[cle]) < n_ex:
            ex[cle].append(os.path.relpath(chemin, SITE))

    for chemin in glob.glob(os.path.join(SITE, '**', '*.html'), recursive=True):
        t = open(chemin, encoding='utf-8', errors='replace').read()
        total += 1
        rob = meta(t, 'robots') or ''
        if 'noindex' in rob.lower():
            noindex += 1
            continue
        if re.search(r'http-equiv="refresh"', t, re.I) or '<html' not in t.lower():
            continue  # redirection ou fragment, pas une page
        img = meta(t, 'og:image')
        if not img:
            note('og_image', chemin)
        elif not img.startswith(('http://', 'https://')):
            note('og_image_relative', chemin)
        if not meta(t, 'og:image:alt'):
            note('og_image_alt', chemin)
        if not meta(t, 'og:title'):
            note('og_title', chemin)
        if not meta(t, 'og:description'):
            note('og_description', chemin)
        if not meta(t, 'og:url'):
            note('og_url', chemin)
        m = re.search(r'<title[^>]*>(.*?)</title>', t, re.S | re.I)
        if not m or not 15 <= len(m.group(1).strip()) <= 65:
            note('title_longueur', chemin)
        d = meta(t, 'description')
        if d is None or not 60 <= len(d) <= 165:
            note('description_longueur', chemin)
        corps = re.sub(r'<script.*?</script>', '', t, flags=re.S | re.I)
        liens = re.findall(r'<a\s[^>]*href="(/[^"#]*|[^"#:]*\.html[^"]*)"', corps, re.I)
        if not liens:
            note('maillage_absent', chemin)
        blocs = jsonld(t)
        if not blocs:
            note('jsonld_absent', chemin)
        else:
            ts = set()
            for b in blocs:
                ts.update(types(b))
            if ts and ts <= {'BreadcrumbList'}:
                note('jsonld_fil_ariane_seul', chemin)
        if 'dateModified' not in t:
            note('date_modified_absente', chemin)
        if url_page(chemin) not in sitemap and url_page(chemin).removesuffix('.html') not in sitemap:
            note('hors_sitemap', chemin)

    cles = ['og_image', 'og_image_alt', 'og_title', 'og_description', 'og_url',
            'title_longueur', 'description_longueur', 'maillage_absent',
            'jsonld_absent', 'jsonld_fil_ariane_seul', 'date_modified_absente',
            'og_image_relative', 'hors_sitemap']
    print('pages : %d, noindex écartées : %d, mesurées : %d' % (total, noindex, total - noindex))
    for c in cles:
        print('%-26s %6d  %s' % (c, cpt[c], ', '.join(ex[c])))
    return 0 if not any(cpt[c] for c in cles) else 1


if __name__ == '__main__':
    sys.exit(main())
