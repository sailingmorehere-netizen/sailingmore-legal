#!/usr/bin/env python3
# © 2026 Sailing More — tous droits réservés. All rights reserved.
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

import html as H
import json
import re
import sys
import os
from datetime import date, timedelta
from pathlib import Path

ICI = Path(os.environ.get("SAILINGMORE_RACINE", "/opt/data"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import clics_sortants  # noqa: E402  (comptage des clics sortants, sans cookie)
import carte_epreuves  # noqa: E402

import stages_niveaux  # noqa: E402

JSON = ICI / "projets/sailingmore/stages.json"
AJOUT = ICI / "projets/sailingmore/stages-ajout-2026-11-25.json"
PEREMPTION_JOURS = 60
# Échelle du niveau (sprint 1, 23/11/2026) : définie et documentée dans `stages_niveaux.py`, lue
# dans le titre de l'offre à chaque construction. L'ancienne valeur du relevé (debutant /
# intermediaire / confirme, en partie déduite de la durée) est gardée telle quelle dans
# `niveau_releve`, sans être affichée.
NIVEAUX = stages_niveaux.NIVEAUX
LIBELLES_NIVEAU = {
    "fr": {"decouverte": "Découverte", "equipier": "Équipier", "chef-de-bord": "Chef de bord",
           "hauturier": "Hauturier", "moniteur": "Moniteur", "certif": "Certification",
           "equivalences": "Équivalences des diplômes de voile →", "comparatif": "Comparer les stages par prix au jour →"},
    "en": {"decouverte": "Discovery", "equipier": "Crew", "chef-de-bord": "Skipper",
           "hauturier": "Offshore", "moniteur": "Instructor", "certif": "Certification",
           "equivalences": "Sailing qualification equivalences →", "comparatif": "Compare courses by price per day →"},
    "it": {"decouverte": "Scoperta", "equipier": "Equipaggio", "chef-de-bord": "Skipper",
           "hauturier": "Altura", "moniteur": "Istruttore", "certif": "Certificazione",
           "equivalences": "Equivalenze dei brevetti di vela →", "comparatif": "Confronta i corsi per prezzo al giorno →"},
    "es": {"decouverte": "Descubrimiento", "equipier": "Tripulante", "chef-de-bord": "Patrón",
           "hauturier": "Altura", "moniteur": "Instructor", "certif": "Certificación",
           "equivalences": "Equivalencias de titulaciones de vela →", "comparatif": "Comparar cursos por precio al día →"},
    "pt": {"decouverte": "Descoberta", "equipier": "Tripulante", "chef-de-bord": "Skipper",
           "hauturier": "Oceano", "moniteur": "Instrutor", "certif": "Certificação",
           "equivalences": "Equivalências de cartas de vela →", "comparatif": "Comparar cursos por preço por dia →"},
    "de": {"decouverte": "Schnuppern", "equipier": "Crew", "chef-de-bord": "Skipper",
           "hauturier": "Hochsee", "moniteur": "Ausbilder", "certif": "Zertifikat",
           "equivalences": "Gleichwertigkeit von Segelscheinen →", "comparatif": "Kurse nach Tagespreis vergleichen →"},
}


def avec_niveau(o: dict) -> dict:
    """L'offre avec `niveau` et `certif` lus dans son titre (vides si le titre ne permet pas de trancher)."""
    out = {**o, **stages_niveaux.classer(o.get("titre") or "")}
    if o.get("niveau") and o.get("niveau") not in NIVEAUX:
        out["niveau_releve"] = o["niveau"]
    return out

UI = {
 "fr": {"titre": "Stages de voile", "retour": "← Sailing More",
        "chapo": "Les stages et cours que vendent des écoles de voile européennes, sur leurs propres eaux comme aux Antilles, en Atlantique ou en mer du Nord. Chaque offre renvoie à la fiche de l'école, qui fait foi.",
        "langue": "Langue du stage", "destination": "Destination", "pays_ecole": "Pays de l'école",
        "ecole": "École", "niveau": "Niveau", "quand": "Date", "prix": "Prix max.",
        "tous": "Toutes", "tout_age": "Tout âge", "avenir": "À venir", "mois": "Ce mois-ci",
        "chercher": "Chercher (école, stage, lieu)", "dates_ecole": "dates chez l'école",
        "compte": "{n} offres · {e} écoles", "aucune": "Aucune offre ne répond à ces filtres.", "effacer": "Tout effacer",
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
        "compte": "{n} offers · {e} schools", "aucune": "No offer matches these filters.", "effacer": "Clear all",
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
        "compte": "{n} offerte · {e} scuole", "aucune": "Nessuna offerta con questi filtri.", "effacer": "Cancella tutto",
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
        "compte": "{n} ofertas · {e} escuelas", "aucune": "Ninguna oferta con estos filtros.", "effacer": "Borrar todo",
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
        "compte": "{n} ofertas · {e} escolas", "aucune": "Nenhuma oferta com estes filtros.", "effacer": "Limpar tudo",
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
        "compte": "{n} Angebote · {e} Schulen", "aucune": "Kein Angebot mit diesen Filtern.", "effacer": "Alles zurücksetzen",
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
/* Le bouton « Enregistrer » des favoris arrive dans l'en-tête de la carte : il se pose à droite,
   pas au milieu du titre (25/11/2026). */
.offre .tete .fav-btn{margin-left:auto;align-self:flex-start;white-space:nowrap}
.offre .ecole a{color:inherit;text-decoration:none;border-bottom:1px solid rgba(95,211,196,.28)}
.offre .ecole a:hover{border-bottom-color:var(--accent)}
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
/* Comparateur intégré (25/11/2026) : un onglet collé au bord droit, visible dès l'ouverture de la page,
   qui ouvre un panneau. L'onglet ne dépend d'aucun script pour s'afficher ; le panneau se remplit à
   l'ouverture. Sur téléphone l'onglet devient une pastille en bas à droite. */
.cmp-o{position:fixed;right:0;top:44%;z-index:65;display:flex;align-items:center;gap:.55rem;writing-mode:vertical-rl;
  background:var(--accent);color:#04202b;border:0;border-radius:11px 0 0 11px;padding:.9rem .55rem;
  font:inherit;font-size:.8rem;font-weight:700;letter-spacing:.08em;text-transform:uppercase;cursor:pointer;
  box-shadow:0 8px 26px rgba(0,0,0,.45)}
.cmp-o:hover{filter:brightness(1.07)}
.cmp-o .cmp-n{writing-mode:horizontal-tb;background:#04202b;color:var(--accent);border-radius:99px;padding:.06rem .42rem;font-size:.72rem}
.cmp-o .cmp-n:empty{display:none}
@media (max-width:560px){
  .cmp-o{top:auto;bottom:1rem;right:1rem;writing-mode:horizontal-tb;border-radius:99px;padding:.62rem .95rem;font-size:.78rem}
}
.cmp-v{position:fixed;inset:0;z-index:75;background:rgba(4,12,20,.62)}
.cmp-v[hidden]{display:none}
.cmp-p{position:fixed;top:0;right:0;bottom:0;z-index:80;width:min(42rem,100vw);background:var(--fond);
  border-left:1px solid var(--trait);display:flex;flex-direction:column;transform:translateX(102%);visibility:hidden;
  transition:transform .22s ease,visibility .22s}
.cmp-p.ouvert{transform:none;visibility:visible}
@media (prefers-reduced-motion:reduce){.cmp-p{transition:none}}
.cmp-h{display:flex;align-items:center;justify-content:space-between;gap:.6rem;padding:.85rem 1rem;
  border-bottom:1px solid var(--trait);background:var(--carte)}
.cmp-h h2{font-size:1rem;margin:0}
.cmp-x{background:none;border:1px solid var(--trait);color:var(--encre);border-radius:9px;width:34px;height:34px;
  font:inherit;font-size:.95rem;line-height:1;cursor:pointer;flex:0 0 auto}
.cmp-c{flex:1;overflow:auto;padding:1rem;-webkit-overflow-scrolling:touch}
.cmp-aide{color:var(--doux);font-size:.85rem;margin:0 0 .9rem}
.cmp-sous{font-size:.72rem;letter-spacing:.06em;text-transform:uppercase;color:var(--doux);font-weight:400;margin:1.5rem 0 .55rem}
.cmp-tab{overflow-x:auto;border:1px solid var(--trait);border-radius:12px;background:var(--carte)}
table.cmp-t{border-collapse:collapse;width:100%;font-size:.85rem}
table.cmp-t th,table.cmp-t td{border-bottom:1px solid var(--trait);padding:.5rem .6rem;text-align:left;vertical-align:top}
table.cmp-t th{font-weight:600}
table.cmp-t .lab{position:sticky;left:0;z-index:2;background:var(--carte);color:var(--doux);font-weight:400;
  font-size:.7rem;letter-spacing:.05em;text-transform:uppercase;white-space:nowrap}
table.cmp-t td{min-width:9.5rem}
table.cmp-t .cmp-meilleur{color:var(--accent);font-weight:700}
table.cmp-t tr:last-child th,table.cmp-t tr:last-child td{border-bottom:0}
.cmp-l{display:grid;gap:.35rem;margin:0;padding:0;list-style:none}
.cmp-l button{display:flex;gap:.55rem;align-items:flex-start;width:100%;text-align:left;background:var(--carte);
  border:1px solid var(--trait);color:inherit;border-radius:10px;padding:.5rem .6rem;font:inherit;font-size:.82rem;cursor:pointer}
.cmp-l button[aria-pressed="true"]{border-color:var(--accent);box-shadow:inset 0 0 0 1px var(--accent)}
.cmp-l button:disabled{opacity:.4;cursor:not-allowed}
.cmp-l b{display:block;font-weight:600;font-size:.86rem}
.cmp-l span{color:var(--doux)}
.cmp-f{border-top:1px solid var(--trait);padding:.7rem 1rem;display:flex;justify-content:flex-end;gap:.6rem;background:var(--carte)}
.cmp-b{font:inherit;font-size:.8rem;cursor:pointer;background:transparent;color:var(--accent);
  border:1px solid var(--trait);border-radius:99px;padding:.28rem .65rem}
.cmp-b[aria-pressed="true"]{background:var(--accent);color:#04202b;border-color:var(--accent)}
.offre .bas-d{display:flex;align-items:center;gap:.55rem}
/* Offres rangées par école, servies par lots (25/11/2026). */
.grp{border:1px solid var(--trait);border-radius:14px;background:var(--fond);margin:0 0 1rem;overflow:hidden}
.grp>summary{cursor:pointer;list-style:none}
.grp>summary::-webkit-details-marker{display:none}
.grp>summary::after{content:'▾';margin-left:auto;color:var(--doux);font-size:.9rem;transition:transform .18s}
.grp[open]>summary::after{transform:rotate(180deg)}
.grp-t{display:flex;align-items:center;gap:.6rem;padding:.65rem .85rem;background:var(--carte);border-bottom:1px solid var(--trait);flex-wrap:wrap}
.grp>summary.grp-t{border-bottom:0}
.grp[open]>summary.grp-t{border-bottom:1px solid var(--trait)}
.grp-n{min-width:0}
.grp-n h2{font-size:.98rem;margin:0;line-height:1.2}
.grp-n .n{color:var(--doux);font-size:.78rem}
.grp-t .des{margin-left:auto;color:var(--doux);font-size:.8rem;white-space:nowrap}
.grp-t .des b{color:var(--encre);font-weight:700}
.grp-l{display:grid;gap:.7rem;padding:.8rem}
.grp-l .offre{background:var(--carte);border:1px solid var(--trait)}
.ses{border-top:1px solid var(--trait)}
.ses:first-of-type{border-top:0}
.ses>summary{display:flex;align-items:center;gap:.55rem;cursor:pointer;padding:.6rem .1rem;list-style:none}
.ses>summary::-webkit-details-marker{display:none}
.ses>summary::after{content:'▾';margin-left:auto;color:var(--doux);font-size:.8rem;transition:transform .18s}
.ses[open]>summary::after{transform:rotate(180deg)}
.ses-t{font-size:.72rem;letter-spacing:.07em;text-transform:uppercase;color:var(--doux)}
.ses>summary:hover .ses-t{color:var(--encre)}
.ses-n{font-size:.7rem;color:var(--doux);opacity:.75}
.ses-c{display:grid;gap:.7rem;padding:.15rem 0 .9rem}
.tab-ecole{width:100%;border-collapse:collapse;font-size:.9rem;margin:1rem 0}
.tab-ecole th,.tab-ecole td{border-bottom:1px solid var(--trait);padding:.5rem .6rem;text-align:left;vertical-align:top}
.tab-ecole th{font-size:.72rem;letter-spacing:.06em;text-transform:uppercase;color:var(--doux);font-weight:500}
.tab-ecole td.p{white-space:nowrap;font-weight:600}
.tab-ecole a{color:var(--encre);text-decoration:none;border-bottom:1px solid rgba(95,211,196,.35)}
.tab-ecole a:hover{border-bottom-color:var(--accent)}
.offre .dates{grid-column:1/-1;color:var(--accent);font-size:.84rem;font-weight:600;letter-spacing:.01em;margin:.1rem 0 .1rem}
.grp-l .sous{font-size:.72rem;letter-spacing:.07em;text-transform:uppercase;color:var(--doux);font-weight:500;
  margin:.9rem 0 .1rem;display:flex;align-items:baseline;gap:.5rem}
.grp-l .sous:first-child{margin-top:0}
.grp-l .sous span{font-size:.7rem;color:var(--doux);opacity:.75;letter-spacing:0}
.grp-plus,.liste-plus{font:inherit;font-size:.82rem;cursor:pointer;background:transparent;color:var(--accent);border:1px dashed var(--trait);border-radius:10px;padding:.55rem .8rem}
.grp-plus:hover,.liste-plus:hover{border-style:solid}
.liste-plus{display:block;width:100%;margin:1rem 0 0;padding:.8rem;font-size:.88rem;background:var(--carte);border-style:solid}
@media (max-width:560px){.grp-t .des{margin-left:0}}
__CARTE_CSS__
@media(max-width:560px){input[type=search]{grid-column:1/-1}.offre{grid-template-columns:1fr}}
"""


def charger() -> dict:
    if not JSON.exists():
        return {"offres": []}
    d = json.loads(JSON.read_text(encoding="utf-8"))
    # Les offres trouvées à la main le 25/11/2026 vivent dans leur propre fichier : le relevé
    # automatique réécrit `stages.json` et les effacerait. Elles s'ajoutent ici, à chaque lecture,
    # et seulement si le couple lien + titre n'est pas déjà là.
    if AJOUT.exists():
        try:
            a = json.loads(AJOUT.read_text(encoding="utf-8"))
        except ValueError:
            a = {"offres": []}
        deja = {(o.get("lien"), o.get("titre")) for o in d.get("offres", [])}
        d.setdefault("offres", []).extend(
            o for o in a.get("offres", []) if (o.get("lien"), o.get("titre")) not in deja)
    return d


def affichable(o: dict, aujourdhui: date | None = None) -> bool:
    aujourdhui = aujourdhui or date.today()
    if o.get("hors_offre"):  # page d'info, galerie, actualité : pas un stage (drapeau réversible)
        return False
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



# ---- Le premier lot écrit en HTML réel (25/11/2026) -------------------------------------------
# Nicolas : « il faudrait pas full en javascript pour le référencement ? » — non, et c'est la règle
# du site depuis le 24/11. Les robots qui n'exécutent pas JavaScript (GPTBot, ClaudeBot,
# PerplexityBot, OAI-SearchBot) ne voyaient ici que le menu et le chapô. Douze écoles et leurs
# offres sont donc écrites dans la page à la construction ; le script les remplace au premier
# dessin pour l'internaute, mais ce qui est écrit reste lisible par un robot et par un navigateur
# sans JavaScript.
def _sigle(nom: str) -> str:
    mots = [m for m in re.sub(r"[^\w\s]", "", nom or "?").split() if m]
    if len(mots) > 1:
        return (mots[0][0] + mots[1][0]).upper()
    return (mots[0][:2] if mots else "?").upper()


def _teinte(s: str) -> int:
    h = 0
    for c in s or "":
        h = (h * 31 + ord(c)) % 360
    return h


def _dt(iso: str | None) -> str:
    """« 2026-11-24 » → « 24/11/26 », comme le fait le script."""
    if not iso:
        return ""
    j, m, a = iso.split("-")
    return f"{a}/{m}/{j[2:]}"


def _prix(o: dict) -> str:
    if o.get("prix") is None:
        return f'<span style="font-weight:400;font-size:.85rem">{UI["fr"]["prix_vide"]}</span>'
    return f'{o["prix"]:,.0f}'.replace(",", " ") + " " + {"EUR": "€", "GBP": "£", "CHF": "CHF", "NOK": "NOK",
                                                         "SEK": "SEK", "DKK": "DKK", "USD": "$"}.get(o.get("devise") or "EUR", o.get("devise") or "")


def _carte_html(o: dict) -> str:
    T = UI["fr"]
    if not o.get("debut"):
        dates = T["dates_ecole"]
    elif o.get("fin") and o["fin"] != o["debut"]:
        dates = f'{T["du"]} {_dt(o["debut"])} {T["au"]} {_dt(o["fin"])}'
    else:
        dates = _dt(o["debut"])
    lieu = o.get("lieu") or ""
    if lieu and lieu != o.get("pays_nom"):
        lieu = f"{lieu} · {o.get('pays_nom') or ''}"
    else:
        lieu = o.get("region") or o.get("pays_nom") or ""
    langue = LANGUES.get(o.get("langue") or "", (o.get("langue") or "").upper())
    morceaux = [f"<span>{H.escape(lieu)}</span>"]
    if o.get("langue_src") in ("offre", "page", "stage"):
        morceaux.append(f"<span>{H.escape(langue)}</span>")
    if o.get("niveau"):
        morceaux.append(f'<span>{H.escape(T.get(o["niveau"], o["niveau"]))}</span>')
    return (
        '<article class="offre">'
        f'<div class="tete"><span class="badge" style="background:hsl({_teinte(o.get("ecole_slug") or "")},38%,22%);'
        f'border:1px solid hsl({_teinte(o.get("ecole_slug") or "")},45%,34%)">{H.escape(_sigle(o.get("ecole") or ""))}</span>'
        f'<div><h2>{H.escape(o.get("titre") or "")}</h2>'
        f'<div class="ecole"><a href="ecole-{_slug_fichier(o.get("ecole_slug") or "")}.html">{H.escape(o.get("ecole") or "")}</a>'
        + (f' · {H.escape(o["ecole_pays_nom"])}' if o.get("ecole_pays_nom") else "") + "</div></div></div>"
        f'<div class="prix">{_prix(o)}</div>'
        f'<div class="dates">{H.escape(dates)}'
        + (f' · {o["duree_jours"]} {"jour" if o["duree_jours"] == 1 else T["jours"]}' if o.get("duree_jours") else "")
        + '</div>'
        f'<div class="ligne">{"".join(morceaux)}</div>'
        f'<div class="bas"><span>{T["verifie"]} {_dt(o.get("verifie"))}</span>'
        '<div class="bas-d">'
        f'<a class="lien" href="{H.escape(o.get("lien") or "")}" rel="noopener nofollow" target="_blank">{T["voir"]}</a>'
        "</div></div></article>"
    )


def _sessions(offres: list[dict]) -> list[tuple[str, list[dict]]]:
    """Les offres d'une école rangées par session : même début, même fin, dans l'ordre du calendrier,
    celles sans date à la fin. Même règle que le script."""
    ix, ordre = {}, []
    for o in offres:
        k = (o.get("debut") or "")[:7]
        if k not in ix:
            ix[k] = {"debut": o.get("debut") or "", "os": []}
            ordre.append(k)
        ix[k]["os"].append(o)
    out = []
    for k in ordre:
        g = ix[k]
        lib = UI["fr"]["dates_ecole"] if not g["debut"] else _mois(g["debut"])
        out.append((g["debut"] or "9999", lib, g["os"]))
    out.sort(key=lambda x: x[0])
    return [(lib, lot) for _, lib, lot in out]


def _mois(iso: str) -> str:
    """« 2027-04-12 » → « Avril 2027 » (le mois de début, comme le script)."""
    noms = ("Janvier", "Février", "Mars", "Avril", "Mai", "Juin", "Juillet", "Août", "Septembre",
            "Octobre", "Novembre", "Décembre")
    return f"{noms[int(iso[5:7]) - 1]} {iso[:4]}"


def _liste_html(offres: list[dict], ecoles_max: int = 12, par_famille: int = 3) -> str:
    """Les douze premières écoles, rangées en sous-groupes de cours, trois offres par sous-groupe."""
    vus, groupes = set(), []
    for o in offres:
        k = o.get("ecole_slug") or o.get("ecole")
        if k in vus or len(groupes) >= ecoles_max:
            continue
        vus.add(k)
        groupes.append([x for x in offres if (x.get("ecole_slug") or x.get("ecole")) == k])
    blocs = []
    for os_ in groupes:
        bas = min((x["prix"] for x in os_ if x.get("prix") is not None), default=None)
        devise = "€"
        for x in os_:
            if bas is not None and x.get("prix") == bas:
                devise = {"EUR": "€", "GBP": "£"}.get(x.get("devise") or "EUR", x.get("devise") or "€")
                break
        tete = (
            f'<span class="badge" style="background:hsl({_teinte(os_[0].get("ecole_slug") or "")},38%,22%);'
            f'border:1px solid hsl({_teinte(os_[0].get("ecole_slug") or "")},45%,34%)">{H.escape(_sigle(os_[0].get("ecole") or ""))}</span>'
            f'<div class="grp-n"><h2>{H.escape(os_[0].get("ecole") or "")}</h2>'
            f'<span class="n">{len(os_)} offres'
            + (f' · {H.escape(os_[0]["ecole_pays_nom"])}' if os_[0].get("ecole_pays_nom") else "") + "</span></div>"
            + (f'<span class="des">dès <b>{bas:,.0f}'.replace(",", " ") + f" {devise}</b></span>" if bas is not None else "")
        )
        corps, montres, premier = "", 0, True
        for libelle, lot in _sessions(os_):
            corps += (f'<details class="ses"{" open" if premier else ""}>'
                      f'<summary><span class="ses-t">{H.escape(libelle)}</span>'
                      f'<span class="ses-n">{len(lot)}</span></summary>'
                      f'<div class="ses-c">' + "".join(_carte_html(x) for x in lot[:par_famille])
                      + "</div></details>")
            premier = False
            montres += min(len(lot), par_famille)
        reste = len(os_) - montres
        if reste > 0:
            corps += (f'<button type="button" class="grp-plus" data-g="{H.escape(os_[0].get("ecole_slug") or "")}">'
                      f"+ {reste} autres offres</button>")
        blocs.append(f'<details class="grp"{" open" if not blocs else ""}>'
                     f'<summary class="grp-t">{tete}</summary>'
                     f'<div class="grp-l">{corps}</div></details>')
    return "".join(blocs)


def _itemlist(offres: list[dict]) -> dict:
    """La liste des offres du premier lot, pour les moteurs : un `ItemList` de `Course`."""
    return {"@type": "ItemList", "numberOfItems": len(offres), "itemListElement": [
        {"@type": "ListItem", "position": i + 1,
         "item": {"@type": "Course", "name": o.get("titre") or "", "url": o.get("lien") or "",
                  "inLanguage": o.get("langue") or "fr",
                  "provider": {"@type": "Organization", "name": o.get("ecole") or ""},
                  **({"offers": {"@type": "Offer", "price": o["prix"], "priceCurrency": o.get("devise") or "EUR",
                                 "url": o.get("lien") or ""}} if o.get("prix") is not None else {})}}
        for i, o in enumerate(offres)]}



# ---- Familles de cours (25/11/2026) ---------------------------------------------------------
# Nicolas : « faudrait que tu fasses des sous-groupes encore pour les cours des différentes
# écoles ». Une école vend souvent quatre choses très différentes : la croisière, le dériveur, la
# théorie, la régate. On range par là, avec les mêmes mots-clés que le script — l'ordre compte :
# la théorie d'abord (« Day Skipper Theory » est un cours de théorie, pas de croisière).
ORDRE_FAMILLES = ("fam_croisiere", "fam_deriveur", "fam_theorie", "fam_regate", "fam_autre")
_FAMILLES = (
    ("fam_theorie", re.compile(r"th[ée]ori|theory|\bvhf\b|radio|m[ée]t[ée]o|first aid|secour|diesel|"
                               r"navigation|navigatie|avondcursus|zaterdagcursus|cours du soir|theorie-examen", re.I)),
    ("fam_regate", re.compile(r"r[ée]gat|regatt|racing|spinnaker|performance|course au large", re.I)),
    ("fam_deriveur", re.compile(r"d[ée]riveur|dinghy|jolle|laser|optimist|catamaran|planche|windsurf|"
                                r"\bkite\b|hobie|\b420\b|\b470\b|jolle", re.I)),
    ("fam_croisiere", re.compile(r"croisi[èe]re|cruising|habitable|yacht|keelboat|skipper|coastal|"
                                 r"offshore|hauturier|c[o]mp[ée]tent|crew", re.I)),
)


def _famille(o: dict) -> str:
    base = f"{o.get('titre') or ''} {o.get('type') or ''}"
    for cle, motif in _FAMILLES:
        if motif.search(base):
            return cle
    return "fam_autre"


def construire(d: dict | None = None) -> str:
    d = d if d is not None else charger()
    offres = [o for o in d.get("offres", []) if affichable(o) and not non_stage(o.get("titre"), o.get("prix_eur"))]
    offres = [avec_niveau(_avec_position(o)) for o in offres]
    # La photo ne part plus dans la page (25/11/2026 : « enlève les images et ne les cherche pas »).
    # Le champ restait dans les données et pesait 375 adresses dans le JSON de la page.
    for o in offres:
        o.pop("image", None)
    offres.sort(key=lambda o: (o.get("debut") or "9999-12-31", o.get("prix_eur") or 0))
    ui = {lg: {**textes, **LIBELLES_NIVEAU.get(lg, LIBELLES_NIVEAU["en"])} for lg, textes in UI.items()}
    donnees = {
        "ui": ui, "offres": offres, "langues": LANGUES,
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
    import site_blocks  # la barre du site et le menu : un seul endroit
    # Audit SEO du 24/11/2026, correction 4 : textes de l'audit ; les trois compteurs viennent des données.
    # Le premier lot en HTML réel : ce qu'un robot lit sans exécuter le script (25/11/2026).
    offres = d.get("offres", [])
    statique = _liste_html(offres)
    compte_texte = (f"{len(offres)} offres dans "
                    f"{len({o.get('ecole_slug') or o.get('ecole') for o in offres})} écoles")
    seo_titre = "Stages de voile en Europe, prix publiés | Sailing More"
    seo_desc = (f"Comparez {len(d['offres'])} stages de voile de {len(d['ecoles'])} écoles dans "
                f"{len(d['pays'])} pays : croisière, dériveur, RYA ou FFVoile. Prix, dates et niveau "
                "affichés, lien direct vers l'école.")
    corps = ("<!doctype html><html lang=\"fr\"><head><meta charset=\"utf-8\">"
             "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">"
             f"<title>{H.escape(seo_titre)}</title>"
             "<link rel=\"canonical\" href=\"https://sailingmore.fr/stages.html\">"
             f"{__import__('jsonld').page_simple('stages.html', UI['fr']['titre'])}"
             + __import__('jsonld').bloc(_itemlist(offres[:48])) +
             f"<meta name=\"description\" content=\"{H.escape(seo_desc, quote=True)}\">"
             + __import__('jsonld').social("stages.html", seo_titre, seo_desc) +
             f"<style>{site_blocks.ENTETE_CSS}{CSS}</style></head><body>\n"
             f"{site_blocks.entete_site('stages.html', site_blocks.LANGUES)}\n"
             # L'onglet et le panneau sont écrits en clair dans le HTML : l'onglet s'affiche même si le
             # script n'a pas encore tourné, et un robot lit le panneau. Le contenu se remplit au clic.
             '<button type="button" class="cmp-o" id="cmp-o" aria-controls="cmp-p" aria-expanded="false" aria-haspopup="dialog">'
             '<span class="cmp-o-t" data-c="onglet">Comparer</span><b class="cmp-n" id="cmp-n"></b></button>'
             '<div class="cmp-v" id="cmp-v" hidden></div>'
             '<aside class="cmp-p" id="cmp-p" role="dialog" aria-modal="true" aria-labelledby="cmp-t" aria-hidden="true">'
             f'<header class="cmp-h"><h2 id="cmp-t" data-c="titre">{H.escape(CMP_TEXTES["fr"]["titre"])}</h2>'
             '<button type="button" class="cmp-x" id="cmp-x" aria-label="Fermer">✕</button></header>'
             '<div class="cmp-c">'
             f'<p class="cmp-aide" id="cmp-aide" data-c="aide">{H.escape(CMP_TEXTES["fr"]["aide"])}</p>'
             '<div class="cmp-tab" id="cmp-selection"></div>'
             f'<h3 class="cmp-sous" data-c="toutes">{H.escape(CMP_TEXTES["fr"]["toutes"])}</h3>'
             '<div id="cmp-toutes"></div>'
             '</div>'
             f'<footer class="cmp-f"><button type="button" class="cmp-b" id="cmp-vider" data-c="vider">{H.escape(CMP_TEXTES["fr"]["vider"])}</button></footer>'
             '</aside>'
             f"<main class=\"page\">"
             f"<a class=\"retour\" href=\"/\" data-t=\"retour\">{H.escape(UI['fr']['retour'])}</a>"
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
             "<label><span data-t=\"niveau\">Niveau</span><select id=\"f-niveau\"></select></label>"
             "<label><span data-t=\"quand\">Date</span><select id=\"f-quand\"></select></label>"
             "<label><span data-t=\"tri\">Trier</span><select id=\"f-tri\"></select></label>"
             "<label><span data-t=\"prix\">Prix max.</span><input id=\"f-prix\" type=\"number\" min=\"0\" step=\"50\" inputmode=\"numeric\"></label>"
             "<label><span data-c=\"support\">Support</span><select id=\"f-support\"></select></label>"
             "<label><span data-c=\"du\">Du</span><input id=\"f-debut\" type=\"date\"></label>"
             "<label><span data-c=\"au\">Au</span><input id=\"f-fin\" type=\"date\"></label>"
             "<label><span data-c=\"pres\">À quelques jours près</span><select id=\"f-tol\"></select></label>"
             "<label><span data-c=\"duree\">Durée</span><select id=\"f-duree\"></select></label>"
             "</section>"
             + carte_epreuves.html() +
             f"<p class=\"compte\" id=\"compte\" role=\"status\" aria-live=\"polite\">{compte_texte}</p>"
             f"<div class=\"liste\" id=\"liste\">{statique}</div>"
             f"<p class=\"pied\" data-t=\"pied\">{H.escape(UI['fr']['pied'])}</p>"
             f"<p class=\"pied\"><a href=\"comparatif-stages.html\" data-t=\"comparatif\">"
             f"{H.escape(LIBELLES_NIVEAU['fr']['comparatif'])}</a></p>"
             f"<p class=\"pied\"><a href=\"equivalences.html\" data-t=\"equivalences\">"
             f"{H.escape(LIBELLES_NIVEAU['fr']['equivalences'])}</a></p>"
             "</main>"
             "<script id=\"donnees\" type=\"application/json\">"
             + json.dumps(d, ensure_ascii=False).replace("</", "<\\/")
             + "</script><script src=\"/geo-accueil.js\"></script><script>" + carte_epreuves.js() + JS + "</script></body></html>")
    return corps


CSS = CSS.replace("__CARTE_CSS__", carte_epreuves.CSS)

JS = r"""
var D=JSON.parse(document.getElementById('donnees').textContent),U=D.ui;
/* Chaque offre garde son rang dans D.offres : c'est la clé du comparateur dans l'adresse. */
D.offres.forEach(function(o,i){o.__i=i});
var CL=__CMP__;
var L='fr';try{L=(window.smLangue?window.smLangue():'en')}catch(e){}
if(!U[L])L='en';
function t(k){return (U[L]&&U[L][k])||U.fr[k]||k}
function esc(s){return String(s==null?'':s).replace(/[&<>"']/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]})}
function sigle(nom){var m=(nom||'?').replace(/[^\p{L} ]/gu,'').split(/\s+/).filter(Boolean);
  return m.length>1?(m[0][0]+m[1][0]).toUpperCase():((m[0]||'?').slice(0,2).toUpperCase())}
function teinte(s){var h=0;s=s||'';for(var i=0;i<s.length;i++)h=(h*31+s.charCodeAt(i))%360;return h}
function dt(s){if(!s)return '';var p=s.split('-');return p[2]+'/'+p[1]+'/'+p[0].slice(2)}
function sym(d){return {EUR:'€',GBP:'£',CHF:'CHF',USD:'$',NOK:'NOK',SEK:'SEK',DKK:'DKK'}[d]||d}
/* langue et pays proposés par défaut : ceux du navigateur, quand des offres y répondent */
var nav='fr';var navLang='fr';
var m=null;var navPays='';
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
  ['titre','chapo','pied','retour','chercher','langue','destination','pays_ecole','ecole','niveau','quand','prix','tous','equivalences'].forEach(function(k){
    var e=document.querySelector('[data-t="'+k+'"]');if(e)e.textContent=t(k)});
  var f=document.getElementById('f-q');if(f)f.placeholder=t('chercher');
  options('f-langue',D.langues_presentes.map(function(c){return [c,D.langues[c]||c.toUpperCase()]}));
  options('f-pays',D.pays.map(function(p){return [p[0],p[1]]}));
  options('f-pays-ecole',D.pays_ecole.map(function(p){return [p[0],p[1]]}));
  options('f-ecole',D.ecoles.map(function(e){return [e[0],e[1]]}));
  options('f-niveau',D.niveaux.map(function(n){return [n,t(n)]}));
  /* options('f-type') retiré : le filtre Support le remplace. */
  var tri=document.getElementById('f-tri'),gt=tri.value;
  tri.innerHTML='<option value="proche">'+t('proche')+'</option><option value="prix">'+t('prix_croissant')+
    '</option><option value="date">'+t('date_proche')+'</option>';
  tri.value=gt||mem('tri','proche');
  var q=document.getElementById('f-quand'),gq=q.value;
  q.innerHTML='<option value="">'+t('tous')+'</option><option value="avenir">'+t('avenir')+'</option><option value="mois">'+t('mois')+'</option>';
  q.value=gq;
  /* Aucun filtre de langue ni de pays coché d'avance (25/11/2026) : la langue de la page ne dit rien
     de la langue du cours, et un visiteur français se retrouvait devant 15 offres sur 799. La liste
     s'ouvre complète, triée par proximité ; celui qui veut filtrer le fait. */
  /* « Par défaut il faut choisir langue tous » (Nicolas, 25/11/2026) : on ne restaure plus le
     dernier choix de langue ni de pays — la page s'ouvre sur tout le catalogue. */
  var fl=document.getElementById('f-langue');
  fl.value='';
  var fp=document.getElementById('f-pays');
  fp.value='';
  var fs=document.getElementById('f-support');
  if(fs&&!fs.options.length){fs.innerHTML='<option value="">'+t('tous')+'</option>'+FAM_ORDRE.map(function(f){
    return '<option value="'+f+'">'+esc(c(f))+'</option>'}).join('')}
  var ft=document.getElementById('f-tol');
  if(ft&&!ft.options.length){ft.innerHTML=[[0,c('tol0')],[3,c('tol3')],[7,c('tol7')],[14,c('tol14')]]
    .map(function(x){return '<option value="'+x[0]+'">'+esc(x[1])+'</option>'}).join('')}
  var fd=document.getElementById('f-duree');
  if(fd&&!fd.options.length){fd.innerHTML=[['',t('tous')],['1',c('d1')],['2-3',c('d23')],['4-7',c('d47')],['8','8 +']]
    .map(function(x){return '<option value="'+x[0]+'">'+esc(x[1])+'</option>'}).join('')}
  /* les défauts se relâchent si le couple langue + destination ne laisse aucune offre */
  var qp=fp.value,ql=fl.value;
  function reste(lg,py){return D.offres.some(function(o){return (!lg||o.langue===lg)&&(!py||o.pays===py)})}
  if(!reste(ql,qp)){if(reste('',qp))fl.value='';else if(reste(ql,''))fp.value='';else{fl.value='';fp.value=''}}
  /* Le choix de langue de la page en menu déroulant, comme la barre du site (Nicolas, 23/11/2026). */
  var NOMS={fr:'Français',en:'English',de:'Deutsch',it:'Italiano',es:'Español',pt:'Português'};
  var l=document.getElementById('langues');
  l.innerHTML='<select id="lng-sel" aria-label="Langue de la page" style="background:transparent;color:inherit;font:inherit;font-size:.8rem;border:1px solid rgba(255,255,255,.34);border-radius:.4rem;padding:.5rem .6rem;min-height:38px;cursor:pointer">'
    +Object.keys(U).map(function(c){return '<option value="'+c+'"'+(c===L?' selected':'')+'>'+(NOMS[c]||c.toUpperCase())+'</option>'}).join('')+'</select>';
  l.querySelector('select').onchange=function(){L=this.value;try{if(window.smChoisirLangue)window.smChoisirLangue(L)}catch(e){}remplir();dessiner()};
  etiquettesCmp();
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
      .then(function(d){if(d&&d.success&&d.latitude!=null&&!(POS&&POS[2]==='gps')){POS=[d.latitude,d.longitude,'ip'];dessiner()}})
      .catch(function(){});
  }
  /* La demande de position est unique et vit dans geo-accueil.js (26/11/2026) : cette page ne la
     déclenche plus. Accord : pays de l'école + langue pré-remplis, tri par proximité, carte à 100 km.
     Refus ou pas de réponse : l'IP trie comme avant, aucun filtre ne bouge. */
  var vuGeo=false;
  if(window.smGeo){window.smGeo.sur(function(g){
    POS=[g.lat,g.lon,'gps'];
    function pre(id,val){var e=document.getElementById(id);if(!e||!val||e.value)return;
      for(var i=0;i<e.options.length;i++){if(e.options[i].value===val){e.value=val;e.dispatchEvent(new Event('change'));return}}}
    if(!vuGeo){vuGeo=true;pre('f-pays-ecole',g.iso3);pre('f-langue',g.langue)}
    dessiner();
    if(window.carteStages&&window.carteStages.zoomSur)window.carteStages.zoomSur(g.lat,g.lon,100);
  })}
  parIP();
}
function futur(o){if(!o.debut)return true;var a=new Date().toISOString().slice(0,10);return (o.fin||o.debut)>=a}

/* Les offres sont rangées par école et servies par lots (Nicolas, 25/11/2026 : « faudrait que les
   offres soient triées par école, qu'on ne les affiche pas toutes mais par lot »). Une école = un
   bloc : son nom, son nombre d'offres, son prix le plus bas, puis ses offres. Douze écoles au
   premier écran, douze de plus au clic ; quatre offres par école, le reste au clic.
   Le comparateur lit toujours VUS en entier : le découpage ne retire rien de la comparaison. */
var GROUPES=[],LIM_E=12,OUVERTES={};
var O_MIN=4;
function grouper(vus){
  GROUPES=[];OUVERTES={};
  var ix={};
  vus.forEach(function(o){
    var k=o.ecole_slug||o.ecole;
    if(!(k in ix)){ix[k]={ecole:o.ecole,slug:k,pays:o.ecole_pays_nom||'',offres:[]};GROUPES.push(ix[k])}
    ix[k].offres.push(o);
  });
}
/* Même découpage que côté Python : croisière, dériveur, théorie, régate, autres. L'ordre compte. */
var FAM_ORDRE=['fam_croisiere','fam_deriveur','fam_theorie','fam_regate','fam_autre'];
var FAM_RX=[['fam_theorie',/th[ée]ori|theory|\bvhf\b|radio|m[ée]t[ée]o|first aid|secour|diesel|navigation|navigatie|avondcursus|zaterdagcursus|cours du soir|theorie-examen/i],
  ['fam_regate',/r[ée]gat|regatt|racing|spinnaker|performance|course au large/i],
  ['fam_deriveur',/d[ée]riveur|dinghy|jolle|laser|optimist|catamaran|planche|windsurf|\bkite\b|hobie|\b420\b|\b470\b/i],
  ['fam_croisiere',/croisi[èe]re|cruising|habitable|yacht|keelboat|skipper|coastal|offshore|hauturier|c[o]mp[ée]tent|crew/i]];
function famille(o){
  var base=(o.titre||'')+' '+(o.type||'');
  for(var i=0;i<FAM_RX.length;i++){if(FAM_RX[i][1].test(base))return FAM_RX[i][0]}
  return 'fam_autre';
}
function moinsCher(os){var m=null;os.forEach(function(o){if(o.prix_eur!=null&&(m===null||o.prix_eur<m.prix_eur))m=o});return m}
function ecrireListe(){
  var total=GROUPES.length;
  var lot=GROUPES.slice(0,LIM_E);
  var html=lot.map(function(g,ie){var premierEcole=(ie===0);
    var os=g.offres, ouv=!!OUVERTES[g.slug], bas=moinsCher(os);
    var corps='', montres=0, premier=true;
    sessions(os).forEach(function(s){
      var lot=s.os, n=ouv?lot.length:Math.min(lot.length,O_MIN);
      corps+='<details class="ses"'+(premier?' open':'')+'><summary>'
        +'<span class="ses-t">'+esc(s.libelle)+'</span><span class="ses-n">'+lot.length+'</span></summary>'
        +'<div class="ses-c">'+lot.slice(0,n).map(carteHtml).join('')+'</div></details>';
      premier=false; montres+=n;
    });
    var reste=os.length-montres;
    return '<details class="grp"'+(premierEcole?' open':'')+'><summary class="grp-t">'
      +'<span class="badge" style="background:hsl('+teinte(g.slug)+',38%,22%);border:1px solid hsl('+teinte(g.slug)+',45%,34%)">'+esc(sigle(g.ecole))+'</span>'
      +'<div class="grp-n"><h2>'+esc(g.ecole)+'</h2><span class="n">'+os.length+' '+(os.length>1?c('offres'):c('offre1'))+(g.pays?' · '+esc(g.pays):'')+'</span></div>'
      +(bas?'<span class="des">'+c('des')+' <b>'+bas.prix.toLocaleString(L)+' '+sym(bas.devise)+'</b></span>':'')
      +'</summary>'
      +'<div class="grp-l">'+corps
      +(reste>0?'<button type="button" class="grp-plus" data-g="'+esc(g.slug)+'">+ '+reste+' '+(reste>1?c('autres_offres'):c('autre_offre'))+'</button>':'')
      +'</div></details>';
  }).join('');
  if(total>LIM_E)html+='<button type="button" class="liste-plus" id="liste-plus">'+c('plus_ecoles').replace('{n}',total-LIM_E)+'</button>';
  document.getElementById('liste').innerHTML=html||('<p class="vide">'+(D.offres.length?t('aucune')+' <button type="button" id="tout-effacer" class="lien" style="cursor:pointer;font:inherit">'+esc(t('effacer'))+'</button>':t('vide'))+'</p>');
}

/* Les offres d'une école rangées par session : même début et même fin ensemble, dans l'ordre du
   calendrier, celles sans date à la fin. « comme ça s'ils sont dans la même saison » (25/11/2026). */
function sessions(os){
  /* Des périodes, pas des sessions (Nicolas, 25/11/2026) : les stages d'un même mois sont ensemble.
     Un stage qui chevauche deux mois reste rangé dans son mois de début. Sans date : à la fin. */
  var ix={}, ordre=[];
  os.forEach(function(o){
    var k=o.debut?o.debut.slice(0,7):'';
    if(!(k in ix)){ix[k]={debut:o.debut||'',os:[]};ordre.push(k)}
    ix[k].os.push(o);
  });
  var out=ordre.map(function(k){
    var g=ix[k];
    var lib=!g.debut?t('dates_ecole'):mois(g.debut);
    return {debut:g.debut||'9999',libelle:lib,os:g.os};
  });
  out.sort(function(a,b){return a.debut<b.debut?-1:a.debut>b.debut?1:0});
  return out;
}
/* « 2027-04-12 » → « avril 2027 », dans la langue de la page. */
function mois(iso){
  var y=+iso.slice(0,4), m=+iso.slice(5,7);
  var N={fr:['janvier','février','mars','avril','mai','juin','juillet','août','septembre','octobre','novembre','décembre'],
    en:['January','February','March','April','May','June','July','August','September','October','November','December'],
    de:['Januar','Februar','März','April','Mai','Juni','Juli','August','September','Oktober','November','Dezember'],
    it:['gennaio','febbraio','marzo','aprile','maggio','giugno','luglio','agosto','settembre','ottobre','novembre','dicembre'],
    es:['enero','febrero','marzo','abril','mayo','junio','julio','agosto','septiembre','octubre','noviembre','diciembre'],
    pt:['janeiro','fevereiro','março','abril','maio','junho','julho','agosto','setembro','outubro','novembro','dezembro']};
  var t=(N[L]||N.fr)[m-1];
  return t.charAt(0).toUpperCase()+t.slice(1)+' '+y;
}
function carteHtml(o){
    var dates=!o.debut?t('dates_ecole'):(o.fin&&o.fin!==o.debut?t('du')+' '+dt(o.debut)+' '+t('au')+' '+dt(o.fin):dt(o.debut));
    var ou=o.lieu?(o.lieu===o.pays_nom?o.lieu:o.lieu+' · '+o.pays_nom):(o.region||o.pays_nom);
    /* Langue : on n'affiche que ce qui est certain (Nicolas, 25/11/2026 : « si t'es pas sûr de la
       langue, affiche rien »). Les 801 offres actuelles ont une langue déduite de l'école
       (`langue_src = 'ecole'`) : aucune ne l'affiche, et le « ? » a disparu. */
    var lng=(o.langue&&(o.langue_src==='offre'||o.langue_src==='page'||o.langue_src==='stage'))
      ?(D.langues[o.langue]||o.langue.toUpperCase()):'';
    var d=distance(o);
    var loin=(d==null?'':(o.precision==='pays'?' · ~':' · ')+Math.round(d).toLocaleString(L)+' km');
    var marque='';
    return '<article class="offre">'
      +'<div class="tete"><span class="badge" style="background:hsl('+teinte(o.ecole_slug)+',38%,22%);border:1px solid hsl('+teinte(o.ecole_slug)+',45%,34%)">'+esc(sigle(o.ecole))+'</span>'
      +'<div><h2>'+esc(o.titre)+'</h2>'
      +'<div class="ecole"><a href="ecole-'+esc(o.ecole_slug||'ecole')+'.html">'+esc(o.ecole)+'</a>'
      +(o.ecole_pays_nom?' · '+esc(o.ecole_pays_nom):'')+'</div></div></div>'
      +'<div class="prix">'+(o.prix!=null?o.prix.toLocaleString(L)+' '+sym(o.devise):'<span style="font-weight:400;font-size:.85rem">'+t('prix_vide')+'</span>')+'</div>' 
      +'<div class="dates">'+esc(dates)+(o.duree_jours?' · '+o.duree_jours+' '+(o.duree_jours===1?c('jour'):t('jours')):'')+'</div>'
      +'<div class="ligne"><span>'+esc(ou)+loin+'</span>' 
      +'<span>'+esc(lng)+marque+'</span>'
      +(o.niveau?'<span>'+t(o.niveau)+'</span>':'')+'</div>'
      +'<div class="bas"><span>'+t('verifie')+' '+dt(o.verifie)+'</span>'
      +'<div class="bas-d"><button type="button" class="cmp-b" data-i="'+o.__i+'" aria-pressed="'+(cmpPos(o.__i)>=0?'true':'false')+'">'+esc(cmpLibelle(o.__i))+'</button>'
      +'<a class="lien" href="'+esc(o.lien)+'" rel="noopener nofollow" target="_blank">'+t('voir')+'</a></div></div>'
      +'</article>';
}

function dessiner(){
  var q=(document.getElementById('f-q').value||'').toLowerCase().trim();
  var lg=document.getElementById('f-langue').value,py=document.getElementById('f-pays').value;
  var pe=document.getElementById('f-pays-ecole').value,ec=document.getElementById('f-ecole').value;
  var nv=document.getElementById('f-niveau').value,qd=document.getElementById('f-quand').value;
  var ty='';  /* l'ancien filtre « Type » (pratique/théorie) est remplacé par le Support (25/11/2026) */
  var px=parseFloat(document.getElementById('f-prix').value||'0');
  var sp=document.getElementById('f-support').value;
  var d1=document.getElementById('f-debut').value,d2=document.getElementById('f-fin').value;
  var tol=parseInt(document.getElementById('f-tol').value||'0',10)||0;
  var du=document.getElementById('f-duree').value;
function plus(s,n){var t=new Date(s+'T12:00:00');t.setDate(t.getDate()+n);return t.toISOString().slice(0,10)}
  var w1=d1?plus(d1,-tol):'', w2=d2?plus(d2,tol):'';
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
    if(sp&&famille(o)!==sp)return false;
    if(w1||w2){
      if(!o.debut)return false;
      var od=o.debut, of=o.fin||o.debut;
      if(w1&&of<w1)return false;
      if(w2&&od>w2)return false;
    }
    if(du){
      var dj=o.duree_jours; if(!dj)return false;
      if(du==='1'&&dj!==1)return false;
      if(du==='2-3'&&(dj<2||dj>3))return false;
      if(du==='4-7'&&(dj<4||dj>7))return false;
      if(du==='8'&&dj<8)return false;
    }
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
  VUS=vus;
  grouper(vus);
  ecrireListe();
  ecrireUrl();
  if(OUVERT)dessinerCmp();
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
['f-q','f-langue','f-pays','f-pays-ecole','f-ecole','f-niveau','f-quand','f-prix','f-tri',
 'f-support','f-debut','f-fin','f-tol','f-duree'].forEach(function(i){
  var e=document.getElementById(i);if(e){e.addEventListener('input',dessiner);e.addEventListener('change',dessiner)}});
/* « Tout effacer » (zéro résultat) : vide tous les filtres, garde le tri. */
document.getElementById('liste').addEventListener('click',function(ev){
  if(!ev.target||ev.target.id!=='tout-effacer')return;
  CLES_URL.forEach(function(c){if(c[1]!=='f-tri'){document.getElementById(c[1]).value=''}});
  majBadge();dessiner();
});
/* État dans l'adresse : ?q=…&langue=fr&pays=FRA&ecole=…&niveau=…&type=…&quand=…&prix=…&tri=… ; seules les valeurs
   qui diffèrent de celles de l'ouverture s'écrivent (« tous » = filtre vidé alors que l'ouverture en posait un) ;
   une valeur inconnue est ignorée. */
var CLES_URL=[['q','f-q'],['langue','f-langue'],['pays','f-pays'],['pays_ecole','f-pays-ecole'],['ecole','f-ecole'],
  ['niveau','f-niveau'],['quand','f-quand'],['prix','f-prix'],['tri','f-tri'],
  ['support','f-support'],['debut','f-debut'],['fin','f-fin'],['pres','f-tol'],['duree','f-duree']];
var BASE_URL={};
function lireUrl(){
  var p;try{p=new URLSearchParams(location.search)}catch(x){return}
  CLES_URL.forEach(function(c){
    var v=p.get(c[0]);if(v===null)return;
    var e=document.getElementById(c[1]);if(!e)return;
    if(v==='tous')v='';
    if(c[1]==='f-q'||c[1]==='f-prix'){e.value=v.slice(0,80);return}
    if(c[1]==='f-debut'||c[1]==='f-fin'){if(/^\d{4}-\d{2}-\d{2}$/.test(v))e.value=v;return}
    if(Array.prototype.some.call(e.options,function(o){return o.value===v}))e.value=v;
  });
  var cp=p.get('cmp');
  if(cp){CMP=cp.split(',').map(Number).filter(function(i){return i>=0&&i<D.offres.length}).slice(0,4)}
  else CMP=cmpDepuisIds(cmpLire());
}
function ecrireUrl(){
  var a=[];
  CLES_URL.forEach(function(c){
    var e=document.getElementById(c[1]);if(!e)return;
    var v=e.value,b=BASE_URL[c[1]];
    if(v!==b)a.push(c[0]+'='+encodeURIComponent(v===''?'tous':v));
  });
  if(CMP.length)a.push('cmp='+CMP.join(','));
  try{history.replaceState(null,'',location.pathname+(a.length?'?'+a.join('&'):'')+location.hash)}catch(x){}
}
document.getElementById('f-tri').addEventListener('change',function(){garde('tri',this.value)});

/* ---- Comparateur intégré à la page (Nicolas, 25/11/2026) -------------------------------
   « le comparateur doit être dedans et lire tout et connecté ; présenté dès le début de côté
   et on clique pour l'ouvrir ». Il ne quitte jamais la page, il lit les offres de la page
   (D.offres, la même liste que les cartes et la carte), il suit les filtres, et l'état vit dans
   l'adresse (?cmp=3,17) : un lien copié rouvre la même comparaison. Rien n'est envoyé.
   Quatre offres au plus, sinon la table ne se lit plus sur un téléphone. */
var CMP=[],VUS=[],OUVERT=false;
function c(k){var m=CL[L]||CL.fr;return m[k]||CL.fr[k]||k}
function etiquettesCmp(){
  var el=document.querySelectorAll('[data-c]');
  for(var k=0;k<el.length;k++)el[k].textContent=c(el[k].getAttribute('data-c'));
  var x=document.getElementById('cmp-x');if(x)x.setAttribute('aria-label',c('fermer'));
  var ong=document.getElementById('cmp-o');if(ong)ong.title=c('onglet');
}
/* Stockage (sans compte) : localStorage « sm-comparatif » = {v:1, ids:[école|lien|titre|début,…], maj:ms}.
   On range l'identité de l'offre (le lien seul ne suffit pas : 725 offres, 531 liens), pas son rang dans la page (le rang change à chaque régénération) ;
   c'est le format qu'une synchronisation par l'API des favoris (rangs 500→507) pourra lire et
   écrire tel quel. L'adresse (?cmp=) l'emporte sur le stockage quand elle est présente. */
var CLE_CMP='sm-comparatif';
function cmpId(o){return [o.ecole_slug,o.lien,o.titre,o.debut||''].join('|')}
function cmpLire(){try{var s=JSON.parse(localStorage.getItem(CLE_CMP)||'null');return s&&s.v===1&&Array.isArray(s.ids)?s.ids:[]}catch(e){return[]}}
function cmpSauve(){try{localStorage.setItem(CLE_CMP,JSON.stringify({v:1,ids:CMP.map(function(i){return cmpId(D.offres[i])}),maj:Date.now()}))}catch(e){}}
function cmpDepuisIds(ids){var r=[];ids.forEach(function(id){for(var i=0;i<D.offres.length;i++)if(cmpId(D.offres[i])===id){if(r.indexOf(i)<0)r.push(i);break}});return r.slice(0,4)}
function cmpLibelle(i){var p=cmpPos(i);return p>=0?'✓ '+(p+1)+' · '+c('dans'):c('ajouter')}
function cmpPos(i){for(var k=0;k<CMP.length;k++)if(CMP[k]===i)return k;return -1}
function cmpBascule(i){var p=cmpPos(i);if(p>=0){CMP.splice(p,1);return true}
  if(CMP.length>=4)return false;CMP.push(i);return true}
function parJour(o){var p=(o.prix_eur!=null?o.prix_eur:null),d=o.duree_jours;if(p==null||!d)return null;return p/d}
function cmpPrix(o){return o.prix!=null?o.prix.toLocaleString(L)+' '+sym(o.devise):c('np')}
function cmpDates(o){if(!o.debut)return t('dates_ecole');
  return o.fin&&o.fin!==o.debut?t('du')+' '+dt(o.debut)+' '+t('au')+' '+dt(o.fin):dt(o.debut)}
function cmpLieu(o){return o.lieu?(o.lieu===o.pays_nom?o.lieu:o.lieu+' · '+o.pays_nom):(o.region||o.pays_nom||'')}
function cmpLigne(lab,fn,mieux){
  var os=CMP.map(function(i){return D.offres[i]});
  return '<tr><th class="lab" scope="row">'+esc(lab)+'</th>'+os.map(function(o,k){
    var v=fn(o);return '<td'+(mieux&&mieux(k)?' class="cmp-meilleur"':'')+'>'+(v==null||v===''?'—':v)+'</td>'}).join('')+'</tr>';
}
function dessinerCmp(){
  var n=document.getElementById('cmp-n');if(n)n.textContent=CMP.length?String(CMP.length):'';
  var ong=document.getElementById('cmp-o');
  if(ong){ong.setAttribute('aria-expanded',OUVERT?'true':'false');ong.setAttribute('aria-hidden','false')}
  var sel=document.getElementById('cmp-selection');if(!sel)return;
  if(!CMP.length){
    sel.innerHTML='<p class="cmp-aide" style="margin:0">'+esc(c('vide'))+'</p>';
  }else{
    var os=CMP.map(function(i){return D.offres[i]});
    var pj=os.map(parJour),best=-1;
    pj.forEach(function(v,k){if(v!=null&&(best<0||v<pj[best]))best=k});
    sel.innerHTML='<table class="cmp-t"><thead><tr><th class="lab" scope="col"></th>'
      +os.map(function(o){
        return '<th scope="col">'+esc(o.ecole)
          +'<div style="font-weight:400;font-size:.78rem;color:var(--doux)">'+esc(o.ecole_pays_nom||o.pays_nom||'')+'</div>'
          +'<button type="button" class="cmp-x" data-i="'+o.__i+'" style="width:26px;height:26px;font-size:.75rem;margin-top:.35rem" aria-label="'+esc(c('retirer'))+'">✕</button></th>'
      }).join('')+'</tr></thead><tbody>'
      +cmpLigne(c('stage'),function(o){return esc(o.titre)})
      +cmpLigne(c('prix'),function(o){return cmpPrix(o)})
      +cmpLigne(c('prix_jour'),function(o){var v=parJour(o);
          return v==null?null:Math.round(v).toLocaleString(L)+' €'},function(k){return k===best&&CMP.length>1})
      +cmpLigne(c('duree'),function(o){return o.duree_jours?(o.duree_jours+' '+(o.duree_jours===1?c('jour'):t('jours'))):null})
      +cmpLigne(c('dates'),function(o){return esc(cmpDates(o))})
      +cmpLigne(c('lieu'),function(o){return esc(cmpLieu(o))})
      +cmpLigne(c('langue'),function(o){return o.langue?(D.langues[o.langue]||o.langue.toUpperCase()):null})
      +cmpLigne(c('niveau'),function(o){return o.niveau?t(o.niveau):null})
      +cmpLigne(c('type'),function(o){return t(o.type==='theorie'?'theorie':'pratique')})
      +cmpLigne(c('ecole_pays'),function(o){return esc(o.ecole_pays_nom||o.pays_nom||'')})
      +cmpLigne(c('verifie'),function(o){return dt(o.verifie)})
      +cmpLigne(c('lien'),function(o){return '<a class="lien" href="'+esc(o.lien)+'" rel="noopener nofollow" target="_blank">'+t('voir')+'</a>'})
      +'</tbody></table>';
  }
  if(OUVERT)dessinerListeCmp();
}
function dessinerListeCmp(){
  var l=document.getElementById('cmp-toutes');if(!l)return;
  var plein=CMP.length>=4;
  l.innerHTML='<ul class="cmp-l">'+VUS.map(function(o){
    var on=cmpPos(o.__i)>=0;
    return '<li><button type="button" data-i="'+o.__i+'" aria-pressed="'+(on?'true':'false')+'"'+(plein&&!on?' disabled':'')+'>'
      +'<b>'+esc(o.titre)+'</b><span>'+esc(o.ecole)+(o.prix!=null?' · '+o.prix.toLocaleString(L)+' '+sym(o.devise):'')+'</span></button></li>'
  }).join('')+'</ul>';
}
function majBoutonsCmp(){
  var bs=document.querySelectorAll('.offre .cmp-b');
  for(var k=0;k<bs.length;k++){var i=+bs[k].getAttribute('data-i');
    bs[k].setAttribute('aria-pressed',cmpPos(i)>=0?'true':'false');bs[k].textContent=cmpLibelle(i)}
}
function ouvrirCmp(f,sansFocus){
  OUVERT=f!==false;
  var p=document.getElementById('cmp-p'),v=document.getElementById('cmp-v'),o=document.getElementById('cmp-o');
  if(!p)return;
  p.classList.toggle('ouvert',OUVERT);
  p.setAttribute('aria-hidden',OUVERT?'false':'true');
  if(v)v.hidden=!OUVERT;
  if(o)o.setAttribute('aria-expanded',OUVERT?'true':'false');
  if(OUVERT){dessinerCmp();p.querySelector('.cmp-c').scrollTop=0;
    if(!sansFocus){var x=document.getElementById('cmp-x');if(x)try{x.focus({preventScroll:true})}catch(e){x.focus()}}
  }else if(o&&!sansFocus)try{o.focus({preventScroll:true})}catch(e){}
}
function basculerCmp(i){
  if(!cmpBascule(i)){ouvrirCmp(true,true);var a=document.getElementById('cmp-aide');if(a)a.textContent=c('max');return}
  cmpSauve();majBoutonsCmp();dessinerCmp();ecrireUrl();
  if(!OUVERT&&CMP.length===1)ouvrirCmp(true);
}
document.getElementById('cmp-o').addEventListener('click',function(){ouvrirCmp(!OUVERT)});
document.getElementById('cmp-x').addEventListener('click',function(){ouvrirCmp(false)});
document.getElementById('cmp-v').addEventListener('click',function(){ouvrirCmp(false)});
document.getElementById('cmp-vider').addEventListener('click',function(){CMP=[];cmpSauve();majBoutonsCmp();dessinerCmp();ecrireUrl()});
document.addEventListener('keydown',function(e){if((e.key==='Escape'||e.key==='Esc')&&OUVERT)ouvrirCmp(false)});
document.getElementById('cmp-selection').addEventListener('click',function(e){
  var b=e.target.closest?e.target.closest('button[data-i]'):null;if(!b)return;basculerCmp(+b.getAttribute('data-i'))});
/* Le bouton « Comparer » de chaque carte : un seul écouteur pour toute la liste, qui survit aux
   redessins (les cartes sont réécrites à chaque filtre). */
document.addEventListener('click',function(e){
  var b=e.target.closest?e.target.closest('.offre .cmp-b'):null;if(!b)return;
  basculerCmp(+b.getAttribute('data-i'))});
document.getElementById('cmp-toutes').addEventListener('click',function(e){
  var b=e.target.closest?e.target.closest('button[data-i]'):null;if(!b||b.disabled)return;basculerCmp(+b.getAttribute('data-i'))});
/* Les lots : une école de plus à déplier, ou douze écoles de plus dans la liste. */
document.getElementById('liste').addEventListener('click',function(e){
  if(!e.target.closest)return;
  var g=e.target.closest('.grp-plus');
  if(g){OUVERTES[g.getAttribute('data-g')]=1;ecrireListe();return}
  if(e.target.closest('#liste-plus')){LIM_E+=12;ecrireListe()}
});


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
  ['f-q','f-langue','f-pays','f-pays-ecole','f-ecole','f-niveau','f-quand','f-prix',
   'f-support','f-debut','f-fin','f-tol','f-duree'].forEach(function(id){
    var e = document.getElementById(id);
    DEFAUT[id] = e ? e.value : '';
    if(e) e.addEventListener('change', majBadge);
  });
  majBadge();
}
CLES_URL.forEach(function(c){var e=document.getElementById(c[1]);BASE_URL[c[1]]=e?e.value:''});
lireUrl();majBadge();
if(CMP.length)ouvrirCmp(true,true);
dessiner();poserPosition();
"""

SITE = ICI / "projets/sailingmore/site"


# Photos : plus utilisées (25/11/2026). Le dossier reste sur le disque, la page n'y touche plus.
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
# Les mots du comparateur, dans les six langues de la page. Ils vivent dans le script et non dans
# `UI` : le panneau se remplit à l'ouverture, ils n'ont pas à alourdir chaque carte.
CMP_TEXTES = {
    "fr": {"onglet": "Comparer", "titre": "Comparer les stages",
           "aide": "Cochez deux à quatre offres : elles se comparent ici, ligne par ligne. Le prix par jour met les durées sur la même base.",
           "vide": "Aucune offre cochée pour l'instant.", "toutes": "Toutes les offres de la page",
           "vider": "Tout retirer", "fermer": "Fermer", "ajouter": "Ajouter au comparatif", "dans": "Dans le comparatif", "retirer": "Retirer",
           "max": "Quatre offres au maximum : retirez-en une pour en ajouter une autre.",
           "stage": "Stage", "prix": "Prix", "prix_jour": "Prix par jour", "duree": "Durée", "jour": "jour",
           "dates": "Dates", "lieu": "Lieu", "langue": "Langue", "niveau": "Niveau", "type": "Type",
           "ecole_pays": "Pays de l'école", "verifie": "Vérifié le", "lien": "L'offre",
           "np": "Prix non publié",
           "offres": "offres", "offre1": "offre", "autre_offre": "autre offre", "autres_offres": "autres offres",
           "des": "dès", "plus_ecoles": "Afficher {n} écoles de plus",
           "fam_croisiere": "Croisière", "fam_deriveur": "Dériveur", "fam_theorie": "Théorie",
           "fam_regate": "Régate", "fam_autre": "Autres cours",
           "support": "Support", "du": "Du", "au": "Au", "pres": "À quelques jours près",
           "duree": "Durée", "tol0": "exactes", "tol3": "± 3 jours", "tol7": "± 7 jours",
           "tol14": "± 14 jours", "d1": "1 jour", "d23": "2 à 3 jours", "d47": "4 à 7 jours"},
    "en": {"onglet": "Compare", "titre": "Compare the courses",
           "aide": "Tick two to four offers: they are compared here, line by line. Price per day puts the durations on the same footing.",
           "vide": "No offer ticked yet.", "toutes": "Every offer on this page",
           "vider": "Clear all", "fermer": "Close", "ajouter": "Add to comparison", "dans": "In comparison", "retirer": "Remove",
           "max": "Four offers at most: remove one to add another.",
           "stage": "Course", "prix": "Price", "prix_jour": "Price per day", "duree": "Duration", "jour": "day",
           "dates": "Dates", "lieu": "Place", "langue": "Language", "niveau": "Level", "type": "Type",
           "ecole_pays": "School country", "verifie": "Checked on", "lien": "The offer",
           "np": "Price not published",
           "offres": "offers", "offre1": "offer", "autre_offre": "more offer", "autres_offres": "more offers",
           "des": "from", "plus_ecoles": "Show {n} more schools",
           "fam_croisiere": "Cruising", "fam_deriveur": "Dinghy", "fam_theorie": "Theory",
           "fam_regate": "Racing", "fam_autre": "Other courses",
           "support": "Type", "du": "From", "au": "To", "pres": "Within a few days",
           "duree": "Duration", "tol0": "exact", "tol3": "± 3 days", "tol7": "± 7 days",
           "tol14": "± 14 days", "d1": "1 day", "d23": "2–3 days", "d47": "4–7 days"},
    "de": {"onglet": "Vergleichen", "titre": "Kurse vergleichen",
           "aide": "Zwei bis vier Angebote ankreuzen: sie werden hier Zeile für Zeile verglichen. Der Tagespreis bringt die Dauer auf dieselbe Basis.",
           "vide": "Noch kein Angebot angekreuzt.", "toutes": "Alle Angebote dieser Seite",
           "vider": "Alles entfernen", "fermer": "Schließen", "ajouter": "Zum Vergleich hinzufügen", "dans": "Im Vergleich", "retirer": "Entfernen",
           "max": "Höchstens vier Angebote: eines entfernen, um ein anderes hinzuzufügen.",
           "stage": "Kurs", "prix": "Preis", "prix_jour": "Preis pro Tag", "duree": "Dauer", "jour": "Tag",
           "dates": "Termine", "lieu": "Ort", "langue": "Sprache", "niveau": "Niveau", "type": "Art",
           "ecole_pays": "Land der Schule", "verifie": "Geprüft am", "lien": "Das Angebot",
           "np": "Preis nicht veröffentlicht",
           "offres": "Angebote", "offre1": "Angebot", "autre_offre": "weitere Angebote", "autres_offres": "weitere Angebote",
           "des": "ab", "plus_ecoles": "{n} weitere Schulen zeigen",
           "fam_croisiere": "Fahrtensegeln", "fam_deriveur": "Jolle", "fam_theorie": "Theorie",
           "fam_regate": "Regatta", "fam_autre": "Weitere Kurse",
           "support": "Art", "du": "Von", "au": "Bis", "pres": "Einige Tage Spielraum",
           "duree": "Dauer", "tol0": "genau", "tol3": "± 3 Tage", "tol7": "± 7 Tage",
           "tol14": "± 14 Tage", "d1": "1 Tag", "d23": "2–3 Tage", "d47": "4–7 Tage"},
    "it": {"onglet": "Confronta", "titre": "Confrontare i corsi",
           "aide": "Spunta da due a quattro offerte: si confrontano qui, riga per riga. Il prezzo al giorno mette le durate sulla stessa base.",
           "vide": "Nessuna offerta spuntata.", "toutes": "Tutte le offerte della pagina",
           "vider": "Togli tutto", "fermer": "Chiudi", "ajouter": "Aggiungi al confronto", "dans": "Nel confronto", "retirer": "Togli",
           "max": "Quattro offerte al massimo: togli una per aggiungerne un'altra.",
           "stage": "Corso", "prix": "Prezzo", "prix_jour": "Prezzo al giorno", "duree": "Durata", "jour": "giorno",
           "dates": "Date", "lieu": "Luogo", "langue": "Lingua", "niveau": "Livello", "type": "Tipo",
           "ecole_pays": "Paese della scuola", "verifie": "Verificato il", "lien": "L'offerta",
           "np": "Prezzo non pubblicato",
           "offres": "offerte", "offre1": "offerta", "autre_offre": "altra offerta", "autres_offres": "altre offerte",
           "des": "da", "plus_ecoles": "Mostra altre {n} scuole",
           "fam_croisiere": "Crociera", "fam_deriveur": "Deriva", "fam_theorie": "Teoria",
           "fam_regate": "Regata", "fam_autre": "Altri corsi",
           "support": "Tipo", "du": "Dal", "au": "Al", "pres": "Con qualche giorno di margine",
           "duree": "Durata", "tol0": "esatte", "tol3": "± 3 giorni", "tol7": "± 7 giorni",
           "tol14": "± 14 giorni", "d1": "1 giorno", "d23": "2–3 giorni", "d47": "4–7 giorni"},
    "es": {"onglet": "Comparar", "titre": "Comparar los cursos",
           "aide": "Marca de dos a cuatro ofertas: se comparan aquí, línea por línea. El precio por día pone las duraciones en la misma base.",
           "vide": "Ninguna oferta marcada.", "toutes": "Todas las ofertas de la página",
           "vider": "Quitar todo", "fermer": "Cerrar", "ajouter": "Añadir a la comparación", "dans": "En la comparación", "retirer": "Quitar",
           "max": "Cuatro ofertas como máximo: quita una para añadir otra.",
           "stage": "Curso", "prix": "Precio", "prix_jour": "Precio por día", "duree": "Duración", "jour": "día",
           "dates": "Fechas", "lieu": "Lugar", "langue": "Idioma", "niveau": "Nivel", "type": "Tipo",
           "ecole_pays": "País de la escuela", "verifie": "Verificado el", "lien": "La oferta",
           "np": "Precio no publicado",
           "offres": "ofertas", "offre1": "oferta", "autre_offre": "oferta más", "autres_offres": "ofertas más",
           "des": "desde", "plus_ecoles": "Mostrar {n} escuelas más",
           "fam_croisiere": "Crucero", "fam_deriveur": "Vela ligera", "fam_theorie": "Teoría",
           "fam_regate": "Regata", "fam_autre": "Otros cursos",
           "support": "Tipo", "du": "Desde", "au": "Hasta", "pres": "Con unos días de margen",
           "duree": "Duración", "tol0": "exactas", "tol3": "± 3 días", "tol7": "± 7 días",
           "tol14": "± 14 días", "d1": "1 día", "d23": "2–3 días", "d47": "4–7 días"},
    "pt": {"onglet": "Comparar", "titre": "Comparar os cursos",
           "aide": "Marca de duas a quatro ofertas: comparam-se aqui, linha a linha. O preço por dia põe as durações na mesma base.",
           "vide": "Nenhuma oferta marcada.", "toutes": "Todas as ofertas da página",
           "vider": "Retirar tudo", "fermer": "Fechar", "ajouter": "Adicionar à comparação", "dans": "Na comparação", "retirer": "Retirar",
           "max": "Quatro ofertas no máximo: retire uma para acrescentar outra.",
           "stage": "Curso", "prix": "Preço", "prix_jour": "Preço por dia", "duree": "Duração", "jour": "dia",
           "dates": "Datas", "lieu": "Local", "langue": "Língua", "niveau": "Nível", "type": "Tipo",
           "ecole_pays": "País da escola", "verifie": "Verificado em", "lien": "A oferta",
           "np": "Preço não publicado",
           "offres": "ofertas", "offre1": "oferta", "autre_offre": "oferta mais", "autres_offres": "ofertas mais",
           "des": "desde", "plus_ecoles": "Mostrar mais {n} escolas",
           "fam_croisiere": "Cruzeiro", "fam_deriveur": "Vela ligeira", "fam_theorie": "Teoria",
           "fam_regate": "Regata", "fam_autre": "Outros cursos",
           "support": "Tipo", "du": "De", "au": "Até", "pres": "Com alguns dias de margem",
           "duree": "Duração", "tol0": "exatas", "tol3": "± 3 dias", "tol7": "± 7 dias",
           "tol14": "± 14 dias", "d1": "1 dia", "d23": "2–3 dias", "d47": "4–7 dias"},
}

JS = JS.replace("__CMP__", json.dumps(CMP_TEXTES, ensure_ascii=False))

JS_BLOC = r"""(function(){
var T=__TEXTES__;
var host=document.getElementById('stages-proches');if(!host)return;
var L='fr';try{L=(window.smLangue?window.smLangue():document.documentElement.lang||'en')}catch(e){}
L=String(L).slice(0,2).toLowerCase();if(L==='bz')L='fr';if(!T[L])L='en';var X=T[L];
function esc(s){return String(s==null?'':s).replace(/[&<>"']/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]})}
function hav(a,b,c,d){var r=Math.PI/180,p=(c-a)*r,q=(d-b)*r,h=Math.sin(p/2)*Math.sin(p/2)+Math.cos(a*r)*Math.cos(c*r)*Math.sin(q/2)*Math.sin(q/2);return 12742*Math.asin(Math.sqrt(h))}
function teinte(s){var h=0;s=s||'';for(var i=0;i<s.length;i++)h=(h*31+s.charCodeAt(i))%360;return h}
function sigle(n){var m=(n||'?').replace(/[^\p{L} ]/gu,'').split(/\s+/).filter(Boolean);return m.length>1?(m[0][0]+m[1][0]).toUpperCase():((m[0]||'?').slice(0,2).toUpperCase())}
var ISO={FR:'FRA',DE:'DEU',NL:'NLD',GB:'GBR',IE:'IRL',ES:'ESP',IT:'ITA',PT:'PRT',GR:'GRC',HR:'HRV',TR:'TUR',BE:'BEL',CH:'CHE',AT:'AUT',DK:'DNK',SE:'SWE',NO:'NOR',FI:'FIN',PL:'POL',SI:'SVN',MT:'MLT',CY:'CYP'};
var m=null,navPays='';
var DATA=null,POS=null,posFaite=false,vu=false;
function position(fin){
  function ip(){fetch('https://ipwho.is/?fields=latitude,longitude,success').then(function(r){return r.json()})
    .then(function(d){if(d&&d.success&&d.latitude!=null)POS=[d.latitude,d.longitude]}).catch(function(){}).then(fin)}
  /* demande unique : geo-accueil.js (26/11/2026) ; ici on lit seulement la position déjà accordée */
  var g=window.smGeo&&window.smGeo.get();
  if(g){POS=[g.lat,g.lon];fin();return}
  ip();
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
     var vis='<span style="display:inline-grid;place-items:center;width:30px;height:30px;border-radius:8px;font-weight:700;font-size:.75rem;margin-bottom:.4rem;background:hsl('+teinte(o[4])+',38%,22%);color:#dff3ef">'+esc(sigle(o[4]))+'</span>';
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


# Titres qui ne sont pas des stages (tâche 44, 24/11/2026). Le relevé des pages d'écoles ramasse aussi les
# titres de navigation, d'actualité, de conseils et de location : on les repère ici, à la source, et la ligne
# du bloc les porte marqués (positions 15 = motif, 16 = 1) ; le script du bloc les saute.
_NON_STAGE = [
    ("nav", r"^(informatie|information|general information|infos? pratiques?|la storia|le sedi|offerte aanvragen|"
            r"vergaderen|regatas|quienes somos|fundaci[oó]n .*|cenizas al mar|veiligheid|erkenningen zeilschool|"
            r"de accommodatie|de locatie .*|bedrijfsevenement|bedrijfsuitje zeilen|training & coaching|"
            r"zeilschoolvloot|ontwikkeling van de zeilscholen|thema's seizoen.*|verhalen|zeilschool gezocht\?|"
            r"zeilschool aanbiedingen|welk theorieboek.*|exclusief zeilinstituut.*|zeilinstructeur worden.*|"
            r"'s avonds bij .*|our sailing areas|adh[ée]sion .*|prot[ée]g[ée] ?:.*|heiß|termine & kursplan|"
            r"entscheidungshilfe.*|costo dei corsi|calendario corsi.*|open day.*|.* archiv(os|i|es)|"
            r"escola de vela|escuela de vela|scuola vela|ecole de croisi[èe]re|courses|cursussen|sailing trips|"
            r"specialist courses|rya training centres|.* training centre|zeilkampen|bootkeuze / zeilkampen|"
            r"book your sailing adventure|first time sailing\?|course preparation checklist|in wolgast|"
            r"in mecklenburg-vorpommern|angebote für studenten|le basi di .*|actividades de nuestra .*|"
            r"zeilles voor jeugd|zeilles volwassenen & privéles)$"),
    ("actu", r"^(el|la|los|las) .*(conquista|acoge|llega|abre inscripciones|no termina)|^todo listo para|"
             r"^¿quieres saber|^which sailing course is right|^\d+ reasons|reasons to join|^reefing a sail|"
             r"^sailing tips|^winds in |^marinas in |^sailing itinerary|^attractive sailing destinations|"
             r"^regatta schedule|^sailing distance calculator|^knots for boating|^next step after|"
             r"^10 essentials|pre course requirements|^postage payment|top up payment|"
             r"^course cancellation|^l'effetto che fa|^apnea a vela|sailing through galicia|"
             r"^quiz patent|^welk |^sailing holiday in "),
    ("location", r"yacht charter|bareboat sailing|charter\b|noleggio|tariffe noleggio|stay and sail|"
                 r"flotilla holidays|skippered flotilla|^flottielje zeilen|^meezeilen in |zeilvakantie|"
                 r"^zeilen in (kroatië|griekenland)|^turkije$|^zeilen voor de vakantie"),
]
_NON_STAGE = [(m, re.compile(p, re.I)) for m, p in _NON_STAGE]
_PLURIEL_VITRINE = re.compile(r"\b(courses|cursos|cursussen|corsi|kurse|courses?,)\b.*$|^(rya )?(powerboat|motorboat|sailing)"
                              r" (training )?courses?\b", re.I)


def non_stage(titre: str, prix=None) -> str:
    """Motif ('nav', 'actu', 'location', 'encodage', 'vitrine') si le titre n'est pas un stage, '' sinon.
    'vitrine' : page de rubrique au pluriel (« RYA Powerboat Courses ») sans prix — pas une offre."""
    t = (titre or "").strip()
    if "�" in t or "�" in t:
        return "encodage"
    for motif, rx in _NON_STAGE:
        if rx.search(t):
            return motif
    if prix is None and _PLURIEL_VITRINE.search(t) and not re.search(r"\b(course|cursus|corso|kurs)\b.*\b(20\d\d|day|week)", t, re.I):
        return "vitrine"
    return ""


def _marque(o: dict) -> list:
    """Positions 15 (motif) et 16 (1 si ce n'est pas un stage, 0 sinon)."""
    m = non_stage(o.get("titre") or "", o.get("prix"))
    return [m, 1 if m else 0]


def ecrire_bloc(dossier: Path, offres: list[dict]) -> int:
    """JSON compact + script du bloc « près de chez vous », à côté de stages.html. Une ligne par offre :
    [lat, lon, approx(0/1), titre, école, lieu, pays, début, prix, devise, lien, image, pays ISO3,
    niveau, certif]. `niveau` et `certif` sont ajoutés en fin de ligne (23/11/2026) : le script du bloc
    lit par position, les treize premières ne bougent pas. Vides quand le titre ne permet pas de trancher.
    Positions 15 et 16 (24/11/2026) : motif et drapeau « n'est pas un stage » (voir `non_stage`) ; le bloc
    n'affiche pas les lignes marquées."""
    lignes = []
    for o in offres:
        o = avec_niveau(_avec_position(o))
        if o.get("lat") is None or o.get("lon") is None or not o.get("lien"):
            continue
        lignes.append([round(o["lat"], 2), round(o["lon"], 2), 1 if o.get("precision") != "ville" else 0,
                       o.get("titre") or "", o.get("ecole") or "", o.get("lieu") or "", o.get("pays_nom") or "",
                       o.get("debut") or "", o.get("prix"), o.get("devise") or "",
                       clics_sortants.lien(o["lien"], "stages"),
                       # Position 11 : la photo. Vidée le 25/11/2026 (Nicolas : « enlève les images et ne
                       # les cherche pas »). La position ne bouge pas : le script du bloc lit par position.
                       "", o.get("pays") or "", o.get("niveau") or "", o.get("certif") or "",
                       *_marque(o)])
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



# ---- Une page par école (25/11/2026) ---------------------------------------------------------
# Nicolas : « les écoles sont des pages avec leur produit et info ? si non fais-le ». Non, elles ne
# l'étaient pas : 63 écoles, une seule adresse. Chaque école a maintenant la sienne, avec ses stages,
# ses prix, ses dates et son lien. C'est aussi ce qui rend le catalogue lisible par les moteurs :
# « école de voile à Split » a enfin une page à qui répondre.
def _slug_fichier(slug: str) -> str:
    return re.sub(r"[^a-z0-9\-]+", "-", (slug or "").lower()).strip("-") or "ecole"


def _page_ecole(slug: str, offres: list[dict]) -> str:
    import site_blocks  # la barre du site : un seul endroit
    nom = offres[0].get("ecole") or slug
    pays = offres[0].get("ecole_pays_nom") or ""
    prix = [o["prix"] for o in offres if o.get("prix") is not None]
    dates = sorted(o["debut"] for o in offres if o.get("debut"))
    bas, haut = (min(prix), max(prix)) if prix else (None, None)
    devise = {"EUR": "€", "GBP": "£"}.get(offres[0].get("devise") or "EUR", offres[0].get("devise") or "€")
    derniere = max((o.get("verifie") or "" for o in offres), default="")
    titre = f"{nom} — stages de voile, prix et dates | Sailing More"
    desc = (f"{len(offres)} stage(s) chez {nom}"
            + (f" ({pays})" if pays else "")
            + (f", de {bas:,.0f}".replace(",", " ") + f" à {haut:,.0f}".replace(",", " ") + f" {devise}" if bas is not None else "")
            + ". Prix, dates et durée publiés, lien direct vers l'école.")
    lignes = []
    for o in sorted(offres, key=lambda x: (x.get("debut") or "9999", x.get("prix") or 0)):
        quand = (f'{_dt(o["debut"])}' + (f' → {_dt(o["fin"])}' if o.get("fin") and o["fin"] != o.get("debut") else "")
                 if o.get("debut") else "dates chez l'école")
        duree = (f'{o["duree_jours"]} ' + ("jour" if o["duree_jours"] == 1 else "jours")) if o.get("duree_jours") else ""
        p = (f'{o["prix"]:,.0f}'.replace(",", " ") + " " + {"EUR": "€", "GBP": "£"}.get(o.get("devise") or "EUR", o.get("devise") or "")) if o.get("prix") is not None else "prix non publié"
        lignes.append(
            '<tr>'
            f'<td>{H.escape(quand)}</td>'
            f'<td><a href="{H.escape(o.get("lien") or "")}" rel="noopener nofollow" target="_blank">{H.escape(o.get("titre") or "")}</a></td>'
            f'<td>{H.escape(duree)}</td><td class="p">{H.escape(p)}</td></tr>')
    itemlist = {"@type": "ItemList", "numberOfItems": len(offres), "itemListElement": [
        {"@type": "ListItem", "position": i + 1,
         "item": {"@type": "Course", "name": o.get("titre") or "", "url": o.get("lien") or "",
                  "provider": {"@type": "Organization", "name": nom},
                  **({"offers": {"@type": "Offer", "price": o["prix"], "priceCurrency": o.get("devise") or "EUR"}}
                     if o.get("prix") is not None else {})}}
        for i, o in enumerate(offres)]}
    jsonld = __import__("jsonld")
    return (
        '<!doctype html><html lang="fr"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        f"<title>{H.escape(titre)}</title>"
        f'<link rel="canonical" href="https://sailingmore.fr/ecole-{_slug_fichier(slug)}.html">'
        f'<meta name="description" content="{H.escape(desc, quote=True)}">'
        + jsonld.bloc(jsonld.fil("stages.html", "Stages de voile"), itemlist)
        + f"<style>{site_blocks.ENTETE_CSS}{CSS}</style></head><body>"
        + site_blocks.entete_site("stages.html", site_blocks.LANGUES)
        + '<main class="page">'
        f'<a class="retour" href="/stages.html">← Tous les stages</a>'
        f"<h1>{H.escape(nom)}</h1>"
        f'<p class="chapo">{len(offres)} stage(s) publié(s)'
        + (f" · {H.escape(pays)}" if pays else "")
        + (f' · prix de {bas:,.0f}'.replace(",", " ") + f" à {haut:,.0f}".replace(",", " ") + f" {devise}" if bas is not None else "")
        + (f' · première date le {_dt(dates[0])}' if dates else "")
        + f" · prix vérifiés le {_dt(derniere)}.</p>"
        '<table class="tab-ecole"><thead><tr><th>Dates</th><th>Stage</th><th>Durée</th><th>Prix</th></tr></thead>'
        f'<tbody>{"".join(lignes)}</tbody></table>'
        '<p class="pied">La langue du cours et le niveau ne sont pas affichés : nous ne les connaissons pas '
        'pour cette école, et nous préférons ne rien dire plutôt que de deviner.</p>'
        '<p class="pied"><a href="/stages.html">Comparer ces stages avec ceux des autres écoles</a></p>'
        "</main></body></html>"
    )


def ecrire_ecoles(dossier: Path = SITE) -> int:
    """Écrit une page par école : `ecole-<slug>.html`. Rend le nombre de pages écrites."""
    d = charger()
    offres = [avec_niveau(_avec_position(o)) for o in d.get("offres", [])
              if affichable(o) and not non_stage(o.get("titre"), o.get("prix_eur"))]
    par: dict[str, list[dict]] = {}
    for o in offres:
        par.setdefault(_slug_fichier(o.get("ecole_slug") or o.get("ecole") or ""), []).append(o)
    dossier.mkdir(parents=True, exist_ok=True)
    for slug, lot in par.items():
        (dossier / f"ecole-{slug}.html").write_text(_page_ecole(slug, lot), encoding="utf-8")
    return len(par)


def ecrire_page(dossier: Path = SITE) -> int:
    """Écrit `stages.html` dans `dossier` — appelé par `accueil_site.sortir_le_site`.

    Plus de photos à recopier (25/11/2026 : Nicolas les a fait retirer, « ça ressemble à rien »).
    """
    dossier.mkdir(parents=True, exist_ok=True)
    d = charger()
    (dossier / "stages.html").write_text(construire(d), encoding="utf-8")
    ecrire_bloc(dossier, [o for o in d.get("offres", []) if affichable(o)])
    # Comptes du niveau et de la certification, sur toutes les offres de la base puis sur les publiables.
    toutes = [avec_niveau(o) for o in d.get("offres", [])]
    for libelle, lot in (("base", toutes), ("publiables", [o for o in toutes if affichable(o)])):
        c = stages_niveaux.comptes(lot)
        print(f"stages ({libelle}) : {c['offres']} offres · {c['niveau']} avec un niveau · "
              f"{c['certif']} avec une certification · {c['vides']} sans l'un ni l'autre")
    return sum(1 for o in d.get("offres", []) if affichable(o))


if __name__ == "__main__":
    print(f"stages.html : {ecrire_page()} offre(s) publiable(s)")
