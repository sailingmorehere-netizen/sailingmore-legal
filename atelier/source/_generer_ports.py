"""Génère site/ports.html depuis projets/sailingmore/ports.sqlite (lecture seule).
Lancer depuis la racine de la copie : python3 scripts/_generer_ports.py
"""
import json, sqlite3, html

SEUIL_FICHE = 3  # règle du 24/11/2026 : réglable ici
DB = 'projets/sailingmore/ports.sqlite'
OUT = 'projets/sailingmore/site/ports.html'
NOMS = {'croatia': 'Croatie', 'greece': 'Grèce'}

c = sqlite3.connect(DB)
rows = c.execute("select id, nom, nom_local, pays, lat, lon, type, nb, tags from ports "
                 "where nom is not null and nom<>'' order by nom").fetchall()
releve = c.execute("select max(releve) from ports").fetchone()[0]
total = c.execute("select count(*) from ports").fetchone()[0]

def tag(t, *ks):
    for k in ks:
        if t.get(k):
            return t[k]
    return ''

data = []
for i, nom, loc, pays, lat, lon, typ, nb, tags in rows:
    t = json.loads(tags or '{}')
    data.append([i, nom, pays, round(lat, 4), round(lon, 4), typ or '', nb or 0,
                 tag(t, 'vhf', 'seamark:radio_station:channel', 'seamark:harbour:vhf'),
                 'o' if (t.get('fuel') == 'yes' or t.get('seamark:small_craft_facility:category', '').find('fuel') >= 0) else '',
                 'o' if (t.get('drinking_water') == 'yes' or t.get('water_point') == 'yes') else '',
                 tag(t, 'website', 'contact:website')])

pays_list = sorted({d[2] for d in data})
n_fiches = sum(1 for d in data if d[6] >= SEUIL_FICHE)
js = json.dumps(data, ensure_ascii=False, separators=(',', ':'))
noms = json.dumps({p: NOMS.get(p, p.capitalize()) for p in pays_list}, ensure_ascii=False)

titre = 'Ports du monde et marinas : carte et annuaire | Sailing More'
# Audit SEO du 24/11/2026, correction 4 : texte de l'audit, le nombre vient de `total` (la base des ports).
desc = ('%d ports, marinas et mouillages (OpenStreetMap) : cherchez par nom ou par pays, voyez la carte '
        'et calculez la distance entre deux ports.' % total)
ld = {"@context": "https://schema.org", "@graph": [
    {"@type": "CollectionPage", "name": titre, "url": "https://sailingmore.fr/ports.html", "inLanguage": "fr"},
    {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Accueil", "item": "https://sailingmore.fr/"},
        {"@type": "ListItem", "position": 2, "name": "Ports du monde", "item": "https://sailingmore.fr/ports.html"}]}]}

page = '''<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>%(titre)s</title>
<meta name="description" content="%(desc)s">
<link rel="canonical" href="https://sailingmore.fr/ports.html">
<meta property="og:title" content="%(titre)s"><meta property="og:description" content="%(desc)s">
<meta property="og:url" content="https://sailingmore.fr/ports.html"><meta property="og:type" content="website">
<meta property="og:site_name" content="Sailing More"><meta property="og:image" content="https://sailingmore.fr/og-image.jpg">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:image" content="https://sailingmore.fr/og-image.jpg">
<script type="application/ld+json">%(ld)s</script>
<style>
body{margin:0;background:#0a1a2b;color:#eef3f7;font-family:system-ui,-apple-system,"Helvetica Neue",Arial,sans-serif;line-height:1.5}
.page{max-width:60rem;margin:0 auto;padding:3rem 1.2rem 4rem}
a{color:#fff}a.retour{color:#9db2c6;text-decoration:none;font-size:.64rem;letter-spacing:.14em;text-transform:uppercase}
h1{font-weight:300;font-size:clamp(2rem,6vw,2.8rem);margin:1.4rem 0 .4rem}
h2{color:#9db2c6;font-weight:500;letter-spacing:.18em;font-size:.7rem;text-transform:uppercase;margin:2.4rem 0 .8rem}
.filet{height:1px;max-width:16rem;background:linear-gradient(90deg,#e23a3e 0 34%%,rgba(255,255,255,.18) 34%% 100%%);margin:1rem 0 1.4rem}
input,select,button{font:inherit;color:#fff;background:#12304d;border:1px solid rgba(255,255,255,.25);border-radius:4px;padding:.55rem .7rem;min-width:0}
.barre{display:flex;gap:.6rem;flex-wrap:wrap}.barre input{flex:1 1 14rem}
#carte{width:100%%;height:auto;background:#06121f;border:1px solid rgba(255,255,255,.15);display:block;margin-top:1rem}
ul.liste{list-style:none;padding:0;margin:1rem 0}
ul.liste li{padding:.5rem 0;border-bottom:1px solid rgba(255,255,255,.1);display:flex;gap:.8rem;justify-content:space-between;flex-wrap:wrap}
.meta{color:#9db2c6;font-size:.85rem}
.dist{display:grid;grid-template-columns:1fr 1fr;gap:.6rem}
#res{font-size:1.3rem;font-weight:300;margin-top:.8rem}
.pied{color:#9db2c6;font-size:.8rem;margin-top:3rem}
@media(max-width:34rem){.dist{grid-template-columns:1fr}}
</style>
</head>
<body><div class="page">
<a class="retour" href="/">← Sailing More</a>
<h1>Ports du monde</h1>
<div class="filet"></div>
<p>%(total)d ports, marinas et mouillages relevés dans OpenStreetMap (%(npays)d pays pour l'instant). Cherchez un port, parcourez un pays, mesurez la distance à vol d'oiseau entre deux ports.</p>

<h2>Trouver un port</h2>
<div class="barre">
<input id="q" type="search" placeholder="Nom d'un port (ex. Split, Bonifacio)" autocomplete="off" aria-label="Nom du port">
<select id="p" aria-label="Pays"><option value="">Tous les pays</option></select>
<select id="t" aria-label="Type"><option value="">Tous types</option></select>
</div>
<p class="meta" id="cpt"></p>
<canvas id="carte" width="900" height="420" aria-label="Carte des ports : chaque point est un port"></canvas>
<ul class="liste" id="liste"></ul>
<button id="plus" type="button" hidden>Voir plus</button>

<h2>Distance entre deux ports</h2>
<p class="meta">Orthodromie (ligne la plus courte sur la sphère), pas un itinéraire maritime : contournements, caps et zones interdites ne sont pas comptés.</p>
<div class="dist">
<input id="a" list="dl" placeholder="Port de départ" aria-label="Port de départ">
<input id="b" list="dl" placeholder="Port d'arrivée" aria-label="Port d'arrivée">
</div>
<datalist id="dl"></datalist>
<div id="res" aria-live="polite"></div>

<p class="pied">Données © les contributeurs d'<a href="https://www.openstreetmap.org/copyright" rel="noopener">OpenStreetMap</a>, licence ODbL. Relevé du %(releve)s. Les informations de navigation sont indicatives : vérifiez-les auprès de la capitainerie et des documents nautiques officiels.</p>
</div>
<script>
var D=%(js)s, PAYS=%(noms)s, PAGE=50;
// colonnes : 0 id,1 nom,2 pays,3 lat,4 lon,5 type,6 nb,7 vhf,8 carburant,9 eau,10 site
var $=function(i){return document.getElementById(i)};
function pli(s){return s.toLowerCase().normalize('NFD').replace(/[\\u0300-\\u036f]/g,'')}
D.forEach(function(d){d.push(pli(d[1]))});
var ps=Object.keys(PAYS).sort(), ts=[];
D.forEach(function(d){if(d[5]&&ts.indexOf(d[5])<0)ts.push(d[5])});ts.sort();
ps.forEach(function(p){var o=document.createElement('option');o.value=p;o.textContent=PAYS[p];$('p').appendChild(o)});
ts.forEach(function(p){var o=document.createElement('option');o.value=p;o.textContent=p;$('t').appendChild(o)});
var dl=$('dl');D.forEach(function(d){var o=document.createElement('option');o.value=d[1]+' ('+PAYS[d[2]]+') #'+d[0];dl.appendChild(o)});
var res=[],shown=0;
function filtre(){
  var q=pli($('q').value.trim()),p=$('p').value,t=$('t').value;
  res=D.filter(function(d){return (!q||d[11].indexOf(q)>=0)&&(!p||d[2]===p)&&(!t||d[5]===t)});
  shown=0;$('liste').innerHTML='';suite();
  $('cpt').textContent=res.length+' port'+(res.length>1?'s':'');
  dessin();
}
function suite(){
  var ul=$('liste'),fin=Math.min(res.length,shown+PAGE);
  for(var i=shown;i<fin;i++){var d=res[i],li=document.createElement('li'),a=document.createElement(d[10]?'a':'span');
    a.textContent=d[1];if(d[10]){a.href=d[10];a.rel='noopener nofollow'}
    var m=document.createElement('span');m.className='meta';
    m.textContent=[PAYS[d[2]],d[5],d[7]?'VHF '+d[7]:'',d[8]?'carburant':'',d[9]?'eau':''].filter(Boolean).join(' · ');
    li.appendChild(a);li.appendChild(m);ul.appendChild(li)}
  shown=fin;$('plus').hidden=shown>=res.length;
}
function dessin(){
  var cv=$('carte'),x=cv.getContext('2d'),W=cv.width,H=cv.height;x.clearRect(0,0,W,H);
  if(!res.length)return;
  var a=90,b=-90,c=180,e=-180;res.forEach(function(d){a=Math.min(a,d[3]);b=Math.max(b,d[3]);c=Math.min(c,d[4]);e=Math.max(e,d[4])});
  var mx=Math.max(.5,(e-c)*.05),my=Math.max(.5,(b-a)*.05);c-=mx;e+=mx;a-=my;b+=my;
  var k=Math.cos((a+b)/2*Math.PI/180),sx=W/((e-c)*k),sy=H/(b-a),s=Math.min(sx,sy),ox=(W-(e-c)*k*s)/2,oy=(H-(b-a)*s)/2;
  x.fillStyle='#e23a3e';
  res.forEach(function(d){x.fillRect(ox+(d[4]-c)*k*s-1.5,oy+(b-d[3])*s-1.5,3,3)});
}
function hav(a,b){var R=6371.0088,r=Math.PI/180,dp=(b[3]-a[3])*r,dl=(b[4]-a[4])*r,
  h=Math.sin(dp/2)*Math.sin(dp/2)+Math.cos(a[3]*r)*Math.cos(b[3]*r)*Math.sin(dl/2)*Math.sin(dl/2);
  return 2*R*Math.asin(Math.sqrt(h))}
function trouve(v){var m=/#(\\d+)$/.exec(v);if(m){var id=+m[1];for(var i=0;i<D.length;i++)if(D[i][0]===id)return D[i]}
  var q=pli(v.trim());for(var j=0;j<D.length;j++)if(D[j][11]===q)return D[j];return null}
function calc(){var A=trouve($('a').value),B=trouve($('b').value);
  if(!A||!B){$('res').textContent='';return}
  var km=hav(A,B);$('res').textContent=A[1]+' → '+B[1]+' : '+Math.round(km)+' km, soit '+(km/1.852).toFixed(0)+' milles nautiques (vol d\\'oiseau)'}
$('q').addEventListener('input',filtre);$('p').addEventListener('change',filtre);$('t').addEventListener('change',filtre);
$('plus').addEventListener('click',suite);$('a').addEventListener('input',calc);$('b').addEventListener('input',calc);
filtre();
</script>
</body></html>
''' % dict(titre=titre, desc=html.escape(desc, quote=True), ld=json.dumps(ld, ensure_ascii=False),
           total=total, npays=len(pays_list), releve=releve, js=js, noms=noms)

with open(OUT, 'w', encoding='utf-8') as f:
    f.write(page)
print('ok', len(page), 'octets;', total, 'ports;', n_fiches, 'passent le seuil de fiche (', SEUIL_FICHE, ')')
