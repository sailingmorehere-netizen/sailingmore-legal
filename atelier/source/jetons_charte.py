#!/usr/bin/env python3
"""Jetons de la charte v2.0 : lit projets/sailingmore/jetons.json, produit le bloc
<style id="jetons"> et l'applique à toutes les pages du site (idempotent).

    python3 scripts/jetons_charte.py            # applique (réécrit les pages qui changent)
    python3 scripts/jetons_charte.py --seche    # dit ce qui changerait, n'écrit rien

Source unique : jetons.json. Le contrôle (controle_charte.py) vérifie que chaque page porte
exactement le bloc que ce script produit.
"""
import glob, json, os, re, sys

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(RACINE, 'projets', 'sailingmore', 'site')
JETONS = os.path.join(RACINE, 'projets', 'sailingmore', 'jetons.json')


def charge():
    with open(JETONS, encoding='utf-8') as f:
        return json.load(f)


def pages():
    """Les pages de la charte : *.html à la racine du site, hors pavillon-* et hors _*."""
    return sorted(p for p in glob.glob(os.path.join(SITE, '*.html'))
                  if not os.path.basename(p).startswith(('pavillon-', '_')))


def bloc(j=None):
    j = j or charge()
    pol = j['police']
    ff = ''.join('@font-face{font-family:"%s";src:url(%s) format("woff");font-weight:%s;font-display:swap}\n'
                 % (pol['famille'], f, w) for f, w in pol['fichiers'])
    v = ['--police:%s' % pol['pile'], '--mono:%s' % pol['mono'], '--livre:%s' % pol['livre']]
    v += ['--%s:%s' % (k, c['v']) for k, c in j['couleurs'].items()]
    v += ['--%s:%s' % (k, x) for k, x in j['rayons'].items()]
    v += ['--%s:%s' % (k, x) for k, x in j['tailles'].items()]
    return ('<style id="jetons">\n/* Jetons de la charte v%s. Généré par scripts/jetons_charte.py depuis '
            'projets/sailingmore/jetons.json : ne pas éditer ici. */\n%s:root{%s}\n</style>\n'
            % (j['version'], ff, ';'.join(v)))


def table_snap(j):
    t = {}
    for cible, anciens in j['snap'].items():
        for a in anciens:
            t[a.lower()] = cible
    return t


RE_FACE = re.compile(r'@font-face\{font-family:"Inter SM";[^}]*\}\s*')
RE_FAM = re.compile(r'''font-family:\s*((?:"[^"]*"|'[^']*'|[^;}"'])+)''')
RE_HEX = re.compile(r'(?<![\w&])#[0-9a-fA-F]{3,8}(?![\w])')
RE_PX = re.compile(r'font-size:\s*(\d+(?:\.\d+)?)px')
RE_RAY = re.compile(r'border-radius:\s*([^;}"]+)')
RE_BLOC = re.compile(r'<style id="jetons">.*?</style>\n?', re.S)


def _fam(m):
    v = m.group(1).strip()
    imp = ''
    if v.endswith('!important'):
        v, imp = v[:-10].strip(), '!important'
    low = v.lower()
    if low.startswith(('var(', 'inherit', 'initial', 'unset')):
        return m.group(0)
    if 'mono' in low or 'courier' in low:
        nv = 'var(--mono)'
    elif 'serif' in low and 'sans' not in low and 'system-ui' not in low:
        nv = 'var(--livre)'
    else:
        nv = 'var(--police)'
    return 'font-family:' + nv + imp


def _ray_tok(t):
    m = re.fullmatch(r'(\d*\.?\d+)(px|rem|em)', t)
    if not m:
        return t
    px = float(m.group(1)) * (16 if m.group(2) != 'px' else 1)
    if px == 0:
        return '0'
    if px >= 100:
        return '999px'
    return '4px' if px < 8 else ('12px' if px <= 15 else '18px')


def _ray(m):
    v = m.group(1)
    imp = ''
    if '!important' in v:
        v, imp = v.replace('!important', '').strip(), '!important'
    return 'border-radius:' + ' '.join(_ray_tok(t) for t in v.split()) + imp


def applique(t, j):
    snap = table_snap(j)
    t = RE_BLOC.sub('', t)
    t = RE_FACE.sub('', t)
    t = RE_FAM.sub(_fam, t)
    t = t.replace('Inter SM', j['police']['famille'])
    t = RE_HEX.sub(lambda m: snap.get(m.group(0).lower(), m.group(0)), t)
    t = RE_PX.sub(lambda m: 'font-size:12px' if float(m.group(1)) < 12 else m.group(0), t)
    t = RE_RAY.sub(_ray, t)
    b = bloc(j)
    m = re.search(r'<head[^>]*>\n?', t)
    if not m:
        raise ValueError('pas de <head>')
    return t[:m.end()] + b + t[m.end():]


def main():
    seche = '--seche' in sys.argv
    j = charge()
    n = 0
    for p in pages():
        with open(p, encoding='utf-8') as f:
            t = f.read()
        try:
            nt = applique(t, j)
        except ValueError as e:
            print('ECHEC', os.path.basename(p), e)
            continue
        if nt != t:
            n += 1
            print('modifie', os.path.basename(p), len(t), '->', len(nt))
            if not seche:
                with open(p, 'w', encoding='utf-8') as f:
                    f.write(nt)
    print(n, 'page(s) modifiée(s)' + (' (à blanc)' if seche else ''))


if __name__ == '__main__':
    main()
