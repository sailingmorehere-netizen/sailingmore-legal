import json, re, sys, os
sys.path.insert(0, 'scripts')
d = json.load(open('projets/sailingmore/stages.json', encoding='utf-8'))['offres']
EC = sys.argv[1]
K = int(sys.argv[2]) if len(sys.argv) > 2 else 3
R = re.compile(r'\b\d{1,2}(?:st|nd|rd|th)?[./ ]\s?(?:\d{1,2}|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|[A-Za-zéûä]{3,10})\.?[./ ]\s?(?:2026|2027)\b')
seen = set()
for e in d:
    if e['ecole'] != EC or e.get('debut') or e['lien'] in seen:
        continue
    seen.add(e['lien'])
    p = 'tmp_n33/' + re.sub(r'\W+', '_', e['lien'])[:120] + '.txt'
    t = open(p).read()
    ms = list(R.finditer(t))
    if not ms:
        continue
    print('##', e['lien'], '|', e['titre'][:50], len(ms))
    for m in ms[:K]:
        print('    ', t[max(0, m.start() - 50):m.end() + 70])
