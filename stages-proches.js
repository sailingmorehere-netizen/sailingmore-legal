(function(){
var T={"fr": {"titre": "Stages près de chez vous", "tous": "Tous les stages →", "prix": "prix non publié", "dist": "km"}, "en": {"titre": "Courses near you", "tous": "All courses →", "prix": "price not published", "dist": "km"}, "de": {"titre": "Kurse in Ihrer Nähe", "tous": "Alle Kurse →", "prix": "Preis nicht veröffentlicht", "dist": "km"}, "it": {"titre": "Corsi vicino a te", "tous": "Tutti i corsi →", "prix": "prezzo non pubblicato", "dist": "km"}, "es": {"titre": "Cursos cerca de ti", "tous": "Todos los cursos →", "prix": "precio no publicado", "dist": "km"}, "pt": {"titre": "Cursos perto de si", "tous": "Todos os cursos →", "prix": "preço não publicado", "dist": "km"}};
var host=document.getElementById('stages-proches');if(!host)return;
var L='fr';try{L=(window.smLangue?window.smLangue():document.documentElement.lang||'en')}catch(e){}
L=String(L).slice(0,2).toLowerCase();if(L==='bz')L='fr';if(!T[L])L='en';var X=T[L];
function esc(s){return String(s==null?'':s).replace(/[&<>"']/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]})}
function hav(a,b,c,d){var r=Math.PI/180,p=(c-a)*r,q=(d-b)*r,h=Math.sin(p/2)*Math.sin(p/2)+Math.cos(a*r)*Math.cos(c*r)*Math.sin(q/2)*Math.sin(q/2);return 12742*Math.asin(Math.sqrt(h))}
function teinte(s){var h=0;s=s||'';for(var i=0;i<s.length;i++)h=(h*31+s.charCodeAt(i))%360;return h}
function sigle(n){var m=(n||'?').replace(/[^\p{L} ]/gu,'').split(/\s+/).filter(Boolean);return m.length>1?(m[0][0]+m[1][0]).toUpperCase():((m[0]||'?').slice(0,2).toUpperCase())}
var ISO={FR:'FRA',DE:'DEU',NL:'NLD',GB:'GBR',IE:'IRL',ES:'ESP',IT:'ITA',PT:'PRT',GR:'GRC',HR:'HRV',TR:'TUR',BE:'BEL',CH:'CHE',AT:'AUT',DK:'DNK',SE:'SWE',NO:'NOR',FI:'FIN',PL:'POL',SI:'SVN',MT:'MLT',CY:'CYP'};
var m=(navigator.language||'').match(/[-_]([A-Za-z]{2})$/),navPays=m?ISO[m[1].toUpperCase()]||'':'';
var DATA=null,POS=null,posFaite=false,vu=false;
function position(fin){
  function ip(){fetch('https://ipwho.is/?fields=latitude,longitude,success').then(function(r){return r.json()})
    .then(function(d){if(d&&d.success&&d.latitude!=null)POS=[d.latitude,d.longitude]}).catch(function(){}).then(fin)}
  if(!navigator.geolocation){ip();return}
  navigator.geolocation.getCurrentPosition(function(p){POS=[p.coords.latitude,p.coords.longitude];fin()},ip,{timeout:6000,maximumAge:600000});
}
function dessiner(){
  var a=new Date().toISOString().slice(0,10);
  var l=DATA.o.filter(function(o){return !o[16]&&(!o[7]||o[7]>=a)});
  l=l.map(function(o){return {o:o,d:POS?hav(POS[0],POS[1],o[0],o[1]):null}});
  l.sort(function(x,y){
    if(POS)return x.d-y.d;
    var cx=navPays&&x.o[12]===navPays?0:1,cy=navPays&&y.o[12]===navPays?0:1;if(cx!==cy)return cx-cy;
    return (x.o[7]||'9999')<(y.o[7]||'9999')?-1:1});
  var vus=[],ecoles={};
  l.forEach(function(x){if(vus.length<4&&!ecoles[x.o[4]]){ecoles[x.o[4]]=1;vus.push(x)}});
  host.innerHTML='<h2 style="font-size:1.1rem;margin:0 0 .6rem">'+esc(X.titre)+'</h2><div style="display:grid;gap:.6rem;grid-template-columns:repeat(auto-fit,minmax(15rem,1fr))">'
   +vus.map(function(x){var o=x.o,loin=x.d==null?'':((o[2]?'~':'')+Math.round(x.d).toLocaleString(L)+' '+X.dist+' · ');
     var vis=o[11]?'<img src="/'+esc(o[11])+'" alt="'+esc(o[3]+' — '+o[4])+'" loading="lazy" width="400" height="150" style="width:100%;height:96px;object-fit:cover;border-radius:8px;display:block;margin-bottom:.4rem">'
       :'<span style="display:inline-grid;place-items:center;width:30px;height:30px;border-radius:8px;font-weight:700;font-size:.75rem;margin-bottom:.4rem;background:hsl('+teinte(o[4])+',38%,22%);color:#dff3ef">'+esc(sigle(o[4]))+'</span>';
     return '<a href="'+esc(o[10])+'" rel="noopener nofollow" target="_blank" style="display:block;text-decoration:none;color:inherit;border:1px solid rgba(157,178,199,.3);border-radius:10px;padding:.7rem">'
       +vis+'<b style="display:block;font-size:.95rem">'+esc(o[3])+'</b><span style="font-size:.82rem;opacity:.8">'+esc(o[4])+'</span><br><span style="font-size:.82rem;opacity:.8">'
       +loin+esc(o[5]||o[6])+' · '+(o[8]!=null?o[8].toLocaleString(L)+' '+esc(o[9]):esc(X.prix))+'</span></a>'}).join('')
   +'</div><p style="margin:.6rem 0 0"><a href="/stages.html">'+esc(X.tous)+'</a></p>';
  host.hidden=!vus.length;
}
function charger(){
  fetch('/stages-proches.json').then(function(r){return r.json()}).then(function(d){DATA=d;
    position(function(){dessiner()})}).catch(function(){host.hidden=true});
}
host.hidden=true;
if('IntersectionObserver' in window){var io=new IntersectionObserver(function(es){if(es[0].isIntersecting&&!vu){vu=true;io.disconnect();charger()}},{rootMargin:'200px'});io.observe(host)}
else charger();
})();
