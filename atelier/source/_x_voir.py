import json

c = json.load(open('projets/sailingmore/chants-de-marin.json'))['chants']
ids = {"old-storm-along", "so-handy-my-girls", "tommys-gone-to-hilo", "south-australia", "a-yankee-ship", "st-helena-soldier"}
for x in c:
    if x['id'] in ids:
        print('=====', x['titre'], '|', x['source'], '| partiel' if x.get('partiel') else '')
        print(x['paroles'])
