import json, os, re, sys, subprocess, html
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
F = os.path.join(R, 'projets/sailingmore/site/stages-proches.json')
d = json.load(open(F))
LOT = ['Segelschule Insel Reichenau', 'Compagnia della Vela', 'École de croisière Slowlife',
       'Urban Truant', 'Segelschule Grosse Freiheit', 'La Scuola della Vela', 'Soleil Scuola Nautica',
       'Segelschule Überlingen', 'EZS Zeilschool', 'Real Club de Mar', 'Blue Spirit', 'Solent Sail',
       'Vent du Large', 'Lagoo Segelschule Zürich', 'Segelschule Rehbach', 'Segelschule Schluchsee', 'Windzone']
cache = {}
for i, o in enumerate(d['o']):
    if o[4] in LOT and o[8] in (None, '', 0):
        u = o[10]
        if u not in cache:
            try:
                t = subprocess.run(['curl', '-sL', '-m', '25', '-A', 'Mozilla/5.0', u], capture_output=True).stdout.decode('utf-8', 'replace')
            except Exception as e:
                t = ''
            t = re.sub(r'(?s)<(script|style).*?</\1>', ' ', t)
            t = html.unescape(re.sub(r'<[^>]+>', ' ', t))
            t = re.sub(r'\s+', ' ', t)
            cache[u] = t
        t = cache[u]
        m = [t[max(0, x.start() - 50):x.end() + 20] for x in re.finditer(r'(€\s?\d|\d[\d.,\']*\s?(€|EUR|Euro|£|CHF|Fr\.|euros))', t)][:4]
        print(i, o[4], '|', o[3], '|', u, len(t))
        for s in m:
            print('    ', s)
