import json
r = json.load(open('releve_prix60.json', encoding='utf-8'))
for i, v in r.items():
    if v.get('ex'):
        print(f"#{i} {v['ecole']} | {v['titre'][:60]}")
        for x in v['ex'][:3]:
            print('    ', x[:150])
