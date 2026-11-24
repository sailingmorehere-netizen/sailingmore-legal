"""osm.json + federations.json -> projets/clubs-monde/clubs.json et site/clubs.html (FR).
Lancer depuis la racine de la copie : python3 scripts/clubs_generer.py
Aucun contact sans source : chaque contact porte {valeur, source, url, date}. Sans source, pas de ligne.
"""
import json, os, re, html, unicodedata

SEUIL_FICHE = 3            # nombre d'infos utiles pour avoir une fiche (même règle que les ports)
D = 'projets/clubs-monde/'
OUT = 'projets/sailingmore/site/clubs.html'

def slug(s):
    s = unicodedata.normalize('NFD', s.lower()).encode('ascii', 'ignore').decode()
    return re.sub(r'[^a-z0-9]+', '-', s).strip('-')

def activite(t):
    sp = (t.get('sport') or '').split(';')
    voile = 'sailing' in sp or t.get('club') == 'sailing'
    moteur = any(x in sp for x in ('motor', 'motor_boating', 'boating', 'powerboat'))
    if voile and moteur: return 'les deux'
    if voile: return 'voile'
    if moteur: return 'moteur'
    return 'à préciser'   # club=yacht / sport=yachting seul : on ne devine pas

def charger_osm():
    if not os.path.exists(D + 'osm.json'): return [], ''
    j = json.load(open(D + 'osm.json', encoding='utf-8'))
    out = []
    for e in j['elements']:
        t = e.get('tags', {}); nom = t.get('name')
        if not nom: continue
        lat = e.get('lat') or (e.get('center') or {}).get('lat'); lon = e.get('lon') or (e.get('center') or {}).get('lon')
        src = 'OpenStreetMap (ODbL)'; url = 'https://www.openstreetmap.org/%s/%s' % (e['type'], e['id'])
        c = {}
        for cle, ks in (('site', ('website', 'contact:website')), ('email', ('email', 'contact:email')),
                        ('tel', ('phone', 'contact:phone'))):
            for k in ks:
                if t.get(k): c[cle] = {'valeur': t[k], 'source': src, 'url': url, 'date': j['releve']}; break
        adr = ' '.join(t[k] for k in ('addr:housenumber', 'addr:street', 'addr:postcode', 'addr:city') if t.get(k))
        if adr: c['adresse'] = {'valeur': adr, 'source': src, 'url': url, 'date': j['releve']}
        out.append({'nom': nom, 'pays': (t.get('addr:country') or '').upper(), 'lat': lat, 'lon': lon,
                    'activite': activite(t), 'contacts': c, 'variantes': [t[k] for k in ('short_name', 'alt_name') if t.get(k)]})
    return out, j['releve']

def charger_fed():
    if not os.path.exists(D + 'federations.json'): return []
    out = []
    for f in json.load(open(D + 'federations.json', encoding='utf-8')):
        c = {k: {'valeur': v, 'source': f['source'], 'url': f['url'], 'date': f['date']} for k, v in f.get('contacts', {}).items() if v}
        out.append({'nom': f['nom'], 'pays': f.get('pays', ''), 'lat': f.get('lat'), 'lon': f.get('lon'),
                    'activite': f.get('activite', 'à préciser'), 'contacts': c, 'variantes': f.get('variantes', [])})
    return out

def main():
    osm, releve = charger_osm(); clubs = osm + charger_fed()
    vus = {}
    for c in clubs:   # doublon exact nom+pays : on fusionne les contacts, la première source gagne
        k = (slug(c['nom']), c['pays'])
        if k in vus:
            for kk, v in c['contacts'].items(): vus[k]['contacts'].setdefault(kk, v)
        else: vus[k] = c
    clubs = sorted(vus.values(), key=lambda c: c['nom'].lower())
    deja = {}
    for c in clubs:
        base = slug(c['nom']) + (('-' + c['pays'].lower()) if c['pays'] else '')
        n = deja.get(base, 0); deja[base] = n + 1
        c['id'] = base + ('-%d' % (n + 1) if n else '')
        infos = len(c['contacts']) + (1 if c['lat'] is not None else 0) + (1 if c['activite'] != 'à préciser' else 0)
        c['fiche'] = infos >= SEUIL_FICHE
    os.makedirs(D, exist_ok=True)
    json.dump(clubs, open(D + 'clubs.json', 'w', encoding='utf-8'), ensure_ascii=False)
    lignes = [[c['id'], c['nom'], c['pays'], c['activite'], 'o' if c['fiche'] else '',
               (c['contacts'].get('site') or {}).get('valeur', '')] for c in clubs]
    titre = 'Clubs de voile du monde : annuaire et contacts | Sailing More'
    n = len(clubs)
    desc = 'Annuaire des clubs de voile et yacht clubs (%d clubs) : recherche par nom, filtre voile / moteur, contacts sourcés.' % n
    page = PAGE % dict(titre=titre, desc=html.escape(desc, quote=True), n=n, js=json.dumps(lignes, ensure_ascii=False, separators=(',', ':')),
                       releve=releve or 'aucun relevé pour l\'instant',
                       vide='' if n else '<p class="meta">L\'annuaire est en cours de constitution : les premiers clubs arrivent avec le prochain relevé.</p>')
    open(OUT, 'w', encoding='utf-8').write(page)
    print('ok', n, 'clubs;', sum(c['fiche'] for c in clubs), 'passent le seuil de fiche;', len(page), 'octets')

PAGE = '''<!doctype html>
<html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>%(titre)s</title><meta name="description" content="%(desc)s">
<link rel="canonical" href="https://sailingmore.fr/clubs.html">
<style>body{margin:0;background:#0a1a2b;color:#eef3f7;font-family:system-ui,sans-serif;line-height:1.5}.page{max-width:60rem;margin:0 auto;padding:3rem 1.2rem}
a{color:#fff}input,select{font:inherit;color:#fff;background:#12304d;border:1px solid rgba(255,255,255,.25);border-radius:4px;padding:.55rem .7rem}
h1{font-weight:300}ul{list-style:none;padding:0}li{padding:.5rem 0;border-bottom:1px solid rgba(255,255,255,.1);display:flex;justify-content:space-between;gap:.8rem;flex-wrap:wrap}.meta{color:#9db2c6;font-size:.85rem}</style></head>
<body><div class="page"><a href="/">← Sailing More</a><h1>Clubs de voile du monde</h1>
<p>%(n)d clubs. Un club n'a de ligne de contact que si nous avons la source ; un yacht club de moteur figure dans l'annuaire avec sa mention, hors de la liste « voile ».</p>%(vide)s
<input id="q" type="search" placeholder="Nom d'un club" aria-label="Nom du club"> <select id="a" aria-label="Activité"><option value="">Voile, moteur, les deux</option><option>voile</option><option>moteur</option><option>les deux</option><option>à préciser</option></select>
<p class="meta" id="cpt"></p><ul id="l"></ul><button id="plus" hidden>Voir plus</button>
<p class="meta">Données © les contributeurs d'<a href="https://www.openstreetmap.org/copyright" rel="noopener">OpenStreetMap</a> (ODbL) et fédérations citées fiche par fiche. Relevé : %(releve)s.</p></div>
<script>var D=%(js)s,$=function(i){return document.getElementById(i)},res=[],sh=0;
function pli(s){return s.toLowerCase().normalize('NFD').replace(/[\\u0300-\\u036f]/g,'')}
D.forEach(function(d){d.push(pli(d[1]))});
function f(){var q=pli($('q').value.trim()),a=$('a').value;res=D.filter(function(d){return(!q||d[6].indexOf(q)>=0)&&(!a||d[3]===a)});sh=0;$('l').innerHTML='';s();$('cpt').textContent=res.length+' club'+(res.length>1?'s':'')}
function s(){var e=Math.min(res.length,sh+50);for(var i=sh;i<e;i++){var d=res[i],li=document.createElement('li'),n=document.createElement(d[4]?'a':'span');n.textContent=d[1];if(d[4])n.href='/clubs/'+d[0]+'.html';var m=document.createElement('span');m.className='meta';m.textContent=[d[2],d[3]].filter(Boolean).join(' · ');li.appendChild(n);li.appendChild(m);$('l').appendChild(li)}sh=e;$('plus').hidden=sh>=res.length}
$('q').oninput=f;$('a').onchange=f;$('plus').onclick=s;f();</script></body></html>
'''

main()
