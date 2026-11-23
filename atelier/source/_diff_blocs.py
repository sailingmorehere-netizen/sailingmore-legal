import re, sys
D = "/opt/data/cache/claude-nuit/travail/"
for p in ("regles-de-course", "lexique"):
    a = open(D + "sortie-test/enligne-" + p + ".html", encoding="utf-8").read()
    b = open(D + "projets/sailingmore/site/" + p + ".html", encoding="utf-8").read()
    print(p, "ligne", len(a), "copie", len(b))
    for nom, h in (("ligne", a), ("copie", b)):
        bl = re.findall(r"<script([^>]*)>(.*?)</script>", h, re.S)
        print(" ", nom, [(re.sub(r"\s+", " ", at)[:40], len(c)) for at, c in bl])
        print("   style", [len(x) for x in re.findall(r"<style[^>]*>(.*?)</style>", h, re.S)])
