import json, re, collections
d = json.load(open('projets/sailingmore/stages.json'))
L = d['offres']
m = [e for e in L if not e.get('niveau')]
corps = json.load(open('scripts/_niveau58_corps.json'))
nul = [e for e in m if not corps.get(e['lien'])]
print('restants', len(m), 'sans corps cache', len(nul), 'absents du cache', sum(1 for e in m if e['lien'] not in corps))
print(collections.Counter(e['ecole'] for e in nul).most_common(8))
rx = re.compile(r'.{60}(beginner|experience|d[ée]butant|anf[äa]nger|vorkenntnis|principiant|advanced|confirm[ée]|fortgeschritten|level|niveau|ervaring|beginners).{60}', re.I)
c = collections.Counter()
for e in m:
    t = corps.get(e['lien']) or ''
    for x in rx.finditer(t):
        c[x.group(1).lower()] += 1
print(c.most_common(20))
import random
random.seed(1)
for e in random.sample([e for e in m if corps.get(e['lien'])], 12):
    t = corps[e['lien']]
    hits = [x.group(0) for x in rx.finditer(t)][:2]
    print(e['ecole'], '|', e['titre'][:50], '|', len(t), hits)
