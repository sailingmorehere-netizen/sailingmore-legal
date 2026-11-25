import re, sys, json, urllib.request
d = json.load(open('projets/sailingmore/stages.json', encoding='utf-8'))
L = d if isinstance(d, list) else max([v for v in d.values() if isinstance(v, list)], key=len)
E = ('UKSA', 'Solent Boat Training', 'Tip Top Sailing', 'Segelschule Rückenwind', 'Ultra Sailing', 'Sailing Virgins')
liens = []
for e in L:
    if not e.get('niveau') and e['ecole'] in E and e['lien'] not in liens:
        liens.append(e['lien'])
RX = re.compile(r'.{70}(beginner|no experience|no previous|prerequisite|pre-requisite|experience required|suitable for|ideal for|'
                r'anfänger|vorkenntnisse|geen ervaring|ervaring|beginners|all levels|intermediate|advanced level).{90}', re.I)
for u in liens:
    try:
        h = urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'}), timeout=15).read().decode('utf-8', 'replace')
    except Exception as ex:
        print('##', u[-50:], 'ERREUR'); continue
    t = re.sub(r'<(script|style)[^>]*>.*?</\1>', ' ', h, flags=re.S)
    t = re.sub(r'<[^>]+>', ' ', t); t = re.sub(r'\s+', ' ', t)
    ms = [m.group(0) for m in RX.finditer(t)][:2]
    print('##', u[-60:], '|', ' || '.join(ms))
