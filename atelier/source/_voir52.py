import re, subprocess
for p in ['ado', 'adultes', 'optimist']:
    h = subprocess.run(['curl', '-sL', '-m', '25', 'https://www.cnv.ch/stages-voile/' + p], capture_output=True, text=True).stdout
    h = re.sub(r'<(script|style)[^>]*>.*?</\1>', ' ', h, flags=re.S)
    t = re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', h))
    for m in re.finditer(r'(Débutant|Perfectionnement|Tous niveaux(?: / Perfectionnement)?) \w+ 2027 (.*?) CHF', t):
        if re.search(r'août|octobre|soir', m[2]) and re.search(r'23 au 25|27 août|mardis|vendredis', m[2]):
            print(p, '|', m[1], '|', m[2])
