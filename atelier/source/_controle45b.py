import re, json, collections
s = open('projets/sailingmore/site/stages.html', encoding='utf-8').read()
blocs = re.findall(r'<script(?![^>]*src)[^>]*>(.*?)</script>', s, re.S)
D = [json.loads(b) for b in blocs if b.lstrip().startswith('{"ui"')][0]
of = D['offres']
print(sorted(of[0].keys()))
for name, fn in [
    ('lien|titre|debut', lambda o: '|'.join(str(o.get(k, '')) for k in ('lien', 'titre', 'debut'))),
    ('lien|titre|debut|fin|prix', lambda o: '|'.join(str(o.get(k, '')) for k in ('lien', 'titre', 'debut', 'fin', 'prix'))),
    ('ecole_slug|lien|titre|debut|fin|prix|lieu', lambda o: '|'.join(str(o.get(k, '')) for k in ('ecole_slug', 'lien', 'titre', 'debut', 'fin', 'prix', 'lieu'))),
]:
    c = collections.Counter(fn(o) for o in of)
    print(name, len(of), len(c), [k for k, v in c.items() if v > 1][:3])
