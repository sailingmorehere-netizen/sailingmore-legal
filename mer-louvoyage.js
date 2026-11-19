(function(){
'use strict';

/* ------------------------------------------------------------------ outils */
var PI=Math.PI, TAU=PI*2, RAD=PI/180;
function wrap(a){a=(a+PI)%TAU; if(a<0)a+=TAU; return a-PI}
function clamp(x,a,b){return x<a?a:(x>b?b:x)}
function lerp(a,b,t){return a+(b-a)*t}
function sstep(a,b,x){var t=clamp((x-a)/(b-a),0,1); return t*t*(3-2*t)}
function damp(c,t,tau,dt){return t+(c-t)*Math.exp(-dt/tau)}
function sgn(x){return x<0?-1:1}
var graine=20261119;
function alea(){graine=(graine*1664525+1013904223)|0; return ((graine>>>8)&0xffffff)/0x1000000}

/* matrices 4x4, colonnes d'abord */
function ident(){var m=new Float32Array(16); m[0]=m[5]=m[10]=m[15]=1; return m}
function mul(a,b){var o=new Float32Array(16),c,r;
  for(c=0;c<4;c++)for(r=0;r<4;r++)o[c*4+r]=a[r]*b[c*4]+a[4+r]*b[c*4+1]+a[8+r]*b[c*4+2]+a[12+r]*b[c*4+3];
  return o}
function trans(x,y,z){var m=ident(); m[12]=x; m[13]=y; m[14]=z; return m}
function rotY(t){var m=ident(),c=Math.cos(t),s=Math.sin(t); m[0]=c; m[2]=-s; m[8]=s; m[10]=c; return m}
function rotX(t){var m=ident(),c=Math.cos(t),s=Math.sin(t); m[5]=c; m[6]=s; m[9]=-s; m[10]=c; return m}
function rotZ(t){var m=ident(),c=Math.cos(t),s=Math.sin(t); m[0]=c; m[1]=s; m[4]=-s; m[5]=c; return m}
function rotAxe(ax,t){var x=ax[0],y=ax[1],z=ax[2],c=Math.cos(t),s=Math.sin(t),k=1-c,m=ident();
  m[0]=c+x*x*k; m[1]=y*x*k+z*s; m[2]=z*x*k-y*s;
  m[4]=x*y*k-z*s; m[5]=c+y*y*k; m[6]=z*y*k+x*s;
  m[8]=x*z*k+y*s; m[9]=y*z*k-x*s; m[10]=c+z*z*k; return m}
function perspective(fovy,asp,n,f){var m=new Float32Array(16),t=1/Math.tan(fovy/2);
  m[0]=t/asp; m[5]=t; m[10]=(f+n)/(n-f); m[11]=-1; m[14]=2*f*n/(n-f); return m}
function norm3(v){var l=Math.hypot(v[0],v[1],v[2])||1; return [v[0]/l,v[1]/l,v[2]/l]}
function cross(a,b){return [a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]]}
function regard(eye,cib){ /* renvoie la matrice de vue et la base de la caméra */
  var f=norm3([cib[0]-eye[0],cib[1]-eye[1],cib[2]-eye[2]]), r=norm3(cross(f,[0,1,0])), u=cross(r,f), m=ident();
  m[0]=r[0]; m[4]=r[1]; m[8]=r[2];  m[1]=u[0]; m[5]=u[1]; m[9]=u[2];  m[2]=-f[0]; m[6]=-f[1]; m[10]=-f[2];
  m[12]=-(r[0]*eye[0]+r[1]*eye[1]+r[2]*eye[2]); m[13]=-(u[0]*eye[0]+u[1]*eye[1]+u[2]*eye[2]); m[14]=(f[0]*eye[0]+f[1]*eye[1]+f[2]*eye[2]);
  return {m:m,f:f,r:r,u:u}}

/* ================================================================== RÉGLAGES
   Tout ce qui se bidouille est ici, par son nom. Changez un chiffre, enregistrez, rechargez la page. */
var VENT_DEPART=0;        /* direction d'où vient le vent au départ, en degrés (0 = nord, 90 = est) */
var GITE_MAX=20;          /* gîte au près, en degrés */
var EQUIPAGE=true;        /* trois silhouettes à bord, qui changent de bord au virement (false pour les retirer) */
var EMBRUNS=true;         /* gerbes d'embruns à l'étrave quand le bateau tape dans la houle */
var BRUME_ENTREE=3.6;     /* durée de la sortie de brume à l'ouverture, en secondes (0 pour la retirer) */
/* Heure du jour. La réglette en haut de la scène la règle de 0 à 24 h. */
var AUTO_PAR_DEFAUT=true;  /* true : au chargement, la scène prend l'heure de l'horloge de l'appareil */
var HEURE_DEPART=19.25;    /* heure utilisée quand Auto est coupé au départ (19.25 = 19 h 15, l'heure dorée) */
/* Course du soleil : heures de lever et de coucher, direction au lever et au coucher (degrés, 0 = droit devant
   au départ, positif = vers la droite), hauteur au plus haut (degrés). */
var SOLEIL={lever:6.5, coucher:20.5, azimutLever:34, azimutCoucher:12, hauteurMidi:55};
/* Course de la lune, la nuit : direction en début et en fin de nuit, hauteur au plus haut (degrés). */
var LUNE={azimutDebut:26, azimutFin:10, hauteur:25};
/* Cadrages. d : distance au bateau (m). h : hauteur de la caméra (m). av : visée en avant du bateau (m).
   y : hauteur du point visé (m). tour : la caméra tourne autour du bateau (degrés). travelling : glissement
   vers le côté sous le vent (degrés). focale : angle de champ (degrés, petit = téléobjectif).
   lenteur : temps pour passer à ce cadrage (s). duree : durée du plan d'ouverture (s).
   decal : sur écran large, décale le bateau vers la droite pour dégager la légende (m). */
var PLANS={
  ouverture:{d:31, h:3.2, av:1,  y:6.6, tour:46,  travelling:0,  focale:36, lenteur:1.0, duree:3.4, decal:7},
  bord:     {d:31, h:11,  av:11, y:4.2, tour:0,   travelling:17, focale:40, lenteur:1.7, decal:3},
  virement: {d:24, h:6.5, av:4,  y:5.6, tour:0,   travelling:13, focale:40, lenteur:1.1, decal:4},
  bouee:    {d:32, h:6.5, av:5,  y:6.4, tour:24,  travelling:0,  focale:38, lenteur:2.0, decal:3},
  portrait: {recul:1.30, focale:1.16}    /* téléphone tenu debout : même distance, champ un peu plus large */
};
/* Couleurs de la scène, heure par heure (rouge, vert, bleu, de 0 à 1). La scène passe en fondu d'une ligne à la
   suivante. h : l'heure. zenith et horizon : le ciel. soleil : la lueur autour de l'astre. disque : l'astre.
   eauFond et eauClaire : la mer, du creux à la crête. lueur : la lumière qui traverse la vague.
   ambianceHaut et ambianceBas : la lumière du ciel et celle renvoyée par l'eau. lumiere : la lumière directe. */
var COQUE=[0.055,0.155,0.27];   /* couleur de la coque */
var COULEURS=[
  {h:0,    zenith:[0.025,0.05,0.125], horizon:[0.12,0.185,0.31], soleil:[0.62,0.72,0.95], disque:[0.92,0.95,1.0], eauFond:[0.012,0.042,0.09], eauClaire:[0.04,0.12,0.19], lueur:[0.05,0.16,0.24], ecume:[0.66,0.74,0.86], ambianceHaut:[0.25,0.32,0.48], ambianceBas:[0.08,0.12,0.20], voile:[0.84,0.88,0.97], lumiere:[0.56,0.64,0.88]},
  {h:5.3,  zenith:[0.025,0.05,0.125], horizon:[0.12,0.185,0.31], soleil:[0.62,0.72,0.95], disque:[0.92,0.95,1.0], eauFond:[0.012,0.042,0.09], eauClaire:[0.04,0.12,0.19], lueur:[0.05,0.16,0.24], ecume:[0.66,0.74,0.86], ambianceHaut:[0.25,0.32,0.48], ambianceBas:[0.08,0.12,0.20], voile:[0.84,0.88,0.97], lumiere:[0.56,0.64,0.88]},
  {h:6.0,  zenith:[0.08,0.13,0.32],   horizon:[0.52,0.40,0.52],  soleil:[0.75,0.45,0.48], disque:[1.0,0.80,0.70],  eauFond:[0.016,0.055,0.12], eauClaire:[0.06,0.15,0.25], lueur:[0.10,0.20,0.30], ecume:[0.78,0.78,0.88], ambianceHaut:[0.34,0.36,0.54], ambianceBas:[0.14,0.14,0.22], voile:[0.86,0.86,0.95], lumiere:[0.55,0.50,0.66]},
  {h:6.7,  zenith:[0.30,0.38,0.62],   horizon:[0.99,0.70,0.58],  soleil:[1.0,0.58,0.40],  disque:[1.0,0.88,0.76],  eauFond:[0.03,0.10,0.19],   eauClaire:[0.10,0.27,0.37], lueur:[0.18,0.42,0.48], ecume:[0.97,0.93,0.94], ambianceHaut:[0.52,0.52,0.68], ambianceBas:[0.30,0.27,0.35], voile:[0.97,0.95,0.95], lumiere:[0.98,0.76,0.62]},
  {h:7.7,  zenith:[0.27,0.45,0.74],   horizon:[1.0,0.78,0.58],   soleil:[1.0,0.70,0.40],  disque:[1.0,0.95,0.82],  eauFond:[0.020,0.118,0.21], eauClaire:[0.06,0.32,0.40], lueur:[0.10,0.52,0.52], ecume:[0.99,0.97,0.94], ambianceHaut:[0.54,0.60,0.72], ambianceBas:[0.31,0.31,0.35], voile:[0.98,0.97,0.95], lumiere:[1.0,0.82,0.62]},
  {h:10,   zenith:[0.17,0.44,0.82],   horizon:[0.72,0.86,0.95],  soleil:[1.0,0.94,0.80],  disque:[1.0,0.99,0.93],  eauFond:[0.010,0.14,0.29],  eauClaire:[0.04,0.43,0.54], lueur:[0.10,0.62,0.64], ecume:[1.0,1.0,0.99],   ambianceHaut:[0.60,0.70,0.86], ambianceBas:[0.33,0.40,0.46], voile:[1.0,0.99,0.97],  lumiere:[1.0,0.95,0.85]},
  {h:13.5, zenith:[0.09,0.37,0.84],   horizon:[0.60,0.81,0.96],  soleil:[1.0,0.97,0.90],  disque:[1.0,1.0,0.96],   eauFond:[0.006,0.15,0.34],  eauClaire:[0.03,0.48,0.62], lueur:[0.08,0.68,0.72], ecume:[1.0,1.0,1.0],    ambianceHaut:[0.62,0.74,0.90], ambianceBas:[0.34,0.44,0.50], voile:[1.0,1.0,0.99],   lumiere:[1.0,0.98,0.92]},
  {h:17,   zenith:[0.15,0.42,0.80],   horizon:[0.80,0.86,0.90],  soleil:[1.0,0.88,0.66],  disque:[1.0,0.97,0.86],  eauFond:[0.012,0.13,0.27],  eauClaire:[0.05,0.39,0.49], lueur:[0.10,0.58,0.58], ecume:[1.0,0.99,0.96],  ambianceHaut:[0.58,0.66,0.80], ambianceBas:[0.33,0.36,0.40], voile:[1.0,0.98,0.95],  lumiere:[1.0,0.90,0.74]},
  {h:19.3, zenith:[0.27,0.44,0.72],   horizon:[1.0,0.74,0.52],   soleil:[1.0,0.64,0.32],  disque:[1.0,0.94,0.80],  eauFond:[0.020,0.115,0.205],eauClaire:[0.06,0.31,0.38], lueur:[0.10,0.52,0.50], ecume:[0.98,0.96,0.93], ambianceHaut:[0.52,0.58,0.70], ambianceBas:[0.30,0.30,0.34], voile:[0.97,0.96,0.94], lumiere:[1.0,0.78,0.56]},
  {h:20.4, zenith:[0.21,0.27,0.54],   horizon:[0.98,0.52,0.36],  soleil:[1.0,0.45,0.25],  disque:[1.0,0.80,0.60],  eauFond:[0.022,0.07,0.16],  eauClaire:[0.08,0.19,0.30], lueur:[0.22,0.30,0.40], ecume:[0.93,0.85,0.87], ambianceHaut:[0.44,0.42,0.60], ambianceBas:[0.25,0.21,0.29], voile:[0.92,0.86,0.90], lumiere:[0.92,0.56,0.42]},
  {h:21.2, zenith:[0.07,0.11,0.28],   horizon:[0.44,0.33,0.48],  soleil:[0.60,0.40,0.50], disque:[1.0,0.80,0.70],  eauFond:[0.015,0.05,0.11],  eauClaire:[0.055,0.13,0.22],lueur:[0.08,0.17,0.26], ecume:[0.74,0.76,0.87], ambianceHaut:[0.32,0.35,0.52], ambianceBas:[0.12,0.13,0.21], voile:[0.84,0.86,0.96], lumiere:[0.52,0.52,0.74]},
  {h:22.2, zenith:[0.025,0.05,0.125], horizon:[0.12,0.185,0.31], soleil:[0.62,0.72,0.95], disque:[0.92,0.95,1.0], eauFond:[0.012,0.042,0.09], eauClaire:[0.04,0.12,0.19], lueur:[0.05,0.16,0.24], ecume:[0.66,0.74,0.86], ambianceHaut:[0.25,0.32,0.48], ambianceBas:[0.08,0.12,0.20], voile:[0.84,0.88,0.97], lumiere:[0.56,0.64,0.88]},
  {h:24,   zenith:[0.025,0.05,0.125], horizon:[0.12,0.185,0.31], soleil:[0.62,0.72,0.95], disque:[0.92,0.95,1.0], eauFond:[0.012,0.042,0.09], eauClaire:[0.04,0.12,0.19], lueur:[0.05,0.16,0.24], ecume:[0.66,0.74,0.86], ambianceHaut:[0.25,0.32,0.48], ambianceBas:[0.08,0.12,0.20], voile:[0.84,0.88,0.97], lumiere:[0.56,0.64,0.88]}
];

/* ------------------------------------------------------------------ voile : les chiffres */
/* Polaire, par 14 nœuds de vent réel : angle au vent réel
   en degrés, vitesse en nœuds. C'est une table générique de croiseur de 34 pieds, pas celle du chantier. Sous 32 degrés
   la table ne dit rien : on pose la zone morte (vitesse nulle sous 24 degrés). */
var POLAIRE=[[0,0],[24,0],[28,2.2],[32,5.1],[36,5.5],[40,5.8],[45,6.1],[50,6.3],[60,6.6],[90,7.0],[120,6.9],[150,6.0],[180,5.3]];
function polaire(aDeg){var i; for(i=1;i<POLAIRE.length;i++){ if(aDeg<=POLAIRE[i][0]){ var p=POLAIRE[i-1],q=POLAIRE[i]; return lerp(p[1],q[1],(aDeg-p[0])/(q[0]-p[0])) } } return POLAIRE[POLAIRE.length-1][1]}
/* Angle de près : 42 degrés du vent réel, réglage de croisière. La table donnerait un meilleur gain au vent
   vers 36 à 40 degrés, mais elle est générique : valeur à faire trancher par un moniteur. */
var PRES=42*RAD;
var VPRES=polaire(PRES/RAD);
var ACCEL=2.0;
var RECUL=1.75;   /* recul de la caméra sur le site (1 = cadrage de la démo) */
var DECAL=20;     /* le bateau glisse vers la droite pour dégager le titre (mètres) */                 /* temps accéléré deux fois */
var KN=0.5144*ACCEL;           /* nœuds vers mètres par seconde affichée */
var LONG=10.4;                 /* longueur de coque, mètres */
var COULOIR=14;                /* demi-largeur du couloir de louvoyage, mètres */
var DEPART=142;                /* distance de la bouée au départ, mètres */
var ARRIVEE=17;                /* distance à laquelle on lofe pour s'arrêter à la bouée */

function bordeGV(a){return clamp((a-30*RAD)*0.62,6*RAD,78*RAD)}   /* angle de bôme réglé pour une allure */
function bordeFoc(a){return clamp((a-26*RAD)*0.62,10*RAD,72*RAD)}

/* houle : trois trains d'ondes, direction fixe (la houle ne tourne pas avec le vent) */
var HOULE=[{l:19,a:0.17,d:0,p:0.3},{l:11.5,a:0.09,d:0.52,p:2.1},{l:6.4,a:0.05,d:-0.66,p:4.4}];
var HOULE_AZ=200*RAD;
HOULE.forEach(function(h){h.k=TAU/h.l; h.w=Math.sqrt(9.81*h.k)*0.8; var az=HOULE_AZ+h.d; h.dx=Math.sin(az); h.dz=-Math.cos(az)});
function houle(x,z,t){var y=0,gx=0,gz=0,i,h,ph; for(i=0;i<3;i++){h=HOULE[i]; ph=h.k*(h.dx*x+h.dz*z)-h.w*t+h.p; y+=h.a*Math.sin(ph); var c=h.a*h.k*Math.cos(ph); gx+=c*h.dx; gz+=c*h.dz} return [y,gx,gz]}

/* forme de coque partagée entre le maillage et le shader de mer (écume de carène) */
function demiBau(t){return t<0.62 ? 1.75*(1-Math.pow(1-t/0.62,1.55)) : 1.75-0.22*Math.pow((t-0.62)/0.38,2)}
function quilleY(t){return -0.48*Math.pow(Math.sin(PI*clamp(0.04+t*0.9,0,1)),0.7)}
function livetY(t){return 1.12-0.2*t-0.06*Math.sin(PI*t)}

/* ------------------------------------------------------------------ simulation */
var S={};
var bouee={x:0,z:0};
function nouveauDepart(vent){
  S={t:0, w:vent, camAz:vent, mode:'route', direct:false, amure:1, dernierVirement:-9, man:null, empannage:-9,
     psi:wrap(vent-PRES), om:0, v:VPRES*0.9, cote:1, bome:-bordeGV(PRES), foc:-bordeFoc(PRES), ecoute:1,
     creuxGV:-1, creuxFoc:-1, fasGV:0, fasFoc:0, gite:GITE_MAX*RAD*0.9, tangage:0, roulis:0, pilonnement:0,
     fin:0, echelle:1, sillage:[], dernierPoint:-1, derive:[0,0], risee:[0,0], twa:PRES,
     cam:{d:PLANS.ouverture.d*RECUL,h:PLANS.ouverture.h*RECUL,av:PLANS.ouverture.av,az:PLANS.ouverture.tour*RAD,y:PLANS.ouverture.y,fov:PLANS.ouverture.focale,dec:PLANS.ouverture.decal}, foyer:[0,0], phase:null,
     brume:BRUME_ENTREE>0?1:0, eq:[1,1,1], gouttes:[], reserve:0};
  var ux=Math.sin(vent), uz=-Math.cos(vent);
  bouee.x=0; bouee.z=0;
  S.x=bouee.x-ux*DEPART+Math.cos(vent)*6; S.z=bouee.z-uz*DEPART+Math.sin(vent)*6;
  S.foyer=[S.x,S.z];
  stries.forEach(function(s){semer(s,true)});
}
var stries=[]; (function(){for(var i=0;i<46;i++)stries.push({x:0,z:0,vie:0,max:1,l:6})})();
function semer(s,partout){
  var ax=Math.sin(S.camAz), az=-Math.cos(S.camAz), rx=Math.cos(S.camAz), rz=Math.sin(S.camAz);
  var a=(alea()-0.25)*190, b=(alea()-0.5)*170;
  s.x=S.foyer[0]+ax*a+rx*b; s.z=S.foyer[1]+az*a+rz*b; s.max=1.6+alea()*1.8; s.vie=partout?alea()*s.max:0; s.l=5+alea()*6;
}

function pas(dt){
  var w=S.w, ux=Math.sin(w), uz=-Math.cos(w), rx=Math.cos(w), rz=Math.sin(w);
  var mx=bouee.x-S.x, mz=bouee.z-S.z;
  var loin=mx*ux+mz*uz, travers=mx*rx+mz*rz, dist=Math.hypot(mx,mz), theta=Math.atan2(travers,loin);
  var twa=wrap(w-S.psi), a=Math.abs(twa), cible;
  S.t+=dt;

  /* ---- la route : directe si la bouée est hors de la zone morte, sinon au près en tirant des bords */
  if(S.mode==='route'){
    if(dist<ARRIVEE || S.t>80){ S.mode='arrivee'; S.man=null }
    else{
      var seuil=S.direct ? PRES-1*RAD : PRES+1.5*RAD, avant=S.amure;
      if(Math.abs(theta)>=seuil){ S.direct=true; S.amure=-sgn(theta) }
      else{
        S.direct=false;
        if(S.t-S.dernierVirement>2.5){
          if(S.amure>0 && travers>COULOIR) S.amure=-1;
          else if(S.amure<0 && travers<-COULOIR) S.amure=1;
        }
      }
      if(S.amure!==avant){
        S.dernierVirement=S.t;
        /* virement si l'on change d'amure en passant par le vent debout */
        if(a<100*RAD) S.man={de:avant, t0:S.t, etape:1};
      }
    }
  }
  if(S.mode==='route') cible=S.direct ? wrap(w+theta) : wrap(w-S.amure*PRES);
  else cible=w; /* arrivée : bout au vent */

  /* ---- barre : le bateau tourne d'autant mieux qu'il a de la vitesse */
  var err=wrap(cible-S.psi), vmax=36*RAD*clamp(S.v/VPRES,0.62,1);
  var omc=clamp(err*2.4,-vmax,vmax);
  S.om=damp(S.om,omc,0.32,dt);
  S.psi=wrap(S.psi+S.om*dt);
  twa=wrap(w-S.psi); a=Math.abs(twa); S.twa=twa;

  /* ---- côté du vent, avec une petite marge au vent arrière (on empanne quand le vent passe la poupe) */
  if(sgn(twa)!==S.cote && a<174*RAD){ if(a>120*RAD) S.empannage=S.t; S.cote=sgn(twa) }

  /* ---- voiles : toujours sous le vent. Une voile ne peut pas être plus ouverte que le lit du vent. */
  var fas=sstep(31*RAD,13*RAD,a);
  var cGV=-S.cote*Math.min(bordeGV(a),a*0.86);
  S.bome=damp(S.bome,cGV,0.22,dt);
  /* foc : choqué dès que l'on entre dans le vent, bordé sur le nouveau bord une fois le lit du vent passé */
  var enManoeuvre=S.man!==null || S.mode!=='route';
  if(a<26*RAD && enManoeuvre) S.ecoute=damp(S.ecoute,0,0.2,dt);
  else if(a>29*RAD && S.mode==='route') S.ecoute=damp(S.ecoute,1,0.55,dt);
  var libre=Math.min(a,70*RAD), regle=Math.min(bordeFoc(a),a*0.9);
  var cFoc=-S.cote*lerp(libre,regle,S.ecoute);
  S.foc=damp(S.foc,cFoc,0.16,dt);
  S.fasGV=damp(S.fasGV,fas,0.15,dt);
  S.fasFoc=damp(S.fasFoc,Math.max(fas,(1-S.ecoute)*0.85),0.12,dt);
  S.creuxGV=damp(S.creuxGV,-S.cote*(1-fas),0.2,dt);
  S.creuxFoc=damp(S.creuxFoc,-S.cote*(1-fas)*(0.35+0.65*S.ecoute),0.18,dt);

  /* ---- vitesse : la polaire donne la cible, l'inertie fait le reste */
  var vc=S.mode==='route' ? polaire(a/RAD)*(0.55+0.45*S.ecoute) : 0;
  S.v=damp(S.v,vc,vc>S.v?2.4:(S.mode==='route'?3.6:1.8),dt); /* un croiseur de cinq tonnes garde son erre dans le virement */
  S.x+=Math.sin(S.psi)*S.v*KN*dt; S.z-=Math.cos(S.psi)*S.v*KN*dt;

  /* ---- gîte sous le vent, tangage et roulis sur la houle */
  var gc=S.cote*GITE_MAX*RAD*sstep(16*RAD,40*RAD,a)*(1-0.92*sstep(62*RAD,170*RAD,a))*clamp(S.v/VPRES,0,1.1);
  S.gite=damp(S.gite,gc,0.55,dt);
  var ho=houle(S.x,S.z,S.t), fx=Math.sin(S.psi), fz=-Math.cos(S.psi);
  S.pilonnement=ho[0]*0.55; S.tangage=(ho[1]*fx+ho[2]*fz)*0.9; S.roulis=(ho[1]*Math.cos(S.psi)+ho[2]*Math.sin(S.psi))*0.7;

  /* ---- étapes du virement, pour la légende */
  if(S.man){
    var m=S.man, nouveau=(sgn(twa)!==m.de);
    if(!nouveau && a>20*RAD) m.etape=1;
    else if(a<=20*RAD) m.etape=2;
    else if(S.ecoute<0.8 || a<PRES-7*RAD) m.etape=3;
    else m.etape=4;
    if(m.etape===4 && (S.v>VPRES*0.9 || S.t-m.t0>11)) S.man=null;
    if(S.t-m.t0>14) S.man=null;
  }

  /* ---- sillage : il suit la trajectoire réelle, point par point */
  if(S.t-S.dernierPoint>0.11){
    S.dernierPoint=S.t;
    S.sillage.push({x:S.x,z:S.z,px:Math.cos(S.psi),pz:Math.sin(S.psi),n:S.t,f:clamp(S.v/VPRES,0,1)});
    if(S.sillage.length>130) S.sillage.shift();
  }

  /* ---- le vent pousse les rides, les risées et les stries */
  S.derive[0]-=ux*2.4*dt; S.derive[1]-=uz*2.4*dt;
  S.risee[0]-=ux*8.5*dt; S.risee[1]-=uz*8.5*dt;
  for(var i=0;i<stries.length;i++){var s=stries[i]; s.vie+=dt; s.x-=ux*17*dt; s.z-=uz*17*dt; if(s.vie>s.max) semer(s,false)}

  /* ---- caméra : elle suit avec du retard, d'où la parallaxe */
  var portrait=vue.asp<0.95, c=S.cam, pl;
  if(S.mode!=='route') pl=PLANS.bouee; else if(S.t<PLANS.ouverture.duree) pl=PLANS.ouverture; else if(S.man) pl=PLANS.virement; else pl=PLANS.bord;
  var tc=pl.lenteur, rec=(portrait?PLANS.portrait.recul:1)*RECUL;
  c.d=damp(c.d,pl.d*rec,tc,dt); c.h=damp(c.h,pl.h*rec,tc,dt); c.av=damp(c.av,pl.av,tc,dt); c.y=damp(c.y,pl.y,tc,dt);
  c.az=damp(c.az,(pl.tour+pl.travelling*S.cote)*RAD,tc*1.25,dt); c.fov=damp(c.fov,pl.focale,tc,dt); c.dec=damp(c.dec,pl.decal+DECAL,tc,dt);
  S.foyer[0]=damp(S.foyer[0],S.x,0.8,dt); S.foyer[1]=damp(S.foyer[1],S.z,0.8,dt);
  S.brume=BRUME_ENTREE>0 ? 1-sstep(0,BRUME_ENTREE,S.t) : 0;

  /* ---- équipage : au rappel, du côté du vent. Au virement, chacun traverse le cockpit à son rythme. */
  S.eq[0]=damp(S.eq[0],S.cote,0.45,dt); S.eq[1]=damp(S.eq[1],S.cote,0.75,dt); S.eq[2]=damp(S.eq[2],S.cote,0.6,dt);

  /* ---- embruns : l'étrave soulève une gerbe quand elle plonge dans la houle, emportée sous le vent */
  if(EMBRUNS){
    var ex=S.x+fx*4.9, ez=S.z+fz*4.9, hb=houle(ex,ez,S.t), plonge=Math.max(0,-(hb[1]*fx+hb[2]*fz))*9;
    S.reserve+=dt*sstep(0.45,1,S.v/VPRES)*(8+150*plonge);
    while(S.reserve>=1 && S.gouttes.length<140){ S.reserve-=1; var co=(alea()<0.72?-S.cote:S.cote), la=co*(1.2+alea()*3.2);
      S.gouttes.push({x:ex,y:0.25,z:ez, vx:fx*(1+alea()*2)+Math.cos(S.psi)*la-ux*1.5, vy:1.8+alea()*3.6, vz:fz*(1+alea()*2)+Math.sin(S.psi)*la-uz*1.5, vie:0, max:0.5+alea()*0.55}) }
    if(S.reserve>3) S.reserve=3;
    for(i=S.gouttes.length-1;i>=0;i--){ var go=S.gouttes[i]; go.vie+=dt; go.vy-=11*dt; go.x+=go.vx*dt; go.y+=go.vy*dt; go.z+=go.vz*dt; if(go.vie>go.max||go.y<0) S.gouttes.splice(i,1) }
  }

  /* ---- fin : le bateau est arrêté bout au vent, la mer se pose, puis plus rien ne tourne */
  if(S.mode==='arrivee' && S.v<0.45 && Math.abs(err)<8*RAD){ S.mode='pose'; S.fin=0 }
}

function decrire(){
  var a=Math.abs(S.twa), deg=a/RAD, trib=S.twa>0, am=trib?'tribord amures':'bâbord amures';
  var cote=trib?'Le vent vient de tribord, les voiles sont à bâbord':'Le vent vient de bâbord, les voiles sont à tribord';
  if(S.mode==='repos') return {p:'Arrivé à la bouée au vent', d:'Le bateau est arrêté bout au vent, la mer se pose. Tournez le vent pour repartir.', e:0};
  if(S.mode==='arrivee'||S.mode==='pose') return {p:'Bout au vent à la bouée', d:'On lofe face au vent. Les voiles faseyent, le bateau s’arrête sur son erre.', e:0};
  if(S.man){
    var e=S.man.etape;
    if(e===1) return {p:'Virement de bord', d:'On lofe : l’étrave monte vers le vent, le bateau garde son élan.', e:1};
    if(e===2) return {p:'Virement de bord', d:'Bout au vent : l’étrave passe le lit du vent, les voiles faseyent, la vitesse tombe.', e:2};
    if(e===3) return {p:'Virement de bord', d:'La bôme et la grand-voile ont changé de bord. Le foc, choqué, est bordé sous le vent.', e:3};
    return {p:'Près '+am, d:'On relance : les voiles portent, le bateau gîte et reprend sa vitesse.', e:4};
  }
  if(S.t-S.empannage<2.2) return {p:'Empannage', d:'Le vent passe par l’arrière : la bôme change de bord.', e:0};
  if(deg<34) return {p:'Trop près du vent', d:'Les voiles faseyent. On abat pour retrouver le près.', e:0};
  if(deg<54) return {p:'Près '+am, d:cote+', bordées serré. Cap à '+Math.round(deg)+'° du vent.', e:0};
  if(deg<76) return {p:'Bon plein '+am, d:cote+', un peu choquées.', e:0};
  if(deg<106) return {p:'Travers '+am, d:cote+', ouvertes à mi-course.', e:0};
  if(deg<152) return {p:'Largue '+am, d:cote+', largement choquées.', e:0};
  if(deg<172) return {p:'Grand largue '+am, d:cote+', choquées en grand.', e:0};
  return {p:'Vent arrière', d:'Le vent pousse par la poupe, la grand-voile est ouverte en grand.', e:0};
}

/* ------------------------------------------------------------------ WebGL */
var canvas=document.getElementById('mer'), cadre=document.getElementById('cadre');
var gl=null, P={}, G={}, vue={w:1,h:1,asp:1.6,pr:1,qualite:1,bas:0};
var pal=null;

/* L'ambiance pour une heure donnée : couleurs fondues entre deux lignes de COULEURS, position du soleil ou de la lune. */
function ambiance(h){
  var i=0, k, c={}, a, b, t, n;
  h=((h%24)+24)%24;
  while(i<COULEURS.length-2 && h>=COULEURS[i+1].h) i++;
  a=COULEURS[i]; b=COULEURS[i+1]; t=sstep(a.h,b.h,h);
  for(k in a) if(k!=='h'){ c[k]=[lerp(a[k][0],b[k][0],t),lerp(a[k][1],b[k][1],t),lerp(a[k][2],b[k][2],t)] }
  var f=(h-SOLEIL.lever)/(SOLEIL.coucher-SOLEIL.lever), brut=SOLEIL.hauteurMidi*Math.sin(PI*clamp(f,-0.5,1.5)), az, el, force;
  if(brut>-2){ az=lerp(SOLEIL.azimutLever,SOLEIL.azimutCoucher,clamp(f,0,1)); el=Math.max(brut,1.2); force=sstep(-2,3,brut) }
  else{ var nuitLongue=24-(SOLEIL.coucher-SOLEIL.lever), fn=clamp((((h-SOLEIL.coucher)%24)+24)%24/nuitLongue,0,1);
    az=lerp(LUNE.azimutDebut,LUNE.azimutFin,fn); el=LUNE.hauteur*(0.6+0.4*Math.sin(PI*fn)); force=sstep(-2,-9,brut) }
  az*=RAD; el*=RAD; n=sstep(-3,-10,brut);
  var plat=[Math.sin(az),0,-Math.cos(az)], l=0.45+0.55*force;
  return {nuit:n, soleil:[plat[0]*Math.cos(el),Math.sin(el),plat[2]*Math.cos(el)], plat:plat, zen:c.zenith, hor:c.horizon,
    sol:[c.soleil[0]*force,c.soleil[1]*force,c.soleil[2]*force], disque:[c.disque[0]*force,c.disque[1]*force,c.disque[2]*force],
    fond:c.eauFond, clair:c.eauClaire, lueur:c.lueur, ecume:c.ecume, ambH:c.ambianceHaut, ambB:c.ambianceBas, voile:c.voile,
    lum:[c.lumiere[0]*l,c.lumiere[1]*l,c.lumiere[2]*l], marine:COQUE,
    brume:[c.horizon[0]*0.62+c.zenith[0]*0.38,c.horizon[1]*0.62+c.zenith[1]*0.38,c.horizon[2]*0.62+c.zenith[2]*0.38]};
}
function nomHeure(h){ return h<5.4?'nuit':h<7.2?'aube':h<11.5?'matin':h<14.5?'midi':h<18.3?'après-midi':h<20.2?'heure dorée':h<21.6?'crépuscule':'nuit' }
function lireHeure(h){ var m=Math.round(h*60)%1440, hh=Math.floor(m/60), mm=m%60; return hh+' h '+(mm<10?'0':'')+mm }

var GLSL_CIEL=[
'uniform vec3 uSoleil,uSol,uZen,uHor,uBrumeC; uniform float uBrume;',
'vec3 ciel(vec3 d){',
'  float h=clamp(d.y,0.,1.);',
'  vec3 c=mix(uHor,uZen,1.-exp(-h*4.2));',
'  float s=max(dot(d,uSoleil),0.);',
'  c+=uSol*(pow(s,5.)*.22+pow(s,40.)*.34+pow(s,260.)*.5);',
'  return c;',
'}',
'vec3 brumer(vec3 c,float d){ return mix(c,uBrumeC,uBrume*(1.-exp(-d/26.))); }',
'vec3 tons(vec3 c){ vec3 h=max(c-.72,0.); return min(c,vec3(.72))+.28*(1.-exp(-h/.28)); }'].join('\n');
var GLSL_BRUIT=[
'float hach(vec2 p){vec3 q=fract(vec3(p.xyx)*.1031); q+=dot(q,q.yzx+33.33); return fract((q.x+q.y)*q.z);}',
'vec3 bruitd(vec2 p){',
'  vec2 i=floor(p),f=fract(p),u=f*f*(3.-2.*f),du=6.*f*(1.-f);',
'  float a=hach(i),b=hach(i+vec2(1.,0.)),c=hach(i+vec2(0.,1.)),d=hach(i+vec2(1.,1.));',
'  return vec3(a+(b-a)*u.x+(c-a)*u.y+(a-b-c+d)*u.x*u.y, du*(vec2(b-a,c-a)+(a-b-c+d)*u.yx));',
'}'].join('\n');
var PREC='#ifdef GL_FRAGMENT_PRECISION_HIGH\nprecision highp float;\n#else\nprecision mediump float;\n#endif\n';

function glslHoule(){ /* les mêmes trois ondes que la fonction houle() du JavaScript */
  var s='',i,h;
  for(i=0;i<3;i++){h=HOULE[i];
    s+='ph='+h.k.toFixed(5)+'*dot(vec2('+h.dx.toFixed(5)+','+h.dz.toFixed(5)+'),p)-'+h.w.toFixed(5)+'*uT+'+h.p.toFixed(3)+';\n';
    s+='hh+='+h.a.toFixed(3)+'*sin(ph); g+='+(h.a*h.k).toFixed(5)+'*cos(ph)*vec2('+h.dx.toFixed(5)+','+h.dz.toFixed(5)+')*(1./(1.+d*d*'+(0.00009/(h.l/6.4)).toFixed(7)+'));\n';
  }
  return s;
}

var SRC={
ciel:{v:'attribute vec2 aP; varying vec2 vN; void main(){vN=aP; gl_Position=vec4(aP,0.,1.);}',
  f:PREC+'varying vec2 vN; uniform vec3 uF,uR,uU,uDisque; uniform float uNuit,uBas;\n'+GLSL_CIEL+'\n'+GLSL_BRUIT+'\n'+
  'void main(){ vec3 d=normalize(uF+vN.x*uR+(vN.y+uBas)*uU); vec3 c=ciel(d);\n'+
  ' float s=max(dot(d,uSoleil),0.); c+=uDisque*smoothstep(.99955,.99975,s)*1.6;\n'+
  ' float az=atan(d.x,-d.z); float n=bruitd(vec2(az*5.,d.y*34.+3.)).x*.6+bruitd(vec2(az*13.+9.,d.y*80.)).x*.4;\n'+
  ' float band=smoothstep(.52,.78,n)*exp(-abs(d.y-.11)*13.)*.55; c=mix(c,mix(uHor,uSol,.5)*(1.-.45*uNuit)+.05,band*(1.-.5*uNuit));\n'+
  ' if(uNuit>.01){ vec2 q=vec2(az*150.,d.y*240.); vec2 ce=floor(q); float r=hach(ce); vec2 o=fract(q)-.5-(vec2(hach(ce+7.),hach(ce+13.))-.5)*.7; c+=step(.972,r)*smoothstep(.16,.0,length(o))*smoothstep(.02,.2,d.y)*(.5+.5*hach(ce+3.))*.9*uNuit; }\n'+
  ' c=mix(c,uBrumeC,uBrume*.93); gl_FragColor=vec4(tons(c),1.); }'},
mer:{v:'attribute vec2 aP; uniform mat4 uVP; uniform vec3 uCam; varying vec3 vW; void main(){vW=vec3(aP.x*3600.+uCam.x,0.,aP.y*3600.+uCam.z); gl_Position=uVP*vec4(vW,1.);}',
  f:null},
objet:{v:'attribute vec3 aP,aN,aC; uniform mat4 uVP,uM; varying vec3 vN,vC,vL,vW; void main(){vec4 w=uM*vec4(aP,1.); vW=w.xyz; vN=mat3(uM[0].xyz,uM[1].xyz,uM[2].xyz)*aN; vC=aC; vL=aP; gl_Position=uVP*w;}',
  f:PREC+'varying vec3 vN,vC,vL,vW; uniform vec3 uSoleil,uLum,uAmbH,uAmbB,uCam,uMarine,uBrumeC; uniform float uBrume;\n'+
  'void main(){ vec3 n=normalize(vN); vec3 V=normalize(uCam-vW); vec3 col=vC; float gl0=0.;\n'+
  ' if(vC.r<0.){ float y=vL.y; col=mix(vec3(.50,.10,.085),vec3(.93,.94,.95),smoothstep(.035,.05,y)); col=mix(col,uMarine,smoothstep(.135,.15,y)); col=mix(col,vec3(.93,.94,.95),smoothstep(.80,.812,y)*(1.-smoothstep(.842,.854,y))); gl0=1.; }\n'+
  ' float di=max(dot(n,uSoleil),0.); vec3 amb=mix(uAmbB,uAmbH,n.y*.5+.5);\n'+
  ' vec3 c=col*(amb+uLum*di*.95);\n'+
  ' c+=gl0*uLum*pow(max(dot(reflect(-V,n),uSoleil),0.),36.)*.38;\n'+
  ' c+=uAmbH*pow(1.-max(dot(n,V),0.),3.)*.10;\n'+
  ' c=mix(c,uBrumeC,uBrume*(1.-exp(-length(uCam-vW)/26.)));\n'+
  ' gl_FragColor=vec4(c,1.); }'},
voile:{v:'attribute vec2 aP; uniform mat4 uVP,uM; uniform vec3 uGuindant,uBordure; uniform float uE,uPuis,uRond,uCreux,uFas,uT,uVrille; varying vec3 vN,vW; varying vec2 vUV;\n'+
  'vec3 f(float u,float v){ float ch=uE*(pow(max(1.-v,0.),uPuis)+uRond*sin(3.14159*v)*(1.-.4*v)); vec3 p=uGuindant*v+uBordure*(u*ch);\n'+
  ' float ventre=sin(3.14159*pow(u,.78))*(1.-.3*v);\n'+
  ' float x=uCreux*ch*(.118*ventre+uVrille*u*v);\n'+
  ' x+=uFas*ch*(.055*sin(u*12.-uT*23.+v*5.)+.03*sin(u*21.+uT*31.-v*9.))*sqrt(u);\n'+
  ' p.x+=x; return p; }\n'+
  'void main(){ float u=aP.x,v=aP.y; vec3 p=f(u,v); float e=.02; vec3 du=f(u+e,v)-p, dv=f(u,min(v+e,1.))-p; if(v>.975) dv=p-f(u,v-e);\n'+
  ' vec3 n=cross(dv,du)+vec3(1e-6,0.,0.); vec4 w=uM*vec4(p,1.); vW=w.xyz; vN=mat3(uM[0].xyz,uM[1].xyz,uM[2].xyz)*n; vUV=aP; gl_Position=uVP*w; }',
  f:PREC+'varying vec3 vN,vW; varying vec2 vUV; uniform vec3 uSoleil,uLum,uAmbH,uAmbB,uCam,uVoile,uBrumeC; uniform float uBrume;\n'+
  'void main(){ vec3 n=normalize(vN); vec3 V=normalize(uCam-vW); if(dot(n,V)<0.) n=-n; float ndl=dot(n,uSoleil);\n'+
  ' vec3 amb=mix(uAmbB,uAmbH,.72);\n'+
  ' vec3 c=uVoile*(amb+uLum*max(ndl,0.)*.75)+uVoile*uLum*max(-ndl,0.)*.62;\n'+
  ' float couture=1.-.07*smoothstep(.035,.0,abs(fract(vUV.y*7.+vUV.x*.6)-.5)-.0)*step(vUV.y,.97);\n'+
  ' float ralingue=1.-.16*(smoothstep(.03,.0,vUV.x)+smoothstep(.975,1.,vUV.x));\n'+
  ' c=mix(c*couture*ralingue,uBrumeC,uBrume*(1.-exp(-length(uCam-vW)/26.)));\n'+
  ' gl_FragColor=vec4(c,1.); }'},
trait:{v:'attribute vec4 aP; uniform mat4 uVP,uM; varying float vA; void main(){vA=aP.w; gl_Position=uVP*uM*vec4(aP.xyz,1.);}',
  f:PREC+'varying float vA; uniform vec4 uCol; void main(){gl_FragColor=vec4(uCol.rgb,uCol.a*vA);}'},
sillage:{v:'attribute vec4 aA; attribute vec3 aB; uniform mat4 uVP; uniform float uT; varying vec3 vS; varying vec2 vP;\n'+
  'void main(){ float age=max(uT-aB.y,0.); float demi=min(.75+.86*age,7.0); vec2 p=aA.xy+aA.zw*aB.x*demi; vS=vec3(aB.x,age,aB.z); vP=p; gl_Position=uVP*vec4(p.x,.03,p.y,1.); gl_Position.z-=.0006*gl_Position.w; }',
  f:PREC+'varying vec3 vS; varying vec2 vP; uniform vec3 uEcume; uniform vec2 uDerive; uniform float uBrume;\n'+GLSL_BRUIT+'\n'+
  'void main(){ float ax=abs(vS.x), age=vS.y; float demi=min(.75+.86*age,7.0); float lat=ax*demi;\n'+
  ' float nz=bruitd(vP*2.3+uDerive*.3).x*.5+bruitd(vP*5.9+3.1).x*.32+bruitd(vP*13.).x*.18;\n'+
  ' float bord=smoothstep(.45,.82,ax)*smoothstep(1.,.80,ax)*exp(-age*.34)*smoothstep(.25,.9,nz+.1)*.34;\n'+
  ' float coeur=smoothstep(1.35,.1,lat)*exp(-age*.50)*smoothstep(.22,.85,nz+.25*exp(-age*.8));\n'+
  ' float bandes=smoothstep(.60,.68,fract(lat*.62-age*.5+nz*.85))*smoothstep(.22,.5,ax)*smoothstep(1.,.72,ax)*exp(-age*.27)*.42;\n'+
  ' float a=(bord+coeur*.8+bandes)*vS.z*(1.-smoothstep(7.,12.,age))*smoothstep(0.,.5,age+.25);\n'+
  ' gl_FragColor=vec4(uEcume,clamp(a,0.,1.)*.8*(1.-uBrume*.85)); }'},
embruns:{v:'attribute vec4 aP; uniform mat4 uVP; uniform float uEch; varying float vA; void main(){ vA=aP.w; gl_Position=uVP*vec4(aP.xyz,1.); gl_PointSize=max(uEch*(.5+.5*aP.w)/gl_Position.w,1.5); }',
  f:PREC+'varying float vA; uniform vec3 uEcume; void main(){ vec2 q=gl_PointCoord-.5; float r=dot(q,q)*4.; gl_FragColor=vec4(uEcume,smoothstep(1.,.1,r)*vA*.6); }'}
};
SRC.mer.f=PREC+'varying vec3 vW; uniform vec3 uCam,uFond,uClair,uLueur,uEcume,uPlat,uVoileR; uniform float uT,uQual; uniform vec2 uDerive,uRisee,uLarg; uniform vec4 uBateau; uniform vec3 uBateauS,uBouee,uMat,uMatD;\n'+GLSL_CIEL+'\n'+GLSL_BRUIT+'\n'+
'float demiBau(float t){ return t<.62 ? 1.75*(1.-pow(max(1.-t/.62,0.),1.55)) : 1.75-.22*pow((t-.62)/.38,2.); }\n'+
/* le gréement vu depuis un point de l'eau, le long d'un rayon : sert au reflet des voiles et à leur ombre portée */
'float greement(vec3 P,vec3 R,float larg){ vec3 w0=P-uMat; float b=dot(R,uMatD), d0=dot(R,w0), e=dot(uMatD,w0); float den=max(1.-b*b,1e-4);\n'+
' float sg=clamp((e-b*d0)/den,0.,14.5); vec3 Q=uMat+uMatD*sg; float t=dot(Q-P,R); if(t<0.) return 0.; float di=length(P+R*t-Q);\n'+
' float w=(.28+2.3*(1.-sg/14.5))*larg; return smoothstep(w,w*.3,di)*smoothstep(.2,1.6,sg)*exp(-t/90.); }\n'+
'void main(){ vec2 p=vW.xz; vec3 V=uCam-vW; float d=length(V); V/=d; vec2 g=vec2(0.); float hh=0.,ph;\n'+
glslHoule()+
' float ri=smoothstep(.40,.70,bruitd((p+uRisee)/44.).x*.62+bruitd((p+uRisee)/15.+7.3).x*.38);\n'+
' vec2 hd=vec2(HDX,HDZ), hp=vec2(-hd.y,hd.x); vec2 pd=p+uDerive; vec2 q=vec2(dot(pd,hd),dot(pd,hp)*.42); float rf=1./(1.+d*d*.00016);\n'+
' vec3 n1=bruitd(q/1.55), n2=bruitd(q/.52+vec2(uT*.35,0.)), n3=bruitd(q/.19-vec2(0.,uT*.5));\n'+
' vec2 gr=(n1.yz*.17+n2.yz*.20+n3.yz*.15*rf)*(.45+1.05*ri)*rf; g+=hd*gr.x+hp*gr.y*.42;\n'+
' vec3 n=normalize(vec3(-g.x*1.25,1.,-g.y*1.25));\n'+
' float th=max(dot(n,V),0.);\n'+
' float F=.02+.98*pow(1.-th,5.);\n'+
' vec3 R=reflect(-V,n); R.y=abs(R.y)+.012; R=normalize(R);\n'+
/* corps de l'eau : du creux à la crête, plus clair quand on regarde vers le bas, lueur à contre-jour dans la vague */
' float cre=clamp(.26+hh*1.7+(n1.x-.5)*.45,0.,1.);\n'+
' vec3 corps=mix(uFond,uClair,cre*.72)*(.72+.55*th);\n'+
' corps+=uLueur*pow(max(dot(-V,uPlat),0.),3.)*clamp(hh*2.4+.38+(n2.x-.5)*.5,0.,1.)*.55;\n'+
' corps*=1.-.30*ri;\n'+
' vec3 refl=ciel(R);\n'+
' float om=0.;\n'+
' if(uQual>.5){ refl=mix(refl,uVoileR,greement(vW,R,uLarg.x)*.78); om=greement(vW,uSoleil,uLarg.y); }\n'+
' vec3 col=mix(corps,refl,F);\n'+
' col*=1.-.30*om;\n'+
/* soleil : nappe douce, plus des éclats nets seuillés qui scintillent sur les rides */
' float s=max(dot(R,uSoleil),0.); float ecl=pow(s,340.);\n'+
' col+=uSol*(ecl*3.2*(.35+.65*rf)+smoothstep(.30,.42,ecl*(.35+n3.x))*1.5*rf+pow(s,44.)*.44)*(1.-.8*om);\n'+
/* moutons : écume seuillée sur les crêtes, seulement dans les risées */
' col=mix(col,uEcume,smoothstep(.56,.62,hh*1.5+n2.x*.44+n3.x*.16+ri*.22-.30)*smoothstep(.35,.9,ri)*.55*rf);\n'+
/* carène : ombre de contact, écume qui se déchire en s'éloignant de la coque, vaguelettes d'étrave en bandes */
' vec2 qb=p-uBateau.xy; vec2 fw=uBateau.zw; float al=dot(qb,fw), sd=dot(qb,vec2(-fw.y,fw.x)); float t=.5-al/10.4;\n'+
' if(t>-.3&&t<1.5&&abs(sd)<5.5){ float tt=clamp(t,0.,1.); float bw=demiBau(tt)*.84*smoothstep(-.02,.05,t); float di=abs(sd)-bw; float mk=smoothstep(-.06,.02,t)*smoothstep(1.1,1.0,t);\n'+
'  col*=1.-.42*mk*smoothstep(1.5,-.3,di);\n'+
'  float bn=bruitd(p*2.6+uDerive).x*.6+bruitd(p*6.3-uDerive).x*.4; float vi=.22+.78*uBateauS.x;\n'+
'  float ec=mk*smoothstep(bn-.16,bn+.16,(1.-di/1.0)*vi*mix(1.15,.42,tt))*step(-.5,di)*.82;\n'+
'  float vg=mk*smoothstep(.62,.70,fract(di*.85-uT*1.1+bn*.9))*smoothstep(3.6,1.2,di)*step(.9,di)*uBateauS.x*mix(.55,.12,tt);\n'+
'  col=mix(col,uEcume,clamp(ec+vg,0.,1.)); }\n'+
' float db=length(p-uBouee.xy)-uBouee.z; col*=1.-.4*smoothstep(1.1,-.2,db); col=mix(col,uEcume,smoothstep(.45,0.,abs(db-.12))*.5*bruitd(p*3.+uDerive).x);\n'+
' float br=1.-exp(-pow(d/1150.,1.55)); col=mix(col,ciel(normalize(vec3(-V.x,.012,-V.z))),br);\n'+
' col=brumer(col,d);\n'+
' gl_FragColor=vec4(tons(col),1.); }';
SRC.mer.f=SRC.mer.f.replace('HDX',Math.sin(HOULE_AZ).toFixed(5)).replace('HDZ',(-Math.cos(HOULE_AZ)).toFixed(5));

function programme(src){
  function sh(type,code){var s=gl.createShader(type); gl.shaderSource(s,code); gl.compileShader(s);
    if(!gl.getShaderParameter(s,gl.COMPILE_STATUS)) throw new Error(gl.getShaderInfoLog(s)+'\n'+code.slice(0,200)); return s}
  var p=gl.createProgram(); gl.attachShader(p,sh(gl.VERTEX_SHADER,src.v)); gl.attachShader(p,sh(gl.FRAGMENT_SHADER,src.f)); gl.linkProgram(p);
  if(!gl.getProgramParameter(p,gl.LINK_STATUS)) throw new Error(gl.getProgramInfoLog(p));
  var o={p:p,a:{},u:{}},i,n,info;
  n=gl.getProgramParameter(p,gl.ACTIVE_ATTRIBUTES); for(i=0;i<n;i++){info=gl.getActiveAttrib(p,i); o.a[info.name]=gl.getAttribLocation(p,info.name)}
  n=gl.getProgramParameter(p,gl.ACTIVE_UNIFORMS); for(i=0;i<n;i++){info=gl.getActiveUniform(p,i); o.u[info.name]=gl.getUniformLocation(p,info.name)}
  return o}
function U(pr,n,v){var l=pr.u[n]; if(l==null) return;
  if(typeof v==='number') gl.uniform1f(l,v); else if(v.length===2) gl.uniform2fv(l,v); else if(v.length===3) gl.uniform3fv(l,v); else if(v.length===4) gl.uniform4fv(l,v); else gl.uniformMatrix4fv(l,false,v)}

/* ---- constructeur de maillages (position, normale, couleur) */
function Maille(){this.p=[];this.c=[];this.i=[];this.n=null}
Maille.prototype.s=function(x,y,z,c){this.p.push(x,y,z); this.c.push(c[0],c[1],c[2]); return this.p.length/3-1};
Maille.prototype.tri=function(a,b,c){this.i.push(a,b,c)};
Maille.prototype.quad=function(A,B,C,D,col){var a=this.s(A[0],A[1],A[2],col),b=this.s(B[0],B[1],B[2],col),c=this.s(C[0],C[1],C[2],col),d=this.s(D[0],D[1],D[2],col); this.tri(a,b,c); this.tri(a,c,d)};
/* oriente vers l'extérieur les faces ajoutées depuis l'indice i0, par rapport à un centre */
Maille.prototype.orienter=function(i0,ctr){var p=this.p,ix=this.i,k;
  for(k=i0;k<ix.length;k+=3){var a=ix[k]*3,b=ix[k+1]*3,c=ix[k+2]*3;
    var n=cross([p[b]-p[a],p[b+1]-p[a+1],p[b+2]-p[a+2]],[p[c]-p[a],p[c+1]-p[a+1],p[c+2]-p[a+2]]);
    var gx=(p[a]+p[b]+p[c])/3-ctr[0], gy=(p[a+1]+p[b+1]+p[c+1])/3-ctr[1], gz=(p[a+2]+p[b+2]+p[c+2])/3-ctr[2];
    if(n[0]*gx+n[1]*gy+n[2]*gz<0){var t=ix[k+1]; ix[k+1]=ix[k+2]; ix[k+2]=t}}};
Maille.prototype.normales=function(){var p=this.p,ix=this.i,n=new Float32Array(p.length),k;
  for(k=0;k<ix.length;k+=3){var a=ix[k]*3,b=ix[k+1]*3,c=ix[k+2]*3;
    var f=cross([p[b]-p[a],p[b+1]-p[a+1],p[b+2]-p[a+2]],[p[c]-p[a],p[c+1]-p[a+1],p[c+2]-p[a+2]]);
    [a,b,c].forEach(function(j){n[j]+=f[0]; n[j+1]+=f[1]; n[j+2]+=f[2]})}
  for(k=0;k<n.length;k+=3){var l=Math.hypot(n[k],n[k+1],n[k+2])||1; n[k]/=l; n[k+1]/=l; n[k+2]/=l}
  this.n=n};
Maille.prototype.boite=function(x0,x1,y0,y1,z0,z1,col,av){ /* av : rétrécissement de la face avant (z0) */
  var i0=this.i.length, a=av||1, yt=y0+(y1-y0)*(av?0.6:1);
  var A=[x0*a,y0,z0],B=[x1*a,y0,z0],C=[x1*a,yt,z0],D=[x0*a,yt,z0],E=[x0,y0,z1],F=[x1,y0,z1],Gq=[x1,y1,z1],H=[x0,y1,z1];
  this.quad(A,B,C,D,col); this.quad(E,F,Gq,H,col); this.quad(A,E,H,D,col); this.quad(B,F,Gq,C,col); this.quad(D,C,Gq,H,col); this.quad(A,B,F,E,col);
  this.orienter(i0,[(x0+x1)/2,(y0+y1)/2,(z0+z1)/2])};
Maille.prototype.tube=function(A,B,r0,r1,col,seg){seg=seg||8; var i0=this.i.length, ax=norm3([B[0]-A[0],B[1]-A[1],B[2]-A[2]]);
  var t=Math.abs(ax[1])<0.9?[0,1,0]:[1,0,0], u=norm3(cross(ax,t)), v=cross(ax,u), k, ra=[], rb=[];
  for(k=0;k<seg;k++){var an=k/seg*TAU, cx=Math.cos(an), sx=Math.sin(an), dx=u[0]*cx+v[0]*sx, dy=u[1]*cx+v[1]*sx, dz=u[2]*cx+v[2]*sx;
    ra.push(this.s(A[0]+dx*r0,A[1]+dy*r0,A[2]+dz*r0,col)); rb.push(this.s(B[0]+dx*r1,B[1]+dy*r1,B[2]+dz*r1,col))}
  for(k=0;k<seg;k++){var j=(k+1)%seg; this.tri(ra[k],ra[j],rb[j]); this.tri(ra[k],rb[j],rb[k])}
  var ca=this.s(A[0],A[1],A[2],col), cb=this.s(B[0],B[1],B[2],col);
  for(k=0;k<seg;k++){j=(k+1)%seg; this.tri(ca,ra[k],ra[j]); this.tri(cb,rb[k],rb[j])}
  this.orienter(i0,[(A[0]+B[0])/2,(A[1]+B[1])/2,(A[2]+B[2])/2])};
function televerser(m){ m.normales(); var nv=m.p.length/3, d=new Float32Array(nv*9), k;
  for(k=0;k<nv;k++){d[k*9]=m.p[k*3]; d[k*9+1]=m.p[k*3+1]; d[k*9+2]=m.p[k*3+2]; d[k*9+3]=m.n[k*3]; d[k*9+4]=m.n[k*3+1]; d[k*9+5]=m.n[k*3+2]; d[k*9+6]=m.c[k*3]; d[k*9+7]=m.c[k*3+1]; d[k*9+8]=m.c[k*3+2]}
  var vb=gl.createBuffer(); gl.bindBuffer(gl.ARRAY_BUFFER,vb); gl.bufferData(gl.ARRAY_BUFFER,d,gl.STATIC_DRAW);
  var ib=gl.createBuffer(); gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER,ib); gl.bufferData(gl.ELEMENT_ARRAY_BUFFER,new Uint16Array(m.i),gl.STATIC_DRAW);
  return {vb:vb,ib:ib,n:m.i.length}}

var MAT=[0,2.3,-0.9];             /* vit-de-mulet : pied de la grand-voile */
var POINT_AMURE=[0,1.15,-5.0];    /* point d'amure du foc, à l'étrave */
var GUINDANT_FOC=[0,12.45,3.93], BORDURE_FOC=norm3([0,0.6,4.25]), AXE_ETAI=norm3(GUINDANT_FOC);

function construire(){
  var HULL=[-1,0,0], PONT=[0.84,0.85,0.85], ROUF=[0.93,0.94,0.94], ALU=[0.72,0.75,0.79], SOMBRE=[0.16,0.19,0.24], CARENE=[0.50,0.10,0.085], ROUGE=[0.85,0.2,0.15], BLANC=[0.95,0.95,0.94];
  var m=new Maille(), NS=30, NR=9, i, j, rangs=[], i0;
  /* coque : sections de l'étrave (t=0) à la poupe (t=1) */
  for(i=0;i<=NS;i++){ var t=i/NS, z=-LONG/2+t*LONG, b=demiBau(t), ky=quilleY(t), sy=livetY(t), rg=[];
    for(j=-NR;j<=NR;j++){ var ph=Math.abs(j)/NR*PI/2, x=sgn(j)*b*Math.pow(Math.sin(ph),0.65), y=ky+(sy-ky)*(1-Math.pow(Math.cos(ph),1.6)); if(j===0)x=0; rg.push(m.s(x,y,z,HULL)) }
    rangs.push(rg) }
  i0=m.i.length;
  for(i=0;i<NS;i++)for(j=0;j<2*NR;j++){ var a=rangs[i][j], b2=rangs[i][j+1], c=rangs[i+1][j+1], d=rangs[i+1][j]; m.tri(a,b2,c); m.tri(a,c,d) }
  m.orienter(i0,[0,0.45,0]);
  /* tableau arrière */
  i0=m.i.length; var ctr=m.s(0,livetY(1)+0.06,LONG/2,HULL), der=[]; for(j=0;j<=2*NR;j++){ var q=rangs[NS][j]*3; der.push(m.s(m.p[q],m.p[q+1],m.p[q+2],HULL)) }
  for(j=0;j<2*NR;j++) m.tri(ctr,der[j],der[j+1]); m.orienter(i0,[0,0.5,0]);
  /* pont, avec un léger bouge */
  i0=m.i.length; var pr=null; for(i=0;i<=NS;i++){ var tt=i/NS, zz=-LONG/2+tt*LONG, bb=demiBau(tt), yy=livetY(tt);
    var cur=[m.s(-bb,yy,zz,PONT),m.s(0,yy+0.06,zz,PONT),m.s(bb,yy,zz,PONT)];
    if(pr){ m.tri(pr[0],pr[1],cur[1]); m.tri(pr[0],cur[1],cur[0]); m.tri(pr[1],pr[2],cur[2]); m.tri(pr[1],cur[2],cur[1]) } pr=cur }
  m.orienter(i0,[0,-5,0]);
  /* rouf, hublots, cockpit */
  m.boite(-1.02,1.02,0.97,1.42,-3.1,1.75,ROUF,0.5);
  m.boite(-1.035,-1.0,1.13,1.3,-1.9,1.2,SOMBRE); m.boite(1.0,1.035,1.13,1.3,-1.9,1.2,SOMBRE);
  m.boite(-0.78,0.78,0.99,1.035,2.15,4.85,[0.33,0.36,0.40]);
  m.boite(-0.9,0.9,1.0,1.2,1.75,2.1,ROUF);
  /* quille et safran */
  m.boite(-0.09,0.09,-1.95,-0.3,-1.25,0.35,CARENE); m.boite(-0.24,0.24,-2.05,-1.72,-1.5,0.7,CARENE); m.boite(-0.05,0.05,-1.5,-0.1,4.05,4.5,CARENE);
  /* mât, barres de flèche */
  m.tube([0,0.95,-0.9],[0,15.25,-0.9],0.095,0.06,ALU,8);
  m.tube([-0.82,7.2,-0.78],[0.82,7.2,-0.78],0.03,0.03,ALU,5); m.tube([-0.62,11.0,-0.8],[0.62,11.0,-0.8],0.026,0.026,ALU,5);
  G.coque=televerser(m);

  var bm=new Maille(); bm.tube([0,0,0.02],[0,0.04,4.7],0.085,0.075,ALU,8); G.bome=televerser(bm);

  var bo=new Maille(); bo.tube([0,-0.5,0],[0,0.45,0],0.62,0.62,ROUGE,14); bo.tube([0,0.45,0],[0,0.62,0],0.62,0.5,BLANC,14); bo.tube([0,0.62,0],[0,2.1,0],0.5,0.09,ROUGE,14); bo.tube([0,2.1,0],[0,2.5,0],0.035,0.035,SOMBRE,5); bo.tube([0,2.5,0],[0,2.72,0],0.16,0.16,ROUGE,8);
  G.bouee=televerser(bo);

  /* voiles : une grille (u du guindant à la chute, v du bas vers la tête), déformée dans le shader */
  var NU=14, NV=24, uv=[], ix=[]; for(j=0;j<=NV;j++)for(i=0;i<=NU;i++) uv.push(i/NU,j/NV);
  for(j=0;j<NV;j++)for(i=0;i<NU;i++){ var a2=j*(NU+1)+i; ix.push(a2,a2+1,a2+NU+2,a2,a2+NU+2,a2+NU+1) }
  var vb=gl.createBuffer(); gl.bindBuffer(gl.ARRAY_BUFFER,vb); gl.bufferData(gl.ARRAY_BUFFER,new Float32Array(uv),gl.STATIC_DRAW);
  var ib=gl.createBuffer(); gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER,ib); gl.bufferData(gl.ELEMENT_ARRAY_BUFFER,new Uint16Array(ix),gl.STATIC_DRAW);
  G.voile={vb:vb,ib:ib,n:ix.length};

  /* gréement dormant : étai, pataras, haubans */
  var gr=[0,1.15,-5.05, 0,14.05,-0.95,  0,15.25,-0.9, 0,0.95,5.15,
          -1.55,1.0,-0.75, -0.82,7.2,-0.78,  -0.82,7.2,-0.78, -0.62,11.0,-0.8,  -0.62,11.0,-0.8, 0,14.6,-0.9,
           1.55,1.0,-0.75,  0.82,7.2,-0.78,   0.82,7.2,-0.78,  0.62,11.0,-0.8,   0.62,11.0,-0.8, 0,14.6,-0.9];
  var gd=[]; for(i=0;i<gr.length;i+=3) gd.push(gr[i],gr[i+1],gr[i+2],1);
  G.greement={vb:gl.createBuffer(),n:gd.length/4}; gl.bindBuffer(gl.ARRAY_BUFFER,G.greement.vb); gl.bufferData(gl.ARRAY_BUFFER,new Float32Array(gd),gl.STATIC_DRAW);

  /* girouette de tête de mât : un petit pavillon rouge qui s'aligne dans le vent */
  var pv=new Maille(); pv.quad([0,0,0],[0,0.34,0],[0,0.2,1.15],[0,0.14,1.15],ROUGE); pv.quad([0.004,0,0],[0.004,0.14,1.15],[0.004,0.2,1.15],[0.004,0.34,0],ROUGE); G.pavillon=televerser(pv);

  /* équipage stylisé : un buste et une tête, trois couleurs */
  function silhouette(veste){ var e=new Maille(); e.tube([0,0,0],[0,0.56,0],0.21,0.17,veste,7); e.tube([0,0.6,0],[0,0.86,0],0.125,0.115,[0.86,0.68,0.55],7); return televerser(e) }
  G.equipage=[silhouette([0.07,0.12,0.2]),silhouette([0.82,0.16,0.14]),silhouette([0.92,0.93,0.94])];
  G.embruns={vb:gl.createBuffer(),d:new Float32Array(140*4)};

  G.plein=gl.createBuffer(); gl.bindBuffer(gl.ARRAY_BUFFER,G.plein); gl.bufferData(gl.ARRAY_BUFFER,new Float32Array([-1,-1,1,-1,-1,1,1,1]),gl.STATIC_DRAW);
  G.stries={vb:gl.createBuffer(),d:new Float32Array(stries.length*8)};
  G.sillage={vb:gl.createBuffer(),d:new Float32Array(134*2*7)};
}

function initGL(){
  var opt={antialias:true,alpha:false,depth:true,stencil:false,powerPreference:'high-performance',preserveDrawingBuffer:false};
  gl=canvas.getContext('webgl',opt)||canvas.getContext('experimental-webgl',opt);
  if(!gl) return false;
  for(var k in SRC) P[k]=programme(SRC[k]);
  construire();
  gl.enable(gl.DEPTH_TEST); gl.depthFunc(gl.LEQUAL); gl.disable(gl.CULL_FACE);
  return true;
}

function dessiner(pr,mesh){
  gl.bindBuffer(gl.ARRAY_BUFFER,mesh.vb); gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER,mesh.ib);
  var st=36; gl.enableVertexAttribArray(pr.a.aP); gl.vertexAttribPointer(pr.a.aP,3,gl.FLOAT,false,st,0);
  if(pr.a.aN>=0){gl.enableVertexAttribArray(pr.a.aN); gl.vertexAttribPointer(pr.a.aN,3,gl.FLOAT,false,st,12)}
  if(pr.a.aC>=0){gl.enableVertexAttribArray(pr.a.aC); gl.vertexAttribPointer(pr.a.aC,3,gl.FLOAT,false,st,24)}
  gl.drawElements(gl.TRIANGLES,mesh.n,gl.UNSIGNED_SHORT,0);
}
function couper(pr){for(var k in pr.a) if(pr.a[k]>=0) gl.disableVertexAttribArray(pr.a[k])}

function rendre(){
  if(!gl) return;
  var c=S.cam, az=S.camAz+c.az, fx=Math.sin(az), fz=-Math.cos(az);
  var dk=c.dec*clamp((vue.asp-1)/0.5,0,1), gx=-Math.cos(az)*dk, gz=-Math.sin(az)*dk; /* décalage vers la gauche de la caméra */
  var eye=[S.foyer[0]-fx*c.d+gx, c.h, S.foyer[1]-fz*c.d+gz], cib=[S.foyer[0]+fx*c.av+gx, c.y, S.foyer[1]+fz*c.av+gz];
  var portrait=vue.asp<0.95, fov=c.fov*(portrait?PLANS.portrait.focale:1)*RAD, V=regard(eye,cib), PR=perspective(fov,vue.asp,1.5,5200), th=Math.tan(fov/2);
  PR[9]=vue.bas; /* l'image descend de la hauteur de la réglette : le cadrage reste entier sous elle */
  var VP=mul(PR,V.m);
  var T=S.t, p;
  gl.viewport(0,0,canvas.width,canvas.height);
  gl.clear(gl.DEPTH_BUFFER_BIT);

  /* ciel */
  p=P.ciel; gl.useProgram(p.p); gl.disable(gl.DEPTH_TEST); gl.depthMask(false);
  U(p,'uF',V.f); U(p,'uR',[V.r[0]*th*vue.asp,V.r[1]*th*vue.asp,V.r[2]*th*vue.asp]); U(p,'uU',[V.u[0]*th,V.u[1]*th,V.u[2]*th]); U(p,'uBas',vue.bas);
  U(p,'uSoleil',pal.soleil); U(p,'uSol',pal.sol); U(p,'uZen',pal.zen); U(p,'uHor',pal.hor); U(p,'uDisque',pal.disque); U(p,'uNuit',pal.nuit); U(p,'uBrume',S.brume); U(p,'uBrumeC',pal.brume);
  gl.bindBuffer(gl.ARRAY_BUFFER,G.plein); gl.enableVertexAttribArray(p.a.aP); gl.vertexAttribPointer(p.a.aP,2,gl.FLOAT,false,0,0); gl.drawArrays(gl.TRIANGLE_STRIP,0,4);
  gl.enable(gl.DEPTH_TEST); gl.depthMask(true);

  /* mer */
  p=P.mer; gl.useProgram(p.p);
  U(p,'uVP',VP); U(p,'uCam',eye); U(p,'uT',T); U(p,'uDerive',S.derive); U(p,'uRisee',S.risee);
  U(p,'uSoleil',pal.soleil); U(p,'uSol',pal.sol); U(p,'uZen',pal.zen); U(p,'uHor',pal.hor); U(p,'uFond',pal.fond); U(p,'uClair',pal.clair); U(p,'uEcume',pal.ecume);
  U(p,'uLueur',pal.lueur); U(p,'uPlat',pal.plat); U(p,'uBrume',S.brume); U(p,'uBrumeC',pal.brume); U(p,'uQual',vue.qualite); U(p,'uVoileR',[pal.voile[0]*(0.5+0.4*pal.lum[0]),pal.voile[1]*(0.5+0.4*pal.lum[1]),pal.voile[2]*(0.5+0.4*pal.lum[2])]);
  /* le mât, incliné par la gîte : le shader de mer en tire le reflet et l'ombre des voiles */
  var gi=S.gite+S.roulis, cg=Math.cos(S.psi), sg=Math.sin(S.psi), mdx=-Math.sin(gi)*cg, mdz=-Math.sin(gi)*sg, mdy=Math.cos(gi);
  var planV=S.psi+PI-(S.bome+S.foc)*0.5, vx=Math.sin(planV), vz=-Math.cos(planV); /* direction du plan des voiles */
  function largeur(dx,dz){ var l=Math.hypot(dx,dz)||1; return 0.2+0.8*Math.abs((dx*vz-dz*vx)/l) }
  U(p,'uMat',[S.x+sg*0.9+mdx*1.0,1.0,S.z-cg*0.9+mdz*1.0]); U(p,'uMatD',[mdx,mdy,mdz]); U(p,'uLarg',[largeur(fx,fz),largeur(pal.plat[0],pal.plat[2])]);
  U(p,'uBateau',[S.x,S.z,Math.sin(S.psi),-Math.cos(S.psi)]); U(p,'uBateauS',[clamp(S.v/VPRES,0,1.1),0,0]); U(p,'uBouee',[bouee.x,bouee.z,0.62]);
  gl.bindBuffer(gl.ARRAY_BUFFER,G.plein); gl.enableVertexAttribArray(p.a.aP); gl.vertexAttribPointer(p.a.aP,2,gl.FLOAT,false,0,0); gl.drawArrays(gl.TRIANGLE_STRIP,0,4);

  /* bateau : cap, tangage, gîte */
  var M=mul(mul(mul(trans(S.x,S.pilonnement-0.02,S.z),rotY(-S.psi)),rotX(S.tangage)),rotZ(S.gite+S.roulis));
  var Mb=mul(mul(M,trans(MAT[0],MAT[1],MAT[2])),rotY(S.bome));
  var Mf=mul(mul(M,trans(POINT_AMURE[0],POINT_AMURE[1],POINT_AMURE[2])),rotAxe(AXE_ETAI,S.foc));
  var hb=houle(bouee.x,bouee.z,T), Mbo=mul(mul(trans(bouee.x,hb[0]*0.7,bouee.z),rotX(hb[2]*0.9+0.05*Math.sin(T*1.7))),rotZ(-hb[1]*0.9));
  /* pavillon : il s'aligne sur le vent apparent (vent réel moins vitesse du bateau) */
  var wx=-Math.sin(S.w)*14*0.5144, wz=Math.cos(S.w)*14*0.5144, bx=Math.sin(S.psi)*S.v*0.5144, bz=-Math.cos(S.psi)*S.v*0.5144;
  var ax=wx-bx, azv=wz-bz, capFlux=Math.atan2(ax,-azv), rel=wrap(capFlux-S.psi);
  var Mp=mul(mul(M,trans(0,15.3,-0.9)),rotY(PI-rel+0.12*Math.sin(T*9)*S.echelle));

  p=P.objet; gl.useProgram(p.p);
  U(p,'uVP',VP); U(p,'uCam',eye); U(p,'uSoleil',pal.soleil); U(p,'uLum',pal.lum); U(p,'uAmbH',pal.ambH); U(p,'uAmbB',pal.ambB); U(p,'uMarine',pal.marine); U(p,'uBrume',S.brume); U(p,'uBrumeC',pal.brume);
  U(p,'uM',M); dessiner(p,G.coque);
  if(EQUIPAGE){ /* barreur à l'arrière, deux équipiers au rappel */
    U(p,'uM',mul(M,trans(S.eq[0]*0.62,1.04,4.25))); dessiner(p,G.equipage[0]);
    U(p,'uM',mul(M,trans(S.eq[1]*1.28,1.03,2.55))); dessiner(p,G.equipage[1]);
    U(p,'uM',mul(M,trans(S.eq[2]*1.30,1.03,3.25))); dessiner(p,G.equipage[2]);
  }
  U(p,'uM',Mb); dessiner(p,G.bome);
  U(p,'uM',Mbo); dessiner(p,G.bouee);
  U(p,'uM',Mp); dessiner(p,G.pavillon);
  couper(p);

  /* voiles */
  p=P.voile; gl.useProgram(p.p);
  U(p,'uVP',VP); U(p,'uCam',eye); U(p,'uSoleil',pal.soleil); U(p,'uLum',pal.lum); U(p,'uAmbH',pal.ambH); U(p,'uAmbB',pal.ambB); U(p,'uVoile',pal.voile); U(p,'uT',T); U(p,'uBrume',S.brume); U(p,'uBrumeC',pal.brume);
  gl.bindBuffer(gl.ARRAY_BUFFER,G.voile.vb); gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER,G.voile.ib); gl.enableVertexAttribArray(p.a.aP); gl.vertexAttribPointer(p.a.aP,2,gl.FLOAT,false,0,0);
  var calme=0.3+0.7*S.echelle;
  U(p,'uM',Mb); U(p,'uGuindant',[0,12.3,0]); U(p,'uBordure',[0,0.01,1]); U(p,'uE',4.5); U(p,'uPuis',0.92); U(p,'uRond',0.09); U(p,'uCreux',S.creuxGV); U(p,'uFas',S.fasGV*calme); U(p,'uVrille',0.10);
  gl.drawElements(gl.TRIANGLES,G.voile.n,gl.UNSIGNED_SHORT,0);
  U(p,'uM',Mf); U(p,'uGuindant',GUINDANT_FOC); U(p,'uBordure',BORDURE_FOC); U(p,'uE',4.29); U(p,'uPuis',1.0); U(p,'uRond',0.0); U(p,'uCreux',S.creuxFoc); U(p,'uFas',S.fasFoc*1.25*calme); U(p,'uVrille',0.08);
  gl.drawElements(gl.TRIANGLES,G.voile.n,gl.UNSIGNED_SHORT,0);
  couper(p);

  /* gréement */
  gl.enable(gl.BLEND); gl.blendFunc(gl.SRC_ALPHA,gl.ONE_MINUS_SRC_ALPHA); gl.depthMask(false);
  p=P.trait; gl.useProgram(p.p); U(p,'uVP',VP); U(p,'uM',M); U(p,'uCol',pal.nuit>0.5?[0.5,0.56,0.66,0.55]:[0.13,0.16,0.21,0.6]);
  gl.bindBuffer(gl.ARRAY_BUFFER,G.greement.vb); gl.enableVertexAttribArray(p.a.aP); gl.vertexAttribPointer(p.a.aP,4,gl.FLOAT,false,0,0); gl.drawArrays(gl.LINES,0,G.greement.n);

  /* stries de vent */
  var d=G.stries.d, ux=Math.sin(S.w), uz=-Math.cos(S.w), i, s, o;
  for(i=0;i<stries.length;i++){ s=stries[i]; o=i*8; var al=Math.sin(PI*clamp(s.vie/s.max,0,1));
    d[o]=s.x; d[o+1]=0.5; d[o+2]=s.z; d[o+3]=al; d[o+4]=s.x+ux*s.l; d[o+5]=0.5; d[o+6]=s.z+uz*s.l; d[o+7]=0 }
  U(p,'uM',ident()); U(p,'uCol',pal.nuit>0.5?[0.8,0.87,1,0.30]:[1,0.97,0.92,0.5]);
  gl.bindBuffer(gl.ARRAY_BUFFER,G.stries.vb); gl.bufferData(gl.ARRAY_BUFFER,d,gl.DYNAMIC_DRAW); gl.vertexAttribPointer(p.a.aP,4,gl.FLOAT,false,0,0); gl.drawArrays(gl.LINES,0,stries.length*2);
  couper(p);

  /* sillage : un ruban qui s'élargit et s'efface avec l'âge de chaque point */
  var pts=S.sillage, n=pts.length, sd=G.sillage.d, k=0;
  function pousser(q,birth){ for(var c2=-1;c2<=1;c2+=2){ sd[k++]=q.x; sd[k++]=q.z; sd[k++]=q.px; sd[k++]=q.pz; sd[k++]=c2; sd[k++]=birth; sd[k++]=q.f } }
  for(i=0;i<n;i++) pousser(pts[i],pts[i].n);
  pousser({x:S.x,z:S.z,px:Math.cos(S.psi),pz:Math.sin(S.psi),f:clamp(S.v/VPRES,0,1)},T);
  p=P.sillage; gl.useProgram(p.p); U(p,'uVP',VP); U(p,'uT',T); U(p,'uEcume',pal.ecume); U(p,'uDerive',S.derive); U(p,'uBrume',S.brume);
  gl.bindBuffer(gl.ARRAY_BUFFER,G.sillage.vb); gl.bufferData(gl.ARRAY_BUFFER,sd.subarray(0,k),gl.DYNAMIC_DRAW);
  gl.enableVertexAttribArray(p.a.aA); gl.vertexAttribPointer(p.a.aA,4,gl.FLOAT,false,28,0); gl.enableVertexAttribArray(p.a.aB); gl.vertexAttribPointer(p.a.aB,3,gl.FLOAT,false,28,16);
  gl.drawArrays(gl.TRIANGLE_STRIP,0,k/7);
  couper(p);
  /* embruns */
  var ng=S.gouttes.length; if(ng){ var ed=G.embruns.d; for(i=0;i<ng;i++){ var go=S.gouttes[i]; ed[i*4]=go.x; ed[i*4+1]=go.y; ed[i*4+2]=go.z; ed[i*4+3]=(1-go.vie/go.max)*(1-S.brume) }
    p=P.embruns; gl.useProgram(p.p); U(p,'uVP',VP); U(p,'uEcume',pal.ecume); U(p,'uEch',canvas.height*0.2);
    gl.bindBuffer(gl.ARRAY_BUFFER,G.embruns.vb); gl.bufferData(gl.ARRAY_BUFFER,ed.subarray(0,ng*4),gl.DYNAMIC_DRAW); gl.enableVertexAttribArray(p.a.aP); gl.vertexAttribPointer(p.a.aP,4,gl.FLOAT,false,0,0); gl.drawArrays(gl.POINTS,0,ng); couper(p) }
  gl.disable(gl.BLEND); gl.depthMask(true);
}

/* ------------------------------------------------------------------ interface */
var elPhase=document.getElementById('phase'), elDetail=document.getElementById('detail'), elV=document.getElementById('iV'), elA=document.getElementById('iA'), elG=document.getElementById('iG');
var elFleche=document.getElementById('fleche'), elRose=document.getElementById('rose'), elVent=document.getElementById('ventValeur'), elCadran=document.getElementById('cadran'), elRejouer=document.getElementById('rejouer');
var etapes=(document.getElementById('etapes')||{children:[]}).children, vu={p:'',d:'',e:-1,cap:-1,instr:0};
function fr(x){return x.toFixed(1).replace('.',',')}
function afficher(force){
  var ds=decrire();
  if(ds.p!==vu.p){vu.p=ds.p; elPhase.textContent=ds.p}
  if(ds.d!==vu.d){vu.d=ds.d; elDetail.textContent=ds.d}
  if(ds.e!==vu.e){vu.e=ds.e; for(var i=0;i<etapes.length;i++) etapes[i].className=(i+1===ds.e)?'actif':''}
  var now=S.t; if(force||Math.abs(now-vu.instr)>0.2){ vu.instr=now;
    var a=Math.abs(S.twa); elV.textContent=fr(Math.max(S.v,0)); elA.textContent=String(Math.round(a/RAD)); elG.textContent=fr(Math.max(S.v,0)*Math.cos(a)) }
  var cap=((Math.round(S.w/RAD)%360)+360)%360;
  if(cap!==vu.cap||force){ vu.cap=cap; var txt=('00'+cap).slice(-3);
    elVent.textContent='Vent du '+txt+'°'; elCadran.setAttribute('aria-valuenow',String(cap)); elCadran.setAttribute('aria-valuetext','Vent du '+txt+' degrés') }
  var rot=(S.w-S.camAz-S.cam.az)/RAD; elFleche.setAttribute('transform','rotate('+rot.toFixed(1)+' 52 52)'); elRose.setAttribute('transform','rotate('+((-S.camAz-S.cam.az)/RAD).toFixed(1)+' 52 52)');
}

/* ------------------------------------------------------------------ boucle : elle s'arrête seule */
var etat={images:0, tourne:false, raf:0, dernier:0, visible:true, aLecran:true, sorti:false, veut:false, mesure:[], reduit:false};
window.__louvoyage=etat; etat.lire=function(){return S};
function image(now){
  etat.raf=0; if(!etat.tourne) return;
  var dt=Math.min((now-etat.dernier)/1000,0.05); etat.dernier=now; if(dt<=0) dt=0.016;
  etat.images++;
  if(etat.mesure && etat.images>25){ etat.mesure.push(dt); if(etat.mesure.length===50){ var m=0; etat.mesure.forEach(function(x){m+=x}); m/=50; var lent=m>0.024; if(lent){ if(vue.pr>1.05){ vue.plafond=Math.max(1,vue.pr*0.72); tailler() } else if(vue.qualite>0){ vue.qualite=0 } else lent=false } etat.mesure=lent?[]:null; etat.ms=m*1000 } }
  if(S.mode==='pose'){ S.fin+=dt; S.echelle=1-sstep(0,2.6,S.fin); if(S.fin>=2.6) S.mode='repos' }
  pas(dt*S.echelle); rendre(); afficher(false);
  if(S.mode==='repos'){ arreter(); etat.veut=false; elRejouer.hidden=false; afficher(true); return }
  etat.raf=requestAnimationFrame(image);
}
function lancer(){ if(etat.tourne||!gl) return; if(!etat.visible||!etat.aLecran) return; etat.tourne=true; etat.dernier=performance.now(); etat.raf=requestAnimationFrame(image) }
function arreter(){ etat.tourne=false; if(etat.raf){cancelAnimationFrame(etat.raf); etat.raf=0} }
function uneImage(){ if(gl&&!etat.tourne){ rendre(); afficher(true) } }
function repartir(){
  elRejouer.hidden=true; arreter(); cadre.classList.add('fondu');
  setTimeout(function(){ nouveauDepart(S.w); etat.veut=true; vu.e=-1; rendre(); afficher(true); cadre.classList.remove('fondu'); lancer() },230);
}
function tailler(){
  var r=cadre.getBoundingClientRect(), w=Math.max(1,r.width), h=Math.max(1,r.height);
  var pr=Math.min(window.devicePixelRatio||1,2,vue.plafond||2); var px=w*h*pr*pr; if(px>2.3e6) pr*=Math.sqrt(2.3e6/px);
  vue.pr=pr; vue.w=w; vue.h=h; vue.asp=w/h;
  var barre=document.querySelector('.heure'); vue.bas=barre ? 2*(barre.offsetTop+barre.offsetHeight)/h*0.9 : 0;
  var cw=Math.round(w*pr), ch=Math.round(h*pr); if(canvas.width!==cw||canvas.height!==ch){canvas.width=cw; canvas.height=ch}
  uneImage();
}

/* ------------------------------------------------------------------ le vent, du doigt ou de la souris */
function tourner(nv){ S.w=wrap(nv); if(S.mode==='repos'){ attente=true } if(!etat.tourne) uneImage() }
var attente=false, glisse=null;
function finGeste(){ if(attente){ attente=false; repartir() } else if(etat.reduit && !etat.tourne && S.mode!=='repos'){ etat.veut=true; lancer() } }
elCadran.addEventListener('pointerdown',function(e){ glisse='cadran'; try{elCadran.setPointerCapture(e.pointerId)}catch(_){} viser(e); e.preventDefault() });
elCadran.addEventListener('pointermove',function(e){ if(glisse==='cadran') viser(e) });
function lacher(){ if(glisse){ glisse=null; finGeste() } }
elCadran.addEventListener('pointerup',lacher); elCadran.addEventListener('pointercancel',lacher);
function viser(e){ var r=elCadran.getBoundingClientRect(), dx=e.clientX-(r.left+r.width/2), dy=e.clientY-(r.top+r.height/2); if(dx*dx+dy*dy<36) return; tourner(Math.atan2(dx,-dy)+S.camAz+S.cam.az) }
var touche=0;
elCadran.addEventListener('keydown',function(e){ var d=0; if(e.key==='ArrowLeft'||e.key==='ArrowDown') d=-5; else if(e.key==='ArrowRight'||e.key==='ArrowUp') d=5; else return;
  e.preventDefault(); tourner(S.w+d*RAD); clearTimeout(touche); touche=setTimeout(finGeste,500) });
/* à la souris, on peut aussi faire glisser la scène */
var x0=0;
canvas.addEventListener('pointerdown',function(e){ if(e.pointerType!=='mouse') return; glisse='scene'; x0=e.clientX; try{canvas.setPointerCapture(e.pointerId)}catch(_){} });
canvas.addEventListener('pointermove',function(e){ if(glisse!=='scene') return; tourner(S.w+(e.clientX-x0)*0.007); x0=e.clientX });
canvas.addEventListener('pointerup',lacher); canvas.addEventListener('pointercancel',lacher);
elRejouer.addEventListener('click',repartir);

/* ------------------------------------------------------------------ l'heure du jour */
var elHeure=document.getElementById('heure'), elHeureLue=document.getElementById('heureLue'), elAuto=document.getElementById('auto');
var heure=HEURE_DEPART, auto=AUTO_PAR_DEFAUT;
function heureAppareil(){ var d=new Date(); return d.getHours()+d.getMinutes()/60 }
/* Aucune horloge ne tourne : on ne recalcule qu'au geste, au chargement et au retour sur l'onglet. */
function reglerHeure(h,depuisReglette){
  heure=clamp(h,0,24); pal=ambiance(heure);
  var txt=lireHeure(heure);
  elHeureLue.textContent=txt; elHeure.setAttribute('aria-valuetext',txt+', '+nomHeure(heure%24));
  if(!depuisReglette) elHeure.value=String(Math.round(heure*4)/4);
  elAuto.setAttribute('aria-checked',auto?'true':'false');
  if(gl && !etat.tourne) uneImage();
}
function synchroniser(){ if(auto) reglerHeure(heureAppareil(),false) }
elHeure.addEventListener('input',function(){ auto=false; reglerHeure(parseFloat(elHeure.value),true) });
elAuto.addEventListener('click',function(){ auto=!auto; if(auto) reglerHeure(heureAppareil(),false); else reglerHeure(heure,false) });

/* ------------------------------------------------------------------ démarrage */
function demarrer(){
  vue.asp=1.6; reglerHeure(auto?heureAppareil():HEURE_DEPART,false);
  nouveauDepart(VENT_DEPART*RAD);
  var ok=false; try{ ok=initGL() }catch(err){ ok=false; if(window.console) console.error(err) }
  if(!ok){ var s=document.createElement('p'); s.className='secours'; s.textContent='Ce navigateur n’affiche pas la scène animée (WebGL indisponible). La légende ci-dessous décrit la manœuvre.'; cadre.appendChild(s); cadre.classList.add('pret'); return }
  etat.reduit=!!(window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches);
  tailler();
  if(etat.reduit){
    /* image fixe soignée : on avance la simulation sans l'afficher, puis on pose une seule image */
    for(var i=0;i<135;i++) pas(1/30);
    rendre(); afficher(true); elRejouer.textContent='Lancer l’animation'; elRejouer.hidden=false;
  } else { etat.veut=true; rendre(); afficher(true) }
  cadre.classList.add('pret');

  if(window.ResizeObserver) new ResizeObserver(tailler).observe(cadre); else window.addEventListener('resize',tailler);
  document.addEventListener('visibilitychange',function(){ etat.visible=!document.hidden; if(!etat.visible) arreter(); else{ synchroniser(); if(etat.veut) lancer() } });
  if(window.IntersectionObserver){
    new IntersectionObserver(function(en){ var v=en[0].isIntersecting; etat.aLecran=v;
      if(!v){ arreter(); etat.sorti=true }
      else{ if(etat.sorti && S.mode==='repos' && !etat.reduit){ etat.sorti=false; repartir() } else if(etat.veut) lancer(); etat.sorti=false }
    },{threshold:0.2}).observe(cadre);
  }
  canvas.addEventListener('webglcontextlost',function(e){ e.preventDefault(); arreter() });
  canvas.addEventListener('webglcontextrestored',function(){ P={}; G={}; try{ initGL(); if(etat.veut) lancer(); else uneImage() }catch(_){} });
  if(etat.veut) lancer();
}
demarrer();
})();