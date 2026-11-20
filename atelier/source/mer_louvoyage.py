"""La mer en fond du site : la scène du louvoyage reste fixe derrière toute la page d'accueil,
et le voilier continue de naviguer pendant qu'on descend.

Le moteur vient de `demo-v3-detaillee.html` (Nicolas, 19/11/2026) : trois bateaux au choix, WebGL
écrit à la main, aucune bibliothèque. On ne garde que la scène — plus de cadre, plus de largeur
limitée. Le JavaScript est publié à part (`mer-louvoyage.js`) pour que `index.html` reste léger et
que le navigateur le garde en cache.
"""
import os
from pathlib import Path

RACINE = Path(os.environ.get("SITE_ROOT", "/opt/data"))
DEMO = RACINE / "cache/documents/demo-v3-detaillee.html"
SITE = RACINE / "projets/sailingmore/site"
JS = SITE / "mer-louvoyage.js"

# réglages du site, appliqués au script de la démo à l'extraction
RECUL = 1.0     # distance de caméra : 1 = celle de la démo
DECAL = 18      # glissement latéral du bateau (m)
BORD_SECONDES = 20  # un bord dure vingt secondes : c'est le rythme du louvoyage
ALLURE = 2.0    # avance sur l'eau multipliée : le bateau traverse l'écran deux fois plus vite
RAYON = 520     # rayon de la zone où la marque et le départ sont tirés au sort (m)
Y_BORD = 4.2    # hauteur du point visé (valeur d'origine de ses fichiers : je n'y touche pas)
AV_BORD = -11   # caméra devant le bateau : le vent vient de l'utilisateur (voir plus bas)
FOCS = 2.2      # objectif plus large que celui de la démo : le bateau rapetisse sans
                # passer sous la ligne d'horizon (1 = focale de la démo)
PORTRAIT = 1.3  # téléphone tenu debout : un peu plus loin, sinon il prend tout l'écran


def extrait_js() -> str:
    """Le script de la démo, tel quel, avec les retouches du site."""
    txt = DEMO.read_text(encoding="utf-8")
    debut = txt.index("<script>") + len("<script>")
    fin = txt.index("</script>", debut)
    js = txt[debut:fin]

    # les éléments de la démo qui ne sont pas sur le site : liste des quatre temps, note longue,
    # titre de la réglette. Remplacés par un objet muet, sinon plantage au démarrage.
    stub = ("var MUET={children:[],innerHTML:'',textContent:'',style:{},"
            "classList:{add:function(){},remove:function(){},toggle:function(){}}};\n")
    # La légende est retirée de la page (Nicolas, 19/11/2026 : « retire cette légende partout ») ;
    # #phase, #detail et les trois instruments restent écrits par le moteur chaque image, donc ils
    # reçoivent le même objet muet que les autres éléments absents.
    for nom in ("etapes", "note", "tempsTitre", "phase", "detail", "iV", "iA", "iG"):
        vieux = "document.getElementById('%s')" % nom
        assert js.count(vieux) == 1, "élément %s introuvable" % nom
        js = js.replace(vieux, "(document.getElementById('%s')||MUET)" % nom)
    js = stub + js

    # Le site s'ouvre à l'heure de l'appareil (Nicolas, 19/11/2026) : « faut que le temps soit en
    # mode auto par défaut ». La réglette reste là pour qui veut fixer une heure ; on ne touche plus
    # au réglage du moteur (AUTO_PAR_DEFAUT=true dans la démo).

    # Bâbord amures au départ (Nicolas, 19/11/2026) : « faut qu'ils naviguent bâbord amure pour
    # qu'on voie les équipiers ». On ne retourne pas l'amure en cours de route — on part du bon
    # bord : amure -1 et cap de près symétrique, sinon le bateau vire pendant quinze secondes.
    for a, b in (("mode:'route', direct:false, amure:1,", "mode:'route', direct:false, amure:-1,"),
                 ("psi:wrap(vent-PRES),", "psi:wrap(vent+PRES),"),
                 ("twa:PRES,", "twa:-PRES,")):
        assert js.count(a) == 1, "réglage d'amure introuvable : %s" % a
        js = js.replace(a, b)

    # « faut jamais que ça s'arrête » : à la fin de la manœuvre, la scène repart au lieu de
    # proposer « Rejouer », et le réglage « mouvement réduit » n'arrête plus rien.
    vieux = ("if(S.mode==='repos'){ arreter(); etat.veut=false; elRejouer.hidden=false; afficher(true); return }")
    assert js.count(vieux) == 1, "fin de manœuvre introuvable"
    js = js.replace(vieux,
        "if(S.mode==='repos'){ arreter(); afficher(true); etat.veut=false; clearTimeout(etat.reprise);"
        " etat.reprise=setTimeout(function(){ etat.veut=true; repartir() },900); return }")
    vieux = "etat.reduit=!!(window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches);"
    assert js.count(vieux) == 1, "réglage mouvement réduit introuvable"
    js = js.replace(vieux, "etat.reduit=false;")

    # le bateau ne s'arrête plus jamais à la bouée au vent : elle recule de 700 m à chaque fois qu'il
    # l'atteint, donc il continue de tirer des bords indéfiniment — c'est le louvoyage demandé
    # (Nicolas, 19/11/2026 : « que le bateau lovoye »).
    vieux = "if(dist<ARRIVEE || S.t>80){ S.mode='arrivee'; S.man=null }"
    assert js.count(vieux) == 1, "arrivée à la bouée introuvable"
    js = js.replace(vieux, ("if(dist<ARRIVEE){ S.bordBouee=-(S.bordBouee||1);"
                            " bouee.x=S.x+ux*700+rx*S.bordBouee*260;"
                            " bouee.z=S.z+uz*700+rz*S.bordBouee*260; }"))

    # et il tire un bord franc toutes les douze secondes : sans ça, la bouée étant pile au vent, le
    # bateau trouvait sa route sur un seul bord et ne virait plus jamais (constaté au navigateur le
    # 19/11/2026 : 65 s sans un seul virement).
    vieux = "var seuil=S.direct ? PRES-1*RAD : PRES+1.5*RAD, avant=S.amure;"
    assert js.count(vieux) == 1, "seuil de route introuvable"
    js = js.replace(vieux, vieux + " if(S.t-(S.dernierVirement||0)>BORD_SECONDES) S.amure=-S.amure;")
    # la bouée change de côté à chaque fois : le bateau doit virer pour la suivre, et il tire donc
    # des bords tant qu'il navigue (Nicolas, 19/11/2026).

    # le TP52 est un bateau lourd : il suit moins la vague que le F50. Un seul nombre par bateau,
    # absent = 1 (réaction d'origine).
    vieux = "S.pilonnement=ho[0]*0.55*(1-S.vol)+S.vol*((B.hauteurVol||0)+0.06*Math.sin(S.t*1.9));"
    assert js.count(vieux) == 1, "pilonnement introuvable"
    js = js.replace(vieux, "S.pilonnement=ho[0]*0.55*(B.houle||1)*(1-S.vol)+S.vol*((B.hauteurVol||0)+0.06*Math.sin(S.t*1.9));")
    vieux = "S.tangage=(ho[1]*fx+ho[2]*fz)*0.9*(1-0.85*S.vol)"
    assert js.count(vieux) == 1, "tangage introuvable"
    js = js.replace(vieux, "S.tangage=(ho[1]*fx+ho[2]*fz)*0.9*(B.houle||1)*(1-0.85*S.vol)")
    vieux = "S.roulis=(ho[1]*Math.cos(S.psi)+ho[2]*Math.sin(S.psi))*0.7*(1-0.85*S.vol);"
    assert js.count(vieux) == 1, "roulis introuvable"
    js = js.replace(vieux, "S.roulis=(ho[1]*Math.cos(S.psi)+ho[2]*Math.sin(S.psi))*0.7*(B.houle||1)*(1-0.85*S.vol);")
    vieux = "    depart:235,         /* distance du départ à la bouée, en mètres */"
    assert js.count(vieux) == 1, "bloc TP52 introuvable"
    js = js.replace(vieux, "    houle:0.40,          /* une coque lourde de 52 pieds suit moins la vague */\n" + vieux)

    # pas de plan d'ouverture en gros plan sur une page d'accueil : sinon un voile occupe tout
    # l'écran les 3,4 premières secondes, et de nouveau à chaque changement de bateau
    vieux = "lenteur:1.0, duree:3.4, decal:7}"
    assert js.count(vieux) == 1, "plan d'ouverture introuvable"
    js = js.replace(vieux, "lenteur:1.0, duree:0, decal:7}")

    # ---- les commandes : la hauteur de la souris choisit l'allure ----------------------
    # immobile = travers, on monte = près, on descend = largue ; la barre tourne le bateau
    # toute seule, la polaire donne la vitesse et les voiles se règlent comme avant.
    vieux = "function pas(dt){"
    assert js.count(vieux) == 1, "pas() introuvable"
    js = js.replace(vieux, "function pas(dt){\n  if(S.allure==null){ S.allure=90*RAD; S.allureLue=90*RAD }")
    vieux = "if(S.mode==='route') cible=S.direct ? wrap(w+theta) : wrap(w-S.amure*PRES);"
    assert js.count(vieux) == 1, "cap de route introuvable"
    js = js.replace(vieux, "if(S.mode==='route'){ S.allureLue=damp(S.allureLue,S.allure,0.45,dt); cible=wrap(w-S.amure*S.allureLue) }")
    # plus de virement automatique sur la bouée : le bateau garde l'amure que l'on tient
    for a, b in (("if(Math.abs(theta)>=seuil){ S.direct=true; S.amure=-sgn(theta) }",
                  "if(false){ S.direct=true; S.amure=-sgn(theta) }"),
                 ("if(S.amure>0 && travers>COULOIR) S.amure=-1;", "if(false) S.amure=-1;"),
                 ("else if(S.amure<0 && travers<-COULOIR) S.amure=1;", "else if(false) S.amure=1;")):
        assert js.count(a) == 1, "morceau de routage introuvable : " + a[:40]
        js = js.replace(a, b)
    # le glissement horizontal de la scène n'a plus de sens : il ne reste que le cadran
    vieux = "canvas.addEventListener('pointermove',function(e){ if(glisse!=='scene') return; tourner(S.w+(e.clientX-x0)*0.007); x0=e.clientX });"
    assert js.count(vieux) == 1, "glissement de scène introuvable"
    js = js.replace(vieux, "/* le glissement de la scène est désactivé : la hauteur de la souris tient la barre */")
    # ---- plus de bouée : le bateau navigue à l'infini ---------------------------------
    vieux = "if(dist<ARRIVEE){ S.bordBouee=-(S.bordBouee||1); bouee.x=S.x+ux*700+rx*S.bordBouee*260; bouee.z=S.z+uz*700+rz*S.bordBouee*260; }"
    assert js.count(vieux) == 1, "respawn de bouée introuvable"
    js = js.replace(vieux, "if(false){ /* plus de bouée à atteindre */ }")
    vieux = "if(S.t-(S.dernierVirement||0)>BORD_SECONDES) S.amure=-S.amure;"
    assert js.count(vieux) == 1, "bordées imposées introuvables"
    js = js.replace(vieux, "/* plus de bordées imposées : on tient l'allure que la souris donne */")
    # la bouée n'est plus qu'un point de repère lointain, hors de vue
    vieux = "  if(S.allure==null){ S.allure=90*RAD; S.allureLue=90*RAD }"
    assert js.count(vieux) == 1, "init d'allure introuvable"
    js = js.replace(vieux, "  if(S.allure==null){ S.allure=90*DEG; S.allureLue=90*DEG; bouee.x=S.x+1e6; bouee.z=S.z+1e6 }")

    # la boucle du moteur est une fonction anonyme : le pointeur doit être branché dedans,
    # sinon il n'a accès ni à l'état S, ni à la barre, ni au bateau B
    i = js.rindex("})();")
    js = js[:i] + r"""var DEG=Math.PI/180;
/* ---- la barre suit le sens du mouvement : on descend = largue, on monte = près,
        on ne bouge plus = travers. Le défilement du site et le pointeur comptent pareil. */
(function(){
  var repos=null, dernierY=null;
  function pousse(dy){
    if(!dy || Math.abs(dy)<0.5) return;
    var p=((B&&B.pres)||40)*DEG, trav=90*DEG, larg=150*DEG;
    var v=S.allure + dy*0.25*DEG;   /* 4 px de geste = 1 degré d'allure */
    S.allure = v<p ? p : (v>larg ? larg : v);
    if(repos) clearTimeout(repos);
    repos=setTimeout(function(){ S.allure=trav; repos=null },1600);
  }
  window.addEventListener('pointermove',function(e){ if(dernierY!==null) pousse(e.clientY-dernierY); dernierY=e.clientY },{passive:true});
  window.addEventListener('pointerdown',function(e){ dernierY=e.clientY },{passive:true});
  var dernierDefile=null;
  window.addEventListener('scroll',function(){
    var y=window.pageYOffset||document.documentElement.scrollTop||0;
    if(dernierDefile!==null) pousse(y-dernierDefile);
    dernierDefile=y;
  },{passive:true});
  window.addEventListener('touchmove',function(e){ var t=e.touches&&e.touches[0]; if(!t) return; if(dernierY!==null) pousse(t.clientY-dernierY); dernierY=t.clientY },{passive:true});
})();
""" + js[i:]


    # la première image est déjà le cadrage large du site, pas le gros plan d'ouverture
    vieux = 'cam:{d:PLANS.ouverture.d*B.echelle*((B.zoom&&B.zoom.ouverture)||1),h:PLANS.ouverture.h*B.echelle*((B.zoom&&B.zoom.ouverture)||1),av:PLANS.ouverture.av*B.echelle,az:((B.vue&&B.vue.ouverture!=null)?B.vue.ouverture:PLANS.ouverture.tour)*RAD,y:PLANS.ouverture.y*B.echelle*((B.zoom&&B.zoom.ouverture)||1),fov:PLANS.ouverture.focale,dec:PLANS.ouverture.decal*B.echelle}'
    assert js.count(vieux) == 1, "caméra initiale introuvable"
    # nombres écrits en dur : la caméra de départ est construite avant la ligne qui déclare
    # RECUL, DECAL et FOCS, donc y toucher donnerait NaN et un écran noir
    js = js.replace(vieux, 'cam:{d:PLANS.bord.d*B.echelle*%.2f,h:PLANS.bord.h*B.echelle*%.2f,av:PLANS.bord.av*B.echelle,az:((B.vue&&B.vue.bord!=null)?B.vue.bord:PLANS.bord.tour)*RAD,y:PLANS.bord.y*B.echelle*%.2f,fov:PLANS.bord.focale*%.2f,dec:PLANS.bord.decal*B.echelle+%.1f}' % (RECUL, RECUL, RECUL, FOCS, DECAL))

    # le point visé monte : le bateau passe sous le titre au lieu de se cacher derrière
    # Le vent vient de l'utilisateur, pas du fond du site (Nicolas, 19/11/2026) : « faudrait que le
    # bateau ait le vent de l'autre côté… que le vent vienne de l'utilisateur plutôt que le fond du
    # site ». `av` est l'avance de la caméra le long de l'axe du bateau : +11 la mettait derrière (on
    # voyait la poupe et le bateau s'éloignait), -11 la met devant, on voit la proue et les voiles
    # face à l'écran.
    vieux = "bord:     {d:31, h:11,  av:11, y:4.2,"
    assert js.count(vieux) == 1, "cadrage du bord introuvable"
    js = js.replace(vieux, "bord:     {d:31, h:11,  av:%s, y:%s," % (AV_BORD, Y_BORD))

    # cadrage : deux nombres à toucher, en tête de fichier
    assert js.count("var PLANS={") == 1, "table des cadrages introuvable"
    js = js.replace("var PLANS={", "var RECUL=%s, DECAL=%s, BORD_SECONDES=%s, ALLURE=%s, RAYON=%s;\nvar PLANS={"
                    % (RECUL, DECAL, BORD_SECONDES, ALLURE, RAYON))

    # Le bateau avance plus vite à l'écran (Nicolas, 19/11/2026) : « les bateaux ne bougent pas assez
    # rapidement ». ALLURE multiplie l'avance sur l'eau sans toucher à la vitesse annoncée ni aux voiles.
    vieux = "S.x+=Math.sin(S.psi)*S.v*KN*dt; S.z-=Math.cos(S.psi)*S.v*KN*dt;"
    assert js.count(vieux) == 1, "avance du bateau introuvable"
    js = js.replace(vieux, "S.x+=Math.sin(S.psi)*S.v*KN*ALLURE*dt; S.z-=Math.cos(S.psi)*S.v*KN*ALLURE*dt;")

    # Départ tiré au hasard à chaque visite (Nicolas, 19/11/2026) : « il faut qu'ils aient un départ
    # aléatoire à chaque visite ». La marque tombe ailleurs dans la zone et le bateau part sur l'amure
    # et à l'angle tirés au sort — deux visites ne montrent jamais la même image d'ouverture.
    vieux = "  bouee.x=0; bouee.z=0;"
    assert js.count(vieux) == 1, "marque introuvable"
    js = js.replace(vieux, "  bouee.x=(Math.random()-0.5)*2*RAYON; bouee.z=(Math.random()-0.5)*2*RAYON;")
    for a, b in (("psi:wrap(vent+PRES),", "psi:wrap(vent+PRES*(Math.random()<0.5?-1:1)),"),
                 ("amure:-1, dernierVirement:-9", "amure:(Math.random()<0.5?-1:1), dernierVirement:-9")):
        assert js.count(a) == 1, "départ du bateau introuvable : %s" % a
        js = js.replace(a, b)

    vieux = "c.d=damp(c.d,pl.d*rec*E*zo,tc,dt); c.h=damp(c.h,pl.h*E*zo,tc,dt);"
    assert js.count(vieux) == 1, "caméra introuvable"
    js = js.replace(vieux, "c.d=damp(c.d,pl.d*rec*E*ZS*RECUL,tc,dt); "
                           "c.h=damp(c.h,pl.h*E*ZS*RECUL,tc,dt);")
    # la ligne de réglages est partagée avec d'autres travaux : on y ajoute ZS et FOCS
    # au lieu de la réécrire, sinon on efface ce qu'un autre y a mis (BORD_SECONDES, etc.)
    import re
    m = re.search(r"^var RECUL=[^;]*;", js, re.M)
    assert m, "ligne de réglages introuvable"
    ligne = m.group(0)
    ajout = ""
    if "ZS=" not in ligne:
        ajout += ", ZS=1"
    if "FOCS=" not in ligne:
        ajout += ", FOCS=%s" % FOCS
    if ajout:
        js = js[:m.start()] + ligne[:-1] + ajout + ";" + js[m.end():]

    vieux = "c.fov=damp(c.fov,pl.focale,tc,dt);"
    assert js.count(vieux) == 1, "objectif introuvable"
    js = js.replace(vieux, "c.fov=damp(c.fov,pl.focale*FOCS,tc,dt);")

    vieux = "c.dec=damp(c.dec,pl.decal*E*zo,tc,dt);"
    assert js.count(vieux) == 1, "décalage caméra introuvable"
    js = js.replace(vieux, "c.dec=damp(c.dec,pl.decal*E*zo+DECAL,tc,dt);")

    vieux = "portrait: {recul:1.0, focale:1.16}"
    assert js.count(vieux) == 1, "réglage portrait introuvable"
    js = js.replace(vieux, "portrait: {recul:%s, focale:1.16}" % PORTRAIT)

    return js.strip()


def ecrire_js() -> int:
    js = extrait_js()
    JS.write_text(js, encoding="utf-8")
    return len(js)


MER_CSS = """
/* ---- la mer en fond : fixe, derrière tout le contenu (Nicolas, 19/11/2026) ---- */
.mer-fond{position:fixed;inset:0;z-index:0;overflow:hidden;background:#071c31;
  isolation:isolate;pointer-events:none}
.mer-fond canvas{position:absolute;inset:0;width:100%;height:100%;display:block;
  opacity:0;transition:opacity 1.1s cubic-bezier(.23,1,.32,1);cursor:grab;pointer-events:auto}
.mer-fond.pret canvas{opacity:1}
.mer-fond.fondu canvas{opacity:0;transition-duration:.22s}
/* voile : l'eau reste visible comme fond, le texte reste lisible par-dessus */
.mer-fond .mer-ombre{position:absolute;inset:0;z-index:1;pointer-events:none;
  background:radial-gradient(120% 85% at 50% 28%,rgba(5,16,30,.20) 0%,rgba(5,16,30,.34) 55%,rgba(5,16,30,.52) 100%),
             linear-gradient(180deg,rgba(6,18,33,.30) 0%,rgba(6,18,33,.12) 30%,rgba(6,18,33,.40) 78%,rgba(5,15,28,.62) 100%)}
.contenu{position:relative;z-index:1;pointer-events:none;
  background:linear-gradient(180deg,rgba(6,18,33,0) 0,rgba(6,18,33,0) 62vh,
    rgba(6,18,33,.55) 96vh,rgba(6,18,33,.55) 100%)}

/* les commandes de la scène : posées sur la mer, elles s'effacent dès qu'on descend */
.mer-fond .heure,.mer-fond .choix,.mer-fond .vent,.mer-fond .legende,.mer-fond .rejouer{
  transition:opacity .45s ease,transform .45s ease}
.mer-fond.loin .heure,.mer-fond.loin .choix,.mer-fond.loin .vent,.mer-fond.loin .legende,
.mer-fond.loin .rejouer{opacity:0;pointer-events:none;transform:translateY(-6px)}

/* Le tableau de bord détaché des pages annexes : mêmes commandes, hors de la couche du fond
   (z-index -1) qui les rendrait invisibles et incliquables. */
.mer-fond.mer-fond-commandes{position:relative;inset:auto;height:auto;width:100%;max-width:100%;
  background:none;overflow:visible;z-index:60;pointer-events:none;display:flex;flex-direction:column;
  align-items:flex-start;gap:.55rem;padding:1rem 1.1rem .2rem}
.mer-fond.mer-fond-commandes .heure,.mer-fond.mer-fond-commandes .choix{position:relative!important;
  left:auto!important;right:auto!important;top:auto!important;bottom:auto!important;
  margin:0!important;pointer-events:auto}
.mer-fond .heure{position:absolute;left:14px;top:80px;z-index:4;height:46px;padding:0 8px 0 14px;
  display:flex;align-items:center;gap:10px;border-radius:999px;width:min(360px,calc(100% - 28px));
  background:rgba(6,18,33,.66);color:var(--creme,#f4efe4);
  -webkit-backdrop-filter:blur(10px);backdrop-filter:blur(10px);pointer-events:auto}
.mer-fond .heure .lue{flex:none;min-width:4.6em;font-size:14px;font-weight:600;
  font-variant-numeric:tabular-nums;white-space:nowrap}
.mer-fond .heure .piste{flex:1 1 auto;min-width:0;height:42px;margin:0;background:transparent;
  cursor:pointer;-webkit-appearance:none;appearance:none;touch-action:none;outline:none}
.mer-fond .heure .piste::-webkit-slider-runnable-track{height:8px;border-radius:4px;background:linear-gradient(90deg,#0b1730 0%,#0b1730 21%,#d9879a 27%,#f2c48a 31%,#6fb1e6 42%,#3f97e6 56%,#7fb6e0 72%,#f5b56b 81%,#d9694f 85%,#3a2c55 89%,#0b1730 93%,#0b1730 100%)}
.mer-fond .heure .piste::-moz-range-track{height:8px;border-radius:4px;background:linear-gradient(90deg,#0b1730 0%,#0b1730 21%,#d9879a 27%,#f2c48a 31%,#6fb1e6 42%,#3f97e6 56%,#7fb6e0 72%,#f5b56b 81%,#d9694f 85%,#3a2c55 89%,#0b1730 93%,#0b1730 100%)}
.mer-fond .heure .piste::-webkit-slider-thumb{-webkit-appearance:none;appearance:none;width:22px;height:22px;
  margin-top:-7px;border-radius:50%;background:var(--creme,#f4efe4);border:0;box-shadow:0 1px 5px rgba(0,0,0,.5)}
.mer-fond .heure .piste::-moz-range-thumb{width:22px;height:22px;border-radius:50%;background:var(--creme,#f4efe4);
  border:0;box-shadow:0 1px 5px rgba(0,0,0,.5)}
.mer-fond .heure .auto{flex:none;display:flex;align-items:center;gap:6px;height:34px;padding:0 11px 0 9px;
  border-radius:999px;font:600 12.5px/1 system-ui,sans-serif;color:var(--creme,#f4efe4);
  background:rgba(255,255,255,.10);border:1px solid rgba(255,255,255,.22);cursor:pointer}
.mer-fond .heure .auto .pastille{width:8px;height:8px;border-radius:50%;background:#93a8bc}
.mer-fond .heure .auto[aria-checked="true"]{background:var(--creme,#f4efe4);color:#08162a;border-color:var(--creme,#f4efe4)}
.mer-fond .heure .auto[aria-checked="true"] .pastille{background:var(--rouge,#e23a3e)}

/* le choix du bateau */
.mer-fond .choix{position:absolute;left:14px;top:80px;z-index:4;display:flex;flex-direction:column;
  align-items:stretch;gap:4px;padding:4px;border-radius:22px;background:rgba(6,18,33,.66);
  -webkit-backdrop-filter:blur(10px);backdrop-filter:blur(10px);pointer-events:auto;width:max-content}
.mer-fond .choix button{font:600 13px/1 system-ui,sans-serif;color:#e8eff5;background:transparent;
  border:0;border-radius:18px;min-height:36px;padding:0 14px;cursor:pointer;white-space:nowrap;
  text-align:left;transition:background-color .15s ease,color .15s ease}
.mer-fond .choix button[aria-checked="true"]{background:var(--creme,#f4efe4);color:#08162a}
.mer-fond .choix button:focus-visible{outline:3px solid var(--rouge,#e23a3e);outline-offset:2px}

/* plus de girouette : le vent ne se règle plus à la main (Nicolas, 19/11/2026) */
.mer-fond .vent{display:none!important}
/* le cadran du vent, en bas à droite */
.mer-fond .vent{position:absolute;right:16px;top:50%;transform:translateY(-50%);z-index:4;width:104px;
  display:flex;flex-direction:column;align-items:center;gap:3px;color:var(--creme,#f4efe4);text-align:center;
  pointer-events:auto}
.mer-fond .vent .cadran{width:96px;height:96px;border-radius:50%;background:rgba(6,18,33,.62);
  -webkit-backdrop-filter:blur(10px);backdrop-filter:blur(10px);touch-action:none;cursor:grab;outline:none;
  -webkit-tap-highlight-color:transparent;user-select:none;-webkit-user-select:none}
.mer-fond .vent .cadran:active{cursor:grabbing}
.mer-fond .vent svg{display:block;width:100%;height:100%}
.mer-fond .vent .valeur{font-size:12px;font-weight:600;font-variant-numeric:tabular-nums;
  text-shadow:0 1px 4px rgba(0,0,0,.85)}
.mer-fond .vent .geste{font-size:10.5px;color:#c3d2e0;text-shadow:0 1px 4px rgba(0,0,0,.85)}

/* la légende de la manœuvre, en bas à gauche */
.mer-fond .legende{position:absolute;left:14px;bottom:14px;z-index:4;width:min(330px,calc(100% - 150px));
  background:rgba(6,18,33,.66);color:var(--creme,#f4efe4);-webkit-backdrop-filter:blur(10px);backdrop-filter:blur(10px);
  border-radius:12px;padding:12px 14px 10px;display:flex;flex-direction:column;gap:4px;text-align:left;
  pointer-events:auto}
.mer-fond .legende .oeil{margin:0;font-size:10.5px;letter-spacing:.14em;text-transform:uppercase;color:#a8bccc}
.mer-fond .legende .phase{margin:0;font-weight:700;font-size:17px;line-height:1.2;min-height:1.2em}
.mer-fond .legende .detail{margin:0;font-size:12.5px;line-height:1.35;color:#b9cbdc;min-height:2.7em}
.mer-fond .instruments{display:flex;gap:16px;margin:5px 0 0;padding:7px 0 0;
  border-top:1px solid rgba(255,255,255,.16)}
.mer-fond .instruments div{display:flex;flex-direction:column;min-width:0}
.mer-fond .instruments dt{font-size:10px;letter-spacing:.1em;text-transform:uppercase;color:#a8bccc}
.mer-fond .instruments dd{margin:0;font-variant-numeric:tabular-nums;font-size:16px;font-weight:600;white-space:nowrap}
.mer-fond .instruments dd small{font-size:10.5px;font-weight:500;color:#a8bccc;margin-left:2px}

.mer-fond .rejouer{position:absolute;left:50%;bottom:18px;transform:translateX(-50%);z-index:4;
  font:600 13.5px/1 system-ui,sans-serif;color:#08162a;background:var(--creme,#f4efe4);border:0;border-radius:999px;
  padding:10px 17px;min-height:42px;cursor:pointer;pointer-events:auto}
.mer-fond .rejouer:active{transform:translateX(-50%) scale(.97)}
.mer-fond .secours{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;
  padding:24px;text-align:center;color:var(--creme,#f4efe4);z-index:2}

/* le héros : plus qu'un texte posé sur l'eau */
.hero.hero-mer{position:relative;max-width:none;margin:0;padding:0;text-align:center;
  min-height:100svh;display:flex;align-items:center;justify-content:center;background:transparent;pointer-events:none}
.hero-mer .hero-texte{position:relative;z-index:3;padding:2rem 1.4rem 7.75rem;pointer-events:none}
.contenu a,.contenu button,.contenu input,.contenu select,.contenu textarea,
.contenu summary,.contenu [tabindex],.contenu video,.contenu audio{pointer-events:auto}

@media (max-width:820px){
  .mer-fond .choix{left:10px;top:64px}
  .mer-fond .legende{display:none}
  .mer-fond .vent{top:auto;bottom:150px;left:8px;right:auto;transform:none;width:84px}
  .mer-fond .vent .cadran{width:78px;height:78px}
  .mer-fond .rejouer{bottom:12px}
  .hero.hero-mer{align-items:flex-start}
  .hero-mer .hero-texte{padding:13.2rem 1.2rem .5rem}
  .hero-mer .reseaux-barre{gap:1.3rem;flex-wrap:wrap;margin-top:2.2rem}
}
@media (prefers-reduced-motion: reduce){
  .mer-fond canvas{transition-duration:.2s}
  .mer-fond .heure,.mer-fond .choix,.mer-fond .vent,.mer-fond .legende,.mer-fond .rejouer{transition:none}
}
"""

MER_JS = """
/* les commandes de la scène s'effacent dès qu'on a quitté le haut de la page */
(function(){
  var m=document.getElementById('cadre'); if(!m) return;
  function maj(){ var s=window.scrollY||window.pageYOffset||0;
    m.classList.toggle('loin', s > window.innerHeight*0.72); }
  window.addEventListener('scroll', maj, {passive:true});
  window.addEventListener('resize', maj); maj();
})();
"""


# Nicolas, 20/11/2026 : « ce ne sera pas possible de régler l'heure pour l'utilisateur, par défaut
# c'est auto et ça restera comme ça ». La piste et le bouton Auto ont quitté la page ; le moteur garde
# son heure automatique et ne cherche plus d'`#auto` à cliquer (il regarde `AUTO_PAR_DEFAUT`).
# Le choix du bateau reste, à gauche et désormais en colonne : trois pastilles empilées se lisent d'un
# coup d'œil là où trois boutons côte à côte mangeaient la largeur de l'écran.
COMMANDES = """
  <div class="choix" id="choix" role="radiogroup" aria-label="Bateau"></div>
"""


def html_fond(commandes: bool = True) -> str:
    # L'adresse du script porte l'empreinte du fichier : un visiteur qui revient ne garde pas
    # l'ancien moteur dans son cache quand on le change — et deux constructions identiques donnent
    # la même adresse, donc un `diff` propre (la date de modification, elle, changeait à chaque
    # construction et salissait les sept pages d'un `?v=` différent, 20/11/2026).
    if JS.exists():
        import hashlib
        version = hashlib.sha1(JS.read_bytes()).hexdigest()[:8]
    else:
        version = "1"
    """La couche fixe : le canvas, les commandes, la légende. Elle passe derrière tout le contenu."""
    return f"""
<div class="mer-fond" id="cadre">

  <canvas id="mer" aria-hidden="true"></canvas>
  <div class="mer-ombre" aria-hidden="true"></div>
  {COMMANDES if commandes else ""}
  <button class="rejouer" id="rejouer" type="button" hidden>Rejouer</button>
  <div class="vent">
    <div class="cadran" id="cadran" role="slider" tabindex="0" aria-label="Direction d'où vient le vent"
      aria-valuemin="0" aria-valuemax="359" aria-valuenow="0" aria-valuetext="Vent du 000 degrés">
      <svg viewBox="0 0 104 104" aria-hidden="true">
        <circle cx="52" cy="52" r="44" fill="none" stroke="#f4f7fa" stroke-opacity=".28" stroke-width="1"/>
        <g id="rose" stroke="#f4f7fa" stroke-opacity=".5" stroke-width="1">
          <line x1="52" y1="8" x2="52" y2="15"/><line x1="96" y1="52" x2="89" y2="52"/>
          <line x1="52" y1="96" x2="52" y2="89"/><line x1="8" y1="52" x2="15" y2="52"/>
        </g>
        <g id="fleche">
          <line x1="52" y1="10" x2="52" y2="66" stroke="#f4f7fa" stroke-width="2.4" stroke-linecap="round"/>
          <path d="M52 76 L44.5 61 L52 65 L59.5 61 Z" fill="#f4f7fa"/>
          <circle cx="52" cy="10" r="4.2" fill="#E2232E"/>
        </g>
      </svg>
    </div>
    <span class="valeur" id="ventValeur">Vent du 000°</span>
    <span class="geste">Faites-le tourner</span>
  </div>
</div>
<style>{MER_CSS}</style>
<script src="mer-louvoyage.js?v={version}" defer></script>
<script>{MER_JS}</script>
"""


def hero(interieur: str) -> str:
    """Le texte d'ouverture, posé sur la mer."""
    return f"""
<section class="hero hero-mer">
  <div class="hero-texte">{interieur}</div>
</section>
"""
