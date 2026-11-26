import json, re, collections
d = json.load(open('projets/sailingmore/stages.json', encoding='utf-8'))['offres']
P = re.compile(r'\b\d{1,2}(?:st|nd|rd|th)? (?:Dec|December|Décembre|Dezember|dicembre|diciembre|Jan|January|janvier|Januar|gennaio|enero)\w* ?2?0?2?[67]?|(?:Dec|Jan)\w* \d{1,2}(?:st|nd|rd|th)?,? 202[67]|\b\d{1,2}[./]\d{1,2}[./]202[67]|\b202[67]-\d\d-\d\d|\b2027\b|Dec 2026|December 2026', re.I)
c = collections.Counter(); err = collections.Counter(); tot = collections.Counter()
for e in d:
    if e.get('debut') or not e['lien']:
        continue
    tot[e['ecole']] += 1
    t = open('tmp_n33/' + re.sub(r'\W+', '_', e['lien'])[:120] + '.txt').read()
    if t.startswith('ERR'):
        err[e['ecole']] += 1
    elif P.search(t):
        c[e['ecole']] += 1
print('vides par école (dont ERR, dont motif 2026-27):')
for k, v in tot.most_common(25):
    print(v, k, 'ERR', err[k], 'motif', c[k])
