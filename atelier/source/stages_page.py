#!/usr/bin/env python3
"""Construit la page `stages.html` : les stages et cours de voile des écoles privées et des clubs
qui en vendent, en France et en Suisse. Filtres : lieu, âge, niveau, date, prix.

Entrée  : `projets/sailingmore/stages.json`, tenu à la main depuis les sites des écoles (Les Glénans
          en tête, puis Léman, Haute-Savoie, Suisse romande). Aucune extraction de base FFVoile ni
          Destination Voile (CGU §9.1) : une offre = une ligne saisie, avec son lien et sa date de
          vérification.
Sortie  : `projets/sailingmore/site/stages.html` (appelée par `accueil_site.sortir_le_site`).

Une offre dans le JSON :
  {"ecole": "Les Glénans", "titre": "Stage Dériveur initiation", "lieu": "Paimpol", "region": "Bretagne",
   "pays": "FRA" | "SUI", "age_min": 15, "age_max": null, "niveau": "debutant|intermediaire|confirme",
   "debut": "2027-04-12", "fin": "2027-04-17", "prix": 560, "devise": "EUR" | "CHF",
   "lien": "https://…", "verifie": "2026-11-22"}
`age_*`, `fin` et `prix` peuvent manquer : la page écrit alors « — » plutôt que d'inventer.

Comment la page reste juste :
  - le passé disparaît seul : à la génération (offre dont la fin est passée) ET dans le navigateur
    (le JS compare à la date du jour), donc une page non reconstruite ne montre pas un stage fini ;
  - une offre non revérifiée depuis plus de `PEREMPTION_JOURS` jours n'est plus publiée : mieux vaut
    l'absence qu'un prix d'il y a un an ;
  - une école qui change son offre : on corrige la ligne et on met `verifie` à jour — le lien
    renvoie toujours vers la page de l'école, qui fait foi.
Rythme de changement : les catalogues d'été s'ouvrent à l'automne-hiver, les prix bougent une fois
par an, les places partent au fil des mois : revérification mensuelle, hebdomadaire de mai à août.
"""
from __future__ import annotations

import html as _html
import json
import os
import sys
from datetime import date, timedelta
from pathlib import Path

ICI = Path(os.environ.get("SAILINGMORE_RACINE", "/opt/data"))
JSON = ICI / "projets/sailingmore/stages.json"
PEREMPTION_JOURS = 60
NIVEAUX = ("debutant", "intermediaire", "confirme")

UI = {
    "fr": {"titre": "Stages et cours de voile", "retour": "← Sailing More",
           "chapo": "Les stages et cours proposés par les écoles de voile et les clubs, en France et en Suisse. Chaque offre renvoie vers l'école, qui fait foi : prix et dates se confirment chez elle.",
           "lieu": "Lieu", "age": "Âge", "niveau": "Niveau", "quand": "Date", "prix": "Prix max.",
           "tous": "Tous", "tout_age": "Tout âge", "avenir": "À venir", "mois": "Ce mois-ci",
           "debutant": "Débutant", "intermediaire": "Intermédiaire", "confirme": "Confirmé",
           "FRA": "France", "SUI": "Suisse", "verifie": "vérifié le", "voir": "Voir l'offre",
           "du": "du", "au": "au", "ans": "ans", "n_offres": "offres", "aucune": "Aucune offre ne correspond à ces filtres.",
           "vide": "Aucune offre n'est publiée pour le moment : la liste se remplit à la main depuis les sites des écoles, et chaque offre est retirée seule une fois passée.",
           "pied": "Liste tenue à la main, école par école, sans reprise de base de données tierce. Un stage manque ou un prix a changé ?"},
    "en": {"titre": "Sailing courses and camps", "retour": "← Sailing More",
           "chapo": "Courses and camps offered by sailing schools and clubs in France and Switzerland. Each offer links to the school, which is the authority: confirm prices and dates there.",
           "lieu": "Place", "age": "Age", "niveau": "Level", "quand": "Date", "prix": "Max. price",
           "tous": "All", "tout_age": "Any age", "avenir": "Upcoming", "mois": "This month",
           "debutant": "Beginner", "intermediaire": "Intermediate", "confirme": "Advanced",
           "FRA": "France", "SUI": "Switzerland", "verifie": "checked on", "voir": "See the offer",
           "du": "from", "au": "to", "ans": "years", "n_offres": "offers", "aucune": "No offer matches these filters.",
           "vide": "No offer is published yet: the list is filled by hand from the schools' own sites, and each offer drops off by itself once it has passed.",
           "pied": "Hand-kept list, school by school, no third-party database reused. A course missing or a price changed?"},
    "it": {"titre": "Corsi e stage di vela", "retour": "← Sailing More",
           "chapo": "Corsi e stage proposti da scuole di vela e circoli in Francia e Svizzera. Ogni offerta rimanda alla scuola, che fa fede: prezzi e date si confermano da loro.",
           "lieu": "Luogo", "age": "Età", "niveau": "Livello", "quand": "Data", "prix": "Prezzo max.",
           "tous": "Tutti", "tout_age": "Ogni età", "avenir": "In arrivo", "mois": "Questo mese",
           "debutant": "Principiante", "intermediaire": "Intermedio", "confirme": "Esperto",
           "FRA": "Francia", "SUI": "Svizzera", "verifie": "verificato il", "voir": "Vedi l'offerta",
           "du": "dal", "au": "al", "ans": "anni", "n_offres": "offerte", "aucune": "Nessuna offerta corrisponde ai filtri.",
           "vide": "Nessuna offerta è ancora pubblicata: l'elenco si compila a mano dai siti delle scuole e ogni offerta sparisce da sola una volta passata.",
           "pied": "Elenco tenuto a mano, scuola per scuola, senza riuso di banche dati di terzi. Manca un corso o un prezzo è cambiato?"},
    "es": {"titre": "Cursos y estancias de vela", "retour": "← Sailing More",
           "chapo": "Cursos y estancias que ofrecen escuelas de vela y clubes en Francia y Suiza. Cada oferta remite a la escuela, que es la que manda: precios y fechas se confirman allí.",
           "lieu": "Lugar", "age": "Edad", "niveau": "Nivel", "quand": "Fecha", "prix": "Precio máx.",
           "tous": "Todos", "tout_age": "Cualquier edad", "avenir": "Próximos", "mois": "Este mes",
           "debutant": "Principiante", "intermediaire": "Intermedio", "confirme": "Avanzado",
           "FRA": "Francia", "SUI": "Suiza", "verifie": "verificado el", "voir": "Ver la oferta",
           "du": "del", "au": "al", "ans": "años", "n_offres": "ofertas", "aucune": "Ninguna oferta coincide con los filtros.",
           "vide": "Todavía no hay ofertas publicadas: la lista se rellena a mano desde las webs de las escuelas y cada oferta desaparece sola al pasar.",
           "pied": "Lista hecha a mano, escuela por escuela, sin reutilizar bases de datos de terceros. ¿Falta un curso o ha cambiado un precio?"},
    "pt": {"titre": "Cursos e estágios de vela", "retour": "← Sailing More",
           "chapo": "Cursos e estágios propostos por escolas de vela e clubes em França e na Suíça. Cada oferta remete para a escola, que é quem decide: preços e datas confirmam-se aí.",
           "lieu": "Local", "age": "Idade", "niveau": "Nível", "quand": "Data", "prix": "Preço máx.",
           "tous": "Todos", "tout_age": "Qualquer idade", "avenir": "Próximos", "mois": "Este mês",
           "debutant": "Iniciante", "intermediaire": "Intermédio", "confirme": "Avançado",
           "FRA": "França", "SUI": "Suíça", "verifie": "verificado em", "voir": "Ver a oferta",
           "du": "de", "au": "a", "ans": "anos", "n_offres": "ofertas", "aucune": "Nenhuma oferta corresponde aos filtros.",
           "vide": "Ainda não há ofertas publicadas: a lista é preenchida à mão a partir dos sites das escolas e cada oferta sai sozinha depois de passar.",
           "pied": "Lista feita à mão, escola por escola, sem reutilizar bases de dados de terceiros. Falta um curso ou mudou um preço?"},
    "de": {"titre": "Segelkurse und Segelcamps", "retour": "← Sailing More",
           "chapo": "Kurse und Camps von Segelschulen und Clubs in Frankreich und der Schweiz. Jedes Angebot führt zur Schule, die massgebend ist: Preise und Termine dort bestätigen.",
           "lieu": "Ort", "age": "Alter", "niveau": "Niveau", "quand": "Datum", "prix": "Max. Preis",
           "tous": "Alle", "tout_age": "Jedes Alter", "avenir": "Kommende", "mois": "Diesen Monat",
           "debutant": "Anfänger", "intermediaire": "Fortgeschritten", "confirme": "Erfahren",
           "FRA": "Frankreich", "SUI": "Schweiz", "verifie": "geprüft am", "voir": "Angebot ansehen",
           "du": "vom", "au": "bis", "ans": "Jahre", "n_offres": "Angebote", "aucune": "Kein Angebot passt zu diesen Filtern.",
           "vide": "Noch kein Angebot veröffentlicht: die Liste wird von Hand nach den Seiten der Schulen gefüllt, jedes Angebot verschwindet nach Ablauf von selbst.",
           "pied": "Von Hand geführte Liste, Schule für Schule, ohne Übernahme fremder Datenbanken. Ein Kurs fehlt oder ein Preis hat sich geändert?"},
}

CSS = """
:root{--nuit:#0a1a2b;--panneau:#0f2438;--ivoire:#eef3f7;--gris:#9db2c6;--rouge:#e23a3e}
*{box-sizing:border-box}
body{margin:0;background:#071c31;color:var(--ivoire);font-family:ui-sans-serif,system-ui,-apple-system,"Helvetica Neue",Arial,sans-serif;line-height:1.55;-webkit-font-smoothing:antialiased}
.page{max-width:56rem;margin:0 auto;padding:2rem 1.4rem 5rem}
.haut{display:flex;justify-content:space-between;align-items:center;gap:1rem;flex-wrap:wrap}
a.retour{color:var(--gris);text-decoration:none;font-size:.64rem;letter-spacing:.14em;text-transform:uppercase;font-weight:500}
.langues button{background:none;border:1px solid #27425b;color:var(--gris);font-size:.64rem;padding:.25rem .5rem;margin-left:.2rem;cursor:pointer;border-radius:3px}
.langues button[aria-pressed=true]{color:var(--ivoire);border-color:var(--rouge)}
h1{font-size:2rem;margin:2rem 0 .4rem}
.chapo{color:var(--gris)}
.filtres{display:flex;flex-wrap:wrap;gap:.8rem;margin:1.4rem 0 .6rem}
.filtres label{display:flex;flex-direction:column;font-size:.62rem;letter-spacing:.12em;text-transform:uppercase;color:var(--gris);gap:.25rem}
.filtres select,.filtres input{background:var(--panneau);color:var(--ivoire);border:1px solid #27425b;border-radius:3px;padding:.4rem .5rem;font-size:.85rem;min-width:8rem}
.compte{color:var(--gris);font-size:.8rem;margin:.4rem 0 1rem}
.offre{background:var(--panneau);border-left:3px solid var(--rouge);padding:.9rem 1.2rem;margin:.8rem 0;border-radius:3px}
.offre h2{font-size:1.05rem;margin:0 0 .2rem}
.offre .ecole{color:var(--gris);font-size:.8rem}
.offre .ligne{display:flex;flex-wrap:wrap;gap:.3rem 1.2rem;font-size:.88rem;margin:.4rem 0}
.offre .prix{font-weight:600}
.offre .verif{color:var(--gris);font-size:.74rem}
.offre a{color:var(--ivoire)}
.vide,.pied{color:var(--gris);font-size:.88rem;margin-top:2rem}
a{color:var(--ivoire)}
"""

JS = r"""
(function(){
var D=JSON.parse(document.getElementById('donnees').textContent),U=D.ui,L='fr';
var $=function(i){return document.getElementById(i)};
var MOIS={fr:'fr-FR',en:'en-GB',it:'it-IT',es:'es-ES',pt:'pt-PT',de:'de-DE'};
function dt(iso){return new Date(iso+'T12:00:00').toLocaleDateString(MOIS[L],{day:'numeric',month:'short',year:'numeric'})}
function t(k){return (U[L]&&U[L][k])||U.fr[k]||k}
function esc(s){return String(s).replace(/[&<>"]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]})}
function futur(o){var auj=new Date().toISOString().slice(0,10);return (o.fin||o.debut)>=auj}
function remplir(){
  var v={lieu:$('f-lieu').value,niveau:$('f-niveau').value,quand:$('f-quand').value};
  var l=$('f-lieu');l.innerHTML='<option value="">'+t('tous')+'</option>'+D.lieux.map(function(x){return '<option>'+esc(x)+'</option>'}).join('');l.value=v.lieu;
  var n=$('f-niveau');n.innerHTML='<option value="">'+t('tous')+'</option>'+D.niveaux.map(function(x){return '<option value="'+x+'">'+t(x)+'</option>'}).join('');n.value=v.niveau;
  var q=$('f-quand');q.innerHTML='<option value="avenir">'+t('avenir')+'</option><option value="mois">'+t('mois')+'</option>';q.value=v.quand||'avenir';
  ['lieu','age','niveau','quand','prix'].forEach(function(k){$('e-'+k).textContent=t(k)});
}
function ok(o){
  var lieu=$('f-lieu').value,niv=$('f-niveau').value,age=$('f-age').value,prix=$('f-prix').value,q=$('f-quand').value;
  if(!futur(o))return false;
  if(lieu&&o.lieu!==lieu)return false;
  if(niv&&o.niveau!==niv)return false;
  if(age!==''){var a=+age;if(o.age_min!=null&&a<o.age_min)return false;if(o.age_max!=null&&a>o.age_max)return false}
  if(prix!==''&&o.prix!=null&&o.prix>+prix)return false;
  if(q==='mois'){var m=new Date().toISOString().slice(0,7);if(o.debut.slice(0,7)>m||(o.fin||o.debut).slice(0,7)<m)return false}
  return true;
}
function carte(o){
  var ages=o.age_min!=null?(o.age_max!=null?o.age_min+'–'+o.age_max:o.age_min+'+')+' '+t('ans'):t('tout_age');
  var dates=o.fin&&o.fin!==o.debut?t('du')+' '+dt(o.debut)+' '+t('au')+' '+dt(o.fin):dt(o.debut);
  var prix=o.prix!=null?o.prix.toLocaleString(MOIS[L])+' '+(o.devise==='CHF'?'CHF':'€'):'—';
  return '<div class="offre"><h2>'+esc(o.titre)+'</h2><div class="ecole">'+esc(o.ecole)+'</div>'
   +'<div class="ligne"><span>'+esc(o.lieu)+' · '+t(o.pays)+'</span><span>'+dates+'</span><span>'+ages+'</span>'
   +(o.niveau?'<span>'+t(o.niveau)+'</span>':'')+'<span class="prix">'+prix+'</span></div>'
   +'<div class="verif">'+t('verifie')+' '+dt(o.verifie)+' · <a href="'+esc(o.lien)+'" rel="noopener" target="_blank">'+t('voir')+' →</a></div></div>';
}
function dessiner(){
  var r=D.offres.filter(ok);
  $('compte').textContent=r.length+' '+t('n_offres');
  $('liste').innerHTML=r.length?r.map(carte).join(''):'<p class="vide">'+(D.offres.filter(futur).length?t('aucune'):t('vide'))+'</p>';
}
function langue(l){L=l;document.documentElement.lang=l;
  document.querySelectorAll('#langues button').forEach(function(b){b.setAttribute('aria-pressed',b.dataset.lang===l)});
  document.querySelectorAll('[data-t]').forEach(function(e){e.textContent=t(e.dataset.t)});
  $('f-age').placeholder=t('tout_age');remplir();dessiner();try{localStorage.setItem('lang',l)}catch(e){}}
['f-lieu','f-niveau','f-quand','f-age','f-prix'].forEach(function(i){$(i).addEventListener('input',dessiner)});
document.querySelectorAll('#langues button').forEach(function(b){b.addEventListener('click',function(){langue(b.dataset.lang)})});
var l0='fr';try{l0=localStorage.getItem('lang')||(navigator.language||'fr').slice(0,2)}catch(e){}
langue(U[l0]?l0:'fr');
})();
"""


def charger() -> dict:
    if not JSON.exists():
        return {"maj": "", "offres": []}
    return json.loads(JSON.read_text(encoding="utf-8"))


def affichable(o: dict, aujourdhui: date | None = None) -> bool:
    """Une offre se publie si elle a ce qu'il faut pour être vérifiée, n'est pas passée et n'est pas périmée."""
    aujourdhui = aujourdhui or date.today()
    try:
        debut = date.fromisoformat(o["debut"])
        fin = date.fromisoformat(o.get("fin") or o["debut"])
        verifie = date.fromisoformat(o["verifie"])
    except (KeyError, ValueError):
        return False
    if not (o.get("titre") and o.get("ecole") and o.get("lieu") and str(o.get("lien", "")).startswith("https://")):
        return False
    if o.get("pays") not in ("FRA", "SUI"):
        return False
    if fin < aujourdhui or fin < debut:
        return False
    return verifie >= aujourdhui - timedelta(days=PEREMPTION_JOURS)


def construire(d: dict | None = None) -> str:
    d = d if d is not None else charger()
    offres = sorted((o for o in d.get("offres", []) if affichable(o)),
                    key=lambda o: (o["debut"], o["ecole"].lower()))
    donnees = {
        "ui": UI, "offres": offres,
        "lieux": sorted({o["lieu"] for o in offres}),
        "niveaux": [n for n in NIVEAUX if any(o.get("niveau") == n for o in offres)],
    }
    fr = UI["fr"]
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import site_blocks  # la barre du site : un seul endroit
    maj = d.get("maj", "")[:10]
    return (
        '<!doctype html>\n<html lang="fr"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        f"<title>{fr['titre']} — Sailing More</title>"
        '<link rel="canonical" href="https://sailingmore.fr/stages.html">'
        '<meta name="description" content="Stages et cours de voile des écoles et clubs en France et en Suisse : '
        'lieu, âge, niveau, date, prix, lien vers l\'école.">'
        "<style>" + site_blocks.ENTETE_CSS + CSS + "</style></head><body>"
        + site_blocks.entete_site("stages.html", ["fr", "en", "it", "es", "pt", "de"], auto=False)
        + "<div class=\"page\">"
        f'<h1 data-t="titre">{fr["titre"]}</h1><p class="chapo" data-t="chapo">{fr["chapo"]}</p>'
        '<div class="filtres">'
        '<label><span id="e-lieu">Lieu</span><select id="f-lieu"></select></label>'
        '<label><span id="e-age">Âge</span><input id="f-age" type="number" min="3" max="99" inputmode="numeric"></label>'
        '<label><span id="e-niveau">Niveau</span><select id="f-niveau"></select></label>'
        '<label><span id="e-quand">Date</span><select id="f-quand"></select></label>'
        '<label><span id="e-prix">Prix max.</span><input id="f-prix" type="number" min="0" step="10" inputmode="numeric"></label>'
        '</div><div class="compte" id="compte" role="status"></div><div id="liste"></div>'
        f'<p class="pied"><span data-t="pied">{fr["pied"]}</span> '
        '<a href="annonceurs.html">Contact</a>'
        + (f" · {maj}" if maj else "") + "</p></div>"
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
