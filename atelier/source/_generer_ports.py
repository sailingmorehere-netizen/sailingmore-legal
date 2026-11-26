"""Génère site/ports.html depuis projets/sailingmore/ports.sqlite (lecture seule).
Lancer depuis la racine de la copie : python3 scripts/_generer_ports.py
"""
import json, sqlite3, html, os, base64, sys
sys.path.insert(0, '/opt/data/scripts')
from ports_fiches import PAYS_FR

# id -> nom de fichier de la fiche, écrit par ports_fiches.py : la carte ne recalcule pas
# un slug de son côté, elle recopie celui qui existe (sinon lien mort).
try:
    _PAGES = json.load(open('/opt/data/cache/ports-fiches-pages.json'))
except (OSError, ValueError):
    _PAGES = {}

SEUIL_FICHE = 3  # règle du 24/11/2026 : réglable ici
DB = os.path.join(os.environ.get('SITE_ROOT', '.'), 'projets/sailingmore/ports.sqlite')  # même base que le site reconstruit
OUT = os.path.join(os.environ.get('SITE_ROOT', '.'), 'projets/sailingmore/site/ports.html')

c = sqlite3.connect(DB)
# Le pays est en base au code ISO 3166-1 alpha-3 (`pays`), le nom lisible à côté (`pays_nom`). La page
# n'a plus de table à maintenir : ajouter un pays dans la base suffit à le voir apparaître dans le menu,
# avec son nom en français (Intl.DisplayNames côté navigateur).
rows = c.execute("select id, nom, nom_local, pays, pays_nom, lat, lon, type, nb, tags, berths_emodnet"
                 " from ports where nom is not null and nom<>'' order by nom").fetchall()
releve = c.execute("select max(releve) from ports").fetchone()[0]
# Le compte affiché est celui des ports que la page montre : une marina sans nom reste en base pour la
# carte du pays, mais elle n'apparaît pas ici, et annoncer un total plus gros que la liste serait faux.
total = len(rows)  # recalculé après le filtre des noms, plus bas


def tag(t, *ks):
    for k in ks:
        if t.get(k):
            return t[k]
    return ''


def nom_utile(nom):
    """Un nom qui dit quelque chose — même règle que ports_fiches.py.

    « Dok 3 », « C10 », « SG 53 » sont des places de ponton : les lister remplissait la page de
    numéros et faisait des fiches intitulées « 1 ».
    """
    import re as _re
    nom = ' '.join(str(nom).split())
    nom = _re.sub(r"\s*;\s*", " / ", nom)
    lettres = len(_re.findall(r'[^\W\d_]', nom, _re.U))
    if len(_re.sub(r"[^\w]", "", nom, _re.U)) < 3 or lettres < 1:
        return ''
    if _re.search(r"\d", nom) and lettres < 4:
        return ''
    return nom


def _nom_pays(code, pays_nom):
    """Le pays en français. La page affichait « HUN » à côté de « Allemagne » : le convertisseur de
    site_blocks attend des codes à deux lettres, la base porte de l'ISO à trois."""
    return PAYS_FR.get(code or '') or (pays_nom or '').capitalize() or (code or '')

data = []

for i, nom, loc, pays, pays_nom, lat, lon, typ, nb, tags, places in rows:
    nom = nom_utile(nom)
    if not nom:
        continue
    t = json.loads(tags or '{}')
    data.append([i, nom, pays or '', round(lat, 4), round(lon, 4), typ or '', nb or 0,
                 tag(t, 'vhf', 'seamark:radio_station:channel', 'seamark:harbour:vhf'),
                 'o' if (t.get('fuel') == 'yes' or t.get('seamark:small_craft_facility:category', '').find('fuel') >= 0) else '',
                 'o' if (t.get('drinking_water') == 'yes' or t.get('water_point') == 'yes') else '',
                 tag(t, 'website', 'contact:website'),
                 places or '', pays_nom or '',
                 ('/ports/' + _PAGES[str(i)]) if str(i) in _PAGES else '',
                 _nom_pays(pays, pays_nom)])

total = len(data)

# Le fond de carte : les côtes du monde, les mêmes que la carte du Léman — terre crème, mer bleue.
# Natural Earth 1:110m, arrondi à deux décimales (76 Ko). Embarqué dans la page : rien à charger.
_terres = json.load(open(os.path.join(os.environ.get('SITE_ROOT', '.'), 'projets/sailingmore/terres-monde.json')))
terres = json.dumps(_terres, separators=(',', ':'))
_lacs = json.load(open(os.path.join(os.environ.get('SITE_ROOT', '.'), 'projets/sailingmore/lacs-monde.json')))
lacs = json.dumps(_lacs, separators=(',', ':'))

# La bathymétrie du monde : le relief ombré de Natural Earth 1:50m, ramené à 2700 px et désaturé
# pour rester aussi sobre que la carte du Léman. Posé au-dessus, il donne les fonds — fosses,
# dorsales, plateaux — sans réclamer de données de profondeur qu'on n'a pas.
_base = os.environ.get('SITE_ROOT', '/opt/data')
_relief = open(os.path.join(_base, 'projets/sailingmore/relief-monde.jpg'), 'rb').read()
relief = 'data:image/jpeg;base64,' + base64.b64encode(_relief).decode('ascii')
# Les noms : villes, mers et océans, lacs, fleuves — Natural Earth 1:50m, en français quand il existe.
_topo = json.load(open(os.path.join(_base, 'projets/sailingmore/toponymes-monde.json')))
topo = json.dumps(_topo, ensure_ascii=False, separators=(',', ':'))

pays_list = sorted({d[2] for d in data if d[2]})
n_fiches = sum(1 for d in data if d[6] >= SEUIL_FICHE)
js = json.dumps(data, ensure_ascii=False, separators=(',', ':'))

titre = 'Ports et marinas du monde : carte et annuaire | Sailing More'
# Audit SEO du 24/11/2026, correction 4 : texte de l'audit, le nombre vient de `total` (la base des ports).
desc = ('%d ports, marinas et mouillages (OpenStreetMap et EMODnet) : cherchez par nom ou par pays, voyez la '
        'carte et calculez la distance entre deux ports.' % total)
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
<p>%(total)d ports, marinas et mouillages relevés dans OpenStreetMap et EMODnet (%(npays)d pays). Cherchez un port, parcourez un pays, mesurez la distance à vol d'oiseau entre deux ports.</p>

<h2>Trouver un port</h2>
<div class="barre">
<input id="q" type="search" placeholder="Nom d'un port (ex. Split, Bonifacio)" autocomplete="off" aria-label="Nom du port">
<select id="p" aria-label="Pays" disabled><option value="">Tous les pays</option></select>
<button type="button" id="moi" hidden>Me localiser</button>
<select id="t" aria-label="Type"><option value="">Tous types</option></select>
</div>
<p class="meta" id="cpt"></p>
<div class="modes" role="group" aria-label="Ce que montre la carte">
<button type="button" id="m-ports" class="on">Ports</button>
<button type="button" id="m-fonds">Fonds et noms</button>
</div>
<div id="carte-wrap">
<canvas id="carte" width="900" height="420" aria-label="Carte des ports : chaque point est un port" tabindex="0"></canvas>
<div id="carte-nav"><button type="button" id="z+">+</button><button type="button" id="z-">−</button><button type="button" id="z0" title="Vue entière">⤢</button></div>
<div id="carte-inf"></div>
<div id="carte-aide">Molette ou pincer pour zoomer · glisser pour se déplacer · double-clic pour rapprocher · cliquez un point pour sa fiche</div>
<div id="fiche" hidden><button type="button" id="fiche-x" aria-label="Fermer">×</button><div id="fiche-c"></div></div>
</div>
<ul class="liste" id="liste"></ul>
<button id="plus" type="button" hidden>Voir plus</button>
<p class="meta" id="geo"></p>

<h2>Distance entre deux ports</h2>
<p class="meta">Orthodromie (ligne la plus courte sur la sphère), pas un itinéraire maritime : contournements, caps et zones interdites ne sont pas comptés.</p>
<div class="dist">
<input id="a" list="dl" placeholder="Port de départ" aria-label="Port de départ">
<input id="b" list="dl" placeholder="Port d'arrivée" aria-label="Port d'arrivée">
</div>
<datalist id="dl"></datalist>
<div id="res" aria-live="polite"></div>

<p class="pied">Données © les contributeurs d'<a href="https://www.openstreetmap.org/copyright" rel="noopener">OpenStreetMap</a>, licence ODbL, et <a href="https://emodnet.ec.europa.eu/en/human-activities" rel="noopener">EMODnet Human Activities</a>, licence CC-BY 4.0. Relevé du %(releve)s. Les informations de navigation sont indicatives : vérifiez-les auprès de la capitainerie et des documents nautiques officiels.</p>
</div>
<script src="/pays-visiteur.js"></script>
<script src="/geo-accueil.js"></script>
<style>
#carte-wrap{position:relative;margin-top:1rem}
#carte{width:100%%;height:auto;background:#06121f;border:1px solid rgba(255,255,255,.15);display:block;cursor:grab;touch-action:none;margin-top:0}
#carte.pan{cursor:grabbing}
#carte-nav{position:absolute;top:.5rem;right:.5rem;display:flex;flex-direction:column;gap:.25rem}
#carte-nav button{width:2.2rem;height:2.2rem;padding:0;font-size:1.1rem;line-height:1;background:rgba(18,48,77,.92);border:1px solid rgba(255,255,255,.25);border-radius:4px;color:#fff;cursor:pointer}
#carte-aide{position:absolute;left:.6rem;bottom:.5rem;font-size:.78rem;color:#eef3f7;background:rgba(12,30,47,.6);padding:.25rem .5rem;border-radius:.4rem;pointer-events:none}
#carte-inf{position:absolute;left:.6rem;top:.5rem;font-size:.8rem;background:rgba(10,26,43,.86);border:1px solid rgba(255,255,255,.15);border-radius:4px;padding:.2rem .5rem;color:#eef3f7;pointer-events:none}
.modes{display:flex;gap:.4rem;margin-top:1rem}
.modes button{background:rgba(18,48,77,.55);border:1px solid rgba(255,255,255,.22);color:#9db2c6;padding:.34rem .85rem;font-size:.82rem;border-radius:999px;cursor:pointer}
.modes button.on{background:#e23a3e;border-color:#e23a3e;color:#fff}
#fiche{position:absolute;left:.6rem;bottom:.6rem;max-width:min(21rem,78%%);background:rgba(10,26,43,.95);border:1px solid rgba(255,255,255,.22);border-radius:6px;padding:.65rem .8rem .55rem;font-size:.85rem;color:#eef3f7;box-shadow:0 .4rem 1.2rem rgba(0,0,0,.45)}
#fiche h3{margin:0 1.5rem .15rem 0;font-size:1rem;font-weight:600}
#fiche p{margin:.15rem 0;color:#c7d5e1;font-size:.8rem}
#fiche p.fp{color:#9db2c6}
#fiche a{color:#8fd0f5}
#fiche-x{position:absolute;top:.25rem;right:.3rem;background:none;border:0;color:#9db2c6;font-size:1.25rem;line-height:1;cursor:pointer;padding:0 .25rem}
#fiche-x:hover{color:#fff}
ul.liste li.joue{cursor:pointer}
</style>
<script>
var TERRES=%(terres)s, LACS=%(lacs)s, D=%(js)s, PAGE=50, RELIEF='%(relief)s', TOPO=%(topo)s, mode='ports';
// colonnes : 0 id,1 nom,2 pays(ISO alpha-3),3 lat,4 lon,5 type,6 nb,7 vhf,8 carburant,9 eau,10 site,11 places,12 pays d'origine
var $=function(i){return document.getElementById(i)};
function pli(s){return s.toLowerCase().normalize('NFD').replace(/[\\u0300-\\u036f]/g,'')}
/* Le nom du pays en français, à partir du code : « HRV » donne « Croatie ». `smPays.nom` lit
   `Intl.DisplayNames`, donc tous les pays de la base sont nommés sans table à tenir à jour. */
function nomPays(c){return (window.smPays&&window.smPays.nom(c))||c}
D.forEach(function(d){d.push(pli(d[1]+' '+(d[14]||'')))});  // 15 : clé de recherche
var ps=[],ts=[];
D.forEach(function(d){if(d[2]&&ps.indexOf(d[2])<0)ps.push(d[2])});
D.forEach(function(d){if(d[5]&&ts.indexOf(d[5])<0)ts.push(d[5])});
ps.sort(function(a,b){return nomPays(a).localeCompare(nomPays(b))});ts.sort();
ps.forEach(function(p){var o=document.createElement('option');o.value=p;o.textContent=nomPays(p);$('p').appendChild(o)});
/* Tous les ports du monde par défaut (25/11/2026). Le pays du visiteur ne coche plus le filtre tout
   seul : la carte s'ouvre sur le monde entier. Le menu des pays reste, et « Me localiser » le remplit
   quand on le demande — c'est un clic, donc un accord. */
function paysLu(c){
  $('p').disabled=false;if('geolocation' in navigator)$('moi').hidden=false;
  if(c&&ps.length&&ps.indexOf(c)<0)$('geo').textContent='Rien encore pour '+nomPays(c)+' : la base couvre '+ps.length+' pays.';
  filtre();
}
ts.forEach(function(p){var o=document.createElement('option');o.value=p;o.textContent=p;$('t').appendChild(o)});
var dl=$('dl');D.forEach(function(d){var o=document.createElement('option');o.value=d[1]+' ('+nomPays(d[2])+') #'+d[0];dl.appendChild(o)});
var res=[],shown=0;
/* POS : la position du visiteur, seulement s'il a cliqué sur « Me localiser » (jamais demandée au
   chargement). Elle reste dans le navigateur et sert à deux choses : remplir le pays, et trier par
   distance. */
var POS=null;
/* Deux choses quand on a la position : le pays, et le nom (« Me localiser » affiche « Près de
   Lausanne, VD », jamais des coordonnées). C'est le seul appel qui sort, et seulement sur ce clic. */
function localisation(lat,lon,fin){
  if(!window.smPays)return fin('','');
  fetch('https://ipwho.is/').then(function(r){return r.json()}).then(function(d){
    var code2=d&&d.country_code?String(d.country_code).toUpperCase():'';
    var c2=code2?window.smPays.ISO[code2]:'';
    var c=c2&&ps.indexOf(c2)>=0?c2:'';
    var nom=[d&&d.city,d&&d.region].filter(Boolean).join(', ');
    window.smPays.retenir(code2);
    fin(c,nom);
  }).catch(function(){fin('','')});
}
function filtre(){
  var q=pli($('q').value.trim()),p=$('p').value,t=$('t').value;
  res=D.filter(function(d){return (!q||d[15].indexOf(q)>=0)&&(!p||d[2]===p)&&(!t||d[5]===t)});
  if(POS)res.sort(function(x,y){return hav(POS[0],POS[1],x[3],x[4])-hav(POS[0],POS[1],y[3],y[4])});
  shown=0;$('liste').innerHTML='';suite();
  $('cpt').textContent=res.length+' port'+(res.length>1?'s':'');
  dessin();
}
function suite(){
  var ul=$('liste'),fin=Math.min(res.length,shown+PAGE);
  for(var i=shown;i<fin;i++){var d=res[i],li=document.createElement('li'),a=document.createElement('a');
    a.textContent=nomPort(d);
    if(d[13]){a.href=d[13];a.title='Ouvrir la fiche de '+d[1];}else{a.href=d[10]||'#';if(d[10])a.rel='noopener nofollow';}
    var m=document.createElement('span');m.className='meta';
    m.textContent=[d[14]||nomPays(d[2]),d[5],d[12]!=='emodnet'&&d[11]?d[11]+' places':'',d[7]?'VHF '+d[7]:'',d[8]?'carburant':'',d[9]?'eau':''].filter(Boolean).join(' · ');
    li.appendChild(a);li.appendChild(m);li.className='joue';li.title='Voir sur la carte';
    /* la fonction garde le port de SA ligne : sans elle, toutes les lignes ouvriraient le dernier */
    (function(port){li.addEventListener('click',function(ev){
      if(ev.target.tagName==='A')return;
      mode='ports';$('m-ports').classList.add('on');$('m-fonds').classList.remove('on');
      centre(port);ouvre(port)})})(d);
    ul.appendChild(li)}
  shown=fin;$('plus').hidden=shown>=res.length;
}
function dessin(){
  var cv=$('carte'),x=cv.getContext('2d'),W=cv.width,H=cv.height;
  x.clearRect(0,0,W,H);
  HIT=[];
  if(mode==='fonds')return fondsDessin();
  if(!res.length){$('carte-inf').textContent='aucun port avec ce filtre';return}
  /* Le cadre : là où sont vraiment les ports, pas les exceptions. La France et ses DOM-TOM cadraient
     sur l'Atlantique entier, la métropole dans un coin. On prend la médiane des positions — le centre
     du gros de la troupe — puis la bbox des 90 %% les plus proches d'elle. */
  var lats=res.map(function(d){return d[3]}).sort(function(a,b){return a-b});
  var lons=res.map(function(d){return d[4]}).sort(function(a,b){return a-b});
  var n=res.length;
  var minlat=lats[0],maxlat=lats[n-1],minlon=lons[0],maxlon=lons[n-1];
  if(n>20){
    var mlat=lats[Math.floor(n/2)],mlon=lons[Math.floor(n/2)];
    var kc2=Math.cos(Math.max(-85,Math.min(85,mlat))*Math.PI/180);
    var dd=res.map(function(d){var dy=d[3]-mlat,dx=(d[4]-mlon)*kc2;return dy*dy+dx*dx}).sort(function(a,b){return a-b});
    var lim=dd[Math.floor(n*0.9)];
    minlat=90;maxlat=-90;minlon=180;maxlon=-180;
    res.forEach(function(d){var dy=d[3]-mlat,dx=(d[4]-mlon)*kc2;
      if(dy*dy+dx*dx<=lim){minlat=Math.min(minlat,d[3]);maxlat=Math.max(maxlat,d[3]);
        minlon=Math.min(minlon,d[4]);maxlon=Math.max(maxlon,d[4])}});
  }
  /* et la bbox brute, pour le bouton « tout voir » : les DOM-TOM existent, on les cache au cadrage
     automatique, pas quand on demande explicitement à tout voir */
  var tlat0=lats[0],tlat1=lats[n-1],tlon0=lons[0],tlon1=lons[n-1];
  var k=Math.cos((minlat+maxlat)/2*Math.PI/180);
  var bw=Math.max((maxlon-minlon)*k,1e-6), bh=Math.max(maxlat-minlat,1e-6);
  var VU={minlat:minlat,maxlat:maxlat,minlon:minlon,maxlon:maxlon,k:k,bw:bw,bh:bh};
  if(cadre.mode!=='manuel'){cadre={mode:'auto',k:k,bw:bw,bh:bh,minlat:minlat,maxlat:maxlat,minlon:minlon,maxlon:maxlon}}
  /* une projection par cadre : le milieu du cadre règle l'échelle des longitudes */
  function projeter(cm){
    var kc=Math.cos(Math.max(-85,Math.min(85,(cm.minlat+cm.maxlat)/2))*Math.PI/180);
    var bw2=Math.max((cm.maxlon-cm.minlon)*kc,1e-6), bh2=Math.max(cm.maxlat-cm.minlat,1e-6);
    var ech2=Math.min((W-24)/bw2,(H-24)/bh2);
    return {k:kc,bw:bw2,bh:bh2,ech:ech2,cx:(cm.minlon+cm.maxlon)/2,cy:(cm.minlat+cm.maxlat)/2};
  }
  /* quand le cadre manuel ne touche plus la vue du filtre, on y revient : sinon on regarde le vide */
  var cm=cadre;
  if(cm.mode==='tout'){cm={mode:'manuel',minlat:tlat0,maxlat:tlat1,minlon:tlon0,maxlon:tlon1}}
  if(cm.mode==='manuel'&&(cm.maxlon<VU.minlon||cm.minlon>VU.maxlon||cm.maxlat<VU.minlat||cm.minlat>VU.maxlat)){
    cadre={mode:'auto',k:k,bw:bw,bh:bh,minlat:minlat,maxlat:maxlat,minlon:minlon,maxlon:maxlon};cm=cadre}
  var P=projeter(cm);
  var X=function(lon){return W/2+(lon-P.cx)*P.k*P.ech}, Y=function(lat){return H/2-(lat-P.cy)*P.ech};
  var pas=P.ech*P.k;
  /* Le fond, avant les points : la mer en dégradé, les terres en crème, la côte d'un trait fin.
     C'est la base graphique de la carte du Léman, sans la bathymétrie qu'on n'a pas ici. */
  var mer=x.createLinearGradient(0,0,0,H);
  mer.addColorStop(0,'#e2ecf3');mer.addColorStop(1,'#b7cfdf');
  x.fillStyle=mer;x.fillRect(0,0,W,H);
  x.beginPath();
  for(var i=0;i<TERRES.length;i++){
    var r=TERRES[i];
    for(var j=0;j<r.length;j++){
      var px=X(r[j][0]),py=Y(r[j][1]);
      if(j)x.lineTo(px,py);else x.moveTo(px,py);
    }
    x.closePath();
  }
  x.fillStyle='#efe7d6';x.fill('nonzero');
  x.strokeStyle='rgba(72,104,126,.55)';x.lineWidth=1;x.stroke();
  /* les noms utiles même ici : à 100 km, savoir qu'on est près de Genève ou Lausanne aide */
  var lon0=P.cx-(W/2)/(P.k*P.ech), lon1=P.cx+(W/2)/(P.k*P.ech);
  noms(x,X,Y,W,H,lon1-lon0);
  /* il y a aussi des points, et eux sont la raison de la carte */
  x.fillStyle='#d6392f';
  res.forEach(function(d){
    var px=X(d[4]),py=Y(d[3]);
    if(px<-4||px>W+4||py<-4||py>H+4)return;
    var r=pas>0.06?2.2:(pas>0.02?1.4:0.8);
    HIT.push([px,py,d]);
    x.beginPath();x.arc(px,py,r,0,6.2832);x.fill();
    if(SEL===d){x.beginPath();x.arc(px,py,r+3.5,0,6.2832);x.strokeStyle='#0a1a2b';x.lineWidth=2;x.stroke();
      x.beginPath();x.arc(px,py,r+5.5,0,6.2832);x.strokeStyle='#fff';x.lineWidth=1.2;x.stroke();}
  });
  var lus=0;res.forEach(function(d){var px=X(d[4]),py=Y(d[3]);if(px>=-4&&px<=W+4&&py>=-4&&py<=H+4)lus++});
  $('carte-inf').textContent=lus+(lus>1?' ports affichés':' port affiché')+' sur '+res.length;
  $('z0').textContent=cadre.mode==='manuel'?'⤢':'';
}
/* ---------- zoom, déplacement, pincer : la carte du monde se pilote à la main ---------- */
var cadre={mode:'auto'};
function versNat(evt){
  var cv=$('carte'),r=cv.getBoundingClientRect();
  return {x:(evt.clientX-r.left)*cv.width/r.width,y:(evt.clientY-r.top)*cv.height/r.height};
}
function projectionDu(cm){
  var cv=$('carte'),W=cv.width,H=cv.height;
  var kc=Math.cos(Math.max(-85,Math.min(85,(cm.minlat+cm.maxlat)/2))*Math.PI/180);
  var bw2=Math.max((cm.maxlon-cm.minlon)*kc,1e-6), bh2=Math.max(cm.maxlat-cm.minlat,1e-6);
  return {k:kc,bw:bw2,bh:bh2,ech:Math.min((W-24)/bw2,(H-24)/bh2),
    cx:(cm.minlon+cm.maxlon)/2,cy:(cm.minlat+cm.maxlat)/2};
}
function zoomer(f,px,py){
  var cv=$('carte'),W=cv.width,H=cv.height;
  var P=projectionDu(cadre),bx=P.bw,by=P.bh,cx=P.cx,cy=P.cy,ech=P.ech;
  if(px==null){px=W/2;py=H/2}
  var lonA=cx+(px-W/2)/(cadre.k*ech), latA=cy-(py-H/2)/ech;
  var nbw=bx/f, nbh=by/f;
  if(nbw<0.004||nbh<0.004)return;
  if(nbw>360*4||nbh>180*4)return;
  var ncx=lonA+(cx-lonA)/f, ncy=latA+(cy-latA)/f;
  cadre={mode:'manuel',minlon:ncx-nbw/2,maxlon:ncx+nbw/2,minlat:ncy-nbh/2,maxlat:ncy+nbh/2,
    k:cadre.k,bw:nbw,bh:nbh};
  dessin();
}
(function(){
  var cv=$('carte'),glisse=null,pince=null;
  cv.addEventListener('wheel',function(e){
    if(!res.length)return;
    e.preventDefault();
    var p=versNat(e);
    zoomer(e.deltaY<0?1.25:0.8,p.x,p.y);
  },{passive:false});
  cv.addEventListener('dblclick',function(e){var p=versNat(e);zoomer(1.8,p.x,p.y)});
  cv.addEventListener('pointerdown',function(e){
    if(pince)return;
    cv.setPointerCapture(e.pointerId);glisse={x:e.clientX,y:e.clientY,mv:false};cv.classList.add('pan');
  });
  cv.addEventListener('pointermove',function(e){
    if(!glisse)return;
    var cvr=cv.getBoundingClientRect(),dx=(e.clientX-glisse.x)*cv.width/cvr.width,
        dy=(e.clientY-glisse.y)*cv.height/cvr.height;
    if(Math.abs(e.clientX-glisse.x)+Math.abs(e.clientY-glisse.y)>2)glisse.mv=true;
    var P=projectionDu(cadre);
    var dlon=-dx/(P.k*P.ech), dlat=dy/P.ech;
    cadre={mode:'manuel',minlon:cadre.minlon+dlon,maxlon:cadre.maxlon+dlon,
      minlat:cadre.minlat+dlat,maxlat:cadre.maxlat+dlat,k:cadre.k,bw:cadre.bw,bh:cadre.bh};
    glisse.x=e.clientX;glisse.y=e.clientY;
    dessin();
  });
  function fin(e){
    var g=glisse;glisse=null;cv.classList.remove('pan');
    if(e&&e.type==='pointerup'&&g&&!g.mv&&mode==='ports')clicCarte(e);
  }
  cv.addEventListener('pointerup',fin);cv.addEventListener('pointercancel',fin);
  /* pincer à deux doigts, sur le téléphone */
  cv.addEventListener('touchstart',function(e){
    if(e.touches.length===2){glisse=null;
      pince={d:Math.hypot(e.touches[0].clientX-e.touches[1].clientX,e.touches[0].clientY-e.touches[1].clientY)}}
  },{passive:true});
  cv.addEventListener('touchmove',function(e){
    if(e.touches.length===2&&pince){
      e.preventDefault();
      var d=Math.hypot(e.touches[0].clientX-e.touches[1].clientX,e.touches[0].clientY-e.touches[1].clientY);
      var r=cv.getBoundingClientRect();
      var mx=(e.touches[0].clientX+e.touches[1].clientX)/2-r.left, my=(e.touches[0].clientY+e.touches[1].clientY)/2-r.top;
      var f=d/pince.d;pince.d=d;
      zoomer(f,mx*cv.width/r.width,my*cv.height/r.height);
    }
  },{passive:false});
  cv.addEventListener('touchend',function(e){if(e.touches.length<2)pince=null},{passive:true});
  $('z+').addEventListener('click',function(){zoomer(1.6)});
  $('z-').addEventListener('click',function(){zoomer(0.62)});
  $('z0').addEventListener('click',function(){cadre={mode:'tout'};dessin()});
})();

/* ---------- le clic sur un point : la fiche du port ---------- */
var HIT=[], SEL=null;
/* 532 ports n'ont qu'un numéro pour nom dans OpenStreetMap : « Port sans nom » vaut mieux. */
function nomPort(d){return /^[0-9]+$/.test(String(d[1]).trim())?'Port sans nom':d[1]}
/* Les types d'OpenStreetMap sont en anglais : on les dit en français, comme le reste de la page. */
var TYPES={anchorage:'mouillage',marina:'port de plaisance',berth:'poste d\u2019amarrage',
  ferry_terminal:'terminal ferry',harbour:'havre',dock:'bassin',pier:'embarcadère',
  ferry:'embarcadère',boatyard:'chantier naval',mooring:'corps-mort',slipway:'cale de mise à l\u2019eau'};
function typeFr(t){return TYPES[t]||t||''}
function places(n){return n+(n>1?' places':' place')}
function coord(lat,lon){
  return Math.abs(lat).toFixed(3)+'° '+(lat>=0?'N':'S')+', '+Math.abs(lon).toFixed(3)+'° '+(lon>=0?'E':'O');
}
/* La fiche s'ouvre sur le point cliqué, sans quitter la carte : nom, pays, type, places, VHF,
   carburant, eau, site, coordonnées. Elle se ferme par sa croix, par Échap, ou par un clic à côté. */
function ouvre(d){
  SEL=d;dessin();
  var c=$('fiche-c');
  while(c.firstChild)c.removeChild(c.firstChild);
  var h3=document.createElement('h3');h3.textContent=nomPort(d);c.appendChild(h3);
  var p1=document.createElement('p');p1.className='fp';
  p1.textContent=[nomPays(d[2]),typeFr(d[5])].filter(Boolean).join(' · ');c.appendChild(p1);
  var det=[(d[11]&&d[12]!=='emodnet')?places(d[11]):'',d[6]?places(d[6]):'',
           d[7]?'VHF canal '+d[7]:'',d[8]?'carburant':'',d[9]?'eau potable':''].filter(Boolean);
  if(det.length){var p2=document.createElement('p');p2.textContent=det.join(' · ');c.appendChild(p2)}
  var p3=document.createElement('p');p3.className='fp';p3.textContent=coord(d[3],d[4]);c.appendChild(p3);
  if(d[10]){var pa=document.createElement('p'),l=document.createElement('a');
    l.href=d[10];l.rel='noopener nofollow';l.textContent='Site du port';pa.appendChild(l);c.appendChild(pa)}
  $('fiche').hidden=false;$('carte-aide').hidden=true;
}
function ferme(){
  if(!SEL){$('fiche').hidden=true;return}
  SEL=null;$('fiche').hidden=true;$('carte-aide').hidden=(mode==='fonds');dessin();
}
function clicCarte(e){
  var p=versNat(e),best=null,bd=16;
  for(var i=0;i<HIT.length;i++){
    var q=HIT[i],dd=Math.sqrt((q[0]-p.x)*(q[0]-p.x)+(q[1]-p.y)*(q[1]-p.y));
    if(dd<bd){bd=dd;best=q[2]}
  }
  if(best)ouvre(best);else ferme();
}
/* Cadrer sur un port : dix degrés de large, ou plus étroit sous les hautes latitudes. */
function centre(d){
  var cv=$('carte'),ratio=cv.height/cv.width;
  var k=Math.cos(Math.max(-85,Math.min(85,d[3]))*Math.PI/180);
  var dw=Math.max(2,Math.min(50,10/k)),dh=dw*k*ratio;
  cadre={mode:'manuel',k:k,bw:dw,bh:dh,minlon:d[4]-dw/2,maxlon:d[4]+dw/2,
         minlat:d[3]-dh/2,maxlat:d[3]+dh/2};
  dessin();
}

/* ---------- le mode « fonds et noms » : la bathymétrie, puis les noms dessus ---------- */
var RELIEF_IMG=new Image(),reliefPret=false;
RELIEF_IMG.onload=function(){reliefPret=true;if(mode==='fonds')dessin()};
RELIEF_IMG.src=RELIEF;
function fondSobre(){
  /* le fond des ports : la mer, les terres, les côtes — sans relief ni noms, pour que les points ressortent */
  var cv=$('carte'),x=cv.getContext('2d'),W=cv.width,H=cv.height;
  x.fillStyle='#dcebf4';x.fillRect(0,0,W,H);
  var P=projectionDu(cadre);
  var X=function(lon){return W/2+(lon-P.cx)*P.k*P.ech},Y=function(lat){return H/2-(lat-P.cy)*P.ech};
  x.beginPath();
  for(var i=0;i<TERRES.length;i++){
    var r=TERRES[i];
    for(var j=0;j<r.length;j++){
      var px=X(r[j][0]),py=Y(r[j][1]);
      if(px<-4000||px>W+4000||py<-4000||py>H+4000){continue}
      if(j)x.lineTo(px,py);else x.moveTo(px,py);
    }
    x.closePath();
  }
  x.fillStyle='#f5f0e2';x.fill('nonzero');
  x.strokeStyle='rgba(46,74,96,.55)';x.lineWidth=1;x.stroke();
  x.beginPath();
  for(var q=0;q<LACS.length;q++){var L=LACS[q];
    for(var w=0;w<L.length;w+=2){var lx=X(L[w]),ly=Y(L[w+1]);if(w)lx===lx&&x.lineTo(lx,ly);else x.moveTo(lx,ly)}
    x.closePath()}
  x.fillStyle='#dcebf4';x.fill('nonzero');
  /* les noms utiles même en mode ports : à 100 km, savoir qu'on est près de Genève ou Lausanne aide */
  var lon0=P.cx-(W/2)/(P.k*P.ech), lon1=P.cx+(W/2)/(P.k*P.ech);
  noms(x,X,Y,W,H,lon1-lon0);
}
function fondsDessin(){
  var cv=$('carte'),x=cv.getContext('2d'),W=cv.width,H=cv.height;
  x.clearRect(0,0,W,H);
  x.fillStyle='#b7cfdf';x.fillRect(0,0,W,H);
  var P=projectionDu(cadre);
  var X=function(lon){return W/2+(lon-P.cx)*P.k*P.ech},Y=function(lat){return H/2-(lat-P.cy)*P.ech};
  var lon0=P.cx-(W/2)/(P.k*P.ech),lon1=P.cx+(W/2)/(P.k*P.ech);
  var lat0=P.cy+(H/2)/P.ech,lat1=P.cy-(H/2)/P.ech;
  var a0=Math.max(lon0,-180),a1=Math.min(lon1,180),b0=Math.max(lat1,-90),b1=Math.min(lat0,90);
  if(reliefPret&&a1>a0&&b1>b0){
    /* le relief mondial est une image équirectangulaire : on y découpe exactement le cadre visible */
    x.drawImage(RELIEF_IMG,(a0+180)/360*2700,(90-b1)/180*1350,(a1-a0)/360*2700,(b1-b0)/180*1350,
      X(a0),Y(b1),(a1-a0)*P.k*P.ech,(b1-b0)*P.ech);
  }
  /* Un voile bleu sur la mer, puis les terres en crème transparent : le relief reste lisible et la
     teinte sépare franchement l'eau de la terre. Enfin les côtes, d'un trait fin. */
  x.fillStyle='rgba(14,44,70,.16)';x.fillRect(0,0,W,H);
  x.beginPath();
  for(var i=0;i<TERRES.length;i++){
    var r=TERRES[i];
    for(var j=0;j<r.length;j++){
      var px=X(r[j][0]),py=Y(r[j][1]);
      if(j)x.lineTo(px,py);else x.moveTo(px,py);
    }
    x.closePath();
  }
  x.fillStyle='rgba(238,228,206,.55)';x.fill('nonzero');
  x.strokeStyle='rgba(46,74,96,.8)';x.lineWidth=1;x.stroke();
  x.beginPath();
  for(var q=0;q<LACS.length;q++){var L=LACS[q];
    for(var w=0;w<L.length;w+=2){var lx=X(L[w]),ly=Y(L[w+1]);if(w)x.lineTo(lx,ly);else x.moveTo(lx,ly)}
    x.closePath()}
  x.fillStyle='rgba(14,44,70,.28)';x.fill('nonzero');
  noms(x,X,Y,W,H,lon1-lon0);
  $('carte-inf').textContent='les fonds de la mer, et les noms';
  $('z0').textContent=cadre.mode==='manuel'?'⤢':'';
}
/* Les noms, du plus important au plus fin selon ce qu'on voit : océans et mers, villes, lacs,
   fleuves. Un nom qui chevaucherait un autre est sauté — la carte reste lisible. */
function noms(x,X,Y,W,H,larg){
  var niv =larg>200?1:(larg>90?2:(larg>40?3:(larg>15?5:(larg>5?7:9))));
  var limV=larg>200?1:(larg>90?2:(larg>40?3:(larg>15?5:(larg>5?7:10))));
  var boites=[];
  function libre(px,py,demiw,hh){
    var b={x:px-demiw,y:py-hh/2,w:demiw*2,h:hh},i,o;
    /* un nom qui pendrait hors du cadre n'est pas dessiné : pas de « mer de Tasman » coupé au bord */
    if(b.x<6||b.y<3||b.x+b.w>W-6||b.y+b.h>H-3)return false;
    if(b.y<34&&b.x<218)return false;   /* le cartouche d'info est posé là */
    for(i=0;i<boites.length;i++){o=boites[i];
      if(b.x<o.x+o.w+4&&b.x+b.w+4>o.x&&b.y<o.y+o.h+2&&b.y+b.h+2>o.y)return false}
    boites.push(b);return true;
  }
  x.textAlign='center';x.textBaseline='middle';
  x.font='italic 600 13px system-ui,-apple-system,sans-serif';
  TOPO.m.forEach(function(t){
    if(t[3]>niv+1)return;
    var px=X(t[0]),py=Y(t[1]);if(px<-60||px>W+60||py<-16||py>H+16)return;
    var s=t[2].toUpperCase(),w=x.measureText(s).width;
    if(!libre(px,py,w/2+4,17))return;
    x.fillStyle='rgba(255,255,255,.6)';x.fillText(s,px+1,py+1);
    x.fillStyle='#35637f';x.fillText(s,px,py);
  });
  x.font='600 11.5px system-ui,-apple-system,sans-serif';
  TOPO.v.forEach(function(t){
    if(t[3]>limV)return;
    var px=X(t[0]),py=Y(t[1]);if(px<-20||px>W+20||py<-16||py>H+16)return;
    var s=t[2],qy=py-9;
    if(!libre(px,qy,x.measureText(s).width/2+5,13))return;
    x.beginPath();x.arc(px,py,2.1,0,6.2832);x.fillStyle='#fff';x.fill();
    x.strokeStyle='#2b3d4d';x.lineWidth=1.1;x.stroke();
    x.fillStyle='rgba(255,255,255,.7)';x.fillText(s,px+1,qy+1);
    x.fillStyle='#16222c';x.fillText(s,px,qy);
  });
  x.font='italic 11px system-ui,-apple-system,sans-serif';
  TOPO.l.forEach(function(t){
    if(t[3]>niv+2)return;
    var px=X(t[0]),py=Y(t[1]);if(px<-30||px>W+30||py<-14||py>H+14)return;
    var s=t[2];
    if(!libre(px,py,x.measureText(s).width/2+4,14))return;
    x.fillStyle='#2f7ea8';x.fillText(s,px,py);
  });
  x.font='italic 10px system-ui,-apple-system,sans-serif';
  TOPO.f.forEach(function(t){
    if(t[3]>niv+2)return;
    var px=X(t[0]),py=Y(t[1]);if(px<-30||px>W+30||py<-12||py>H+12)return;
    var s=t[2];
    if(!libre(px,py,x.measureText(s).width/2+3,12))return;
    x.fillStyle='#4d8bab';x.fillText(s,px,py);
  });
}
/* Les deux vues. « Ports » comme avant ; « Fonds et noms » montre la mer elle-même. */
function setMode(m){
  mode=m;
  $('m-ports').classList.toggle('on',m==='ports');
  $('m-fonds').classList.toggle('on',m==='fonds');
  if(m==='fonds'){
    SEL=null;$('fiche').hidden=true;$('carte-aide').hidden=true;
    if(cadre.mode!=='manuel'){
      var kk=Math.cos(13*Math.PI/180);
      cadre={mode:'manuel',minlat:-58,maxlat:84,minlon:-180,maxlon:180,k:kk,bw:360*kk,bh:142};
    }
  }else{
    $('carte-aide').hidden=false;
    if(cadre.mode==='manuel'&&cadre.minlon<=-179.9&&cadre.maxlon>=179.9)cadre={mode:'auto'};
  }
  dessin();
}
$('m-ports').addEventListener('click',function(){setMode('ports')});
$('m-fonds').addEventListener('click',function(){setMode('fonds')});
$('fiche-x').addEventListener('click',ferme);
document.addEventListener('keydown',function(e){if(e.key==='Escape')ferme()});
function hav(a,b){var R=6371.0088,r=Math.PI/180,dp=(b[3]-a[3])*r,dl=(b[4]-a[4])*r,
  h=Math.sin(dp/2)*Math.sin(dp/2)+Math.cos(a[3]*r)*Math.cos(b[3]*r)*Math.sin(dl/2)*Math.sin(dl/2);
  return 2*R*Math.asin(Math.sqrt(h))}
function trouve(v){var m=/#(\\d+)$/.exec(v);if(m){var id=+m[1];for(var i=0;i<D.length;i++)if(D[i][0]===id)return D[i]}
  var q=pli(v.trim());for(var j=0;j<D.length;j++)if(D[j][15]===q)return D[j];return null}
function calc(){var A=trouve($('a').value),B=trouve($('b').value);
  if(!A||!B){$('res').textContent='';return}
  var km=hav(A,B);$('res').textContent=A[1]+' → '+B[1]+' : '+Math.round(km)+' km, soit '+(km/1.852).toFixed(0)+' milles nautiques (vol d\\'oiseau)'}
$('q').addEventListener('input',filtre);$('p').addEventListener('change',filtre);$('t').addEventListener('change',filtre);
$('plus').addEventListener('click',suite);
/* « Me localiser » : le clic EST l'accord. La position ne sort pas du navigateur ; elle remplit le
   pays, ordonne la liste du plus proche au plus lointain, et nomme l'endroit. */
$('moi').addEventListener('click',function(){
  var b=$('moi');
  function stop(m){b.textContent=m;setTimeout(function(){b.textContent='Me localiser'},5000)}
  function parIP(){
    fetch('https://ipwho.is/?fields=latitude,longitude,country_code,city,region,success').then(function(r){return r.json()})
      .then(function(d){
        if(!d||!d.success||d.latitude==null)return stop('Position indisponible');
        POS=[d.latitude,d.longitude];
        var c2=d.country_code?window.smPays.ISO[String(d.country_code).toUpperCase()]:'';
        if(c2&&ps.indexOf(c2)>=0)$('p').value=c2;
        var nom=[d.city,d.region].filter(Boolean).join(', ');
        stop(nom?'Près de '+nom+' · tri par distance':'Position approximative · tri par distance');
        filtre();
      }).catch(function(){stop('Position indisponible')});
  }
  if(!navigator.geolocation)return parIP();
  b.textContent='Recherche…';
  navigator.geolocation.getCurrentPosition(function(p){
    POS=[p.coords.latitude,p.coords.longitude];
    localisation(POS[0],POS[1],function(c,nom){
      if(c)$('p').value=c;
      stop(nom?'Près de '+nom+' · tri par distance':'Tri du plus proche au plus lointain');
      filtre();
    });
  },parIP,{timeout:10000,maximumAge:600000});
});
/* Le pays du visiteur, une fois tous les menus en place : il coche le filtre et filtre tout de suite. */
if(window.smPays)window.smPays.pays(paysLu);else paysLu('');

/* à l'ouverture, la carte se place chez le visiteur : 100 km de large autour de lui.
   Refus, échec ou pas de navigateur géolocalisé : la vue monde reste, rien ne casse. */
(function(){
  function cadreLocal(lat,lon){
    var cv=$('carte'),W=cv.width||1000,H=cv.height||560;
    var k=Math.cos(Math.max(-85,Math.min(85,lat))*Math.PI/180);
    var larg=100/(111.32*k), haut=larg*H/W;
    cadre={mode:'manuel',minlon:lon-larg/2,maxlon:lon+larg/2,
           minlat:lat-haut/2,maxlat:lat+haut/2,k:k,bw:larg,bh:haut};
    dessin();
  }
  window.smCadreLocal=cadreLocal;
  /* La demande de position est unique (geo-accueil.js, 26/11/2026) : ici on ne la fait plus, on
     l'écoute. Accord : pays pré-rempli, tri par distance, carte à 100 km. Refus : rien ne bouge. */
  if(window.smGeo)window.smGeo.sur(function(g){
    POS=[g.lat,g.lon];
    var s=$('p');
    if(g.iso3&&!s.value){for(var i=0;i<s.options.length;i++){if(s.options[i].value===g.iso3){s.value=g.iso3;break}}}
    filtre();
    cadreLocal(g.lat,g.lon);
  });
})();
</script>
</body></html>
''' % dict(titre=titre, desc=html.escape(desc, quote=True), ld=json.dumps(ld, ensure_ascii=False),
           total=total, npays=len(pays_list), releve=releve, js=js, terres=terres, lacs=lacs,
           relief=relief, topo=topo)

with open(OUT, 'w', encoding='utf-8') as f:
    f.write(page)
print('ok', len(page), 'octets;', total, 'ports;', n_fiches, 'passent le seuil de fiche (', SEUIL_FICHE, ')')
