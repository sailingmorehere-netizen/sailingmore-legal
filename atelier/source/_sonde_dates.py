import json, re, urllib.request, concurrent.futures as cf, html
d = json.load(open('projets/sailingmore/stages.json'))
cand = [e for e in d['offres'] if not e.get('debut') and not e.get('hors_offre')]
M = r'(?:jan|feb|mar|apr|may|mai|jun|jul|aug|sep|oct|okt|nov|dec|dez|janv|févr|avr|juin|juil|août|gen|mag|giu|lug|ago|set|ott|dic|ene|abr|mrt|mei|maa|lis|sty|kwi|cze|lip|sie|wrz|paź|gru)[a-zéûäëüíóúçšž]*'
RX = re.compile(r'\b(\d{1,2})(?:st|nd|rd|th|\.)?\s*(?:-|–|to|bis|au|al|a|tot)?\s*(?:\d{1,2}(?:st|nd|rd|th|\.)?\s*)?(?:of\s+)?(' + M + r')\.?\s+(202[67])', re.I)
RX2 = re.compile(r'\b(\d{1,2})[./](\d{1,2})[./](202[67])\b')
def get(e):
    try:
        r = urllib.request.Request(e['lien'], headers={'User-Agent': 'Mozilla/5.0'})
        t = urllib.request.urlopen(r, timeout=15).read().decode('utf8', 'ignore')
    except Exception as x:
        return e, []
    t = re.sub(r'<(script|style)[\s\S]*?</\1>', ' ', t)
    t = html.unescape(re.sub(r'<[^>]+>', ' ', t))
    t = re.sub(r'\s+', ' ', t)
    out = [t[max(0, m.start()-30):m.end()+30] for m in list(RX.finditer(t)) + list(RX2.finditer(t))]
    return e, out
with cf.ThreadPoolExecutor(8) as ex:
    res = list(ex.map(get, cand))
by = {}
for e, out in res:
    if out:
        by.setdefault(e['ecole_slug'], []).append((e['titre'][:40], len(out), out[:2]))
for s, l in sorted(by.items(), key=lambda kv: -len(kv[1])):
    print('##', s, len(l))
    for x in l[:3]:
        print('  ', x)
