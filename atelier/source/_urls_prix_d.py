import json, os, re
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
g = json.load(open(os.path.join(R, 'projets/sailingmore/site/go-liens.json')))
print(type(g).__name__, len(g))
cle = lambda i: i
items = g.items() if isinstance(g, dict) else enumerate(g)
n = 0
for k, v in items:
    if 'd00215a1' in json.dumps([k, v]) or n < 2:
        print(k, v); n += 1
        if n > 3: break
