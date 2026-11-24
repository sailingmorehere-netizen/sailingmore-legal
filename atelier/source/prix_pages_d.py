import json, os, re, subprocess, sys
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
d = json.load(open(os.path.join(R, 'projets/sailingmore/site/stages-proches.json')))
idx = [int(a) for a in sys.argv[1:]]
for i in idx:
    o = d['o'][i]
    try:
        h = subprocess.run(['curl', '-sL', '-m', '20', o[10]], capture_output=True, timeout=30).stdout.decode('utf8', 'ignore')
    except Exception as e:
        print(i, 'ERR', e); continue
    h = h.replace('&euro;', '€').replace('&#8364;', '€').replace('&nbsp;', ' ')
    h = re.sub(r'(?s)<(script|style).*?</\1>', ' ', h)
    t = re.sub(r'<[^>]+>', ' ', h)
    t = re.sub(r'\s+', ' ', t)
    m = [t[max(0, x.start() - 60):x.end() + 15] for x in re.finditer(r'\d[\d.,\']*\s?(€|EUR|CHF|Euro|Fr\.|,-)|(€|CHF|EUR)\s?\d[\d.,\']*', t)]
    print('==', i, o[4], '|', o[3][:50], len(h), 'octets')
    for s in m[:5]:
        print('   ', s)
