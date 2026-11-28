import json, collections, subprocess
d = json.load(open('projets/sailingmore/stages.json'))
corps = json.load(open('scripts/_niveau58_corps.json'))
m = [e for e in d['offres'] if not e.get('niveau')]
c = collections.Counter(e['ecole'] for e in m if len(corps.get(e['lien']) or '') < 300)
print('courts', sum(c.values()), c.most_common(10))
seen = set()
for e in m:
    if len(corps.get(e['lien']) or '') < 300 and e['ecole'] not in seen:
        seen.add(e['ecole'])
        print(e['ecole'], e['lien'], repr(corps.get(e['lien'])))
        r = subprocess.run(['curl', '-sIL', '--max-time', '15', '-A', 'Mozilla/5.0', e['lien']], capture_output=True, timeout=30)
        print('  ', r.stdout.decode('utf-8', 'ignore').splitlines()[:1])
