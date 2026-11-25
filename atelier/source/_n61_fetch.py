import json, os, re, sys, urllib.request, html
EC = ['Zeezeilschool Scheveningen', 'De Bird', 'Tip Top Sailing', 'Zeilschool Ûp', 'Compagnia della Vela', 'Oltremare Vela']
OUT = 'tmp_n61'
os.makedirs(OUT, exist_ok=True)
d = json.load(open('projets/sailingmore/stages.json', encoding='utf-8'))
seen = set()
for e in d['offres']:
    if e['ecole'] in EC and not e.get('debut') and e['lien'] not in seen:
        seen.add(e['lien'])
        n = re.sub(r'\W+', '_', e['lien'])[:100]
        p = f'{OUT}/{n}.txt'
        try:
            r = urllib.request.urlopen(urllib.request.Request(e['lien'], headers={'User-Agent': 'Mozilla/5.0'}), timeout=25)
            t = r.read().decode('utf-8', 'replace')
        except Exception as x:
            print('ERR', e['lien'], x); continue
        t = re.sub(r'(?s)<(script|style)[^>]*>.*?</\1>', ' ', t)
        t = html.unescape(re.sub(r'<[^>]+>', ' ', t))
        t = re.sub(r'\s+', ' ', t)
        open(p, 'w').write(e['lien'] + '\n' + t)
        print(len(t), e['lien'])
