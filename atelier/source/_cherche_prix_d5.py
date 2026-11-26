import json, os, re, subprocess, html
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
S = os.path.join(R, 'projets/sailingmore/site/')
o = json.load(open(S + 'stages-proches.json'))['o']
g = json.load(open(S + 'go-liens.json'))
DEJA = {76, 100, 101, 106, 209, 211, 291}
IDX = [i for i in range(len(o)) if o[i][4] in (
    'Segelschule Insel Reichenau', 'Compagnia della Vela', 'École de croisière Slowlife', 'Segelschule Grosse Freiheit',
    'La Scuola della Vela', 'Soleil Scuola Nautica', 'Segelschule Überlingen', 'Segelschule Rehbach',
    'Segelschule Schluchsee', 'Solent Sail', 'Vent du Large', 'Windzone', 'Real Club de Mar', 'EZS Zeilschool')
    and not o[i][8] and i not in DEJA]
for i in IDX:
    k = o[i][10].split('id=')[1].split('&')[0]
    u = g.get(k) if isinstance(g, dict) else None
    if isinstance(u, dict):
        u = u.get('u') or u.get('url')
    print(i, o[i][3][:50], '|', u)
    if not u or not str(u).startswith('http'):
        continue
    t = subprocess.run(['curl', '-sL', '-m', '20', '-A', 'Mozilla/5.0', u], capture_output=True).stdout.decode('utf-8', 'replace')
    t = re.sub(r'(?s)<(script|style).*?</\1>', ' ', t)
    t = re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', t)))
    for x in list(re.finditer(r'(\d[\d.,\']{1,6}\s?(€|EUR|CHF|Euro)|(€|EUR|ab|from|da|desde)\s?\d{2,4})', t))[:4]:
        print('     ', t[max(0, x.start() - 50):x.end() + 30])
