import json, re, sys, html, urllib.request, collections
d = json.load(open('projets/sailingmore/stages.json'))['offres']
ecoles = sys.argv[1:]
pat = re.compile(r'(\d{1,2}[./]\d{1,2}[./]?(?:20)?\d{0,2}|\d{1,2}(?:st|nd|rd|th|er)?\s*(?:-|–|to|au|bis)?\s*\d{0,2}\s*(?:jan|feb|mar|apr|may|mai|jun|jul|aug|sep|oct|nov|dec|janv|févr|avr|juin|juil|août|sept|okt|dez|mrt)[a-zéû]*\.?\s*(?:20\d\d)?|20\d\d-\d\d-\d\d)', re.I)
for s in ecoles:
    es = [e for e in d if e['ecole_slug'] == s and not e.get('debut') and not e.get('hors_offre')]
    for e in es[:4]:
        try:
            r = urllib.request.Request(e['lien'], headers={'User-Agent': 'Mozilla/5.0'})
            t = urllib.request.urlopen(r, timeout=15).read().decode('utf8', 'ignore')
        except Exception as x:
            print('ERR', e['lien'], x); continue
        t = re.sub(r'<(script|style)[\s\S]*?</\1>', ' ', t)
        t = re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', t)))
        h = [t[max(0, m.start()-25):m.end()+25] for m in pat.finditer(t)]
        print('##', s, e['titre'][:50], e['lien'], len(h))
        for x in h[:5]: print('    ', x)
