import json, random
d = json.load(open('projets/sailingmore/stages.json'))['offres']
random.seed(2)
m = [e for e in d if not e.get('niveau')]
for e in random.sample(m, 70):
    print(e['ecole'][:18], '|', e['titre'][:70], '|', e.get('type'))
