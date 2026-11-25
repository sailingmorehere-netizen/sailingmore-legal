"""python3 scripts/_voir_plage.py <livre> a-b [a-b ...] : affiche les lignes non vides (>=1 mot de 3 lettres) avec leur numéro."""
import re, sys
from pathlib import Path
R = Path(__file__).resolve().parent.parent / "cache/chants/src"
F = {"w": "seasongsshanties00whal.txt", "t1": "shantybooksailor00terr.txt", "t2": "the-shanty-book-part-two.txt", "s": "musicofwaterscol00smituoft.txt"}
L = (R / F[sys.argv[1]]).read_text(encoding="utf-8").splitlines()
for p in sys.argv[2:]:
    a, b = map(int, p.split("-"))
    print(f"--- {p}")
    for n in range(a, b + 1):
        t = L[n - 1].strip()
        if t and re.search(r"[A-Za-zÀ-ÿ]{3,}", t):
            print(n, t)
