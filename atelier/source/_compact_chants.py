import re, sys
src, dst = sys.argv[1], sys.argv[2]
out = []
for n, l in enumerate(open(src, encoding="utf-8"), 1):
    s = l.strip()
    if not s:
        continue
    letters = sum(ch.isalpha() for ch in s)
    if letters < 4 or letters / max(len(s), 1) < 0.6:
        continue
    # lignes de notation : syllabes séparées par des tirets
    if len(re.findall(r"\w - \w|\w- \w|\w -\w", s)) >= 2:
        continue
    out.append(f"{n}\t{s}")
open(dst, "w", encoding="utf-8").write("\n".join(out))
print(len(out))
