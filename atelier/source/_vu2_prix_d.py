import json, os, re, subprocess, html, sys
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
d = json.load(open(os.path.join(R, 'projets/sailingmore/site/stages-proches.json')))
seen = set()
for o in d['o']:
    if o[4] in ('Urban Truant', 'Segelschule Schluchsee', 'Lagoo Segelschule Zürich', 'Real Club de Mar', 'Soleil Scuola Nautica', 'Vent du Large', 'Segelschule Grosse Freiheit') and o[8] and (o[4], o[9]) not in seen:
        seen.add((o[4], o[9])); print(o[4], '|', o[3][:50], '|', o[8], o[9], '|', o[10])
def get(u):
    t = subprocess.run(['curl', '-sL', '-m', '25', '-A', 'Mozilla/5.0', u], capture_output=True).stdout.decode('utf-8', 'replace')
    return t
for u in sys.argv[1:]:
    h = get(u)
    print('==', u, len(h))
    for m in sorted(set(re.findall(r'href=["\']([^"\']*(?:[Pp]reis|[Pp]rice|[Tt]arif|[Pp]rezzi|[Pp]recio|tarifs|prix)[^"\']*)', h)))[:8]:
        print('   link', m)
