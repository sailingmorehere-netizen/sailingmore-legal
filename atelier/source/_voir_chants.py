import json, sys
d = json.load(open("projets/sailingmore/chants-de-marin.json", encoding="utf-8"))
ids = sys.argv[1:]
for c in d["chants"]:
    if c["id"] in ids:
        print("==", c["id"], "|", c["source"])
        print(c["paroles"][:int(600)])
