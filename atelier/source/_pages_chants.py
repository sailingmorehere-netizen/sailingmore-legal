import re, sys
out = []
for n, l in enumerate(open(sys.argv[1], encoding="utf-8"), 1):
    s = l.strip()
    if re.fullmatch(r"(B\s?)?\d{1,3}", s) and n > 800:
        out.append(f"{n}:{s}")
print(" ".join(out))
