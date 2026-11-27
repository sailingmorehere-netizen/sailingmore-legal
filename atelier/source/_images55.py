import json, collections, sys
F = '/opt/data/cache/claude-nuit/travail/projets/sailingmore/stages.json'
d = json.load(open(F, encoding='utf-8'))
L = d if isinstance(d, list) else max([v for v in d.values() if isinstance(v, list)], key=len)
A = [x for x in L if not x.get('hors_offre')]
cand = collections.Counter((x['ecole'], x['image']) for x in A if x.get('image') and (x.get('pays') == 'CHE' or 'Léman' in (x.get('lieu') or '') or 'Annecy' in (x.get('lieu') or '') or 'Jorioz' in (x.get('lieu') or '')))
print(cand.most_common(8))
if len(sys.argv) > 1:
    img = sys.argv[1]
    n = 0
    for x in L:
        if x.get('ecole_slug') == 'cnv-versoix' and not x.get('image'):
            x['image'] = img
            n += 1
    json.dump(d, open(F, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('posé', n)
