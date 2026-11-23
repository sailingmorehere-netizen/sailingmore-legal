import re, glob, os
D = "/opt/data/cache/claude-nuit/travail/"
marq = ["<!--mer-debut-->", 'class="entete"', 'id="equilibre"', "stages-proches", "<canvas", "mer-fond mer-fond-commandes"]
for f in sorted(glob.glob(D + "projets/sailingmore/site/*.html")):
    h = open(f, encoding="utf-8").read()
    n = os.path.basename(f)
    live = D + "sortie-test/enligne-" + n.replace(".html", "") + ".html"
    l = open(live, encoding="utf-8").read() if os.path.exists(live) else None
    print(n.ljust(26), len(h), [h.count(m) for m in marq], "| ligne", (len(l), [l.count(m) for m in marq]) if l else "-")
