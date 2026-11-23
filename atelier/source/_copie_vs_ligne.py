R = "/opt/data/cache/claude-nuit/travail/"
marq = ["stages-proches.js", "mer-louvoyage.js", 'class="entete', "<main", "og:title", "BreadcrumbList", "<noscript", "retour"]
for p in ["lexique", "stages", "regles-de-course"]:
    a = open(R + "projets/sailingmore/site/%s.html" % p, encoding="utf-8").read()
    b = open(R + "sortie-test/enligne-%s.html" % p, encoding="utf-8").read()
    print(p, len(a), len(b), {m: (a.count(m), b.count(m)) for m in marq}, "identique" if a == b else "different")
