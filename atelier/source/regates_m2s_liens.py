"""Remplit regates.json[].lien pour les événements manage2sail sans lien, par le lien officiel
trouvé dans la recherche manage2sail (lecture seule). Clé : nom + début (+ pays). Sinon vide."""
import json, re, sys, time, html as H, unicodedata, urllib.request, collections
B = '/opt/data/cache/claude-nuit/travail/projets/sailingmore/'
UA = {'User-Agent': 'Mozilla/5.0'}


def lit(u):
    for n in range(3):
        try:
            return urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=60).read().decode('utf-8', 'ignore')
        except Exception:
            time.sleep(2 * (n + 1))
    return ''


def k(s):
    s = unicodedata.normalize('NFKD', s or '')
    return re.sub(r'[\W_]+', '', ''.join(c for c in s if not unicodedata.combining(c)).lower())


def txt(s):
    return H.unescape(re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', s))).strip()


d = json.load(open(B + 'regates.json', encoding='utf-8'))
L = d['regates']
vides = [x for x in L if not x.get('lien')]
annees = sorted({x['debut'][:4] for x in vides})
print('annees', annees, len(vides), flush=True)
trouve = collections.defaultdict(set); lignes = []
for a in annees:
    h = lit(f'https://www.manage2sail.com/en-US/search?filterYear={a}&page=1')
    m = re.search(r'filterYear=\d+&amp;page=(\d+)">Last', h)
    n = int(m.group(1)) if m else 1
    for pg in range(1, n + 1):
        if pg > 1:
            h = lit(f'https://www.manage2sail.com/en-US/search?filterYear={a}&page={pg}')
        for tr in re.findall(r'(?s)<tr>(.*?)</tr>', h):
            tds = re.findall(r'(?s)<td[^>]*>(.*?)</td>', tr)
            if len(tds) < 7:
                continue
            lien = re.search(r'href="/[a-z]{2}-[A-Z]{2}/event/([0-9a-f-]{36})"', tds[3])
            dd = txt(tds[1])
            if not lien or not re.match(r'\d{2}\.\d{2}\.', dd):
                continue
            j, mo = dd[:5].split('.')
            trouve[(k(txt(tds[3])), f'{a}-{mo}-{j}')].add(lien.group(1))
            lignes.append((f'{a}-{mo}-{j}', txt(tds[3]), txt(tds[6]), txt(tds[7]), lien.group(1)))
        if pg % 25 == 0:
            print(a, pg, '/', n, flush=True)
json.dump(lignes, open('/tmp/m2s_lignes.json', 'w'))
import difflib
par_date = collections.defaultdict(list)
for l in lignes:
    par_date[l[0]].append(l)
rempli = 0
for x in vides:
    ids = trouve.get((k(x['nom']), x['debut']))
    if not ids:
        # même début + même ville ou même club + nom proche : un seul candidat sûr
        c = set()
        for l in par_date.get(x['debut'], []):
            if k(l[2]) == k(x['ville']) or (x['club'] and k(l[3]) == k(x['club'])):
                if difflib.SequenceMatcher(None, k(l[1]), k(x['nom'])).ratio() >= 0.6:
                    c.add(l[4])
        ids = c
    if ids and len(ids) == 1:
        i = next(iter(ids))
        x['lien'] = 'https://www.manage2sail.com/fr-CH/event/' + i if False else 'https://www.manage2sail.com/en-US/event/' + i
        rempli += 1
import shutil
shutil.copyfile(B + 'regates.json', B + 'regates.json.bak-avant-56')
json.dump(d, open(B + 'regates.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('remplis', rempli, 'sur', len(vides))
