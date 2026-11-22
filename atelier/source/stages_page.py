#!/usr/bin/env python3
"""Construit `stages.html` : les stages de voile vendus en ligne par des écoles européennes, avec
leur prix, leurs dates et le lien direct vers la fiche de l'école.

Entrée  : `projets/sailingmore/stages.json`, produit par `scripts/stages_releve.py` — c'est-à-dire
          relevé sur les pages publiques des écoles, jamais saisi de mémoire. Une école n'entre que
          si sa page affiche un prix et un lien utilisable.
Sortie  : `projets/sailingmore/site/stages.html`, par `accueil_site.sortir_le_site()`.

Une offre dans le JSON :
  {"ecole": "glenans", "titre": "Grenadines", "zone": "Antilles", "pays_stage": "LCA",
   "lieu": "Grenadines", "niveau": "confirme", "type": "croisiere", "duree_jours": 13,
   "prix": 1320, "devise": "EUR", "prix_eur": 1320, "sessions": [{"debut":…, "fin":…}],
   "lien": "https://…", "reservation_en_ligne": false, "verifie": "2026-11-22"}
`duree_jours`, `sessions` et `prix_max` peuvent manquer : la page écrit « — » ou « dates chez
l'école » plutôt que d'inventer.

Trois règles de vérité :
  - une offre sans prix affiché par l'école n'est pas publiée ;
  - une session passée disparaît au moment de la construction, et une offre sans session future
    disparaît aussi — sauf si l'école ne publie pas de dates (croisières à la demande), auquel cas
    la carte dit « dates chez l'école » ;
  - une offre non revérifiée depuis `PEREMPTION_JOURS` jours n'est plus publiée : mieux vaut
    l'absence qu'un prix de l'an dernier.
"""
from __future__ import annotations

import html as _html
import json
import os
import sys
from datetime import date, timedelta
from pathlib import Path

ICI = Path(os.environ.get("SAILINGMORE_RACINE", "/opt/data"))
JSON = Path(__file__).resolve().parent / "stages.json"  # à côté du script : le fichier part avec lui dans l'atelier
PEREMPTION_JOURS = 60  # un prix non revérifié depuis deux mois ne sort plus
NIVEAUX = ("debutant", "intermediaire", "confirme")
TYPES = ("apprentissage", "croisiere", "traversee", "theorie")
DUREES = ("court", "moyen", "long", "expedition")  # 1-2 j, 3-5 j, 6-9 j, 10 j et +
PAYS = {"FRA": "France", "GBR": "Royaume-Uni", "NLD": "Pays-Bas", "CHE": "Suisse", "DEU": "Allemagne",
        "ESP": "Espagne", "ITA": "Italie", "GRC": "Grèce", "NOR": "Norvège", "IRL": "Irlande",
        "HRV": "Croatie", "PRT": "Portugal", "LCA": "Sainte-Lucie", "ATG": "Antigua-et-Barbuda",
        "GRD": "Grenade", "MTQ": "Martinique", "SXM": "Saint-Martin", "DOM": "République dominicaine",
        "BHS": "Bahamas", "MSR": "Montserrat", "DMA": "Dominique", "CAN": "Canada", "USA": "États-Unis",
        "BLM": "Saint-Barthélemy", "GRL": "Groenland", "ISL": "Islande", "SJM": "Svalbard", "FRO": "Féroé", "TUR": "Turquie",
        "HRG": "Croatie"}

UI = {
 "fr": {"titre": "Stages de voile", "sous": "Les stages vendus en ligne par les écoles européennes, prix et dates affichés, lien direct vers la fiche de l'école.",
        "chapo": "Chaque ligne vient de la page de vente de l'école, relevée le jour indiqué en bas de carte : prix, durée, destination, prochaine session. Le lien mène à la fiche de l'offre, pas à la page d'accueil de l'école.",
        "f_ecole": "École", "f_zone": "Destination", "f_type": "Type", "f_niveau": "Niveau",
        "f_duree": "Durée", "f_quand": "Départ", "f_tri": "Trier par", "recherche": "Chercher un stage",
        "tous": "Toutes", "tous_m": "Tous", "avenir": "Toutes les dates", "mois": "Ce mois-ci",
        "debutant": "Débutant", "intermediaire": "Intermédiaire", "confirme": "Confirmé",
        "apprentissage": "Apprentissage", "croisiere": "Croisière", "traversee": "Traversée", "theorie": "Théorie",
        "court": "1 à 2 jours", "moyen": "3 à 5 jours", "long": "6 à 9 jours", "expedition": "10 jours et plus",
        "tri_prix": "Prix croissant", "tri_date": "Départ le plus proche", "tri_duree": "Durée",
        "prix": "Prix", "jour": "jour", "jours": "jours", "prochaine": "Prochaine session",
        "autres": "autres dates", "dates_ecole": "dates chez l'école", "des": "dès",
        "reserver": "Réserver chez l'école", "voir": "Voir la fiche", "verifie": "relevé le", "releve": "Relevé du",
        "ecoles": "écoles", "offres": "offres", "pays_stage": "Stage en", "aucun": "Aucun stage ne correspond à ces filtres.",
        "vide": "Aucun stage publié : le relevé n'a trouvé aucune école qui affiche à la fois un prix et un lien de réservation.",
        "pied": "Prix et dates relus sur les pages de vente des écoles ; ils font foi. Une offre disparaît d'elle-même une fois sa dernière session passée ou son relevé périmé. Un stage manque, un prix a changé ?",
        "note_devise": "Prix dans la devise de l'école. L'équivalent en euros sert au tri, pas à la vente."},
 "en": {"titre": "Sailing courses", "sous": "Courses sold online by European schools — price and dates shown, direct link to the school's own booking page.",
        "chapo": "Every line comes from the school's booking page, read on the date shown at the bottom of the card: price, length, destination, next start. The link goes to the course page, not the school's homepage.",
        "f_ecole": "School", "f_zone": "Destination", "f_type": "Type", "f_niveau": "Level",
        "f_duree": "Length", "f_quand": "Start", "f_tri": "Sort by", "recherche": "Search a course",
        "tous": "All", "tous_m": "All", "avenir": "Any date", "mois": "This month",
        "debutant": "Beginner", "intermediaire": "Intermediate", "confirme": "Advanced",
        "apprentissage": "Training", "croisiere": "Cruising", "traversee": "Passage", "theorie": "Theory",
        "court": "1–2 days", "moyen": "3–5 days", "long": "6–9 days", "expedition": "10 days and more",
        "tri_prix": "Lowest price", "tri_date": "Earliest start", "tri_duree": "Length",
        "prix": "Price", "jour": "day", "jours": "days", "prochaine": "Next start",
        "autres": "more dates", "dates_ecole": "dates at the school", "des": "from",
        "reserver": "Book at the school", "voir": "See the course", "verifie": "read on", "releve": "Read on",
        "ecoles": "schools", "offres": "courses", "pays_stage": "Course in", "aucun": "No course matches these filters.",
        "vide": "No course published yet: the survey found no school showing both a price and a booking link.",
        "pied": "Prices and dates read on the schools' booking pages; they are the authority. An offer drops out by itself once its last start has passed or its reading is stale. Missing course, changed price?",
        "note_devise": "Price in the school's currency. The euro figure is used for sorting, not for selling."},
 "it": {"titre": "Corsi di vela", "sous": "I corsi venduti online dalle scuole europee, con prezzo e date e il link diretto alla scheda della scuola.",
        "chapo": "Ogni riga viene dalla pagina di vendita della scuola, letta il giorno indicato in fondo alla scheda: prezzo, durata, destinazione, prossima partenza. Il link porta alla scheda del corso, non alla home della scuola.",
        "f_ecole": "Scuola", "f_zone": "Destinazione", "f_type": "Tipo", "f_niveau": "Livello",
        "f_duree": "Durata", "f_quand": "Partenza", "f_tri": "Ordina per", "recherche": "Cerca un corso",
        "tous": "Tutte", "tous_m": "Tutti", "avenir": "Tutte le date", "mois": "Questo mese",
        "debutant": "Principiante", "intermediaire": "Intermedio", "confirme": "Esperto",
        "apprentissage": "Apprendimento", "croisiere": "Crociera", "traversee": "Traversata", "theorie": "Teoria",
        "court": "1–2 giorni", "moyen": "3–5 giorni", "long": "6–9 giorni", "expedition": "10 giorni e più",
        "tri_prix": "Prezzo crescente", "tri_date": "Partenza più vicina", "tri_duree": "Durata",
        "prix": "Prezzo", "jour": "giorno", "jours": "giorni", "prochaine": "Prossima partenza",
        "autres": "altre date", "dates_ecole": "date presso la scuola", "des": "da",
        "reserver": "Prenota dalla scuola", "voir": "Vedi la scheda", "verifie": "letto il", "releve": "Letto il",
        "ecoles": "scuole", "offres": "corsi", "pays_stage": "Corso in", "aucun": "Nessun corso corrisponde ai filtri.",
        "vide": "Nessun corso pubblicato: la rilevazione non ha trovato scuole che mostrino prezzo e link di prenotazione.",
        "pied": "Prezzi e date riletti sulle pagine di vendita delle scuole; fanno fede. Un'offerta sparisce da sola quando l'ultima partenza è passata o la lettura è vecchia. Manca un corso o è cambiato un prezzo?",
        "note_devise": "Prezzo nella valuta della scuola. L'importo in euro serve all'ordinamento, non alla vendita."},
 "es": {"titre": "Cursos de vela", "sous": "Los cursos que venden online las escuelas europeas, con precio y fechas y enlace directo a la ficha de la escuela.",
        "chapo": "Cada línea viene de la página de venta de la escuela, leída el día indicado al pie de la ficha: precio, duración, destino, próxima salida. El enlace lleva a la ficha del curso, no a la portada de la escuela.",
        "f_ecole": "Escuela", "f_zone": "Destino", "f_type": "Tipo", "f_niveau": "Nivel",
        "f_duree": "Duración", "f_quand": "Salida", "f_tri": "Ordenar por", "recherche": "Buscar un curso",
        "tous": "Todas", "tous_m": "Todos", "avenir": "Cualquier fecha", "mois": "Este mes",
        "debutant": "Principiante", "intermediaire": "Intermedio", "confirme": "Avanzado",
        "apprentissage": "Aprendizaje", "croisiere": "Crucero", "traversee": "Travesía", "theorie": "Teoría",
        "court": "1–2 días", "moyen": "3–5 días", "long": "6–9 días", "expedition": "10 días y más",
        "tri_prix": "Precio ascendente", "tri_date": "Salida más próxima", "tri_duree": "Duración",
        "prix": "Precio", "jour": "día", "jours": "días", "prochaine": "Próxima salida",
        "autres": "más fechas", "dates_ecole": "fechas en la escuela", "des": "desde",
        "reserver": "Reservar en la escuela", "voir": "Ver la ficha", "verifie": "leído el", "releve": "Leído el",
        "ecoles": "escuelas", "offres": "cursos", "pays_stage": "Curso en", "aucun": "Ningún curso coincide con los filtros.",
        "vide": "Ningún curso publicado: el relevamiento no encontró escuelas que muestren precio y enlace de reserva.",
        "pied": "Precios y fechas releídos en las páginas de venta de las escuelas; son la referencia. Una oferta desaparece sola cuando pasa su última salida o su lectura caduca. ¿Falta un curso o cambió un precio?",
        "note_devise": "Precio en la moneda de la escuela. El importe en euros sirve para ordenar, no para vender."},
 "pt": {"titre": "Cursos de vela", "sous": "Os cursos vendidos online pelas escolas europeias, com preço e datas e ligação direta à ficha da escola.",
        "chapo": "Cada linha vem da página de venda da escola, lida no dia indicado no fundo do cartão: preço, duração, destino, próxima partida. A ligação vai à ficha do curso, não à página inicial da escola.",
        "f_ecole": "Escola", "f_zone": "Destino", "f_type": "Tipo", "f_niveau": "Nível",
        "f_duree": "Duração", "f_quand": "Partida", "f_tri": "Ordenar por", "recherche": "Procurar um curso",
        "tous": "Todas", "tous_m": "Todos", "avenir": "Todas as datas", "mois": "Este mês",
        "debutant": "Iniciante", "intermediaire": "Intermédio", "confirme": "Avançado",
        "apprentissage": "Aprendizagem", "croisiere": "Cruzeiro", "traversee": "Travessia", "theorie": "Teoria",
        "court": "1–2 dias", "moyen": "3–5 dias", "long": "6–9 dias", "expedition": "10 dias e mais",
        "tri_prix": "Preço crescente", "tri_date": "Partida mais próxima", "tri_duree": "Duração",
        "prix": "Preço", "jour": "dia", "jours": "dias", "prochaine": "Próxima partida",
        "autres": "outras datas", "dates_ecole": "datas na escola", "des": "desde",
        "reserver": "Reservar na escola", "voir": "Ver a ficha", "verifie": "lido a", "releve": "Lido a",
        "ecoles": "escolas", "offres": "cursos", "pays_stage": "Curso em", "aucun": "Nenhum curso corresponde aos filtros.",
        "vide": "Nenhum curso publicado: o levantamento não encontrou escolas que mostrem preço e ligação de reserva.",
        "pied": "Preços e datas relidos nas páginas de venda das escolas; são a referência. Uma oferta desaparece sozinha quando a última partida passa ou a leitura caduca. Falta um curso ou mudou um preço?",
        "note_devise": "Preço na moeda da escola. O valor em euros serve para ordenar, não para vender."},
 "de": {"titre": "Segelkurse", "sous": "Kurse, die europäische Segelschulen online verkaufen – mit Preis, Terminen und direktem Link zur Kursseite der Schule.",
        "chapo": "Jede Zeile stammt von der Buchungsseite der Schule, gelesen am unten angegebenen Tag: Preis, Dauer, Ziel, nächster Start. Der Link führt zur Kursseite, nicht zur Startseite der Schule.",
        "f_ecole": "Schule", "f_zone": "Ziel", "f_type": "Art", "f_niveau": "Niveau",
        "f_duree": "Dauer", "f_quand": "Start", "f_tri": "Sortieren nach", "recherche": "Kurs suchen",
        "tous": "Alle", "tous_m": "Alle", "avenir": "Alle Termine", "mois": "Diesen Monat",
        "debutant": "Anfänger", "intermediaire": "Fortgeschritten", "confirme": "Erfahren",
        "apprentissage": "Ausbildung", "croisiere": "Törn", "traversee": "Überfahrt", "theorie": "Theorie",
        "court": "1–2 Tage", "moyen": "3–5 Tage", "long": "6–9 Tage", "expedition": "10 Tage und mehr",
        "tri_prix": "Günstigster Preis", "tri_date": "Frühester Start", "tri_duree": "Dauer",
        "prix": "Preis", "jour": "Tag", "jours": "Tage", "prochaine": "Nächster Start",
        "autres": "weitere Termine", "dates_ecole": "Termine bei der Schule", "des": "ab",
        "reserver": "Bei der Schule buchen", "voir": "Kursseite ansehen", "verifie": "gelesen am", "releve": "Gelesen am",
        "ecoles": "Schulen", "offres": "Kurse", "pays_stage": "Kurs in", "aucun": "Kein Kurs passt zu diesen Filtern.",
        "vide": "Noch kein Kurs veröffentlicht: die Erhebung fand keine Schule, die Preis und Buchungslink zeigt.",
        "pied": "Preise und Termine von den Buchungsseiten der Schulen; sie sind massgebend. Ein Angebot verschwindet von selbst, wenn der letzte Start vorbei oder die Erhebung veraltet ist. Kurs fehlt, Preis geändert?",
        "note_devise": "Preis in der Währung der Schule. Der Eurobetrag dient der Sortierung, nicht dem Verkauf."},
}

CSS = """
:root{--nuit:#0a1a2b;--panneau:#0f2438;--ivoire:#eef3f7;--gris:#9db2c6;--rouge:#e23a3e}
*{box-sizing:border-box}
body{margin:0;background:#071c31;color:var(--ivoire);font-family:ui-sans-serif,system-ui,-apple-system,"Helvetica Neue",Arial,sans-serif;line-height:1.55;-webkit-font-smoothing:antialiased}
.page{max-width:64rem;margin:0 auto;padding:2rem 1.4rem 5rem}
a.retour{color:var(--gris);text-decoration:none;font-size:.64rem;letter-spacing:.14em;text-transform:uppercase;font-weight:500}
h1{font-size:2rem;margin:1.6rem 0 .3rem}
.sous{color:var(--gris);max-width:44rem}
.bandeau{display:flex;gap:.6rem;flex-wrap:wrap;margin:1.2rem 0 0;font-size:.78rem;color:var(--gris)}
.bandeau b{color:var(--ivoire);font-weight:600}
.filtres{display:grid;grid-template-columns:repeat(auto-fit,minmax(9rem,1fr));gap:.7rem;margin:1.4rem 0 .6rem;padding:1rem;background:var(--panneau);border-radius:4px}
.filtres label{display:flex;flex-direction:column;font-size:.6rem;letter-spacing:.1em;text-transform:uppercase;color:var(--gris);gap:.25rem}
.filtres select,.filtres input{background:#0a1a2b;color:var(--ivoire);border:1px solid #27425b;border-radius:3px;padding:.42rem .5rem;font-size:.82rem;width:100%}
.compte{color:var(--gris);font-size:.8rem;margin:.6rem 0 1rem}
.offre{background:var(--panneau);border-left:3px solid var(--rouge);padding:1rem 1.2rem;margin:.8rem 0;border-radius:4px;display:grid;grid-template-columns:1fr auto;gap:.2rem .9rem}
.offre h2{font-size:1.06rem;margin:0;grid-column:1}
.offre .prix{grid-column:2;grid-row:1;text-align:right;font-weight:700;font-size:1.05rem;white-space:nowrap}
.offre .prix small{display:block;font-weight:400;font-size:.7rem;color:var(--gris)}
.offre .ecole{grid-column:1/-1;color:var(--gris);font-size:.78rem;margin-bottom:.3rem}
.offre .ligne{grid-column:1/-1;display:flex;flex-wrap:wrap;gap:.2rem .9rem;font-size:.86rem}
.offre .ligne span{white-space:nowrap}
.offre .bas{grid-column:1/-1;display:flex;justify-content:space-between;align-items:center;gap:.6rem;flex-wrap:wrap;margin-top:.5rem;padding-top:.5rem;border-top:1px solid #1d3549}
.offre .verif{color:var(--gris);font-size:.72rem}
.offre a.bouton{background:var(--rouge);color:#fff;text-decoration:none;font-size:.8rem;font-weight:600;padding:.42rem .8rem;border-radius:3px}
.offre a.bouton:hover{background:#f04a4e}
.offre a.second{color:var(--gris);font-size:.76rem;text-decoration:none;border-bottom:1px dotted #27425b}
.tag{display:inline-block;font-size:.66rem;letter-spacing:.06em;text-transform:uppercase;color:var(--gris);border:1px solid #27425b;border-radius:2px;padding:0 .35rem;margin-left:.3rem}
.tag.online{color:#8fd6a0;border-color:#2f5b3f}
.vide,.pied{color:var(--gris);font-size:.86rem;margin-top:1.6rem}
.pied a{color:var(--ivoire)}
@media(max-width:520px){.offre{grid-template-columns:1fr}.offre .prix{grid-row:auto;text-align:left;grid-column:1}}
"""

JS = r"""
(function(){
var D=JSON.parse(document.getElementById('donnees').textContent),U=D.ui,L='fr';
var $=function(i){return document.getElementById(i)};
var LOC={fr:'fr-FR',en:'en-GB',it:'it-IT',es:'es-ES',pt:'pt-PT',de:'de-DE'};
function t(k){return (U[L]&&U[L][k])||U.fr[k]||k}
function esc(s){return String(s).replace(/[&<>"]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]})}
function dt(iso){if(!iso)return '';var d=new Date(iso+'T12:00:00');return d.toLocaleDateString(LOC[L],{day:'numeric',month:'short',year:'numeric'})}
function auj(){return new Date().toISOString().slice(0,10)}
function prix(o){var n=o.prix,dev=o.devise==='GBP'?'£':(o.devise==='CHF'?'CHF':'€');
  var s=n.toLocaleString(LOC[L])+' '+dev;
  var eq=(o.devise!=='EUR'&&o.prix_eur)?'<small>≈ '+o.prix_eur.toLocaleString(LOC[L])+' €</small>':'';
  return s+eq}
function remplir(id,cle,vals,libelle){
  var v=$(id).value;
  $(id).innerHTML='<option value="">'+t(libelle)+'</option>'+vals.map(function(x){
    return '<option value="'+esc(x.v)+'">'+esc(x.l)+'</option>'}).join('');
  $(id).value=v;
}
function ok(o){
  if($('f-ecole').value && o.ecole!==$('f-ecole').value)return false;
  if($('f-zone').value && o.zone!==$('f-zone').value)return false;
  if($('f-type').value && o.type!==$('f-type').value)return false;
  if($('f-niveau').value && o.niveau!==$('f-niveau').value)return false;
  if($('f-duree').value && o.duree!==$('f-duree').value)return false;
  if($('f-quand').value==='mois'){
    var m=auj().slice(0,7);
    if(!o.prochaine || o.prochaine.slice(0,7)!==m)return false;
  }
  var q=($('f-recherche').value||'').toLowerCase();
  if(q && (o.titre+' '+o.ecole_nom+' '+o.lieu+' '+o.zone).toLowerCase().indexOf(q)<0)return false;
  return true;
}
function tri(a){
  var k=$('f-tri').value;
  if(k==='prix')return a.sort(function(x,y){return x.prix_eur-y.prix_eur});
  if(k==='duree')return a.sort(function(x,y){return (y.duree||0)-(x.duree||0)});
  return a.sort(function(x,y){return (x.prochaine||'9999')<(y.prochaine||'9999')?-1:1});
}
function carte(o){
  var d=o.duree?o.duree+' '+(o.duree>1?t('jours'):t('jour')):'—';
  var quand=o.prochaine?(t('prochaine')+' '+(o.fin&&o.fin!==o.prochaine?'<span class="tag">'+dt(o.prochaine)+'</span>':'<span class="tag">'+dt(o.prochaine)+'</span>')):('<span class="tag">'+t('dates_ecole')+'</span>');
  var plus=o.nb_sessions>1?' · '+o.nb_sessions+' '+t('autres'):'';
  var online=o.reservation_en_ligne?'<span class="tag online">'+t('reserver')+'</span>':'';
  return '<div class="offre"><h2>'+esc(o.titre)+'</h2>'
   +'<div class="prix">'+prix(o)+'</div>'
   +'<div class="ecole">'+esc(o.ecole_nom)+' · '+esc(o.ecole_pays)+online+'</div>'
   +'<div class="ligne"><span>'+esc(o.zone)+'</span>'
   +(o.pays_stage_lbl?'<span>'+esc(t('pays_stage'))+' '+esc(o.pays_stage_lbl)+'</span>':'')
   +'<span>'+d+'</span><span>'+t(o.niveau)+'</span><span>'+t(o.type)+'</span></div>'
   +'<div class="ligne"><span>'+quand+plus+'</span></div>'
   +'<div class="bas"><span class="verif">'+t('verifie')+' '+dt(o.verifie)+'</span>'
   +'<a class="bouton" href="'+esc(o.lien)+'" rel="noopener" target="_blank">'+t('voir')+' →</a></div></div>';
}
function dessiner(){
  var r=tri(D.offres.filter(ok));
  var nbE={};r.forEach(function(o){nbE[o.ecole]=1});
  $('compte').textContent=r.length+' '+t('offres')+' · '+Object.keys(nbE).length+' '+t('ecoles');
  $('liste').innerHTML=r.length?r.map(carte).join(''):'<p class="vide">'+(D.offres.length?t('aucun'):t('vide'))+'</p>';
}
function langue(l){L=l;document.documentElement.lang=l;
  document.querySelectorAll('#langues button').forEach(function(b){b.setAttribute('aria-pressed',b.dataset.lang===l)});
  document.querySelectorAll('[data-t]').forEach(function(e){e.textContent=t(e.dataset.t)});
  var v={ecole:$('f-ecole').value,zone:$('f-zone').value,type:$('f-type').value,niveau:$('f-niveau').value,duree:$('f-duree').value,quand:$('f-quand').value,tri:$('f-tri').value};
  remplir('f-ecole','tous',D.ecoles.map(function(x){return {v:x,v:x}}),'tous');
  remplir('f-zone','tous',D.zones.map(function(x){return {v:x,v:x}}),'tous');
  remplir('f-type','tous_m',D.types.map(function(x){return {v:x,l:t(x)}}),'tous_m');
  remplir('f-niveau','tous_m',D.niveaux.map(function(x){return {v:x,l:t(x)}}),'tous_m');
  remplir('f-duree','tous_m',D.durees.map(function(x){return {v:x,l:t(x)}}),'tous_m');
  remplir('f-quand','avenir',[{v:'mois',l:t('mois')}],'avenir');
  remplir('f-tri','tri_date',[{v:'prix',l:t('tri_prix')},{v:'date',l:t('tri_date')},{v:'duree',l:t('tri_duree')}],'tri_date');
  $('f-ecole').value=v.ecole;$('f-zone').value=v.zone;$('f-type').value=v.type;$('f-niveau').value=v.niveau;
  $('f-duree').value=v.duree;$('f-quand').value=v.quand||'';$('f-tri').value=v.tri||'date';
  $('f-recherche').placeholder=t('recherche');
  dessiner();
}
['f-ecole','f-zone','f-type','f-niveau','f-duree','f-quand','f-tri','f-recherche'].forEach(function(i){
  $(i).addEventListener('input',dessiner);$(i).addEventListener('change',dessiner)});
document.querySelectorAll('#langues button').forEach(function(b){b.addEventListener('click',function(){langue(b.dataset.lang)})});
var l0='fr';try{l0=localStorage.getItem('lang')||(navigator.language||'fr').slice(0,2)}catch(e){}
langue(U[l0]?l0:'fr');
})();
"""


def charger() -> dict:
    if not JSON.exists():
        return {"ecoles": {}, "offres": [], "releve": ""}
    return json.loads(JSON.read_text(encoding="utf-8"))


def bande(jours: int | None) -> str | None:
    if not jours:
        return None
    if jours <= 2:
        return "court"
    if jours <= 5:
        return "moyen"
    if jours <= 9:
        return "long"
    return "expedition"


def affichable(o: dict, aujourdhui: date | None = None) -> bool:
    """Publiable = prix affiché par l'école + lien profond + relevé frais + une session à venir
    (ou aucune date publiée, ce qui est le cas des croisières à la demande)."""
    aujourdhui = aujourdhui or date.today()
    try:
        verifie = date.fromisoformat(o["verifie"])
    except (KeyError, ValueError):
        return False
    if not (o.get("titre") and o.get("ecole") and str(o.get("lien", "")).startswith("https://")):
        return False
    if not isinstance(o.get("prix"), (int, float)) or o["prix"] <= 0:
        return False
    if verifie < aujourdhui - timedelta(days=PEREMPTION_JOURS):
        return False
    futures = sessions_futures(o, aujourdhui)
    if futures is not None and not futures:
        return False
    return True


def sessions_futures(o: dict, aujourdhui: date | None = None) -> list[dict] | None:
    """Les sessions à venir, triées. `None` quand l'école ne publie pas de dates."""
    if not o.get("sessions"):
        return None  # l'école ne publie pas de dates
    aujourdhui = aujourdhui or date.today()
    garde = []
    for s in o.get("sessions") or []:
        try:
            fin = date.fromisoformat(s.get("fin") or s["debut"])
        except (KeyError, ValueError):
            continue
        if date.fromisoformat(s["debut"]) >= aujourdhui and fin >= aujourdhui:  # pas de session commencée
            garde.append(s)
    return sorted(garde, key=lambda s: s["debut"])


def construire(d: dict | None = None) -> str:
    d = d if d is not None else charger()
    ecoles = d.get("ecoles", {})
    offres, vues = [], []
    for o in d.get("offres", []):
        if not affichable(o):
            continue
        e = ecoles.get(o["ecole"], {})
        fut = sessions_futures(o)
        prochaine = fut[0]["debut"] if fut else ""
        vues.append({
            "titre": o["titre"], "ecole": o["ecole"], "ecole_nom": e.get("nom", o["ecole"]),
            "ecole_pays": PAYS.get(e.get("pays", ""), e.get("pays", "")),
            "zone": o.get("zone", ""), "lieu": o.get("lieu", ""),
            "pays_stage_lbl": PAYS.get(o.get("pays_stage", ""), o.get("pays_stage", "")),
            "type": o.get("type", "croisiere"), "niveau": o.get("niveau", "intermediaire"),
            "duree": o.get("duree_jours"), "bande": bande(o.get("duree_jours")),
            "prix": o["prix"], "devise": o.get("devise", "EUR"),
            "prix_eur": o.get("prix_eur") or o["prix"],
            "prochaine": prochaine,
            "nb_sessions": len(fut) if fut is not None else 0,
            "lien": o["lien"], "reservation_en_ligne": bool(o.get("reservation_en_ligne")),
            "verifie": o["verifie"],
        })
    vues.sort(key=lambda o: (o["prochaine"] or "9999", o["prix_eur"]))
    donnees = {
        "ui": UI, "offres": vues,
        "ecoles": sorted({o["ecole_nom"] for o in vues}),
        "zones": sorted({o["zone"] for o in vues if o["zone"]}),
        "types": [x for x in TYPES if any(o["type"] == x for o in vues)],
        "niveaux": [x for x in NIVEAUX if any(o["niveau"] == x for o in vues)],
        "durees": [x for x in DUREES if any(o["bande"] == x for o in vues)],
    }
    fr = UI["fr"]
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import site_blocks  # la barre du site : un seul endroit
    releve = (d.get("releve") or "")[:10]
    nb_ecoles = len({o["ecole_nom"] for o in vues})
    return (
        '<!doctype html>\n<html lang="fr"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        f"<title>{fr['titre']} — prix, dates et lien direct — Sailing More</title>"
        '<link rel="canonical" href="https://sailingmore.fr/stages.html">'
        '<meta name="description" content="Stages de voile vendus en ligne par des écoles européennes : '
        'prix, durée, destination et prochaine session affichés, lien direct vers la fiche de l\'école.">'
        '<meta property="og:title" content="Stages de voile — Sailing More">'
        '<meta property="og:type" content="website">'
        "<style>" + site_blocks.ENTETE_CSS + CSS + "</style></head><body>"
        + site_blocks.entete_site("stages.html", ["fr", "en", "it", "es", "pt", "de"], auto=False)
        + '<div class="page">'
        f'<h1 data-t="titre">{fr["titre"]}</h1>'
        f'<p class="sous" data-t="sous">{fr["sous"]}</p>'
        f'<div class="bandeau"><span><b>{len(vues)}</b> <span data-t="offres">{fr["offres"]}</span></span>'
        f'<span><b>{nb_ecoles}</b> <span data-t="ecoles">{fr["ecoles"]}</span></span>'
        + (f'<span><span data-t="releve">{fr["releve"]}</span> <b>{releve}</b></span>' if releve else '') + '</div>'
        '<div class="filtres">'
        '<label><span data-t="f_ecole">École</span><select id="f-ecole"></select></label>'
        '<label><span data-t="f_zone">Destination</span><select id="f-zone"></select></label>'
        '<label><span data-t="f_type">Type</span><select id="f-type"></select></label>'
        '<label><span data-t="f_niveau">Niveau</span><select id="f-niveau"></select></label>'
        '<label><span data-t="f_duree">Durée</span><select id="f-duree"></select></label>'
        '<label><span data-t="f_quand">Départ</span><select id="f-quand"></select></label>'
        '<label><span data-t="f_tri">Trier par</span><select id="f-tri"></select></label>'
        '<label><span data-t="recherche">Chercher</span><input id="f-recherche" type="search"></label>'
        '</div><div class="compte" id="compte" role="status"></div><div id="liste"></div>'
        f'<p class="pied"><span data-t="pied">{fr["pied"]}</span> '
        '<a href="annonceurs.html">Contact</a>'
        + (f" · {releve}" if releve else "") + "</p>"
        f'<p class="pied" data-t="note_devise">{fr["note_devise"]}</p></div>'
        '<script type="application/json" id="donnees">'
        + json.dumps(donnees, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
        + "</script><script>" + JS + "</script></body></html>\n"
    )


def ecrire_page(dossier: Path) -> int:
    """Écrit `stages.html` dans `dossier` — le seul chemin de sortie de cette page, appelé par
    `accueil_site.sortir_le_site()` pour passer par le même pipeline que le reste du site."""
    d = charger()
    (dossier / "stages.html").write_text(construire(d), encoding="utf-8")
    return sum(1 for o in d.get("offres", []) if affichable(o))


if __name__ == "__main__":
    SITE = ICI / "projets/sailingmore/site"
    SITE.mkdir(parents=True, exist_ok=True)
    print(f"stages.html : {ecrire_page(SITE)} offre(s) publiable(s)")
