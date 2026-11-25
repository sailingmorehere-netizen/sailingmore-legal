import json, os, re, subprocess, html, sys
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
d = json.load(open(os.path.join(R, 'projets/sailingmore/site/stages-proches.json')))
for o in d['o']:
    if o[4] in ('Urban Truant', 'Segelschule Schluchsee', 'Lagoo Segelschule Zürich') and o[8]:
        print(o[4], o[3][:50], o[8], o[9], o[15:]);
        break
print(sorted({type(o[8]).__name__ for o in d['o']}), [o[8] for o in d['o'] if o[8]][:12])
for u in sys.argv[1:]:
    t = subprocess.run(['curl', '-sL', '-m', '25', '-A', 'Mozilla/5.0', u], capture_output=True).stdout.decode('utf-8', 'replace')
    t = re.sub(r'(?s)<(script|style).*?</\1>', ' ', t)
    t = html.unescape(re.sub(r'<[^>]+>', ' ', t)); t = re.sub(r'\s+', ' ', t)
    print('==', u)
    for x in list(re.finditer(r'(£|€|CHF|Fr\.|EUR|\$)\s?\d|\d\s?(£|€|CHF|Fr\.|EUR|Euro)|[Pp]reis|[Pp]rice|[Pp]rix|[Tt]arif|[Pp]recio|[Pp]rijs', t))[:6]:
        print('   ', t[max(0, x.start() - 60):x.end() + 60])
