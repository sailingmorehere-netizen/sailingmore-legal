import os
S = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "projets", "sailingmore", "site")
for n, l in [("bateaux.html", 131), ("lexique.html", 142), ("stages.html", 30), ("regles-de-course.html", 257), ("annonceurs.html", 824), ("annonceurs.html", 552)]:
    L = open(os.path.join(S, n), encoding="utf-8").read().split("\n")
    for i in range(max(0, l - 3), l + 1):
        print(n, i + 1, L[i][:200])
    print()
