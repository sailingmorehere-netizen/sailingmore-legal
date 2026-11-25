(function(){
var ISO={"FR":"FRA","DE":"DEU","NL":"NLD","GB":"GBR","IE":"IRL","ES":"ESP","IT":"ITA","PT":"PRT","GR":"GRC","HR":"HRV","SI":"SVN","MT":"MLT","CY":"CYP","TR":"TUR","BE":"BEL","CH":"CHE","AT":"AUT","DK":"DNK","SE":"SWE","NO":"NOR","FI":"FIN","IS":"ISL","PL":"POL","EE":"EST","LV":"LVA","LT":"LTU","RO":"ROU","BG":"BGR","ME":"MNE","US":"USA","CA":"CAN","AU":"AUS","NZ":"NZL","ZA":"ZAF","BR":"BRA"},FZ={"Europe/Paris":"FR","Europe/Monaco":"FR","Europe/Brussels":"BE","Europe/Amsterdam":"NL","Europe/Luxembourg":"LU","Europe/Zurich":"CH","Europe/Berlin":"DE","Europe/Vienna":"AT","Europe/Rome":"IT","Europe/Madrid":"ES","Europe/Lisbon":"PT","Europe/Athens":"GR","Europe/Zagreb":"HR","Europe/Ljubljana":"SI","Europe/Malta":"MT","Europe/Nicosia":"CY","Europe/Istanbul":"TR","Europe/Copenhagen":"DK","Europe/Stockholm":"SE","Europe/Oslo":"NO","Europe/Helsinki":"FI","Atlantic/Reykjavik":"IS","Europe/Warsaw":"PL","Europe/Tallinn":"EE","Europe/Riga":"LV","Europe/Vilnius":"LT","Europe/Bucharest":"RO","Europe/Sofia":"BG","Europe/Podgorica":"ME","America/New_York":"US","America/Chicago":"US","America/Denver":"US","America/Los_Angeles":"US","America/Toronto":"CA","America/Vancouver":"CA","Australia/Sydney":"AU","Australia/Melbourne":"AU","Pacific/Auckland":"NZ","Africa/Johannesburg":"ZA","America/Sao_Paulo":"BR","Europe/London":"GB","Europe/Dublin":"IE"};
function norm(c){return c?String(c).toUpperCase().replace(/_/g,'-'):''}
/* 1. la langue du navigateur porte souvent la région : fr-FR, de-CH, en-GB */
function parLangue(){
  var ls=(navigator.languages&&navigator.languages.length?navigator.languages:[navigator.language||'']);
  for(var i=0;i<ls.length;i++){
    var m=/[-_]([A-Za-z]{2})$/.exec(String(ls[i]||''));
    if(m&&ISO[m[1].toUpperCase()])return ISO[m[1].toUpperCase()];
  }
  return '';
}
/* 2. le pays retenu une fois (l'espace de comptes y écrira celui du profil) */
function parMemoire(){
  try{
    var v=String(localStorage.getItem('sm_pays')||'').toUpperCase();
    if(!v)return '';
    if(ISO[v])return ISO[v];          /* code à deux lettres, par sécurité */
    return v;                          /* code à trois lettres : sm_pays écrit par retenir() */
  }catch(e){return ''}
}
/* 3. le fuseau horaire, déjà dans le navigateur */
function parFuseau(){try{var t=Intl.DateTimeFormat().resolvedOptions().timeZone;return FZ[t]?ISO[FZ[t]]:''}catch(e){return ''}}
/* 4. l'adresse IP, en dernier recours seulement */
function parIP(fin){
  fetch('https://ipwho.is/?fields=country_code,success').then(function(r){return r.json()})
    .then(function(d){fin(d&&d.success&&d.country_code&&ISO[d.country_code]?ISO[d.country_code]:'')})
    .catch(function(){fin('')});
}
/* fin(pays, source) : même quand rien n'est trouvé, on appelle fin('', '') une seule fois. */
function pays(fin){
  /* L'ordre dit tout : la mémoire passe AVANT la langue. Un visiteur qui a choisi un pays (ou dont
     le compte le connaît) ne se fait pas reclasser par la langue de son navigateur. */
  var p=parMemoire();if(p)return fin(p,'memoire');
  p=parLangue();if(p)return fin(p,'langue');
  p=parFuseau();if(p)return fin(p,'fuseau');
  parIP(function(p){fin(p,p?'ip':'')});
}
/* Le nom du pays, en français, à partir du code à trois lettres (FRA → France). */
function nom(code3){try{var l=new Intl.DisplayNames(['fr'],{type:'region'});
  for(var k in ISO){if(ISO[k]===code3)return l.of(k)}return ''}catch(e){return ''}}
/* Retient un pays pour la prochaine visite (l'espace de comptes l'appellera avec le pays du profil). */
function retenir(code2){
  try{if(code2&&ISO[String(code2).toUpperCase()])localStorage.setItem('sm_pays',ISO[String(code2).toUpperCase()])}catch(e){}
}
window.smPays={pays:pays,retenir:retenir,ISO:ISO,nom:nom};
})();
