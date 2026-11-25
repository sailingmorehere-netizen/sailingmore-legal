#!/usr/bin/env python3
"""Contrôle de la charte graphique v2.0 — c'est ce script qui tranche, pas une impression.

Lit les pages du site (les *.html de la racine, hors pavillon-* et hors _*) et sort, page par page :
familles typographiques, couleurs employées et leur rôle, tailles sous 12 px, rayons, ombres,
largeurs de colonne. Puis les contrastes AA des couples de jetons.
Code de sortie 1 dès qu'une page sort de la charte (projets/sailingmore/jetons.json).

    python3 scripts/controle_charte.py            # rapport complet + verdict
    python3 scripts/controle_charte.py -q         # verdict et violations seulement
"""
import collections, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import jetons_charte as jc

RE_HEX = jc.RE_HEX
RE_FAM = jc.RE_FAM
RE_PX = re.compile(r'font-size:\s*(\d+(?:\.\d+)?)px')
RE_OMBRE = re.compile(r'box-shadow:\s*([^;}"]+)')
RE_LARG = re.compile(r'max-width:\s*([0-9.]+(?:px|rem|ch))')
RE_RGBA = re.compile(r'rgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)')
RAYONS_OK = {'0', '4px', '12px', '18px', '999px', '50%', 'inherit', 'none', 'initial'}


def norm_ombre(v):
    return re.sub(r'\s+', ' ', v.replace('!important', '')).strip()


def lum(h):
    h = h.lstrip('#')
    if len(h) == 3:
        h = ''.join(c * 2 for c in h)
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    c = [x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]


def ratio(a, b):
    la, lb = sorted((lum(a), lum(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def mesure_page(t, j):
    noyau = {c['v'].lower(): k for k, c in j['couleurs'].items()}
    ill = j['illustration']
    t = jc.RE_BLOC.sub('', t)  # le bloc de jetons est la source, pas un emploi
    r = {}
    r['familles'] = collections.Counter(m.group(1).strip().replace('!important', '').strip() for m in RE_FAM.finditer(t))
    couleurs = collections.Counter(m.group(0).lower() for m in RE_HEX.finditer(t))
    r['couleurs'] = couleurs
    r['noyau'] = {c: n for c, n in couleurs.items() if c in noyau}
    r['illus'] = {c: n for c, n in couleurs.items() if c not in noyau}
    r['petites'] = collections.Counter(m.group(1) for m in RE_PX.finditer(t) if float(m.group(1)) < 12)
    r['rayons'] = collections.Counter(tok for m in jc.RE_RAY.finditer(t)
                                      for tok in m.group(1).replace('!important', '').split())
    r['ombres'] = collections.Counter(norm_ombre(m.group(1)) for m in RE_OMBRE.finditer(t))
    r['largeurs'] = collections.Counter(RE_LARG.findall(t))
    r['rgba'] = collections.Counter('%s,%s,%s' % m for m in RE_RGBA.findall(t))
    return r


def main():
    quiet = '-q' in sys.argv
    j = jc.charge()
    noyau = {c['v'].lower() for c in j['couleurs'].values()}
    ombres_ok = set(j['ombres_tolerees'])
    larg_ok = set(j['largeurs_toleres'])
    bloc = jc.bloc(j)
    fautes = []
    pages = jc.pages()
    if not quiet:
        print('Charte v%s — %d pages mesurées\n' % (j['version'], len(pages)))
    for p in pages:
        nom = os.path.basename(p)
        with open(p, encoding='utf-8') as f:
            t = f.read()
        r = mesure_page(t, j)
        ill_ok = set(j['illustration'].get(nom, {}))
        f_ = []
        if bloc not in t:
            f_.append('bloc <style id="jetons"> absent ou différent de celui que produit jetons_charte.py')
        if re.search(r'@font-face\{font-family:"Inter SM"', jc.RE_BLOC.sub('', t)):
            f_.append('@font-face de la police hors du bloc de jetons (doublon)')
        if not re.search(r'<meta[^>]+name=["\']viewport', t):
            f_.append('pas de meta viewport (illisible sur téléphone)')
        for c in r['illus']:
            if c not in ill_ok:
                f_.append('couleur hors charte %s (×%d)' % (c, r['illus'][c]))
        for fam in r['familles']:
            if not fam.startswith(('var(--police', 'var(--mono', 'var(--livre', 'inherit')):
                f_.append('famille hors charte : %s' % fam[:60])
        for s, n in r['petites'].items():
            f_.append('taille %spx < 12 px (×%d)' % (s, n))
        for ray in r['rayons']:
            if ray not in RAYONS_OK and not ray.startswith('var(--r-'):
                f_.append('rayon hors échelle : %s' % ray)
        for o in r['ombres']:
            if o not in ombres_ok:
                f_.append('ombre hors charte : %s' % o[:70])
        for w in r['largeurs']:
            if w not in larg_ok:
                f_.append('largeur de colonne hors charte : %s' % w)
        fautes += ['%s : %s' % (nom, x) for x in f_]
        if not quiet:
            print('%-32s %s' % (nom, 'OK' if not f_ else '%d écart(s)' % len(f_)))
            print('   familles : %s' % ', '.join('%s×%d' % (k[:24], v) for k, v in r['familles'].most_common()))
            print('   couleurs : %d jetons (%d emplois), %d d\'illustration (%d emplois)' % (
                len(r['noyau']), sum(r['noyau'].values()), len(r['illus']), sum(r['illus'].values())))
            print('   < 12 px  : %s | rayons : %s' % (dict(r['petites']) or 'aucun', ', '.join(sorted(r['rayons'])) or '-'))
            print('   ombres   : %d valeur(s) | colonnes : %s' % (len(r['ombres']), ', '.join(sorted(r['largeurs'])) or '-'))
    # contrastes AA des couples de jetons
    if not quiet:
        print('\nContrastes AA (couples de jetons) :')
    for c in j['contrastes']:
        fg, bg = j['couleurs'][c['fg']]['v'], j['couleurs'][c['bg']]['v']
        rr = ratio(fg, bg)
        ok = rr >= c['min']
        if not quiet:
            print('   %-13s sur %-9s %5.2f:1 (min %.1f) %s' % (c['fg'], c['bg'], rr, c['min'], 'OK' if ok else 'RATÉ'))
        if not ok:
            fautes.append('contraste raté : %s sur %s = %.2f:1 (min %.1f)' % (c['fg'], c['bg'], rr, c['min']))
    # un jeton d'illustration ne doit pas doubler un jeton du noyau
    for nom, d in j['illustration'].items():
        for c in d:
            if c.lower() in noyau:
                fautes.append('%s : %s est listé en illustration alors que c\'est un jeton' % (nom, c))
    print()
    if fautes:
        print('CHARTE NON RESPECTÉE — %d écart(s) :' % len(fautes))
        for x in fautes[:200]:
            print('  -', x)
        sys.exit(1)
    print('CHARTE RESPECTÉE — %d pages, 0 écart.' % len(pages))


if __name__ == '__main__':
    main()
