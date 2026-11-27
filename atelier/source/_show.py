import json
for o in json.load(open('scan.json')):
    if o['d']: print(o['slug'],'|',o['titre'][:40],'|',o['d'][:6])
