import json, re, collections
L = json.load(open('projets/sailingmore/stages.json.bak-avant-54', encoding='utf-8'))['offres']
cb = json.load(open('scripts/_niveau58_corps.json'))
rx = re.compile(r'(level|prerequisites?|niveau|niveaus?|zeilniveau|voorkennis|vorkenntnisse|requisiti|requisitos|pr[ée]requis|experience required|ervaring)\W{0,3}[^.]{0,70}', re.I)
c = collections.Counter(); ex = {}
for e in L:
    if e.get('niveau'): continue
    t = cb.get(e['lien']) or ''
    for m in rx.finditer(t):
        k = (e['ecole_slug'], m.group(0)[:50].lower())
        c[k] += 1; ex.setdefault(k, m.group(0)[:110])
seen = collections.Counter()
for (s, k), n in c.most_common():
    if seen[s] < 3:
        seen[s] += 1; print(s, n, '|', ex[(s, k)])
