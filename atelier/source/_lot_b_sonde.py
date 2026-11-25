import json, os, re, sys, urllib.request, html
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
L = json.load(open(os.path.join(R, 'projets/sailingmore/site/stages-proches.json')))
B = ['De Bird', 'UKSA', 'Segelschule Rückenwind', 'Zeilschool Ûp', 'BH Marine']
ecole = sys.argv[1]
n = int(sys.argv[2]) if len(sys.argv) > 2 else 3
sel = [o for o in L['o'] if o[4] == ecole and o[8] in (None, '', 0)]
for o in sel[:n]:
    print('==', o[3], o[10])
    try:
        r = urllib.request.Request(o[10], headers={'User-Agent': 'Mozilla/5.0'})
        t = urllib.request.urlopen(r, timeout=20).read().decode('utf8', 'ignore')
    except Exception as e:
        print('ERR', e); continue
    t = re.sub(r'(?s)<(script|style).*?</\1>', ' ', t)
    t = html.unescape(re.sub(r'<[^>]+>', ' ', t))
    t = re.sub(r'\s+', ' ', t)
    for m in list(re.finditer(r'(£|€|EUR|CHF)\s?\d[\d.,]*|\d[\d.,]*\s?(£|€|EUR|,-)', t))[:4]:
        print('  ', t[max(0, m.start() - 50):m.end() + 30])
