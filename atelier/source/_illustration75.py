"""Une fois : enregistre dans jetons.json les valeurs d'illustration / ombres / colonnes encore
présentes après application des jetons (dette mesurée, bornée : ce qui n'y est pas ne peut plus entrer)."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import jetons_charte as jc, controle_charte as cc

j = jc.charge()
noyau = {c['v'].lower() for c in j['couleurs'].values()}
ill = {}; om = set(); lg = set()
for p in jc.pages():
    nom = os.path.basename(p)
    r = cc.mesure_page(open(p, encoding='utf-8').read(), j)
    if r['illus']:
        ill[nom] = {c: n for c, n in sorted(r['illus'].items())}
    om |= set(r['ombres']); lg |= set(r['largeurs'])
j['illustration'] = ill
j['ombres_tolerees'] = sorted(om)
j['largeurs_toleres'] = sorted(lg, key=lambda x: (x[-2:], float(x[:-2]) if x[:-2].replace('.', '').isdigit() else 0))
with open(jc.JETONS, 'w', encoding='utf-8') as f:
    json.dump(j, f, ensure_ascii=False, indent=2)
print(len(ill), 'pages avec illustration;', sum(len(d) for d in ill.values()), 'couleurs;', len(om), 'ombres;', len(lg), 'largeurs')
