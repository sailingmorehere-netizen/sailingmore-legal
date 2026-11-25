import json, os, re, subprocess, sys
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
L = json.load(open(R + '/projets/sailingmore/site/stages-proches.json'))['o']
B = ['De Bird', 'UKSA', 'Segelschule Rückenwind', 'Zeilschool Ûp', 'BH Marine']
D = R + '/cache_b'
os.makedirs(D, exist_ok=True)
ecole = sys.argv[1]
for i, o in enumerate(L):
    if o[4] != ecole or o[8]:
        continue
    f = f'{D}/{i}.html'
    if not os.path.exists(f):
        r = subprocess.run(['curl', '-sL', '-m', '25', '-A', 'Mozilla/5.0', '-o', f, '-w', '%{http_code}', o[10]],
                           capture_output=True, text=True)
        code = r.stdout
    else:
        code = 'cache'
    t = open(f, encoding='utf8', errors='replace').read()
    t = re.sub(r'<(script|style)[^>]*>.*?</\1>', ' ', t, flags=re.S)
    t = re.sub(r'<[^>]+>', ' ', t)
    t = re.sub(r'\s+', ' ', t)
    pr = re.findall(r'(?:€|£|EUR|GBP)\s?\d[\d.,]*|\d[\d.,]*\s?(?:€|£|,-|euro)', t)
    print(i, code, o[3][:30], '|', pr[:6])
