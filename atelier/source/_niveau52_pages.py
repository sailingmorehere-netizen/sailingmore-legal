import json, re, urllib.request, sys, os
d = json.load(open('projets/sailingmore/stages.json', encoding='utf-8'))
ECOLES = {'uksa', 'solentboat', 'tiptop', 'rueckenwind', 'ultra', 'virgins'}
CUES = re.compile(r'(for (complete )?beginners?|no (prior )?experience (needed|required|necessary)|complete beginner|absolute beginner|'
                  r'beginner|novice|day skipper|competent crew|yachtmaster|coastal skipper|start yachting|'
                  r'all levels|experienced sailors?|advanced|intermediate|ohne (vor)?erfahrung|anf[aä]nger|fortgeschritten|'
                  r'beginners|beginnende|gevorderd|beginner|ervaren|zonder ervaring|met en zonder ervaring)', re.I)
cache = 'scripts/_niveau52_cache.json'
C = json.load(open(cache)) if os.path.exists(cache) else {}
seen = set()
for e in d['offres']:
    if e['ecole_slug'] in ECOLES and e.get('niveau') in (None, '', []) and e['lien'] not in seen:
        seen.add(e['lien'])
        u = e['lien']
        if u not in C:
            try:
                r = urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'}), timeout=15)
                h = r.read().decode('utf-8', 'ignore')
                h = re.sub(r'(?s)<(script|style|nav|footer|header)\b.*?</\1>', ' ', h)
                C[u] = re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', h))[:60000]
            except Exception as ex:
                C[u] = 'ERR ' + str(ex)[:60]
json.dump(C, open(cache, 'w'))
for u, t in C.items():
    ms = sorted({m.group(0).lower() for m in CUES.finditer(t)})
    print(u[-70:], '|', 'ERR' if t.startswith('ERR') else len(t), '|', ms[:8])
