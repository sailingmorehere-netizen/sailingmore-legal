import re, glob, collections
pat = re.compile(r'\b(Level|Skill level|Niveau|Ervaringsniveau|Zeilniveau|Zeilervaring|Nivel|Livello|Nível|Poziom|Voraussetzung(?:en)?|Erfahrung|Experience|Prerequisites|Required experience)\s*[:\-–]\s*(.{0,50})', re.I)
c = collections.Counter()
pages = collections.defaultdict(set)
for f in glob.glob('claude/niv59_cache/*.txt'):
    t = open(f).read()
    u = t.split('\n', 1)[0]
    for m in pat.finditer(t):
        k = (m.group(1).lower(), m.group(2)[:40].lower())
        c[k] += 1
        pages[k].add(u)
for k, n in c.most_common(80):
    print(n, k, sorted(pages[k])[0])
