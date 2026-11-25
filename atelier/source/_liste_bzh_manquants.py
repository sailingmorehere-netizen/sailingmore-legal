import json, pathlib
d = json.loads(pathlib.Path("projets/sailingmore/lexique.json").read_text(encoding="utf-8"))
n = 0
for t in d["themes"]:
    for x in t.get("termes", []):
        if not x["mot"].get("bzh"):
            n += 1
            print(t["cle"], x["cle"], "|", x["mot"]["fr"], "|", x["mot"]["en"])
print(n, "sans breton")
