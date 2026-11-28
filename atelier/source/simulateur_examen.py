#!/usr/bin/env python3
"""Simulateur d'examen : moteur unique, permis en fichiers de données.

Données : projets/sailingmore/examens/*.json (un fichier = un examen).
Sortie  : projets/sailingmore/site/simulateur-examen.html (français seul pour l'instant).
Usage   : python3 scripts/simulateur_examen.py            -> génère la page
          python3 scripts/simulateur_examen.py --verifier -> contrôle données + page
"""
import json, re, shutil, subprocess, sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
DONNEES = RACINE / "simulateur/permis"
SORTIE = RACINE / "projets/sailingmore/site/simulateur-examen.html"
URL = "https://sailingmore.fr/simulateur-examen.html"

MOTEUR = r"""
(function(){
var D=JSON.parse(document.getElementById('donnees').textContent);
var $=function(i){return document.getElementById(i)};
var ex=null,mat=0,qi=0,rep={},fin=0,tim=null;
function el(t,c,x){var e=document.createElement(t);if(c)e.className=c;if(x!=null)e.textContent=x;return e}
function mel(a){a=a.slice();for(var i=a.length-1;i>0;i--){var j=Math.floor(Math.random()*(i+1)),t=a[i];a[i]=a[j];a[j]=t}return a}
function vider(n){while(n.firstChild)n.removeChild(n.firstChild)}
function accueil(){
 clearInterval(tim);var z=$('zone');vider(z);
 z.appendChild(el('p','intro','Choisissez un examen. La session est chronométrée, les corrections n’apparaissent qu’à la fin, avec un score par matière.'));
 D.forEach(function(d,i){
  var nq=0,det=[];d.matieres.forEach(function(m){nq+=m.questions.length;det.push(m.titre+' : '+(m.questions.length?m.questions.length+' questions':'en préparation'))});
  if(!nq){z.appendChild(el('p','note',d.titre+' — en préparation (aucune question publiée).'));return}
  var b=el('button','gros',d.titre+' — '+d.duree_min+' min — '+nq+' questions');b.onclick=function(){demarrer(i)};z.appendChild(b);
  var sc='';try{var s=localStorage.getItem('sm_exam_'+d.id);if(s)sc=' Dernier score : '+s+'.'}catch(e){}
  z.appendChild(el('p','note',(d.materiel?'Matériel simulé : '+d.materiel+'. ':'')+det.join(' ; ')+'.'+sc))});
}
function demarrer(i,ratees){
 ex=JSON.parse(JSON.stringify(D[i]));ex._i=i;rep={};mat=0;qi=0;fin=Date.now()+ex.duree_min*60000;
 if(ratees){ex.matieres.forEach(function(m){m.questions=m.questions.filter(function(q){return ratees.indexOf(q.q)>=0})})}
 ex.matieres=ex.matieres.filter(function(m){return m.questions.length});
 ex.matieres.forEach(function(m){m.questions.forEach(function(q){
  if(m.type==='qcm'){var ord=mel(q.choix.map(function(_,k){return k}));q._ord=ord}
  else q._ord=mel(q.etapes.map(function(_,k){return k}))})});
 clearInterval(tim);tim=setInterval(tic,500);tic();question();
}
function tic(){var r=fin-Date.now();if(r<=0){terminer();return}var m=Math.floor(r/60000),s=Math.floor(r/1000)%60;$('chrono').textContent='Temps restant : '+m+':'+(s<10?'0':'')+s}
function cle(){return mat+'/'+qi}
function question(){
 var m=ex.matieres[mat],q=m.questions[qi],z=$('zone');vider(z);
 z.appendChild(el('div','entete-sc',m.titre+' — question '+(qi+1)+'/'+m.questions.length));
 z.appendChild(el('p','q',q.q));
 var k=cle();
 if(m.type==='qcm'){
  var box=el('div','rep');
  q._ord.forEach(function(idx){var b=el('button',rep[k]===idx?'choisi':'',q.choix[idx]);b.onclick=function(){rep[k]=idx;question()};box.appendChild(b)});
  z.appendChild(box);
 }else{
  var seq=rep[k]||(rep[k]=[]);
  var ol=el('ol','seq');seq.forEach(function(idx){ol.appendChild(el('li','',q.etapes[idx]))});z.appendChild(ol);
  var box=el('div','rep');
  q._ord.forEach(function(idx){if(seq.indexOf(idx)<0){var b=el('button','',q.etapes[idx]);b.onclick=function(){seq.push(idx);question()};box.appendChild(b)}});
  z.appendChild(box);
  var r=el('button','nav','Recommencer cet ordre');r.onclick=function(){rep[k]=[];question()};z.appendChild(r);
 }
 var nav=el('div','navb');
 var p=el('button','','Précédent');p.onclick=function(){bouger(-1)};
 var s=el('button','',(mat===ex.matieres.length-1&&qi===m.questions.length-1)?'Terminer l’examen':'Suivant');
 s.onclick=function(){if(s.textContent==='Suivant')bouger(1);else terminer()};
 nav.appendChild(p);nav.appendChild(s);z.appendChild(nav);
}
function bouger(d){
 var m=ex.matieres[mat];qi+=d;
 if(qi<0){mat=Math.max(0,mat-1);qi=ex.matieres[mat].questions.length-1}
 else if(qi>=m.questions.length){mat++;qi=0}
 question();
}
function juste(m,q,r){
 if(r==null)return false;
 if(m.type==='qcm')return r===q.bonne;
 return r.length===q.etapes.length&&r.every(function(v,i){return v===i});
}
function terminer(){
 clearInterval(tim);$('chrono').textContent='Examen terminé';
 var z=$('zone');vider(z);var tot=0,n=0,ok=true;
 var tb=el('div','bilan');
 ex.matieres.forEach(function(m,mi){
  var b=0;m.questions.forEach(function(q,qk){if(juste(m,q,rep[mi+'/'+qk]))b++});
  var pc=Math.round(100*b/m.questions.length),r=pc>=ex.seuil_pct;if(!r)ok=false;tot+=b;n+=m.questions.length;
  tb.appendChild(el('p',r?'ok':'ko',m.titre+' : '+b+'/'+m.questions.length+' ('+pc+' %) — '+(r?'acquis':'à revoir')));
 });
 var pt=Math.round(100*tot/n);
 z.appendChild(el('h2','','Score : '+tot+'/'+n+' ('+pt+' %)'));
 z.appendChild(el('p','note','Seuil indicatif : '+ex.seuil_pct+' % par matière — '+(ok?'toutes les matières sont acquises.':'au moins une matière est à revoir.')));
 z.appendChild(tb);
 ex.matieres.forEach(function(m,mi){m.questions.forEach(function(q,qk){
  var r=rep[mi+'/'+qk],c=el('div','corr');
  c.appendChild(el('b','',(juste(m,q,r)?'✓ ':'✗ ')+q.q));
  c.appendChild(el('span','',m.type==='qcm'?'Bonne réponse : '+q.choix[q.bonne]+'. ':'Ordre attendu : '+q.etapes.join(' → ')+'. '));
  c.appendChild(el('span','',q.expl));z.appendChild(c)})});
 try{localStorage.setItem('sm_exam_'+ex.id,tot+'/'+n+' ('+pt+' %)')}catch(e){}
 var rat=[];ex.matieres.forEach(function(m,mi){m.questions.forEach(function(q,qk){if(!juste(m,q,rep[mi+'/'+qk]))rat.push(q.q)})});
 if(rat.length){var rr=el('button','gros','Refaire les '+rat.length+' questions ratées');rr.onclick=function(){demarrer(ex._i,rat)};z.appendChild(rr)}
 var re=el('button','gros','Choisir un autre examen');re.onclick=accueil;z.appendChild(re);
}
accueil();
})();
"""

GABARIT = """<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Simulateur d'examen : SRC (VHF) et permis côtier | Sailing More</title>
<link rel="canonical" href="__URL__">
<meta name="description" content="Entraînez-vous à l'examen SRC (radio VHF, ICOM IC-M330, oral en anglais) et au permis côtier : session chronométrée, score par matière.">
<meta property="og:title" content="Simulateur d'examen : SRC (VHF) et permis côtier | Sailing More">
<meta property="og:description" content="Session chronométrée, score par matière, pratique simulée et oral en anglais.">
<meta property="og:url" content="__URL__">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Sailing More">
<meta property="og:locale" content="fr_FR">
<meta property="og:image" content="https://sailingmore.fr/og-image.jpg">
<script type="application/ld+json">{"@context":"https://schema.org","@type":"WebApplication","name":"Simulateur d'examen nautique","url":"__URL__","applicationCategory":"EducationalApplication","inLanguage":"fr","operatingSystem":"Web","offers":{"@type":"Offer","price":"0","priceCurrency":"EUR"},"publisher":{"@type":"Organization","name":"Sailing More","url":"https://sailingmore.fr/"}}</script>
<style>
:root{--fond:#0a1a2b;--creme:#eef3f7;--gris:#9db2c6;--rouge:#e23a3e;--teal:#7ed6d6}
*{box-sizing:border-box}
body{margin:0;background:var(--fond);color:var(--creme);font-family:system-ui,-apple-system,"Helvetica Neue",Arial,sans-serif;line-height:1.55}
.entete{display:flex;justify-content:space-between;padding:.7rem 1.2rem;background:rgba(6,16,32,.96);border-bottom:1px solid rgba(126,214,214,.14)}
.entete a{color:var(--gris);text-decoration:none;font-weight:800;letter-spacing:.12em;text-transform:uppercase;font-size:.74rem}
.page{max-width:44rem;margin:0 auto;padding:2rem 1.2rem 3.5rem}
h1{font-size:clamp(1.8rem,6vw,2.6rem);font-weight:300;margin:.4rem 0 .6rem}
.filet{height:1px;max-width:16rem;background:linear-gradient(90deg,var(--rouge) 0 34%,rgba(255,255,255,.18) 34% 100%);margin:1rem 0 1.2rem}
button{font:inherit;cursor:pointer;border-radius:.5rem;border:1px solid rgba(238,243,247,.22);background:transparent;color:var(--creme);padding:.6rem 1rem}
button:hover{border-color:var(--teal)}
button.gros{display:block;width:100%;text-align:left;margin:.6rem 0 .2rem;font-size:1.05rem}
button.choisi{background:var(--teal);color:var(--fond);border-color:var(--teal);font-weight:700}
.rep{display:flex;flex-direction:column;gap:.5rem;margin:.8rem 0}
.rep button{text-align:left}
.navb{display:flex;gap:.5rem;margin-top:1rem}
.q{font-size:1.15rem;margin:1rem 0 .5rem}
.entete-sc{color:var(--gris);font-size:.72rem;letter-spacing:.14em;text-transform:uppercase}
.note{color:var(--gris);font-size:.82rem;margin:.2rem 0 .8rem}
#chrono{color:var(--teal);font-variant-numeric:tabular-nums;margin:0 0 .8rem}
.ok{color:#5fd39a}.ko{color:var(--rouge)}
.corr{margin:.8rem 0;padding:.8rem 1rem;border-left:3px solid var(--rouge);background:rgba(255,255,255,.04)}
.corr b{display:block;margin-bottom:.2rem}
ol.seq{padding-left:1.4rem}
</style>
</head>
<body>
<div class="entete"><a href="/">← Sailing More</a></div>
<main class="page">
<h1>Simulateur d'examen nautique</h1><div class="filet"></div>
<p id="chrono" aria-live="polite"></p>
<div id="zone"></div>
<p class="note">Entraînement indicatif : questions rédigées par Sailing More, hors sujets officiels. Ne remplace ni une formation ni l'examen.</p>
</main>
<script type="application/json" id="donnees">__DONNEES__</script>
<script>__MOTEUR__</script>
</body>
</html>
"""


def charger():
    return [json.loads(p.read_text(encoding="utf-8")) for p in sorted(DONNEES.glob("*.json"))]


def controle_donnees(exs):
    err = []
    if not any(e["id"] == "src" for e in exs):
        err.append("examen SRC absent")
    for e in exs:
        for c in ("id", "titre", "duree_min", "seuil_pct", "matieres"):
            if c not in e:
                err.append(f"{e.get('id')}: champ {c} manquant")
        for m in e.get("matieres", []):
            if m["type"] not in ("qcm", "ordre"):
                err.append(f"{e['id']}/{m['id']}: type invalide")
            src_m = m.get("source")
            if m["questions"] and not (src_m and src_m.get("ref") and src_m.get("version")):
                err.append(f"{e['id']}/{m['id']}: questions sans source officielle (ref + version)")
            for q in m["questions"]:
                if q.get("langue") not in ("fr", "en", "de", "it"):
                    err.append(f"{e['id']}/{m['id']}: langue de question manquante : {q['q'][:40]}")
                if m["type"] == "qcm" and not (len(q["choix"]) >= 2 and 0 <= q["bonne"] < len(q["choix"])):
                    err.append(f"{e['id']}/{m['id']}: bonne réponse hors choix : {q['q'][:40]}")
                if m["type"] == "ordre" and len(q["etapes"]) < 2:
                    err.append(f"{e['id']}/{m['id']}: ordre trop court")
                if not q.get("expl"):
                    err.append(f"{e['id']}/{m['id']}: explication manquante")
    src = next((e for e in exs if e["id"] == "src"), None)
    if src:
        ids = {m["id"] for m in src["matieres"]}
        for need in ("reglementation", "procedures", "pratique", "oral"):
            if need not in ids:
                err.append(f"src: matière {need} absente")
        if "IC-M330" not in src.get("materiel", ""):
            err.append("src: matériel IC-M330 absent")
    return err


def construire(exs):
    donnees = json.dumps(exs, ensure_ascii=False).replace("</", "<\\/")
    return (GABARIT.replace("__URL__", URL).replace("__DONNEES__", donnees)
            .replace("__MOTEUR__", MOTEUR))


def verifier():
    exs = charger()
    err = controle_donnees(exs)
    for e in exs:
        tot = sum(len(m["questions"]) for m in e["matieres"])
        print(f"{e['id']} : {tot} questions" + ("  [EN PRÉPARATION]" if not tot else ""))
        for m in e["matieres"]:
            k = len(m["questions"])
            print(f"    {m['id']:<20} {k:>3}" + ("   <- 0 question : matière en préparation, non publiée" if not k else ""))
            if m.get("ouverte") and not k:
                err.append(f"{e['id']}/{m['id']}: matière ouverte avec 0 question")
    html = construire(exs)
    if not SORTIE.exists():
        err.append("page non générée")
    elif SORTIE.read_text(encoding="utf-8") != html:
        err.append("page périmée : relancer sans --verifier")
    for marque in ("chrono", "donnees", "Score :", "acquis"):
        if marque not in html:
            err.append(f"page sans « {marque} »")
    if shutil.which("node"):
        js = DONNEES.parent / ".moteur-test.js"
        js.write_text(MOTEUR, encoding="utf-8")
        r = subprocess.run(["node", "--check", str(js)], capture_output=True, text=True)
        js.unlink()
        if r.returncode:
            err.append("JS invalide : " + r.stderr[:200])
    else:
        print("avertissement : node absent, JS non vérifié syntaxiquement")
    if err:
        print("ÉCHEC\n- " + "\n- ".join(err))
        return 1
    n = sum(len(m["questions"]) for e in exs for m in e["matieres"])
    print(f"OK : {len(exs)} examens, {n} questions, page {SORTIE.name} à jour")
    return 0


if __name__ == "__main__":
    if "--verifier" in sys.argv:
        sys.exit(verifier())
    SORTIE.write_text(construire(charger()), encoding="utf-8")
    print("écrit", SORTIE)
