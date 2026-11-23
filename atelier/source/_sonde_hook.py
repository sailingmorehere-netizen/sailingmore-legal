import re, os, sys
S = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "projets", "sailingmore", "site")
for n, pats in [("stages.html", [r'"titre"', r"function\s+(?:appliquer|setLang|applyLang|langue|traduire)\w*", r"documentElement\.lang"]),
                ("regates.html", [r'"titre"', r"function\s+(?:appliquer|setLang|applyLang|langue|traduire)\w*", r"documentElement\.lang"]),
                ("equivalences.html", [r'"titre"', r"function\s+(?:appliquer|setLang|applyLang|langue|traduire)\w*", r"documentElement\.lang"])]:
    s = open(os.path.join(S, n), encoding="utf-8").read()
    print("==", n)
    for p in pats:
        for m in list(re.finditer(p, s))[:3]:
            a = max(0, m.start() - 120)
            print("  [%s @%d]" % (p[:14], m.start()), s[a:m.start() + 260].replace("\n", " "))
