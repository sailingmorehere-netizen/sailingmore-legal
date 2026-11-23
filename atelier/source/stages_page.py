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
import sys
import os
from datetime import date, timedelta
from pathlib import Path

ICI = Path(os.environ.get("SAILINGMORE_RACINE", "/opt/data"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import carte_epreuves  # noqa: E402

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
        "filtrer": "Filtrer",
        "vide": "Aucune offre n'est publiée pour le moment : le relevé se fait sur les fiches des écoles.",
        "du": "du", "au": "au", "voir": "Voir l'offre →", "jours": "jours", "prix_vide": "prix non publié", "photo": "photo :", "tri": "Trier", "proche": "Au plus près", "prix_croissant": "Prix croissant", "date_proche": "Date", "position_refusee": "Position refusée · pays proposé :", "geoloc": "Autoriser ma position",
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
        "filtrer": "Filters",
        "vide": "No offer is published yet: the list is read from the schools' own pages.",
        "du": "from", "au": "to", "voir": "See the offer →", "jours": "days", "prix_vide": "price not published", "photo": "photo:", "tri": "Sort", "proche": "Nearest first", "prix_croissant": "Lowest price", "date_proche": "Date", "position_refusee": "Location refused · country guessed:", "geoloc": "Use my location",
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
        "filtrer": "Filtra",
        "vide": "Nessuna offerta è ancora pubblicata: l'elenco si legge dalle pagine delle scuole.",
        "du": "dal", "au": "al", "voir": "Vedi l'offerta →", "jours": "giorni", "prix_vide": "prezzo non pubblicato", "photo": "foto:",
        "tri": "Ordina", "proche": "Più vicini", "prix_croissant": "Prezzo crescente", "date_proche": "Data", "position_refusee": "Posizione negata · paese ipotizzato:", "geoloc": "Usa la mia posizione",
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
        "filtrer": "Filtrar",
        "vide": "Todavía no hay ofertas publicadas: la lista se lee de las fichas de las escuelas.",
        "du": "del", "au": "al", "voir": "Ver la oferta →", "jours": "días", "prix_vide": "precio no publicado", "photo": "foto:",
        "tri": "Ordenar", "proche": "Más cercanos", "prix_croissant": "Precio ascendente", "date_proche": "Fecha", "position_refusee": "Ubicación rechazada · país supuesto:", "geoloc": "Usar mi ubicación",
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
        "filtrer": "Filtrar",
        "vide": "Ainda não há ofertas publicadas: a lista é lida das páginas das escolas.",
        "du": "de", "au": "a", "voir": "Ver a oferta →", "jours": "dias", "prix_vide": "preço não publicado", "photo": "foto:",
        "tri": "Ordenar", "proche": "Mais próximos", "prix_croissant": "Preço crescente", "date_proche": "Data", "position_refusee": "Localização recusada · país suposto:", "geoloc": "Usar a minha localização",
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
        "filtrer": "Filtern",
        "vide": "Noch kein Angebot veröffentlicht: die Liste wird von den Seiten der Schulen gelesen.",
        "du": "vom", "au": "bis", "voir": "Zum Angebot →", "jours": "Tage", "prix_vide": "Preis nicht veröffentlicht", "photo": "Foto:", "tri": "Sortieren", "proche": "Am nächsten", "prix_croissant": "Preis aufsteigend", "date_proche": "Datum", "position_refusee": "Standort abgelehnt · Land geschätzt:", "geoloc": "Meinen Standort verwenden",
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
.rech{display:flex;align-items:flex-end;gap:.6rem;margin:.2rem 0 .8rem;flex-wrap:wrap}
.rech .q{flex:1 1 16rem}
.filtre-b{display:none;align-items:center;gap:.45rem;font:inherit;font-size:.86rem;cursor:pointer;
  color:#eef3f7;background:var(--carte);border:1px solid var(--trait);border-radius:10px;padding:.7rem 1rem}
.filtre-b b{font-size:.72rem;background:var(--rouge,#e23a3e);color:#fff;border-radius:999px;padding:.05rem .45rem}
.filtre-b b:empty{display:none}
.filtre-b[aria-expanded="true"]{border-color:var(--rouge,#e23a3e)}
.filtres{display:grid;grid-template-columns:repeat(auto-fit,minmax(9.5rem,1fr));gap:.7rem;background:var(--carte);border:1px solid var(--trait);border-radius:14px;padding:.9rem;margin-bottom:1rem}
@media (max-width:700px){
  .filtres{display:none}
  .filtres.ouvert{display:grid}
  .filtre-b{display:inline-flex}
}
label{display:flex;flex-direction:column;gap:.25rem;font-size:.74rem;letter-spacing:.06em;text-transform:uppercase;color:var(--doux)}
select,input{background:#0b1e30;color:var(--encre);border:1px solid var(--trait);border-radius:9px;padding:.5rem .55rem;font:inherit;font-size:.92rem;min-width:0}
input[type=search]{grid-column:span 2}
.compte{color:var(--doux);font-size:.9rem;margin:.2rem 0 1rem}
.liste{display:grid;gap:.8rem}
.offre{background:var(--carte);border:1px solid var(--trait);border-radius:14px;padding:.9rem 1rem;display:grid;grid-template-columns:1fr auto;gap:.5rem .9rem;align-items:start}
.offre .ph{grid-column:1/-1;width:100%;height:150px;object-fit:cover;border-radius:10px;background:#0b1e30;display:block}
.offre .tete{display:flex;gap:.65rem;align-items:flex-start}
.badge{flex:0 0 auto;width:34px;height:34px;border-radius:9px;display:grid;place-items:center;font-weight:700;font-size:.8rem;letter-spacing:.02em;color:#dff3ef}
.offre h2{font-size:1.02rem;margin:0 0 .2rem;line-height:1.3}
.offre .ecole{color:var(--doux);font-size:.86rem}
.offre .bas{grid-column:1/-1;display:flex;justify-content:space-between;align-items:center;gap:.6rem;flex-wrap:wrap;padding-top:.55rem;border-top:1px solid var(--trait);font-size:.86rem;color:var(--doux)}
.offre .prix{font-size:1.05rem;font-weight:600;color:var(--encre);white-space:nowrap;text-align:right}
.offre .ligne{display:flex;flex-wrap:wrap;gap:.35rem .9rem;font-size:.84rem;color:var(--doux);grid-column:1/-1}
.offre a.lien{color:var(--accent);text-decoration:none;font-size:.88rem}
.marque{font-size:.72rem;border:1px solid var(--trait);border-radius:99px;padding:.06rem .45rem;color:var(--doux)}
.pied{margin-top:2rem;color:var(--doux);font-size:.82rem;border-top:1px solid var(--trait);padding-top:1rem}
.vide{color:var(--doux);padding:2rem 0}
.carte-regates h2{font-size:.74rem;letter-spacing:.06em;text-transform:uppercase;color:var(--doux);font-weight:400;margin:0 0 .5rem}
__CARTE_CSS__
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


def _avec_position(o: dict) -> dict:
    """Ajoute lat/lon (et precision='pays' si c'est le centre du pays) quand le lieu est connu. Sans position,
    l'offre reste dans la liste et n'a simplement pas de pastille."""
    if o.get("lat") is not None and o.get("lon") is not None:
        return o
    import regates_page  # import tardif : la table des ports pèse, et stages n'en a besoin qu'ici
    pos = regates_page.position({"ville": o.get("lieu") or "", "pays": o.get("pays") or ""})
    if not pos:
        return o
    return {**o, "lat": pos[0], "lon": pos[1], **({"precision": "pays"} if pos[2] else {})}


def construire(d: dict | None = None) -> str:
    d = d if d is not None else charger()
    offres = [o for o in d.get("offres", []) if affichable(o)]
    offres = [_avec_position(o) for o in offres]
    offres.sort(key=lambda o: (o.get("debut") or "9999-12-31", o.get("prix_eur") or 0))
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
             "<link rel=\"canonical\" href=\"https://sailingmore.fr/stages.html\">"
             f"{__import__('jsonld').page_simple('stages.html', UI['fr']['titre'])}"
             "<meta name=\"description\" content=\"Stages et cours de voile vendus par des écoles "
             "européennes : prix publiés, destination, langue, lien direct vers la fiche de l'école.\">"
             + __import__('jsonld').social(
                 "stages.html", "Stages de voile — Sailing More",
                 "Stages et cours de voile vendus par des écoles européennes : prix publiés, destination, "
                 "langue, lien direct vers la fiche de l'école.") +
             f"<style>{CSS}</style></head><body><main class=\"page\">"
             f"<a class=\"retour\" href=\"/\" data-t=\"retour\">{H.escape(UI['fr']['retour'])}</a>"
             "<div id=\"langues\"></div>"
             f"<h1 data-t=\"titre\">{H.escape(UI['fr']['titre'])}</h1>"
             f"<p class=\"chapo\" data-t=\"chapo\">{H.escape(UI['fr']['chapo'])}</p>"
             "<section class=\"rech\">"
             "<label class=\"q\"><span data-t=\"chercher\">Chercher</span><input id=\"f-q\" type=\"search\"></label>"
             "<button type=\"button\" class=\"filtre-b\" id=\"filtre-b\" aria-expanded=\"false\" "
             "aria-controls=\"filtres\"><span data-t=\"filtrer\">Filtrer</span> <b id=\"filtre-n\"></b></button>"
             "</section>"
             "<section class=\"filtres\" id=\"filtres\">"
             "<label><span data-t=\"langue\">Langue</span><select id=\"f-langue\"></select></label>"
             "<label><span data-t=\"destination\">Destination</span><select id=\"f-pays\"></select></label>"
             "<label><span data-t=\"pays_ecole\">Pays de l'école</span><select id=\"f-pays-ecole\"></select></label>"
             "<label><span data-t=\"ecole\">École</span><select id=\"f-ecole\"></select></label>"
             "<label><span data-t=\"type\">Type</span><select id=\"f-type\"></select></label>"
             "<label><span data-t=\"niveau\">Niveau</span><select id=\"f-niveau\"></select></label>"
             "<label><span data-t=\"quand\">Date</span><select id=\"f-quand\"></select></label>"
             "<label><span data-t=\"tri\">Trier</span><select id=\"f-tri\"></select></label>"
             "<label><span data-t=\"prix\">Prix max.</span><input id=\"f-prix\" type=\"number\" min=\"0\" step=\"50\" inputmode=\"numeric\"></label>"
             "</section>"
             + carte_epreuves.html() +
             "<p class=\"compte\" id=\"compte\"></p><div class=\"liste\" id=\"liste\"></div>"
             f"<p class=\"pied\" data-t=\"pied\">{H.escape(UI['fr']['pied'])}</p>"
             "</main>"
             "<script id=\"donnees\" type=\"application/json\">"
             + json.dumps(d, ensure_ascii=False).replace("</", "<\\/")
             + "</script><script>" + carte_epreuves.js() + JS + "</script></body></html>")
    return corps


CSS = CSS.replace("__CARTE_CSS__", carte_epreuves.CSS)

JS = r"""
var D=JSON.parse(document.getElementById('donnees').textContent),U=D.ui;
var L='fr';try{L=localStorage.getItem('lang')||(navigator.language||'fr').slice(0,2)}catch(e){}
if(!U[L])L='en';
function t(k){return (U[L]&&U[L][k])||U.fr[k]||k}
function esc(s){return String(s==null?'':s).replace(/[&<>"']/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]})}
function sigle(nom){var m=(nom||'?').replace(/[^\p{L} ]/gu,'').split(/\s+/).filter(Boolean);
  return m.length>1?(m[0][0]+m[1][0]).toUpperCase():((m[0]||'?').slice(0,2).toUpperCase())}
function teinte(s){var h=0;s=s||'';for(var i=0;i<s.length;i++)h=(h*31+s.charCodeAt(i))%360;return h}
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
  var tri=document.getElementById('f-tri'),gt=tri.value;
  tri.innerHTML='<option value="proche">'+t('proche')+'</option><option value="prix">'+t('prix_croissant')+
    '</option><option value="date">'+t('date_proche')+'</option>';
  tri.value=gt||mem('tri','proche');
  var q=document.getElementById('f-quand'),gq=q.value;
  q.innerHTML='<option value="">'+t('tous')+'</option><option value="avenir">'+t('avenir')+'</option><option value="mois">'+t('mois')+'</option>';
  q.value=gq;
  var fl=document.getElementById('f-langue');
  if(fl.value===''){fl.value=mem('langue', D.langues_presentes.indexOf(navLang)>=0?navLang:'');if(fl.value==='')fl.value='';}
  var fp=document.getElementById('f-pays');
  if(fp.value===''){var d=mem('pays',D.pays.some(function(p){return p[0]===defPays})?defPays:'');fp.value=d;}
  /* les défauts se relâchent si le couple langue + destination ne laisse aucune offre */
  var qp=fp.value,ql=fl.value;
  function reste(lg,py){return D.offres.some(function(o){return (!lg||o.langue===lg)&&(!py||o.pays===py)})}
  if(!reste(ql,qp)){if(reste('',qp))fl.value='';else if(reste(ql,''))fp.value='';else{fl.value='';fp.value=''}}
  /* Le choix de langue de la page en menu déroulant, comme la barre du site (Nicolas, 23/11/2026). */
  var NOMS={fr:'Français',en:'English',de:'Deutsch',it:'Italiano',es:'Español',pt:'Português'};
  var l=document.getElementById('langues');
  l.innerHTML='<select id="lng-sel" aria-label="Langue de la page" style="background:transparent;color:inherit;font:inherit;font-size:.8rem;border:1px solid rgba(255,255,255,.34);border-radius:.4rem;padding:.5rem .6rem;min-height:38px;cursor:pointer">'
    +Object.keys(U).map(function(c){return '<option value="'+c+'"'+(c===L?' selected':'')+'>'+(NOMS[c]||c.toUpperCase())+'</option>'}).join('')+'</select>';
  l.querySelector('select').onchange=function(){L=this.value;try{localStorage.setItem('lang',L)}catch(e){}remplir();dessiner()};
}
/* Position du visiteur : le navigateur d'abord (il demande l'accord), l'adresse IP ensuite si elle
   est refusée ou indisponible. Aucune position n'est envoyée ni conservée : elle sert à trier. */
var POS=null;
function haversine(a,b,c,d){var R=6371,r=Math.PI/180;
  var dLa=(c-a)*r,dLo=(d-b)*r,la1=a*r,la2=c*r;
  var h=Math.sin(dLa/2)*Math.sin(dLa/2)+Math.cos(la1)*Math.cos(la2)*Math.sin(dLo/2)*Math.sin(dLo/2);
  return 2*R*Math.asin(Math.sqrt(h))}
function distance(o){if(!POS||o.lat==null||o.lon==null)return null;return haversine(POS[0],POS[1],o.lat,o.lon)}
function poserPosition(){
  function parIP(){
    fetch('https://ipwho.is/?fields=latitude,longitude,success').then(function(r){return r.json()})
      .then(function(d){if(d&&d.success&&d.latitude!=null){POS=[d.latitude,d.longitude,'ip'];dessiner()}})
      .catch(function(){});
  }
  if(!navigator.geolocation){parIP();return}
  navigator.geolocation.getCurrentPosition(
    function(p){POS=[p.coords.latitude,p.coords.longitude,'gps'];dessiner()},
    function(){parIP()}, {timeout:6000,maximumAge:600000});
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
  var ordre=document.getElementById('f-tri').value;
  var sansPos=function(o){return (!POS||o.lat==null)?1:0};
  var chezNous=function(o){return (defPays&&o.pays===defPays)?0:1};
  vus.sort(function(a,b){
    if(ordre==='prix')return ((a.prix_eur!=null?a.prix_eur:1e9)-(b.prix_eur!=null?b.prix_eur:1e9));
    if(ordre==='date')return ((a.debut||'9999')<(b.debut||'9999')?-1:(a.debut||'9999')>(b.debut||'9999')?1:0);
    if(!POS){var ca=chezNous(a),cb=chezNous(b);if(ca!==cb)return ca-cb;
      return ((a.debut||'9999')<(b.debut||'9999')?-1:(a.debut||'9999')>(b.debut||'9999')?1:0)}
    var sp=sansPos(a),sb=sansPos(b);if(sp!==sb)return sp-sb;
    var da=distance(a),db=distance(b);return (da==null?1e9:da)-(db==null?1e9:db);
  });
  var html=vus.map(function(o){
    var dates=!o.debut?t('dates_ecole'):(o.fin&&o.fin!==o.debut?t('du')+' '+dt(o.debut)+' '+t('au')+' '+dt(o.fin):dt(o.debut));
    var ou=o.lieu?(o.lieu===o.pays_nom?o.lieu:o.lieu+' · '+o.pays_nom):(o.region||o.pays_nom);
    var lng=o.langue?(D.langues[o.langue]||o.langue.toUpperCase()):'—';
    var d=distance(o);
    var loin=(d==null?'':(o.precision==='pays'?' · ~':' · ')+Math.round(d).toLocaleString(L)+' km');
    var marque=o.langue&&(o.langue_src==='pays'||o.langue_src==='ecole')?' <span class="marque" title="'+esc(t('langue_supposee'))+'">?</span>':'';
    return '<article class="offre">'
      +(o.image?'<a class="phl" href="'+esc(o.lien)+'" rel="noopener nofollow" target="_blank" style="grid-column:1/-1"><img class="ph" loading="lazy" src="'+esc(o.image)+'" alt="'+esc(o.titre+' — '+o.ecole)+'"></a>':'')
      +'<div class="tete"><span class="badge" style="background:hsl('+teinte(o.ecole_slug)+',38%,22%);border:1px solid hsl('+teinte(o.ecole_slug)+',45%,34%)">'+esc(sigle(o.ecole))+'</span>'
      +'<div><h2>'+esc(o.titre)+'</h2>'
      +'<div class="ecole">'+esc(o.ecole)+(o.ecole_pays_nom?' · '+esc(o.ecole_pays_nom):'')+'</div></div></div>'
      +'<div class="prix">'+(o.prix!=null?o.prix.toLocaleString(L)+' '+sym(o.devise):'<span style="font-weight:400;font-size:.85rem">'+t('prix_vide')+'</span>')+'</div>' 
      +'<div class="ligne"><span>'+esc(ou)+loin+'</span><span>'+dates+'</span>' 
      +(o.duree_jours?'<span>'+o.duree_jours+' '+t('jours')+'</span>':'')
      +'<span>'+esc(lng)+marque+'</span>'
      +(o.niveau?'<span>'+t(o.niveau)+'</span>':'')+'</div>'
      +'<div class="bas"><span>'+t('verifie')+' '+dt(o.verifie)
      +(o.image?' · '+t('photo')+' '+esc(o.ecole):'')+'</span>' 
      +'<a class="lien" href="'+esc(o.lien)+'" rel="noopener nofollow" target="_blank">'+t('voir')+'</a></div>'
      +'</article>';
  }).join('');
  document.getElementById('liste').innerHTML=html||('<p class="vide">'+(D.offres.length?t('aucune'):t('vide'))+'</p>');
  var MT={fr:{groupe:'{n} offres à cet endroit',aide:"Touchez une pastille pour voir l'offre ; un rond numéroté regroupe plusieurs offres.",compte:'{n} sur la carte, {m} sans position (elles figurent dans la liste ci-dessous).',titre:'Les stages sur la carte'},
    en:{groupe:'{n} offers at this place',aide:'Tap a dot to see the offer; a numbered circle groups several offers.',compte:'{n} on the map, {m} without a position (they are in the list below).',titre:'Courses on the map',plus:'and {n} more'},
    de:{groupe:'{n} Angebote an diesem Ort',aide:'Punkt antippen, um das Angebot zu sehen; ein nummerierter Kreis fasst mehrere zusammen.',compte:'{n} auf der Karte, {m} ohne Position (sie stehen in der Liste unten).',titre:'Die Kurse auf der Karte'},
    it:{groupe:'{n} offerte in questo luogo',aide:"Tocca un punto per vedere l'offerta; un cerchio numerato ne raggruppa più d'una.",compte:"{n} sulla mappa, {m} senza posizione (sono nell'elenco qui sotto).",titre:'I corsi sulla mappa'},
    es:{groupe:'{n} ofertas en este lugar',aide:'Toca un punto para ver la oferta; un círculo numerado agrupa varias.',compte:'{n} en el mapa, {m} sin posición (están en la lista de abajo).',titre:'Los cursos en el mapa'},
    pt:{groupe:'{n} ofertas neste local',aide:'Toca num ponto para ver a oferta; um círculo numerado agrupa várias.',compte:'{n} no mapa, {m} sem posição (estão na lista abaixo).',titre:'Os cursos no mapa'}};
  if(!window.carteStages)window.carteStages=CarteEpreuves.creer({textes:MT});
  var dlong=function(s){try{return new Intl.DateTimeFormat(L,{day:'numeric',month:'long',year:'numeric'}).format(new Date(s+'T12:00:00'))}catch(x){return s}};
  window.carteStages.montre(vus.filter(function(o){return o.lat!=null&&o.lon!=null}).map(function(o){
    var dates=!o.debut?t('dates_ecole'):(o.fin&&o.fin!==o.debut?t('du')+' '+dt(o.debut)+' '+t('au')+' '+dt(o.fin):dt(o.debut));
    var ou=o.lieu?(o.lieu===o.pays_nom?o.lieu:o.lieu+' · '+o.pays_nom):(o.region||o.pays_nom);
    return {lat:o.lat,lon:o.lon,ap:o.precision==='pays',champ:false,
      label:o.titre+', '+(o.lieu||o.pays_nom||'')+(o.debut?', '+dlong(o.debut):''),
      html:'<b>'+esc(o.titre)+'</b> — '+esc(ou)+' · '+dates+(o.prix!=null?' · '+o.prix.toLocaleString(L)+' '+sym(o.devise):'')
        +' · <a href="'+esc(o.lien)+'" rel="noopener nofollow" target="_blank">'+t('voir')+'</a>'};
  }),vus.length);
  var ne=new Set(vus.map(function(o){return o.ecole_slug})).size;
  var txt=t('compte').replace('{n}',vus.length).replace('{e}',ne);
  if(ne===1){txt=txt.replace(/1 (schools|écoles|scuole|escuelas|escolas|Schulen)/,'1 $1').replace('1 schools','1 school').replace('1 écoles','1 école').replace('1 scuole','1 scuola').replace('1 escuelas','1 escuela').replace('1 escolas','1 escola').replace('1 Schulen','1 Schule')}
  if(vus.length===1){txt=txt.replace(/^1 (offers|offres|offerte|ofertas|ofertas|Angebote)/,'1 offre').replace(/^1 (offers|offerte|ofertas|Angebote)/,'1 offre')}
  document.getElementById('compte').textContent=txt;
}
['f-q','f-langue','f-pays','f-pays-ecole','f-ecole','f-type','f-niveau','f-quand','f-prix','f-tri'].forEach(function(i){
  var e=document.getElementById(i);if(e){e.addEventListener('input',dessiner);e.addEventListener('change',dessiner)}});
document.getElementById('f-tri').addEventListener('change',function(){garde('tri',this.value)});

/* Les filtres se replient sous un bouton sur téléphone, comme chez Les Glénans et les places de
   marché (23/11/2026) : la recherche reste seule visible, le bouton dit combien de filtres sont
   actifs, et le panneau s'ouvre au tap. Sur ordinateur la grille reste dépliée. */
var fb = document.getElementById('filtre-b'), zoneF = document.getElementById('filtres');
var DEFAUT = {};
function majBadge(){
  var n = 0;
  Object.keys(DEFAUT).forEach(function(id){
    var e = document.getElementById(id); if(!e) return;
    if((e.value||'').trim() !== (DEFAUT[id]||'')) n++;
  });
  var b = document.getElementById('filtre-n');
  if(b) b.textContent = n ? String(n) : '';
}
remplir();
if(fb && zoneF){
  fb.addEventListener('click', function(){
    var ouvert = zoneF.classList.toggle('ouvert');
    fb.setAttribute('aria-expanded', ouvert ? 'true' : 'false');
  });
  ['f-q','f-langue','f-pays','f-pays-ecole','f-ecole','f-type','f-niveau','f-quand','f-prix'].forEach(function(id){
    var e = document.getElementById(id);
    DEFAUT[id] = e ? e.value : '';
    if(e) e.addEventListener('change', majBadge);
  });
  majBadge();
}
dessiner();poserPosition();
"""

SITE = ICI / "projets/sailingmore/site"


IMAGES = ICI / "projets/sailingmore/stages-img"


TEXTES_BLOC = {
    "fr": {"titre": "Stages près de chez vous", "tous": "Tous les stages →", "prix": "prix non publié", "dist": "km"},
    "en": {"titre": "Courses near you", "tous": "All courses →", "prix": "price not published", "dist": "km"},
    "de": {"titre": "Kurse in Ihrer Nähe", "tous": "Alle Kurse →", "prix": "Preis nicht veröffentlicht", "dist": "km"},
    "it": {"titre": "Corsi vicino a te", "tous": "Tutti i corsi →", "prix": "prezzo non pubblicato", "dist": "km"},
    "es": {"titre": "Cursos cerca de ti", "tous": "Todos los cursos →", "prix": "precio no publicado", "dist": "km"},
    "pt": {"titre": "Cursos perto de si", "tous": "Todos os cursos →", "prix": "preço não publicado", "dist": "km"},
}

# Bloc « stages près de chez vous » : un script autonome, chargé en `defer`, qui ne télécharge le JSON compact
# que lorsque le bloc entre dans l'écran. Même ordre de position que stages.html ; rien n'est conservé ni envoyé.
JS_BLOC = r"""(function(){
var T=__TEXTES__;
var host=document.getElementById('stages-proches');if(!host)return;
var L='fr';try{L=localStorage.getItem('lang')||document.documentElement.lang||(navigator.language||'fr')}catch(e){}
L=String(L).slice(0,2).toLowerCase();if(!T[L])L='en';var X=T[L];
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
  var l=DATA.o.filter(function(o){return !o[7]||o[7]>=a});
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
"""

MARQUE_BLOC = "<!--stages-proches-->"
BLOC_HTML = (MARQUE_BLOC + '<section id="stages-proches" style="max-width:60rem;margin:2rem auto;padding:0 1.2rem" hidden></section>'
             '<script src="/stages-proches.js" defer></script>')
PAGES_BLOC = ("index.html", "regates.html", "regles-de-course.html", "lexique.html", "cours.html", "bateaux.html")


def ecrire_bloc(dossier: Path, offres: list[dict]) -> int:
    """JSON compact + script du bloc « près de chez vous », à côté de stages.html. Une ligne par offre :
    [lat, lon, approx(0/1), titre, école, lieu, pays, début, prix, devise, lien, image, pays ISO3]."""
    lignes = []
    for o in offres:
        o = _avec_position(o)
        if o.get("lat") is None or o.get("lon") is None or not o.get("lien"):
            continue
        lignes.append([round(o["lat"], 2), round(o["lon"], 2), 1 if o.get("precision") != "ville" else 0,
                       o.get("titre") or "", o.get("ecole") or "", o.get("lieu") or "", o.get("pays_nom") or "",
                       o.get("debut") or "", o.get("prix"), o.get("devise") or "", o["lien"],
                       o.get("image") or "", o.get("pays") or ""])
    (dossier / "stages-proches.json").write_text(
        json.dumps({"maj": date.today().isoformat(), "o": lignes}, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8")
    (dossier / "stages-proches.js").write_text(
        JS_BLOC.replace("__TEXTES__", json.dumps(TEXTES_BLOC, ensure_ascii=False)), encoding="utf-8")
    return len(lignes)


def injecter_bloc(dossier: Path = SITE) -> list[str]:
    """Ajoute (une seule fois) le bloc avant `</body>` des autres pages. Idempotent : repéré par sa marque."""
    faites = []
    for nom in PAGES_BLOC:
        p = dossier / nom
        if not p.exists():
            continue
        h = p.read_text(encoding="utf-8")
        if MARQUE_BLOC in h or "</body>" not in h:
            continue
        p.write_text(h.replace("</body>", BLOC_HTML + "</body>", 1), encoding="utf-8")
        faites.append(nom)
    return faites


def ecrire_page(dossier: Path = SITE) -> int:
    """Écrit `stages.html` dans `dossier` — appelé par `accueil_site.sortir_le_site`.

    Les photos des stages voyagent avec la page : recopiées une fois, elles ne sont pas relues au
    prochain envoi (mêmes noms, même contenu).
    """
    dossier.mkdir(parents=True, exist_ok=True)
    d = charger()
    (dossier / "stages.html").write_text(construire(d), encoding="utf-8")
    if IMAGES.exists():
        cible = dossier / "stages-img"
        cible.mkdir(exist_ok=True)
        for o in d.get("offres", []):
            nom = (o.get("image") or "").split("/")[-1]
            if not nom:
                continue
            src, dst = IMAGES / nom, cible / nom
            if src.exists() and (not dst.exists() or dst.stat().st_size != src.stat().st_size):
                dst.write_bytes(src.read_bytes())
    ecrire_bloc(dossier, [o for o in d.get("offres", []) if affichable(o)])
    return sum(1 for o in d.get("offres", []) if affichable(o))


if __name__ == "__main__":
    print(f"stages.html : {ecrire_page()} offre(s) publiable(s)")
