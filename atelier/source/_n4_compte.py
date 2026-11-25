import json
from collections import Counter
c = json.load(open('projets/sailingmore/chants-de-marin.json'))['chants']
print('total', len(c))
print('avec paroles', sum(1 for x in c if x.get('paroles')))
print('paroles completes', sum(1 for x in c if x.get('paroles') and not x.get('partiel')))
print('partiels', sum(1 for x in c if x.get('partiel')))
print('sans paroles', [x['id'] for x in c if not x.get('paroles')])
print('audio', [x['id'] for x in c if x.get('audio')])
print('livres', Counter(x.get('livre') for x in c))
print('types', Counter(x['type'] for x in c))
print('langues', Counter(x['lg'] for x in c))
print('sans source', [x['id'] for x in c if not x.get('source')])
print('titres en double', [t for t, n in Counter(x['titre'] for x in c).items() if n > 1])
