import json, os, re, subprocess, html
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
d = json.load(open(os.path.join(R, 'projets/sailingmore/site/stages-proches.json')))
G = json.load(open(os.path.join(R, 'projets/sailingmore/site/go-liens.json')))
src = open(os.path.join(R, 'scripts/verifie_stages_champ.py')).read()
ec = re.findall(r"'([^']+)'", re.search(r"'prix_d': \[(.*?)\]", src, re.S).group(1))
if isinstance(G, dict) and 'l' in G and isinstance(G['l'], dict):
    G = G['l']
cache = {}
for i, o in enumerate(d['o']):
    if o[4] in ec and not o[8]:
        gid = re.search(r'id=(\w+)', o[10]).group(1)
        u = G.get(gid) if isinstance(G, dict) else None
        if isinstance(u, list):
            u = u[0]
        print(i, o[4], '|', o[3][:50], '|', u)
        if not u or not str(u).startswith('http'):
            continue
        if u not in cache:
            t = subprocess.run(['curl', '-sL', '-m', '25', '-A', 'Mozilla/5.0', u], capture_output=True).stdout.decode('utf-8', 'replace')
            t = re.sub(r'(?s)<(script|style).*?</\1>', ' ', t)
            t = html.unescape(re.sub(r'<[^>]+>', ' ', t))
            cache[u] = re.sub(r'\s+', ' ', t)
        t = cache[u]
        print('   len', len(t))
        for x in list(re.finditer(r'(€\s?\d|\d[\d.,\']*\s?(€|EUR|Euro|£|CHF|Fr\.|euros))', t))[:4]:
            print('     ', t[max(0, x.start() - 60):x.end() + 20])
