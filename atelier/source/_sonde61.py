import json, re, sys, html, urllib.request
d = json.load(open('projets/sailingmore/stages.json'))
o = [e for e in d['offres'] if not e.get('debut') and not e.get('hors_offre')]
def texte(u):
    r = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'})
    t = urllib.request.urlopen(r, timeout=15).read().decode('utf8', 'ignore')
    t = re.sub(r'<(script|style)[\s\S]*?</\1>', ' ', t)
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', t)))
M = r'(?:jan|feb|fév|mar|apr|avr|may|mai|jun|jul|aug|sep|oct|nov|dec|déc|janv|févr|juil|sept)[a-zéû]*\.?'
R = re.compile(r'.{0,50}(?:\b20(?:26|27)\b|\d{1,2}[./]\d{1,2}[./]).{0,60}', re.I)
for s in sys.argv[1:]:
    n = 0
    for e in o:
        if e['ecole_slug'] != s: continue
        n += 1
        if n > 3: break
        try: t = texte(e['lien'])
        except Exception as x: print(s, 'ERR', x); continue
        print('==', s, e['lien'], len(t))
        for m in list(R.finditer(t))[:5]: print('   ', m.group(0))
