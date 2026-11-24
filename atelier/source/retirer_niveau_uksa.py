import json
p = "projets/sailingmore/site/stages-proches.json"
d = json.load(open(p, encoding="utf-8"))
n = 0
for x in d["o"]:
    if x[3] == "RYA Powerboat Instructor" and x[13]:
        x[13] = ""
        n += 1
open(p, "w", encoding="utf-8").write(json.dumps(d, ensure_ascii=False, separators=(",", ":")))
print(n, "niveau(x) retiré(s) ;", sum(1 for x in d["o"] if x[13]), "niveaux restants")
