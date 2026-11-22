#!/usr/bin/env python3
"""Construit la page `stages.html` : les stages et cours que vendent des écoles de voile européennes,
sur leurs propres eaux comme aux Antilles, en Atlantique ou en mer du Nord.

Entrée  : `projets/sailingmore/stages.json`, écrit par `stages_releve.py` (relevé des fiches des
          écoles ; un prix n'y entre que s'il est publié par l'école sur la fiche du stage).
Sortie  : `projets/sailingmore/site/stages.html` (appelée par `accueil_site.sortir_le_site`).

Ce que la page montre, et pourquoi ces champs-là :
  - la **destination** (pays du stage) et le **pays de l'école** : une école française qui emmène en
    Grèce n'est ni un stage grec, ni un stage français ;
  - la **langue du stage** : l'école l'écrit rarement. Quand elle ne l'écrit pas, la page prend la
    langue du pays de l'école et l'annonce comme telle (`langue_src = "pays"`), sans jamais la
    présenter comme une certitude ;
  - les **filtres se placent d'eux-mêmes** sur la langue et le pays du visiteur (navigateur), et son
    choix, dès qu'il touche un filtre, est retenu (`localStorage`) ;
  - une offre sans prix publié par l'école n'existe pas ici ; une session passée disparaît seule ; un
    relevé de plus de 60 jours n'est plus publié.

NE PAS RÉÉCRIRE CE FICHIER SANS REPRENDRE LE RELEVÉ. Les offres ne se saisissent pas à la main : elles
sont mesurées par `stages_releve.py` (et `stages_moisson.py` pour les catalogues).
"""
from __future__ import annotations

import json
import os
from datetime import date, timedelta
from pathlib import Path

ICI = Path(os.environ.get("SAILINGMORE_RACINE", "/opt/data"))
JSON = ICI / "projets/sailingmore/stages.json"
PEREMPTION_JOURS = 60
NIVEAUX = ("debutant", "intermediaire", "confirme")

UI = {
 "fr": {"titre": "Stages de voile", "retour": "← Sailing More",
        "chapo": "Les stages et cours que vendent des écoles de voile européennes, sur leurs propres eaux comme aux Antilles, en Atlantique ou en mer du Nord. Chaque offre renvoie à la fiche de l'école, qui fait foi.",
        "langue": "Langue du stage", "destination": "Destination", "pays_ecole": "Pays de l'école",
        "ecole": "École", "niveau": "Niveau", "quand": "Date", "prix": "Prix max.",
        "tous": "Toutes", "tout_age": "Tout âge", "avenir": "À venir", "mois": "Ce mois-ci",
        "chercher": "Chercher (école, stage, lieu)", "dates_ecole": "dates chez l'école",
        "compte": "{n} offres · {e} écoles", "aucune": "Aucune offre ne répond à ces filtres.",
        "vide": "Aucune offre n'est publiée pour le moment : le relevé se fait sur les fiches des écoles.",
        "du": "du", "au": "au", "voir": "Voir l'offre →", "jours": "jours", "prix_vide": "prix non publié",
        "type": "Type", "pratique": "Pratique", "theorie": "Théorie",
        "debutant": "Débutant", "intermediaire": "Intermédiaire", "confirme": "Confirmé",
        "langue_supposee": "langue du pays de l'école : l'école ne l'affiche pas",
        "verifie": "vérifié le", "pied": "Relevé sur les fiches des écoles, offre par offre. Une offre sans prix affiché n'est pas reprise ; un stage manque ou un prix a changé ?"},
 "en": {"titre": "Sailing courses and camps", "retour": "← Sailing More",
        "chapo": "Courses and camps sold by European sailing schools, on their own waters and far from them — Antilles, Atlantic, North Sea. Each offer links to the school's own page, which is the authority.",
        "langue": "Course language", "destination": "Destination", "pays_ecole": "School's country",
        "ecole": "School", "niveau": "Level", "quand": "Date", "prix": "Max. price",
        "tous": "All", "tout_age": "Any age", "avenir": "Upcoming", "mois": "This month",
        "chercher": "Search (school, course, place)", "dates_ecole": "dates at the school",
        "compte": "{n} offers · {e} schools", "aucune": "No offer matches these filters.",
        "vide": "No offer is published yet: the list is read from the schools' own pages.",
        "du": "from", "au": "to", "voir": "See the offer →", "jours": "days", "prix_vide": "price not published",
        "type": "Type", "pratique": "Practical", "theorie": "Theory",
        "debutant": "Beginner", "intermediaire": "Intermediate", "confirme": "Advanced",
        "langue_supposee": "school country's language: the school does not state it",
        "verifie": "checked on", "pied": "Read off the schools' own pages, offer by offer. An offer without a published price is not listed; a course missing or a price changed?"},
 "it": {"titre": "Corsi e stage di vela", "retour": "← Sailing More",
        "chapo": "Corsi e stage venduti da scuole di vela europee, nelle proprie acque come alle Antille, in Atlantico o nel Mare del Nord. Ogni offerta rimanda alla pagina della scuola, che fa fede.",
        "langue": "Lingua del corso", "destination": "Destinazione", "pays_ecole": "Paese della scuola",
        "ecole": "Scuola", "niveau": "Livello", "quand": "Data", "prix": "Prezzo max.",
        "tous": "Tutti", "tout_age": "Ogni età", "avenir": "In arrivo", "mois": "Questo mese",
        "chercher": "Cerca (scuola, corso, luogo)", "dates_ecole": "date presso la scuola",
        "compte": "{n} offerte · {e} scuole", "aucune": "Nessuna offerta con questi filtri.",
        "vide": "Nessuna offerta è ancora pubblicata: l'elenco si legge dalle pagine delle scuole.",
        "du": "dal", "au": "al", "voir": "Vedi l'offerta →", "jours": "giorni", "prix_vide": "prezzo non pubblicato",
        "type": "Tipo", "pratique": "Pratica", "theorie": "Teoria",
        "debutant": "Principiante", "intermediaire": "Intermedio", "confirme": "Avanzato",
        "langue_supposee": "lingua del paese della scuola: la scuola non la indica",
        "verifie": "verificato il", "pied": "Letto dalle pagine delle scuole, offerta per offerta. Un'offerta senza prezzo pubblicato non è ripresa; manca un corso o un prezzo è cambiato?"},
 "es": {"titre": "Cursos y estancias de vela", "retour": "← Sailing More",
        "chapo": "Cursos y estancias que venden escuelas de vela europeas, en sus propias aguas y también en Antillas, Atlántico o mar del Norte. Cada oferta remite a la ficha de la escuela, que es la que manda.",
        "langue": "Idioma del curso", "destination": "Destino", "pays_ecole": "País de la escuela",
        "ecole": "Escuela", "niveau": "Nivel", "quand": "Fecha", "prix": "Precio máx.",
        "tous": "Todos", "tout_age": "Cualquier edad", "avenir": "Próximos", "mois": "Este mes",
        "chercher": "Buscar (escuela, curso, lugar)", "dates_ecole": "fechas en la escuela",
        "compte": "{n} ofertas · {e} escuelas", "aucune": "Ninguna oferta con estos filtros.",
        "vide": "Todavía no hay ofertas publicadas: la lista se lee de las fichas de las escuelas.",
        "du": "del", "au": "al", "voir": "Ver la oferta →", "jours": "días", "prix_vide": "precio no publicado",
        "type": "Tipo", "pratique": "Práctica", "theorie": "Teoría",
        "debutant": "Principiante", "intermediaire": "Intermedio", "confirme": "Avanzado",
        "langue_supposee": "idioma del país de la escuela: la escuela no lo indica",
        "verifie": "verificado el", "pied": "Leído en las fichas de las escuelas, oferta por oferta. Una oferta sin precio publicado no se recoge; ¿falta un curso o ha cambiado un precio?"},
 "pt": {"titre": "Cursos e estágios de vela", "retour": "← Sailing More",
        "chapo": "Cursos e estágios vendidos por escolas de vela europeias, nas suas próprias águas e também nas Antilhas, no Atlântico ou no Mar do Norte. Cada oferta remete para a página da escola, que é quem decide.",
        "langue": "Idioma do curso", "destination": "Destino", "pays_ecole": "País da escola",
        "ecole": "Escola", "niveau": "Nível", "quand": "Data", "prix": "Preço máx.",
        "tous": "Todos", "tout_age": "Qualquer idade", "avenir": "Próximos", "mois": "Este mês",
        "chercher": "Procurar (escola, curso, local)", "dates_ecole": "datas na escola",
        "compte": "{n} ofertas · {e} escolas", "aucune": "Nenhuma oferta com estes filtros.",
        "vide": "Ainda não há ofertas publicadas: a lista é lida das páginas das escolas.",
        "du": "de", "au": "a", "voir": "Ver a oferta →", "jours": "dias", "prix_vide": "preço não publicado",
        "type": "Tipo", "pratique": "Prática", "theorie": "Teoria",
        "debutant": "Iniciante", "intermediaire": "Intermédio", "confirme": "Avançado",
        "langue_supposee": "idioma do país da escola: a escola não o indica",
        "verifie": "verificado a", "pied": "Lido nas páginas das escolas, oferta por oferta. Uma oferta sem preço publicado não é recolhida; falta um curso ou mudou um preço?"},
 "de": {"titre": "Segelkurse und Camps", "retour": "← Sailing More",
        "chapo": "Kurse und Camps von europäischen Segelschulen, auf eigenen Gewässern wie in der Karibik, im Atlantik oder in der Nordsee. Jedes Angebot führt zur Seite der Schule, die massgebend ist.",
        "langue": "Kurssprache", "destination": "Ziel", "pays_ecole": "Land der Schule",
        "ecole": "Schule", "niveau": "Niveau", "quand": "Datum", "prix": "Max. Preis",
        "tous": "Alle", "tout_age": "Jedes Alter", "avenir": "Kommende", "mois": "Diesen Monat",
        "chercher": "Suchen (Schule, Kurs, Ort)", "dates_ecole": "Termine bei der Schule",
        "compte": "{n} Angebote · {e} Schulen", "aucune": "Kein Angebot mit diesen Filtern.",
        "vide": "Noch kein Angebot veröffentlicht: die Liste wird von den Seiten der Schulen gelesen.",
        "du": "vom", "au": "bis", "voir": "Zum Angebot →", "jours": "Tage", "prix_vide": "Preis nicht veröffentlicht",
        "type": "Art", "pratique": "Praxis", "theorie": "Theorie",
        "debutant": "Anfänger", "intermediaire": "Fortgeschritten", "confirme": "Könner",
        "langue_supposee": "Sprache des Schullandes: die Schule gibt sie nicht an",
        "verifie": "geprüft am", "pied": "Von den Seiten der Schulen gelesen, Angebot für Angebot. Ein Angebot ohne veröffentlichten Preis wird nicht aufgenommen; ein Kurs fehlt oder ein Preis hat sich geändert?"},
}

LANGUES = {"fr": "Français", "en": "English", "nl": "Nederlands", "de": "Deutsch", "it": "Italiano",
           "es": "Español", "pt": "Português", "el": "Ελληνικά", "hr": "Hrvatski", "tr": "Türkçe",
           "da": "Dansk", "sv": "Svenska", "no": "Norsk", "pl": "Polski", "fi": "Suomi", "is": "Íslenska",
           "sl": "Slovenščina", "mt": "Malti", "et": "Eesti", "lv": "Latviešu", "lt": "Lietuvių",
           "sq": "Shqip", "ga": "Gaeilge", "cy": "Cymraeg", "ar": "العربية"}
CSS = """
:root{--fond:#0a1a2b;--carte:#0f2438;--trait:#1d3549;--encre:#e8eef5;--doux:#9db2c7;--accent:#5fd3c4}
*{box-sizing:border-box}
body{margin:0;background:var(--fond);color:var(--encre);font:16px/1.5 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}
a{color:inherit}
.page{max-width:60rem;margin:0 auto;padding:2rem 1.2rem 5rem}
h1{font-size:clamp(1.6rem,4vw,2.4rem);margin:.2rem 0 .6rem;letter-spacing:-.02em}
.chapo{color:var(--doux);max-width:44rem;margin:0 0 1.6rem}
.retour{display:inline-block;color:var(--doux);text-decoration:none;font-size:.9rem;margin-bottom:.6rem}
.filtres{display:grid;grid-template-columns:repeat(auto-fit,minmax(9.5rem,1fr));gap:.7rem;background:var(--carte);border:1px solid var(--trait);border-radius:14px;padding:.9rem;margin-bottom:1rem}
label{display:flex;flex-direction:column;gap:.25rem;font-size:.74rem;letter-spacing:.06em;text-transform:uppercase;color:var(--doux)}
select,input{background:#0b1e30;color:var(--encre);border:1px solid var(--trait);border-radius:9px;padding:.5rem .55rem;font:inherit;font-size:.92rem;min-width:0}
input[type=search]{grid-column:span 2}
.compte{color:var(--doux);font-size:.9rem;margin:.2rem 0 1rem}
.liste{display:grid;gap:.8rem}
.offre{background:var(--carte);border:1px solid var(--trait);border-radius:14px;padding:.9rem 1rem;display:grid;grid-template-columns:1fr auto;gap:.5rem .9rem;align-items:start}
.offre h2{font-size:1.02rem;margin:0 0 .2rem;line-height:1.3}
.offre .ecole{color:var(--doux);font-size:.86rem}
.offre .bas{grid-column:1/-1;display:flex;justify-content:space-between;align-items:center;gap:.6rem;flex-wrap:wrap;padding-top:.55rem;border-top:1px solid var(--trait);font-size:.86rem;color:var(--doux)}
.offre .prix{font-size:1.05rem;font-weight:600;color:var(--encre);white-space:nowrap;text-align:right}
.offre .ligne{display:flex;flex-wrap:wrap;gap:.35rem .9rem;font-size:.84rem;color:var(--doux);grid-column:1/-1}
.offre a.lien{color:var(--accent);text-decoration:none;font-size:.88rem}
.marque{font-size:.72rem;border:1px solid var(--trait);border-radius:99px;padding:.06rem .45rem;color:var(--doux)}
.pied{margin-top:2rem;color:var(--doux);font-size:.82rem;border-top:1px solid var(--trait);padding-top:1rem}
.vide{color:var(--doux);padding:2rem 0}
@media(max-width:560px){input[type=search]{grid-column:1/-1}.offre{grid-template-columns:1fr}}
"""


def charger() -> dict:
    if not JSON.exists():
        return {"offres": []}
    return json.loads(JSON.read_text(encoding="utf-8"))


def affichable(o: dict, aujourdhui: date | None = None) -> bool:
    aujourdhui = aujourdhui or date.today()
    try:
        fin = date.fromisoformat(o["fin"]) if o.get("fin") else None
        verifie = date.fromisoformat(o["verifie"])
    except (KeyError, ValueError):
        return False
    if fin and fin < aujourdhui:
        return False
    return verifie >= aujourdhui - timedelta(days=PEREMPTION_JOURS)


def construire(d: dict | None = None) -> str:
    d = d if d is not None else charger()
    offres = [o for o in d.get("offres", []) if affichable(o)]
    # Les offres qui publient un prix passent devant : une ligne sans prix reste utile, mais elle ne
    # doit pas remplir la première page.
    offres.sort(key=lambda o: (o.get("prix") is None, o.get("debut") or "9999-12-31",
                               o.get("prix_eur") or 0))
    donnees = {
        "ui": UI, "offres": offres, "langues": LANGUES,
        "pays": sorted({(o["pays"], o["pays_nom"]) for o in offres if o.get("pays")}),
        "ecoles": sorted({(o["ecole_slug"], o["ecole"]) for o in offres}),
        "pays_ecole": sorted({(o["ecole_pays"], o["ecole_pays_nom"]) for o in offres if o.get("ecole_pays")}),
        "langues_presentes": sorted({o["langue"] for o in offres if o.get("langue")}),
        "niveaux": [n for n in NIVEAUX if any(o.get("niveau") == n for o in offres)],
        "types": [t for t in ("apprentissage", "theorie") if any(
            (o.get("type") == t) or (t == "theorie" and o.get("type") not in ("apprentissage", "theorie"))
            for o in offres)],
    }
    return _html(donnees)


def _html(d: dict) -> str:
    import html as H
    corps = ("<!doctype html><html lang=\"fr\"><head><meta charset=\"utf-8\">"
             "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">"
             f"<title>{H.escape(UI['fr']['titre'])} — Sailing More</title>"
             "<meta name=\"description\" content=\"Stages et cours de voile vendus par des écoles "
             "européennes : prix publiés, destination, langue, lien direct vers la fiche de l'école.\">"
             f"<style>{CSS}</style></head><body><main class=\"page\">"
             f"<a class=\"retour\" href=\"/\" data-t=\"retour\">{H.escape(UI['fr']['retour'])}</a>"
             "<div id=\"langues\"></div>"
             f"<h1 data-t=\"titre\">{H.escape(UI['fr']['titre'])}</h1>"
             f"<p class=\"chapo\" data-t=\"chapo\">{H.escape(UI['fr']['chapo'])}</p>"
             "<section class=\"filtres\">"
             "<label><span data-t=\"chercher\">Chercher</span><input id=\"f-q\" type=\"search\"></label>"
             "<label><span data-t=\"langue\">Langue</span><select id=\"f-langue\"></select></label>"
             "<label><span data-t=\"destination\">Destination</span><select id=\"f-pays\"></select></label>"
             "<label><span data-t=\"pays_ecole\">Pays de l'école</span><select id=\"f-pays-ecole\"></select></label>"
             "<label><span data-t=\"ecole\">École</span><select id=\"f-ecole\"></select></label>"
             "<label><span data-t=\"type\">Type</span><select id=\"f-type\"></select></label>"
             "<label><span data-t=\"niveau\">Niveau</span><select id=\"f-niveau\"></select></label>"
             "<label><span data-t=\"quand\">Date</span><select id=\"f-quand\"></select></label>"
             "<label><span data-t=\"prix\">Prix max.</span><input id=\"f-prix\" type=\"number\" min=\"0\" step=\"50\" inputmode=\"numeric\"></label>"
             "</section>"
             "<p class=\"compte\" id=\"compte\"></p><div class=\"liste\" id=\"liste\"></div>"
             f"<p class=\"pied\" data-t=\"pied\">{H.escape(UI['fr']['pied'])}</p>"
             "</main>"
             "<script id=\"donnees\" type=\"application/json\">"
             + json.dumps(d, ensure_ascii=False).replace("</", "<\\/")
             + "</script><script>" + JS + "</script></body></html>")
    return corps


JS = r"""
var D=JSON.parse(document.getElementById('donnees').textContent),U=D.ui;
var L='fr';try{L=localStorage.getItem('lang')||(navigator.language||'fr').slice(0,2)}catch(e){}
if(!U[L])L='en';
function t(k){return (U[L]&&U[L][k])||U.fr[k]||k}
function esc(s){return String(s==null?'':s).replace(/[&<>"']/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]})}
function dt(s){if(!s)return '';var p=s.split('-');return p[2]+'/'+p[1]+'/'+p[0].slice(2)}
function sym(d){return {EUR:'€',GBP:'£',CHF:'CHF',USD:'$',NOK:'NOK',SEK:'SEK',DKK:'DKK'}[d]||d}
/* langue et pays proposés par défaut : ceux du navigateur, quand des offres y répondent */
var nav=(navigator.language||'fr-FR');var navLang=nav.slice(0,2).toLowerCase();
var m=nav.match(/[-_]([A-Za-z]{2})$/);var navPays=m?m[1].toUpperCase():'';
var ISO2ISO3={FR:'FRA',DE:'DEU',NL:'NLD',GB:'GBR',IE:'IRL',ES:'ESP',IT:'ITA',PT:'PRT',GR:'GRC',HR:'HRV',TR:'TUR',
BE:'BEL',CH:'CHE',AT:'AUT',DK:'DNK',SE:'SWE',NO:'NOR',FI:'FIN',PL:'POL',SI:'SVN',MT:'MLT',CY:'CYP',EE:'EST',
LV:'LVA',LT:'LTU',IS:'ISL',US:'USA',CA:'CAN',SE:'SWE',ZA:'ZAF',AU:'AUS'};
var defPays=ISO2ISO3[navPays]||'';
function mem(k,d){try{var v=localStorage.getItem('st_'+k);return v==null?d:v}catch(e){return d}}
function garde(k,v){try{localStorage.setItem('st_'+k,v)}catch(e){}}
function options(sel,liste,tous){
  var el=document.getElementById(sel);var garde=el.value;
  el.innerHTML='<option value="">'+t('tous')+'</option>'+liste.map(function(o){
    return '<option value="'+esc(o[0])+'">'+esc(o[1])+'</option>'}).join('');
  el.value=garde;
}
function remplir(){
  document.documentElement.lang=L;
  ['titre','chapo','pied','retour','chercher','langue','destination','pays_ecole','ecole','niveau','quand','prix','tous'].forEach(function(k){
    var e=document.querySelector('[data-t="'+k+'"]');if(e)e.textContent=t(k)});
  var f=document.getElementById('f-q');if(f)f.placeholder=t('chercher');
  options('f-langue',D.langues_presentes.map(function(c){return [c,D.langues[c]||c.toUpperCase()]}));
  options('f-pays',D.pays.map(function(p){return [p[0],p[1]]}));
  options('f-pays-ecole',D.pays_ecole.map(function(p){return [p[0],p[1]]}));
  options('f-ecole',D.ecoles.map(function(e){return [e[0],e[1]]}));
  options('f-niveau',D.niveaux.map(function(n){return [n,t(n)]}));
  options('f-type',(D.types||[]).map(function(x){return [x,x==='theorie'?t('theorie'):t('pratique')]}));
  var q=document.getElementById('f-quand'),gq=q.value;
  q.innerHTML='<option value="">'+t('tous')+'</option><option value="avenir">'+t('avenir')+'</option><option value="mois">'+t('mois')+'</option>';
  q.value=gq;
  var fl=document.getElementById('f-langue');
  if(fl.value===''){fl.value=mem('langue', D.langues_presentes.indexOf(navLang)>=0?navLang:'');if(fl.value==='')fl.value='';}
  var fp=document.getElementById('f-pays');
  if(fp.value===''){var d=mem('pays',D.pays.some(function(p){return p[0]===defPays})?defPays:'');fp.value=d;}
  /* Un filtre par défaut qui ne montre rien n'aide personne : si le couple langue+pays du visiteur
     ne laisse aucune offre, on relâche le pays, puis la langue. */
  var pose=false;try{pose=localStorage.getItem('st_pose')==='1'}catch(e){}
  if(!pose){
    var rien=D.offres.filter(function(o){
      return (!fl.value||o.langue===fl.value)&&(!fp.value||o.pays===fp.value)}).length;
    if(!rien){fp.value='';rien=D.offres.filter(function(o){return !fl.value||o.langue===fl.value}).length;}
    if(!rien){fl.value='';}
    try{localStorage.setItem('st_pose','1')}catch(e){}
  }
  var l=document.getElementById('langues');
  l.innerHTML=Object.keys(U).map(function(c){return '<button data-l="'+c+'" style="background:none;border:0;color:'+(c===L?'#5fd3c4':'#9db2c7')+';font:inherit;font-size:.8rem;cursor:pointer;padding:.1rem .25rem">'+c.toUpperCase()+'</button>'}).join('');
  [].forEach.call(l.querySelectorAll('button'),function(b){b.onclick=function(){L=b.dataset.l;try{localStorage.setItem('lang',L)}catch(e){}remplir();dessiner()}});
}
function futur(o){if(!o.debut)return true;var a=new Date().toISOString().slice(0,10);return (o.fin||o.debut)>=a}
function dessiner(){
  var q=(document.getElementById('f-q').value||'').toLowerCase().trim();
  var lg=document.getElementById('f-langue').value,py=document.getElementById('f-pays').value;
  var pe=document.getElementById('f-pays-ecole').value,ec=document.getElementById('f-ecole').value;
  var nv=document.getElementById('f-niveau').value,qd=document.getElementById('f-quand').value;
  var ty=document.getElementById('f-type').value;
  var px=parseFloat(document.getElementById('f-prix').value||'0');
  garde('langue',lg);garde('pays',py);
  var mois=new Date().toISOString().slice(0,7);
  var vus=D.offres.filter(function(o){
    if(lg&&o.langue!==lg)return false;
    if(py&&o.pays!==py)return false;
    if(pe&&o.ecole_pays!==pe)return false;
    if(ec&&o.ecole_slug!==ec)return false;
    if(nv&&o.niveau!==nv)return false;
    if(ty&&((ty==='theorie')!==(o.type==='theorie')))return false;
    if(px&&(o.prix_eur||o.prix||0)>px)return false;
    if(qd==='avenir'&&!futur(o))return false;
    if(qd==='mois'&&(!o.debut||o.debut.slice(0,7)!==mois))return false;
    if(q){var s=(o.titre+' '+o.ecole+' '+o.lieu+' '+o.pays_nom+' '+o.region).toLowerCase();if(s.indexOf(q)<0)return false}
    return true;
  });
  var html=vus.map(function(o){
    var dates=!o.debut?t('dates_ecole'):(o.fin&&o.fin!==o.debut?t('du')+' '+dt(o.debut)+' '+t('au')+' '+dt(o.fin):dt(o.debut));
    var ou=o.lieu?(o.lieu===o.pays_nom?o.lieu:o.lieu+' · '+o.pays_nom):(o.region||o.pays_nom);
    var lng=o.langue?(D.langues[o.langue]||o.langue.toUpperCase()):'—';
    var marque='';
    return '<article class="offre"><div><h2>'+esc(o.titre)+'</h2>'
      +'<div class="ecole">'+esc(o.ecole)+(o.ecole_pays_nom?' · '+esc(o.ecole_pays_nom):'')+'</div></div>'
      +'<div class="prix">'+(o.prix!=null?o.prix.toLocaleString(L)+' '+sym(o.devise):'<span style="font-weight:400;font-size:.85rem">'+t('prix_vide')+'</span>')+'</div>' 
      +'<div class="ligne"><span>'+esc(ou)+'</span><span>'+dates+'</span>'
      +(o.duree_jours?'<span>'+o.duree_jours+' '+t('jours')+'</span>':'')
      +'<span>'+esc(lng)+marque+'</span>'
      +(o.niveau?'<span>'+t(o.niveau)+'</span>':'')+'</div>'
      +'<div class="bas"><span>'+t('verifie')+' '+dt(o.verifie)+'</span>'
      +'<a class="lien" href="'+esc(o.lien)+'" rel="noopener nofollow" target="_blank">'+t('voir')+'</a></div>'
      +'</article>';
  }).join('');
  document.getElementById('liste').innerHTML=html||('<p class="vide">'+(D.offres.length?t('aucune'):t('vide'))+'</p>');
  var ne=new Set(vus.map(function(o){return o.ecole_slug})).size;
  document.getElementById('compte').textContent=t('compte').replace('{n}',vus.length).replace('{e}',ne)
    .replace('offers · 1 schools','offer · 1 school').replace('offres · 1 écoles','offre · 1 école');
}
['f-q','f-langue','f-pays','f-pays-ecole','f-ecole','f-type','f-niveau','f-quand','f-prix'].forEach(function(i){
  var e=document.getElementById(i);if(e){e.addEventListener('input',dessiner);e.addEventListener('change',dessiner)}});
remplir();dessiner();
"""

SITE = ICI / "projets/sailingmore/site"


def ecrire_page(dossier: Path = SITE) -> int:
    """Écrit `stages.html` dans `dossier` — appelé par `accueil_site.sortir_le_site`."""
    dossier.mkdir(parents=True, exist_ok=True)
    d = charger()
    (dossier / "stages.html").write_text(construire(d), encoding="utf-8")
    return sum(1 for o in d.get("offres", []) if affichable(o))


if __name__ == "__main__":
    print(f"stages.html : {ecrire_page()} offre(s) publiable(s)")
