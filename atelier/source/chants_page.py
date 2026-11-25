#!/usr/bin/env python3
"""Page `chants-de-marin.html` : six chants de marins, paroles du domaine public, un enregistrement libre.

Publiée le 24/11/2026 d'après la maquette validée par Nicolas le 23/11/2026
(`maquettes/chants-de-marin-v2.html`). Même chemin que les autres pages : ce module est la source
unique, `accueil_site.sortir_le_site` l'appelle, la barre du site (nom, menu, langues) est posée par
`poser_entete_partout` — la page n'a donc NI son propre en-tête NI son propre sélecteur de langue.

Entrée  : `projets/sailingmore/chants-de-marin.json` (textes d'interface en six langues, six fiches).
Sortie  : `site/chants-de-marin.html` et son entrée dans `site/sitemap.xml`.

Décisions de Nicolas, tenues ici et contrôlées par `verifier()` :
  · six fiches, quatre lecteurs audio (Wikimedia Commons, lien direct, jamais réhébergé) ;
  · les chants ne se traduisent JAMAIS : titre et paroles restent dans la langue d'origine, seuls
    le résumé et l'interface changent de langue ; la mention « jamais traduites » est affichée ;
  · année de création approximative, toujours accompagnée de « date approximative » ;
  · Santiano : l'histoire, jamais le texte (paroles françaises de 1961 protégées jusqu'en 2057) ;
  · breton : la page n'a pas de bloc `bzh` (voir `site_blocks.PAGES_BZH`) ; choisi, le breton laisse le
    français et la barre pose l'encart « pas encore traduit ». `hreflang="br"` ne sort que le jour où
    la page entre dans `PAGES_BZH` ;
  · un emplacement vidéo par chant, vide : la chaîne @SailingMore n'a rien publié pour l'instant.
    Rempli (`video` dans le JSON), il affiche le lecteur et déclenche un `VideoObject`.

    python3 scripts/chants_page.py --verifier   # contrôle les données, n'écrit rien
    python3 scripts/chants_page.py --ecrire     # écrit la page et le sitemap
"""
from __future__ import annotations

import html as H
import json
import os
import re
import sys
from datetime import date
from pathlib import Path

ICI = Path(os.environ.get("SAILINGMORE_RACINE", "/opt/data"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

DONNEES = ICI / "projets/sailingmore/chants-de-marin.json"
SITE = ICI / "projets/sailingmore/site"
URL = "https://sailingmore.fr"
PAGE = "chants-de-marin.html"
from site_blocks import LANGUES as _LANGUES_SITE  # noqa: E402  (une seule liste pour toutes les pages)
LANGUES = tuple(_LANGUES_SITE)

NB_FICHES_MIN = 6   # plancher ; le compte réel est celui du JSON (chaque chant doit citer sa source)
ANNEES = {"haul": "~1840", "wellerman": "~1865", "merck": "1622–1626", "lurrighan": "≤1900",
          "trimartolod": "~1800", "santiano": "~1850"}   # les six d'origine ; les autres portent « ≤ année du livre »
FAMILLES = ("hisser", "virer", "pompe", "festif", "melancolique")   # ordre des groupes et du sommaire
CLES_UI = ("titrePage", "chapo", "chercher", "famille", "tous", "hisser", "virer", "pompe", "festif", "melancolique",
           "compte", "comptes", "paroles", "ecouter", "accords", "tonalite", "dp", "pro", "aucun", "faqT",
           "cockpit", "quitter", "pied", "note", "video", "lic", "an", "faq", "sommaire", "srcLib")

CSS = """
:root{--panneau:#0f2438;--ivoire:#eef3f7;--gris:#9db2c6;--rouge:#e23a3e}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{margin:0;background:#071c31;color:var(--ivoire);font-family:ui-sans-serif,system-ui,-apple-system,"Helvetica Neue",Arial,sans-serif;line-height:1.6;-webkit-font-smoothing:antialiased}
.page{max-width:64rem;margin:0 auto;padding:2.4rem 1.4rem 5rem}
h1{font-size:clamp(1.9rem,6vw,2.7rem);line-height:1.04;margin:1.5rem 0 0;letter-spacing:-.01em;color:#fff;font-weight:300;text-transform:uppercase}
h1::after{content:"";display:block;width:3.4rem;height:3px;background:var(--rouge);margin:1.3rem 0 1.6rem}
.chapo{color:var(--gris);font-size:.95rem;max-width:34rem;margin:0 0 .8rem}
.chapo.note{font-size:.8rem;color:#6f8598;margin:0 0 2rem}
.page a{color:#fff;text-decoration:none}
:focus-visible{outline:2px solid #fff;outline-offset:2px}
.panneau{background:#0a1f33;border:1px solid rgba(255,255,255,.09);border-radius:2px;padding:0 1.2rem 1.2rem;margin:0 0 1rem;box-shadow:0 18px 50px rgba(0,0,0,.35)}
.barre{position:sticky;top:2.9rem;z-index:20;background:#0a1f33;padding:.9rem 1.2rem 1rem;margin:0 -1.2rem .4rem}
.champ{display:flex;align-items:center;gap:.6rem;background:var(--panneau);border:1px solid rgba(255,255,255,.13);border-radius:3px;padding:.62rem .8rem}
.champ:focus-within{border-color:rgba(226,58,62,.7)}
.champ input{flex:1;background:none;border:0;color:var(--ivoire);font-size:.95rem;outline:none;font-family:inherit;min-width:0}
.champ input::placeholder{color:#6f8598}
.filtres{display:flex;flex-wrap:wrap;gap:.35rem;align-items:center;margin-top:.7rem}
.etiq{font-size:.58rem;letter-spacing:.18em;text-transform:uppercase;color:#6f8598;margin-right:.2rem}
.puce{font:inherit;font-size:.72rem;letter-spacing:.04em;color:var(--gris);background:none;border:1px solid rgba(255,255,255,.16);border-radius:2px;padding:.28rem .6rem;cursor:pointer}
.puce:hover{color:#fff;border-color:rgba(255,255,255,.4)}
.puce[aria-pressed="true"]{color:#fff;border-color:var(--rouge);background:rgba(226,58,62,.14)}
.compte{font-size:.68rem;color:#6f8598;margin-left:auto;letter-spacing:.06em}
.fiche{border-top:1px solid rgba(255,255,255,.09);padding:1.05rem .2rem 1.35rem;display:grid;gap:1rem;grid-template-columns:1.5fr 1fr}
.fiche:first-of-type{border-top:0}
.sommaire{display:flex;flex-wrap:wrap;gap:.4rem;align-items:center;margin:0 0 1rem}
.sommaire a{border:1px solid rgba(255,255,255,.18);padding:.35rem .7rem;font-size:.78rem;color:#fff}
.sommaire a b{color:var(--gris);font-weight:400;margin-left:.3rem}
.groupe{scroll-margin-top:7rem}
.gt{margin:1.6rem 0 .2rem;font-size:.82rem;letter-spacing:.18em;text-transform:uppercase;color:var(--gris);font-weight:600;border-bottom:2px solid var(--rouge);padding-bottom:.4rem}
.gt span{color:#6f8598;font-weight:400;margin-left:.4rem}
@media(max-width:52rem){.fiche{grid-template-columns:1fr}}
.entete-f{display:flex;justify-content:space-between;align-items:flex-start;gap:.8rem;flex-wrap:wrap}
.titre{margin:0;font-size:1.08rem;color:#fff;font-weight:400}
.annee{font-size:.82rem;color:var(--gris);margin:.15rem 0 .55rem}.annee b{color:#eaf2fa;font-weight:600}.annee em{font-style:normal;opacity:.65;font-size:.92em}
.fam{display:block;font-size:.58rem;letter-spacing:.16em;text-transform:uppercase;color:#6f8598;margin-top:.28rem;font-weight:400}
.badges{display:flex;gap:.35rem;flex-wrap:wrap}
.badge{font-size:.56rem;letter-spacing:.12em;text-transform:uppercase;padding:.18rem .44rem;border-radius:2px;border:1px solid rgba(255,255,255,.18);color:var(--gris);white-space:nowrap}
.badge.dp{border-color:rgba(120,190,150,.45);color:#8fd6b0}
.badge.pro{border-color:rgba(226,58,62,.5);color:#f08a8c}
.badge.lng{color:#a9d3ff;border-color:rgba(169,211,255,.3)}
.fiche h3{margin:.9rem 0 .35rem;font-size:.58rem;letter-spacing:.18em;text-transform:uppercase;color:#6f8598;font-weight:600}
.txt{margin:.6rem 0 0;font-size:.92rem;color:#cfdae4}
.paroles{white-space:pre-line;font-size:.88rem;color:#e3ebf2;border-left:2px solid rgba(226,58,62,.6);padding-left:.9rem;line-height:1.75;margin:0}
.acords{font-family:ui-monospace,Menlo,monospace;font-size:.84rem;color:#a9d3ff;background:rgba(255,255,255,.04);padding:.6rem .7rem;border-radius:2px;white-space:pre-line;margin:0 0 .4rem}
.transp{display:flex;align-items:center;gap:.4rem}
.transp span{font-size:.58rem;letter-spacing:.12em;text-transform:uppercase;color:#6f8598}
.transp button{width:1.6rem;height:1.6rem;background:none;border:1px solid rgba(255,255,255,.18);color:var(--ivoire);border-radius:2px;cursor:pointer;font:inherit;line-height:1}
.transp button:hover{border-color:var(--rouge)}
.lecteur{background:var(--panneau);border:1px solid rgba(255,255,255,.12);border-radius:3px;padding:.6rem .7rem;display:flex;align-items:center;gap:.7rem}
.lecteur button.play{flex:none;width:2.1rem;height:2.1rem;border-radius:50%;border:0;background:var(--rouge);color:#fff;font-size:.72rem;cursor:pointer;display:grid;place-items:center;line-height:1;padding:0}
.lecteur button.play:hover{background:#f04a4e}
.lecteur .rail{flex:1;min-width:0;display:flex;flex-direction:column;gap:.28rem}
.lecteur .barre-t{height:3px;background:rgba(255,255,255,.16);border-radius:2px;cursor:pointer;position:relative}
.lecteur .barre-t i{position:absolute;left:0;top:0;bottom:0;width:0;background:var(--rouge);border-radius:2px}
.lecteur .ligne{display:flex;justify-content:space-between;gap:.5rem;font-size:.62rem;color:#6f8598;letter-spacing:.04em}
.lecteur .nom{color:#cfdae4;font-size:.66rem;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.src{font-size:.66rem;color:#6f8598;line-height:1.5;margin:.5rem 0 0}
.son-lien{display:flex;justify-content:space-between;gap:.6rem;border:1px solid rgba(255,255,255,.14);border-radius:2px;padding:.5rem .7rem;font-size:.78rem;color:var(--ivoire);margin-top:.45rem}
.son-lien:hover{border-color:rgba(226,58,62,.7)}
.son-lien em{font-style:normal;color:#6f8598;font-size:.66rem}
.vide{font-size:.8rem;color:#6f8598;font-style:italic;margin:0}
.emplacement-video:empty{display:none}
.emplacement-video iframe{width:100%;aspect-ratio:16/9;border:0;margin-top:.6rem;background:#000}
.section{margin:3rem 0 0}
h2.sec{font-size:1.15rem;font-weight:400;color:#fff;margin:0 0 1rem;text-transform:uppercase;letter-spacing:.06em}
.faq details{border-top:1px solid rgba(255,255,255,.09);padding:.9rem 0}
.faq p{margin:.3rem 0 0;color:#cfdae4;font-size:.9rem;max-width:44rem}
.faq summary{cursor:pointer;font-size:.94rem;color:#fff;list-style:none}
.faq summary::-webkit-details-marker{display:none}
.faq summary::before{content:"› ";color:var(--rouge)}
.pied{margin-top:3.4rem;padding-top:1.2rem;border-top:1px solid rgba(255,255,255,.09);color:#6f8598;font-size:.7rem}
.cockpit{position:fixed;right:1rem;bottom:1rem;z-index:40;background:var(--rouge);color:#fff;border:0;border-radius:2px;padding:.7rem .95rem;font-size:.64rem;letter-spacing:.14em;text-transform:uppercase;cursor:pointer;box-shadow:0 12px 30px rgba(0,0,0,.45)}
body.cockpit-on .page{max-width:44rem}
body.cockpit-on .barre,body.cockpit-on .chapo,body.cockpit-on .section,body.cockpit-on .pied{display:none}
body.cockpit-on .fiche>div:last-child{display:none}
body.cockpit-on .fiche>div:first-child{max-width:38rem;margin:0 auto}
body.cockpit-on .fiche{grid-template-columns:1fr}
body.cockpit-on .fiche:not(.actif){display:none}
body.cockpit-on .titre{font-size:1.4rem}
body.cockpit-on .paroles{font-size:1.2rem;line-height:2}
"""

# Le script de la page : même rendu que `fiche_html` (la version française est déjà dans le HTML, pour qu'aucune
# page ne soit blanche sans JavaScript ni pour un moteur de recherche). La langue vient de `?lang=`, puis de la
# barre du site (`localStorage` « sm-langue », boutons cachés `#langues button[data-lang]`), puis du navigateur.
JS = r"""
(function(){
var D=JSON.parse(document.getElementById('chants-donnees').textContent),SIX=D.langues,L='fr',fam='tous',T=D.ui.fr,FAM=['hisser','virer','pompe','festif','melancolique'];
function choisir(){
  try{var q=new URLSearchParams(location.search).get('lang');if(q&&SIX.indexOf(q)>=0)return q}catch(e){}
  var v='auto';try{v=localStorage.getItem('sm-langue')||'auto'}catch(e){}
  if(v!=='auto')return SIX.indexOf(v)>=0?v:'fr';
  var p=navigator.languages||[navigator.language||'en'];
  for(var i=0;i<p.length;i++){var b=String(p[i]).toLowerCase().slice(0,2);if(b==='br')return 'fr';if(SIX.indexOf(b)>=0)return b}
  return 'en'}
function pick(o){return (o&&(o[L]||o.en||o.fr))||''}
function esc(s){return String(s).replace(/[&<>"]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]})}
function fmt(s){if(!isFinite(s))return '–:––';var m=Math.floor(s/60),x=Math.floor(s%60);return m+':'+(x<10?'0':'')+x}
function anneeTxt(v,n){if(!v)return '—';if(v.charAt(0)==='~')return n.p+v.slice(1);if(v.charAt(0)==='≤')return n.b+v.slice(1);return v}
function noteAudio(a){var t=T.lic,corps=a.lic.indexOf('domaine public')===0?t.p:t.l.replace('{l}',a.lic);
  return (a.complet?t.c:t.x).replace('{d}',a.duree)+' · '+corps}
var lecteurs=[];
function stopper(){lecteurs.forEach(function(a){try{a.pause();a.removeAttribute('src');a.load()}catch(e){}});lecteurs=[]}
function fiche(c){
  var nom=(D.langueNoms[L]||D.langueNoms.fr)[c.lg]||c.lg;
  var son=c.audio?'<div class="lecteur" data-src="'+esc(c.audio.src)+'"><button class="play" aria-label="'+esc(T.ecouter)+'">▶</button><div class="rail"><span class="nom">'+esc(c.audio.nom)+'</span><div class="barre-t"><i></i></div><div class="ligne"><span class="t">0:00</span><span class="d">–:––</span></div></div></div><p class="src">'+esc(c.audio.lic)+'</p>':'<p class="vide">'+esc(T.aucun)+'</p>';
  var liens=(c.liens||[]).map(function(a){return '<a class="son-lien" href="'+esc(a.u)+'" target="_blank" rel="noopener">'+esc(a.t)+'<em>↗</em></a>'}).join('');
  var paroles=c.paroles?'<h3>'+esc(T.paroles)+'</h3><div class="paroles" lang="'+esc(c.lg)+'">'+esc(c.paroles)+'</div><p class="src">'+esc(T.note)+'</p>':'';
  var accords=c.accords?'<h3>'+esc(T.accords)+'</h3><div class="acords" data-acc>'+esc(c.accords)+'</div><div class="transp"><span>'+esc(T.tonalite)+'</span><button data-t="-1" aria-label="-1">−</button><button data-t="1" aria-label="+1">+</button></div>':'';
  var vid=c.video&&c.video.id?'<h3>'+esc(T.video)+'</h3><iframe loading="lazy" src="https://www.youtube-nocookie.com/embed/'+esc(c.video.id)+'" title="'+esc(c.video.titre||c.titre)+'" allowfullscreen></iframe>':'';
  return '<article class="fiche" data-fam="'+c.type+'" data-id="'+c.id+'"><div><div class="entete-f"><h2 class="titre" lang="'+esc(c.lg)+'">'+esc(c.titre)+'<span class="fam">'+esc(T[c.type])+' · '+esc(nom)+'</span></h2>'+
    '<div class="badges"><span class="badge '+(c.prot?'pro':'dp')+'">'+esc(c.prot?T.pro:T.dp)+'</span><span class="badge lng">'+esc(c.lg)+'</span></div></div>'+
    '<p class="annee">'+esc(T.an.l)+' : <b>'+esc(anneeTxt(c.annees,T.an))+'</b><em> · '+esc(T.an.a)+'</em></p>'+
    '<p class="txt">'+esc(pick(c.resume))+'</p>'+paroles+(c.source?'<p class="src">'+esc(T.srcLib)+' : '+esc(c.source)+'</p>':'')+'</div>'+
    '<div><h3>'+esc(T.ecouter)+'</h3>'+son+liens+accords+(c.audio?'<p class="src">'+esc(noteAudio(c.audio))+'</p>':'')+'<div class="emplacement-video" data-chant="'+c.id+'">'+vid+'</div></div></article>'}
function rendre(){
  L=choisir();T=D.ui[L]||D.ui.fr;stopper();
  document.documentElement.lang=L;
  var ck=document.getElementById('ck');
  document.getElementById('h1').textContent=T.titrePage;
  document.getElementById('chapo').textContent=T.chapo;
  document.getElementById('note').textContent=T.note;
  document.getElementById('q').placeholder=T.chercher;
  ck.textContent=document.body.classList.contains('cockpit-on')?T.quitter:T.cockpit;
  document.getElementById('pied-r').textContent=T.pied;
  document.getElementById('faq-t').textContent=T.faqT;
  document.getElementById('filtres').innerHTML='<span class="etiq">'+esc(T.famille)+'</span>'+
    ['tous'].concat(FAM).map(function(f){return '<button class="puce" data-f="'+f+'" aria-pressed="'+(f===fam)+'">'+esc(T[f])+'</button>'}).join('')+'<span class="compte" id="compte"></span>';
  document.getElementById('faq').innerHTML=T.faq.map(function(q){return '<details><summary>'+esc(q[0])+'</summary><p>'+esc(q[1])+'</p></details>'}).join('');
  var gr=FAM.map(function(f){return D.chants.filter(function(c){return c.type===f})}),som=[];
  document.getElementById('liste').innerHTML=FAM.map(function(f,i){if(!gr[i].length)return '';
    som.push('<a href="#g-'+f+'">'+esc(T[f])+' <b>'+gr[i].length+'</b></a>');
    return '<section class="groupe" data-g="'+f+'" id="g-'+f+'"><h2 class="gt">'+esc(T[f])+' <span>'+gr[i].length+'</span></h2>'+gr[i].map(fiche).join('')+'</section>'}).join('');
  document.getElementById('sommaire').innerHTML='<span class="etiq">'+esc(T.sommaire)+'</span>'+som.join('');
  filtre();cabler()}
function filtre(){
  var t=(document.getElementById('q').value||'').toLowerCase(),n=0;
  document.querySelectorAll('.fiche').forEach(function(f){
    var ok=(fam==='tous'||f.dataset.fam===fam)&&(!t||f.textContent.toLowerCase().indexOf(t)>-1);
    f.style.display=ok?'':'none';if(ok)n++});
  document.querySelectorAll('.groupe').forEach(function(g){var v=g.querySelector('.fiche:not([style*="none"])');g.style.display=v?'':'none'});
  document.getElementById('compte').textContent=n+' '+(n>1?T.comptes:T.compte)}
function cabler(){
  var noms=['C','C#','D','D#','E','F','F#','G','G#','A','A#','B'];
  document.querySelectorAll('[data-acc]').forEach(function(b){b.dataset.base=b.textContent;b.dataset.ton=0});
  document.querySelectorAll('.transp button').forEach(function(b){
    b.onclick=function(e){e.preventDefault();
      var bloc=b.parentNode.parentNode.querySelector('[data-acc]');
      bloc.dataset.ton=(+bloc.dataset.ton||0)+(+b.dataset.t);
      var n=((+bloc.dataset.ton)%12+12)%12;
      bloc.textContent=bloc.dataset.base.replace(/\b([A-G])(#)?(m|7|maj7|sus4)?\b/g,function(tout,l,dies,s){
        var i=noms.indexOf(l+(dies||''));if(i<0)return tout;return noms[(i+n)%12]+(s||'')});
      b.blur()}});
  document.querySelectorAll('.lecteur').forEach(function(p){
    var au=new Audio(),btn=p.querySelector('.play'),jauge=p.querySelector('.barre-t i'),
        cur=p.querySelector('.t'),dur=p.querySelector('.d'),rail=p.querySelector('.barre-t');
    au.preload='none';au.src=p.dataset.src;lecteurs.push(au);
    btn.onclick=function(){
      if(au.paused){lecteurs.forEach(function(a){if(a!==au)a.pause()});
        var r=au.play();if(r&&r.catch)r.catch(function(){btn.textContent='!'})}
      else au.pause()};
    au.onplay=function(){btn.textContent='❚❚'};
    au.onpause=function(){btn.textContent='▶'};
    au.onloadedmetadata=function(){dur.textContent=fmt(au.duration)};
    au.ontimeupdate=function(){jauge.style.width=(au.currentTime/au.duration*100||0)+'%';cur.textContent=fmt(au.currentTime)};
    rail.onclick=function(e){if(!isFinite(au.duration))return;var r=rail.getBoundingClientRect();
      au.currentTime=(e.clientX-r.left)/r.width*au.duration}})}
document.getElementById('q').addEventListener('input',filtre);
document.getElementById('filtres').addEventListener('click',function(e){
  var p=e.target.closest('.puce');if(!p)return;
  document.querySelectorAll('.puce').forEach(function(x){x.setAttribute('aria-pressed',x===p?'true':'false')});
  fam=p.dataset.f;filtre()});
/* La barre du site pose ses boutons de langue après coup : on écoute au niveau du document. */
document.addEventListener('click',function(e){
  var b=e.target.closest&&e.target.closest('#langues button[data-lang]');if(!b)return;
  var v=b.getAttribute('data-lang');try{localStorage.setItem('sm-langue',v)}catch(_){}
  document.querySelectorAll('#langues button[data-lang]').forEach(function(x){x.setAttribute('aria-pressed',x===b?'true':'false')});
  rendre()});
document.getElementById('ck').addEventListener('click',function(){
  var on=document.body.classList.toggle('cockpit-on');this.textContent=on?T.quitter:T.cockpit;
  if(on){var v=document.querySelector('.fiche:not([style*="none"])');document.querySelectorAll('.fiche').forEach(function(f){f.classList.toggle('actif',f===v)})}});
rendre();
})();
"""


# --------------------------------------------------------------------------- données

def charger() -> dict:
    return json.loads(DONNEES.read_text(encoding="utf-8"))


def verifier(d: dict) -> list[str]:
    """Les décisions de Nicolas, une par une. Un écart = la page n'est pas écrite."""
    pb = []
    ui, chants = d.get("ui", {}), d.get("chants", [])
    if len(chants) < NB_FICHES_MIN:
        pb.append(f"{len(chants)} fiche(s), moins que le plancher {NB_FICHES_MIN}")
    ids = [c.get("id") for c in chants]
    if len(set(ids)) != len(ids):
        pb.append("identifiants en double")
    for l in LANGUES:
        if l not in ui:
            pb.append(f"interface absente en {l}")
            continue
        manque = [k for k in CLES_UI if k not in ui[l]]
        if manque:
            pb.append(f"interface {l} : clé(s) absente(s) {', '.join(manque)}")
    if "bzh" in ui:
        pb.append("bloc `bzh` interdit : jamais de breton produit par un modèle")
    for c in chants:
        i = c.get("id", "?")
        if i in ANNEES and ANNEES[i] != c.get("annees"):
            pb.append(f"{i} : année {c.get('annees')!r} au lieu de {ANNEES.get(i)!r}")
        elif not c.get("annees"):
            pb.append(f"{i} : année manquante")
        if c.get("type") not in FAMILLES:
            pb.append(f"{i} : famille inconnue {c.get('type')!r}")
        if not str(c.get("source", "")).strip():
            pb.append(f"{i} : champ `source` manquant (livre et page, ou URL)")
        if c.get("paroles") and i not in ANNEES and not c.get("livre"):
            pb.append(f"{i} : paroles sans livre d'origine")
        if not isinstance(c.get("resume"), dict) or not all(c["resume"].get(l) for l in ("fr", "en")):
            pb.append(f"{i} : résumé fr/en manquant")
        if isinstance(c.get("titre"), dict):
            pb.append(f"{i} : le titre ne se traduit pas")
        a = c.get("audio")
        if a and not str(a.get("src", "")).startswith("https://upload.wikimedia.org/"):
            pb.append(f"{i} : audio hors Wikimedia Commons (jamais réhéberger)")
        if "video" not in c:
            pb.append(f"{i} : emplacement `video` absent")
    santiano = [c for c in chants if c.get("id") == "santiano"]
    if santiano and (santiano[0].get("paroles") or santiano[0].get("accords")):
        pb.append("santiano : texte protégé jusqu'en 2057, jamais publié")
    return pb


# --------------------------------------------------------------------------- page

def _annee(v: str, n: dict) -> str:
    if v.startswith("~"):
        return n["p"] + v[1:]
    if v.startswith("≤"):
        return n["b"] + v[1:]
    return v


def _note_audio(a: dict, T: dict) -> str:
    t = T["lic"]
    corps = t["p"] if a["lic"].startswith("domaine public") else t["l"].replace("{l}", a["lic"])
    return (t["c"] if a.get("complet") else t["x"]).replace("{d}", a["duree"]) + " · " + corps


def fiche_html(c: dict, d: dict, L: str = "fr") -> str:
    """La fiche en français, écrite dans la page : même balisage que `fiche()` du script."""
    e = lambda s: H.escape(str(s), quote=True)  # noqa: E731
    T = d["ui"][L]
    nom = d["langueNoms"][L].get(c["lg"], c["lg"])
    if c.get("audio"):
        a = c["audio"]
        son = (f'<div class="lecteur" data-src="{e(a["src"])}"><button class="play" aria-label="{e(T["ecouter"])}">▶</button>'
               f'<div class="rail"><span class="nom">{e(a["nom"])}</span><div class="barre-t"><i></i></div>'
               '<div class="ligne"><span class="t">0:00</span><span class="d">–:––</span></div></div></div>'
               f'<p class="src">{e(a["lic"])}</p>')
    else:
        son = f'<p class="vide">{e(T["aucun"])}</p>'
    liens = "".join(f'<a class="son-lien" href="{e(x["u"])}" target="_blank" rel="noopener">{e(x["t"])}<em>↗</em></a>'
                    for x in c.get("liens") or [])
    paroles = (f'<h3>{e(T["paroles"])}</h3><div class="paroles" lang="{e(c["lg"])}">{e(c["paroles"])}</div>'
               f'<p class="src">{e(T["note"])}</p>') if c.get("paroles") else ""
    accords = (f'<h3>{e(T["accords"])}</h3><div class="acords" data-acc>{e(c["accords"])}</div>'
               f'<div class="transp"><span>{e(T["tonalite"])}</span><button data-t="-1" aria-label="-1">−</button>'
               '<button data-t="1" aria-label="+1">+</button></div>') if c.get("accords") else ""
    v = c.get("video") or {}
    vid = (f'<h3>{e(T["video"])}</h3><iframe loading="lazy" src="https://www.youtube-nocookie.com/embed/{e(v["id"])}" '
           f'title="{e(v.get("titre") or c["titre"])}" allowfullscreen></iframe>') if v.get("id") else ""
    badge = "pro" if c.get("prot") else "dp"
    return (f'<article class="fiche" data-fam="{c["type"]}" data-id="{c["id"]}"><div><div class="entete-f">'
            f'<h2 class="titre" lang="{e(c["lg"])}">{e(c["titre"])}<span class="fam">{e(T[c["type"]])} · {e(nom)}</span></h2>'
            f'<div class="badges"><span class="badge {badge}">{e(T[badge])}</span><span class="badge lng">{e(c["lg"])}</span></div></div>'
            f'<p class="annee">{e(T["an"]["l"])} : <b>{e(_annee(c["annees"], T["an"]))}</b><em> · {e(T["an"]["a"])}</em></p>'
            f'<p class="txt">{e(c["resume"].get(L) or c["resume"]["fr"])}</p>{paroles}'
            + (f'<p class="src">{e(T["srcLib"])} : {e(c["source"])}</p>' if c.get("source") else "") + '</div>'
            f'<div><h3>{e(T["ecouter"])}</h3>{son}{liens}{accords}'
            + (f'<p class="src">{e(_note_audio(c["audio"], T))}</p>' if c.get("audio") else "")
            + f'<div class="emplacement-video" data-chant="{c["id"]}">{vid}</div></div></article>')


def _noeuds_jsonld(d: dict) -> list[dict]:
    """Un seul bloc JSON-LD (règle de `jsonld.py`) : fil d'Ariane, liste des six chants, FAQ, vidéos publiées."""
    import jsonld
    fr = d["ui"]["fr"]
    elements, videos = [], []
    for i, c in enumerate(d["chants"], 1):
        oeuvre = {"@type": "MusicComposition", "name": c["titre"],
                  "inLanguage": "br" if c["lg"] == "br" else c["lg"], "description": c["resume"]["fr"]}
        if c.get("audio"):
            a = c["audio"]
            oeuvre["audio"] = {"@type": "AudioObject", "name": a["nom"], "contentUrl": a["src"],
                               "encodingFormat": "audio/wav" if a["src"].endswith(".wav") else "audio/ogg"}
        elements.append({"@type": "ListItem", "position": i, "item": oeuvre})
        v = c.get("video") or {}
        if v.get("id") and v.get("date_mise_en_ligne"):
            videos.append({"@type": "VideoObject", "name": v.get("titre") or c["titre"],
                           "description": c["resume"]["fr"], "uploadDate": v["date_mise_en_ligne"],
                           "thumbnailUrl": f"https://i.ytimg.com/vi/{v['id']}/hqdefault.jpg",
                           "embedUrl": f"https://www.youtube-nocookie.com/embed/{v['id']}",
                           **({"duration": v["duree_iso"]} if v.get("duree_iso") else {})})
    faq = {"@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": r}} for q, r in fr["faq"]]}
    return [jsonld.fil(PAGE, fr["titrePage"]),
            {"@type": "ItemList", "name": fr["titrePage"], "numberOfItems": len(elements),
             "itemListElement": elements}, faq, *videos]


def construire(d: dict) -> str:
    import jsonld
    import site_blocks
    fr = d["ui"]["fr"]
    description = (f"{len(d['chants'])} chants de marins : ce qu'ils faisaient à bord, les paroles du domaine public "
                   "dans leur langue d'origine, chacune adossée à un livre cité (Terry, Whall, Smith).")
    donnees = {"langues": list(LANGUES), "ui": {l: d["ui"][l] for l in LANGUES},
               "langueNoms": d["langueNoms"], "chants": d["chants"]}
    brut = json.dumps(donnees, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    # hreflang : six langues + x-default ; `br` seulement quand la page est traduite et relue (PAGES_BZH).
    alternates = f'<link rel="alternate" hreflang="fr" href="{URL}/{PAGE}">' + "".join(
        f'<link rel="alternate" hreflang="{l}" href="{URL}/{PAGE}?lang={l}">' for l in LANGUES if l != "fr")
    alternates += site_blocks.hreflang_bzh(PAGE, URL + "/") + f'<link rel="alternate" hreflang="x-default" href="{URL}/{PAGE}">'
    n = len(d["chants"])
    tete = ('<!doctype html><html lang="fr"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<title>{H.escape(fr["titrePage"])} — Sailing More</title>'
            f'<meta name="description" content="{H.escape(description, quote=True)}">'
            f'<link rel="canonical" href="{URL}/{PAGE}">{alternates}'
            + jsonld.bloc(*_noeuds_jsonld(d))
            + jsonld.social(PAGE, f'{fr["titrePage"]} — Sailing More', description))
    corps = (f"<style>{CSS}</style></head><body><main class=\"page\">"
             f'<h1 id="h1">{H.escape(fr["titrePage"])}</h1>'
             f'<p class="chapo" id="chapo">{H.escape(fr["chapo"])}</p>'
             f'<p class="chapo note" id="note">{H.escape(fr["note"])}</p>'
             '<div class="panneau"><div class="barre"><div class="champ">'
             '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#9db2c6" stroke-width="2" aria-hidden="true">'
             '<circle cx="11" cy="11" r="7"/><path d="M20 20l-3.5-3.5"/></svg>'
             f'<input id="q" type="search" aria-label="{H.escape(fr["chercher"], quote=True)}" placeholder="{H.escape(fr["chercher"], quote=True)}"></div>'
             f'<div class="filtres" id="filtres"><span class="etiq">{H.escape(fr["famille"])}</span>'
             + "".join(f'<button class="puce" data-f="{f}" aria-pressed="{"true" if f == "tous" else "false"}">{H.escape(fr[f])}</button>'
                       for f in ("tous",) + FAMILLES)
             + f'<span class="compte" id="compte">{n} {H.escape(fr["comptes"])}</span></div></div>'
             f'<nav class="sommaire" id="sommaire"><span class="etiq">{H.escape(fr["sommaire"])}</span>'
             + "".join(f'<a href="#g-{f}">{H.escape(fr[f])} <b>{sum(1 for c in d["chants"] if c["type"] == f)}</b></a>'
                       for f in FAMILLES if any(c["type"] == f for c in d["chants"]))
             + '</nav>'
             f'<div id="liste">' + "".join(
                 f'<section class="groupe" data-g="{f}" id="g-{f}"><h2 class="gt">{H.escape(fr[f])} '
                 f'<span>{sum(1 for c in d["chants"] if c["type"] == f)}</span></h2>'
                 + "".join(fiche_html(c, d) for c in d["chants"] if c["type"] == f) + "</section>"
                 for f in FAMILLES if any(c["type"] == f for c in d["chants"]))
             + '</div></div>'
             f'<section class="section"><h2 class="sec" id="faq-t">{H.escape(fr["faqT"])}</h2><div class="faq" id="faq">'
             + "".join(f"<details><summary>{H.escape(q)}</summary><p>{H.escape(r)}</p></details>" for q, r in fr["faq"])
             + "</div></section>"
             f'<div class="pied"><span id="pied-r">{H.escape(fr["pied"])}</span></div></main>'
             f'<button class="cockpit" id="ck" type="button">{H.escape(fr["cockpit"])}</button>'
             f'<script type="application/json" id="chants-donnees">{brut}</script>'
             f"<script>{JS}</script></body></html>\n")
    return tete + corps


def maj_sitemap(dossier: Path) -> bool:
    """Ajoute (ou rafraîchit) l'entrée de la page dans sitemap.xml. Idempotent."""
    f = dossier / "sitemap.xml"
    if not f.exists():
        return False
    x = f.read_text(encoding="utf-8")
    x = re.sub(r"\s*<url><loc>https://sailingmore\.fr/chants-de-marin\.html</loc>.*?</url>", "", x, flags=re.S)
    ligne = (f"\n  <url><loc>{URL}/{PAGE}</loc><lastmod>{date.today().isoformat()}</lastmod>"
             "<changefreq>monthly</changefreq><priority>0.7</priority></url>")
    f.write_text(x.replace("</urlset>", ligne + "\n</urlset>", 1), encoding="utf-8")
    return True


def ecrire_page(dossier: Path = SITE) -> str:
    """Écrit la page et l'entrée du sitemap — appelé par `accueil_site.sortir_le_site`. Refuse si les décisions ne tiennent pas."""
    d = charger()
    pb = verifier(d)
    if pb:
        raise SystemExit("chants-de-marin.html non écrite : " + " ; ".join(pb))
    dossier.mkdir(parents=True, exist_ok=True)
    (dossier / PAGE).write_text(construire(d), encoding="utf-8")
    sm = maj_sitemap(dossier)
    return (f"{len(d['chants'])} fiches · {sum(1 for c in d['chants'] if c.get('audio'))} lecteurs · "
            f"{sum(1 for c in d['chants'] if (c.get('video') or {}).get('id'))} vidéo(s) · sitemap {'à jour' if sm else 'absent'}")


def main() -> int:
    if "--verifier" in sys.argv:
        pb = verifier(charger())
        print("\n".join(pb) if pb else "données conformes")
        return 1 if pb else 0
    if "--ecrire" in sys.argv:
        print(f"{PAGE} : {ecrire_page()}")
        return 0
    print("Rien à faire : --verifier (lecture seule) ou --ecrire.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
