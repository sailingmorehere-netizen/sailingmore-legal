import re, glob, collections, os
S = 'projets/sailingmore/site/'
pages = sorted(p for p in glob.glob(S + '*.html') if not os.path.basename(p).startswith(('pavillon-', '_')))
sh = collections.Counter(); mw = collections.Counter(); ff = collections.Counter(); links = collections.Counter()
for p in pages:
    t = open(p, encoding='utf-8').read()
    for r in re.findall(r'box-shadow:\s*([^;}"]+)', t): sh[re.sub(r'\s+', ' ', r)[:70]] += 1
    for r in re.findall(r'max-width:\s*([0-9.]+(?:px|rem|ch))', t): mw[r] += 1
    for r in re.findall(r'font-family:\s*([^;}]+)', t): ff[r[:80]] += 1
    links['head-has-charset-first'] += bool(re.search(r'<head>\s*<meta charset', t, re.I))
print(len(sh)); print(sh.most_common(14)); print(mw.most_common(25)); print(ff.most_common(25)); print(links)
t = open(S + 'cours.html', encoding='utf-8').read()
print([m.start() for m in re.finditer('Inter SM', t)][:30], len(re.findall('Inter SM', t)))
