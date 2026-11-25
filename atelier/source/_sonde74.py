import re, glob, collections, os
os.chdir('/opt/data/cache/claude-nuit/travail/projets/sailingmore/site')
c = collections.Counter()
for f in glob.glob('*.html'):
    s = open(f, encoding='utf-8').read()
    m = re.search(r'<html[^>]*>', s)
    c[m.group(0) if m else None] += 1
print(c)
s = open('cours.html', encoding='utf-8').read()
print(s[:1800])
print(collections.Counter(re.findall(r'data-lang="(\w+)"', s)))
print(collections.Counter(re.findall(r'[?&]lang=(\w+)', s)).most_common(5))
print(open('robots.txt').read())
print(open('sitemap.xml').read()[:700])
print(os.listdir('js'))
print([x for x in os.listdir('../../../scripts') if 'control' in x or 'veille' in x or 'langue' in x])
for f in glob.glob('js/*.js') + ['index.html']:
    t = open(f, encoding='utf-8').read()
    for m in re.finditer(r'.{80}(?:navigator\.language|\?lang=|get\(.lang.\)).{120}', t):
        print(f, m.group(0)[:200].replace('\n', ' '))
        break
