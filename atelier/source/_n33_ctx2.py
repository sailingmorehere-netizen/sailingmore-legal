import json, re, sys
d = json.load(open('projets/sailingmore/stages.json', encoding='utf-8'))['offres']
R = re.compile(r'\b\d{1,2}(?:st|nd|rd|th)? (?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\w* (?:2026|2027)|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\w* \d{1,2}(?:st|nd|rd|th)?,? (?:2026|2027)|\b\d{1,2}\.? (?:gennaio|febbraio|marzo|aprile|maggio|giugno|luglio|agosto|settembre|ottobre|novembre|dicembre|Januar|Februar|März|Juni|Juli|Oktober|Dezember|janvier|février|avril|juin|juillet|août|septembre|octobre|décembre|abril|mayo|junio|julio|septiembre|octubre|noviembre|diciembre) (?:2026|2027)', re.I)
for EC in sys.argv[2:]:
    print('=====', EC)
    seen = set()
    for e in d:
        if e['ecole'] != EC or e.get('debut') or e['lien'] in seen:
            continue
        seen.add(e['lien'])
        t = open('tmp_n33/' + re.sub(r'\W+', '_', e['lien'])[:120] + '.txt').read()
        ms = list(R.finditer(t))
        if not ms:
            continue
        print('##', e['lien'], '|', e['titre'][:40], len(ms))
        for m in ms[:int(sys.argv[1])]:
            print('    ', t[max(0, m.start() - 60):m.end() + 60])
