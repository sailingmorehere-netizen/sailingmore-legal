import json, sys
d = json.load(open('projets/sailingmore/stages.json', encoding='utf-8'))
m = [e for e in d['offres'] if e.get('niveau') in (None, '', [])]
for s in sys.argv[1:]:
    print('==', s)
    for i, e in enumerate(m):
        if e['ecole_slug'] == s:
            print(' ', e['titre'][:90], '|', e['lien'][-60:])
