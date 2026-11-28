import json
c = json.load(open('releve_prix60c.json', encoding='utf-8'))
d = json.load(open('projets/sailingmore/stages.json', encoding='utf-8'))
for i, v in c.items():
    if not v.get('ex'):
        print(i, v['ecole'][:22], '|', v['titre'][:45], '|', v.get('n', v.get('err')), '|', d['offres'][int(i)]['lien'][-45:])
