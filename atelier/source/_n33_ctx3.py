import json, re, sys
d = json.load(open('projets/sailingmore/stages.json', encoding='utf-8'))['offres']
P = re.compile(r'\b\d{1,2}(?:st|nd|rd|th)?[ ./-]+\w{3,10}\.?,? ?202[67]\b|\b\d{1,2}[./]\d{1,2}[./]2?0?2[67]\b|\b202[67]-\d\d-\d\d|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\w* \d{1,2}(?:st|nd|rd|th)?,? 202[67]', re.I)
for EC in sys.argv[2:]:
    print('=====', EC)
    seen = set()
    k = 0
    for e in d:
        if e['ecole'] != EC or e.get('debut') or e['lien'] in seen:
            continue
        seen.add(e['lien'])
        t = open('tmp_n33/' + re.sub(r'\W+', '_', e['lien'])[:120] + '.txt').read()
        ms = [m for m in P.finditer(t) if not re.search(r'Copyright|©|Last updated|Posted|Stand', t[max(0, m.start() - 25):m.start()])]
        if not ms:
            continue
        k += 1
        if k > 4:
            break
        print('##', e['lien'], '|', e['titre'][:40], len(ms))
        for m in ms[:int(sys.argv[1])]:
            print('    ', t[max(0, m.start() - 70):m.end() + 70])
