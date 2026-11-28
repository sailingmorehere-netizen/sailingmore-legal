# © 2026 Sailing More — tous droits réservés. All rights reserved.
import json
d = json.load(open("projets/sailingmore/chants-de-marin.json"))
ch = d.get("chants", d)
done = {x["id"] for x in json.load(open("claude/livrables/chants-images.json"))}
rest = [c for c in ch if c.get("id") not in done]
rest.sort(key=lambda c: (c.get("partiel", True), c.get("id", "")))
print(len(ch), len(rest))
for c in rest:
    print(c.get("id"), "|", c.get("titre"), "|", c.get("partiel"), "|", c.get("famille"), "|", str(c.get("source"))[:50])
