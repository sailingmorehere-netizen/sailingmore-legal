#!/usr/bin/env python3
# © 2026 Sailing More — tous droits réservés. All rights reserved.
"""Construit la page `lexique.html` du site : le lexique de voile, avec recherche et filtres par thème.

Entrée  : `projets/sailingmore/lexique.json` — la seule source des mots (six langues par terme).
Sortie  : `projets/sailingmore/site/lexique.html`.

    python3 scripts/lexique_page.py --verifier   # contrôle le JSON (six langues, 12–25 mots) — lecture seule
    python3 scripts/lexique_page.py --site       # écrit la page dans projets/sailingmore/site
    python3 scripts/lexique_page.py --publier    # envoie la page déjà habillée de la mer, sans la réécrire

Sans drapeau, rien n'est écrit. La page est autonome : tous les termes sont embarqués dans un
`<script type="application/json">`, rien n'est chargé par `fetch`, la page s'affiche hors ligne. Une
version française est aussi écrite dans le HTML lui-même : sans JavaScript, la liste reste lisible.

La mer animée n'est pas écrite ici : `accueil_site.poser_mer_partout()` la pose sur chaque page de
`site/` à la construction du site, y compris celle-ci.
"""
from __future__ import annotations

import html as _html
import json
import os
import sys
import unicodedata
from pathlib import Path

ICI = Path(os.environ.get("SAILINGMORE_RACINE", "/opt/data"))
JSON = ICI / "projets/sailingmore/lexique.json"
SITE = ICI / "projets/sailingmore/site"
import sys as _sys
_sys.path.insert(0, str(Path(__file__).resolve().parent))
from site_blocks import LANGUES  # noqa: E402  (une seule liste pour toutes les pages)

# Le texte de la page elle-même (titre, recherche, compteur…), dans les six langues.
UI = {
    "fr": {"titre": "Lexique de voile",
           "chapo": "Les mots de la voile, chacun expliqué en une phrase et traduit en six langues.",
           "retour": "← Sailing More", "placeholder": "Un mot, une pièce du bateau, une définition…",
           "aria": "Rechercher dans le lexique", "tous": "Tous", "theme": "Thème",
           "un": "terme", "n": "termes", "aucun": "Aucun terme ne correspond à cette recherche.",
           "desole": "Désolé pour le français : le breton de ce mot manque encore.",
           "cours": "Le cours", "stage": "Un stage à réserver", "trad": "Traduction", "mot2": "Deuxième mot", "detail": "Le mot en détail"},
    "en": {"titre": "Sailing glossary",
           "chapo": "The words of sailing, each explained in one sentence and translated into six languages.",
           "retour": "← Sailing More", "placeholder": "A word, a part of the boat, a definition…",
           "aria": "Search the glossary", "tous": "All", "theme": "Theme",
           "un": "term", "n": "terms", "aucun": "No term matches this search.",
           "cours": "The lesson", "stage": "Book a course", "trad": "Translation", "mot2": "Second word", "detail": "The word in detail"},
    "it": {"titre": "Lessico della vela",
           "chapo": "Le parole della vela, ciascuna spiegata in una frase e tradotta in sei lingue.",
           "retour": "← Sailing More", "placeholder": "Una parola, un pezzo della barca, una definizione…",
           "aria": "Cerca nel lessico", "tous": "Tutti", "theme": "Tema",
           "un": "termine", "n": "termini", "aucun": "Nessun termine corrisponde a questa ricerca.",
           "cours": "La lezione", "stage": "Prenota un corso", "trad": "Traduzione", "mot2": "Seconda parola", "detail": "La parola in dettaglio"},
    "es": {"titre": "Léxico de vela",
           "chapo": "Las palabras de la vela, cada una explicada en una frase y traducida a seis idiomas.",
           "retour": "← Sailing More", "placeholder": "Una palabra, una pieza del barco, una definición…",
           "aria": "Buscar en el léxico", "tous": "Todos", "theme": "Tema",
           "un": "término", "n": "términos", "aucun": "Ningún término coincide con esta búsqueda.",
           "cours": "La lección", "stage": "Reservar un curso", "trad": "Traducción", "mot2": "Segunda palabra", "detail": "La palabra en detalle"},
    "pt": {"titre": "Léxico de vela",
           "chapo": "As palavras da vela, cada uma explicada numa frase e traduzida para seis línguas.",
           "retour": "← Sailing More", "placeholder": "Uma palavra, uma peça do barco, uma definição…",
           "aria": "Pesquisar no léxico", "tous": "Todos", "theme": "Tema",
           "un": "termo", "n": "termos", "aucun": "Nenhum termo corresponde a esta pesquisa.",
           "cours": "A lição", "stage": "Reservar um curso", "trad": "Tradução", "mot2": "Segunda palavra", "detail": "A palavra em detalhe"},
    "pl": {"titre": "Słownik żeglarski",
           "chapo": "Słowa żeglarstwa, każde wyjaśnione jednym zdaniem i przetłumaczone na sześć języków.",
           "retour": "← Sailing More", "placeholder": "Słowo, część łodzi, definicja…",
           "aria": "Szukaj w słowniku", "tous": "Wszystkie", "theme": "Temat",
           "un": "hasło", "n": "haseł", "aucun": "Żadne hasło nie pasuje do tego wyszukiwania.",
           "cours": "Lekcja", "stage": "Zarezerwuj kurs", "trad": "Tłumaczenie", "mot2": "Drugie słowo", "detail": "Słowo w szczegółach"},
    "de": {"titre": "Segel-Lexikon",
           "chapo": "Die Wörter des Segelns, jedes in einem Satz erklärt und in sechs Sprachen übersetzt.",
           "retour": "← Sailing More", "placeholder": "Ein Wort, ein Bootsteil, eine Definition…",
           "aria": "Im Lexikon suchen", "tous": "Alle", "theme": "Thema",
           "un": "Begriff", "n": "Begriffe", "aucun": "Kein Begriff passt zu dieser Suche.",
           "cours": "Die Lektion", "stage": "Kurs buchen", "trad": "Übersetzung", "mot2": "Zweites Wort", "detail": "Das Wort im Detail"},
}

# Chaque mot renvoie à deux endroits (Nicolas, 25/11/2026 : « il faut que les mots des lexiques renvoient
# vers une proposition de cours lié ») : le chapitre du cours qui traite son thème, puis un stage à
# réserver. Le chapitre se choisit par thème — un mot isolé n'a pas de leçon à lui, et une table de
# 500 entrées une par une serait une devinette. `stages.html?q=<mot français>` ouvre la recherche déjà
# remplie : les stages sont écrits en français, on cherche donc toujours le mot français.
COURS_PAR_THEME = {
    "bateau": "vocabulaire", "manoeuvre": "manoeuvres", "allures": "vent", "meteo": "meteo",
    "course": "priorites", "securite": "securite", "navigation": "cap",
    "accastillage": "equiper", "types-de-bateaux": "vocabulaire", "vie-a-bord": "embarquer",
}
COURS_DEFAUT = "vocabulaire"

# Le nom de chaque langue dans sa propre langue, pour la barre de traduction en tête de page.
NOMS_LANGUES = {"fr": "français", "en": "English", "de": "Deutsch",
                "it": "italiano", "es": "español", "pt": "português"}


def numero_chapitre() -> dict[str, int]:
    """Le numéro de chaque chapitre, lu dans `cours_page.CHAPITRES` — l'ordre de ce fichier décide,
    donc un chapitre déplacé déplace les liens sans qu'on retouche cette page."""
    from cours_page import CHAPITRES
    return {c["id"]: i + 1 for i, c in enumerate(CHAPITRES)}


def ancre_cours(cle_theme: str) -> str:
    """L'ancre réelle dans `cours.html` : `#ch<N>-<langue>`, la langue étant celle de la page."""
    return COURS_PAR_THEME.get(cle_theme, COURS_DEFAUT)


def liens_vers(x: dict, cle_theme: str, lang: str) -> str:
    """Les deux liens d'un mot : son chapitre de cours, puis le stage à réserver."""
    from urllib.parse import quote
    e = _html.escape
    u = UI.get(lang, UI["fr"])
    n = numero_chapitre().get(ancre_cours(cle_theme), 1)
    langue = lang if lang in LANGUES else "fr"
    return (f'<p class="vers"><a href="lexique/{e(x["cle"])}.html">{e(u["detail"])}</a>'
            f'<a href="cours.html#ch{n}-{langue}">{e(u["cours"])}</a>'
            f'<a href="stages.html?q={quote(x["mot"]["fr"])}">{e(u["stage"])}</a></p>')

# Mêmes variables et mêmes gestes que regates_page.py : charte Signal B, filets droits, rouge qui
# souligne et n'écrit pas (jamais de texte courant en rouge).
CSS = """
:root{--nuit:#0a1a2b;--panneau:#0f2438;--ivoire:#eef3f7;--gris:#9db2c6;--rouge:#e23a3e}
*{box-sizing:border-box}
@media (prefers-reduced-motion:no-preference){html{scroll-behavior:smooth}}
body{margin:0;background:#071c31;color:var(--ivoire);
  font-family:ui-sans-serif,system-ui,-apple-system,"Helvetica Neue",Arial,sans-serif;
  line-height:1.6;-webkit-font-smoothing:antialiased}
.page{max-width:64rem;margin:0 auto;padding:3.6rem 1.4rem 5rem}
.haut{display:flex;justify-content:space-between;align-items:center;gap:1rem;flex-wrap:wrap}
a.retour{color:var(--gris);text-decoration:none;font-size:.64rem;letter-spacing:.14em;
  text-transform:uppercase;font-weight:500}
a.retour:hover{color:#fff}
.langues{display:flex;gap:.15rem;align-items:center}
.langues button{background:none;border:0;color:var(--gris);font:inherit;font-size:.72rem;
  padding:.2rem .45rem;border-radius:2px;cursor:pointer;letter-spacing:.04em}
.langues button:hover{color:#fff}
.langues button[aria-pressed="true"]{color:#fff;box-shadow:inset 0 -2px 0 var(--rouge)}
h1{font-size:clamp(1.9rem,6vw,2.7rem);line-height:1.04;margin:1.6rem 0 0;letter-spacing:-.01em;
  color:#fff;font-weight:300;text-transform:uppercase}
h1::after{content:"";display:block;width:3.4rem;height:3px;background:var(--rouge);margin:1.3rem 0 1.6rem}
.chapo{color:var(--gris);font-size:.95rem;max-width:34rem;margin:0 0 1.5rem}
.trad{display:flex;gap:.4rem;flex-wrap:wrap;align-items:center;margin:0 0 2rem}
.trad .dit{font-size:.66rem;letter-spacing:.14em;text-transform:uppercase;color:#6f8598;margin-right:.45rem}
.trad button{background:none;border:1px solid rgba(157,178,198,.32);color:#9db2c6;border-radius:999px;
  padding:.3rem .75rem;font:inherit;font-size:.78rem;line-height:1.2;cursor:pointer;
  transition:color .15s,border-color .15s,background .15s}
.trad button:hover{color:#fff;border-color:#9db2c6}
.trad button[aria-pressed="true"]{border-color:var(--rouge);color:#fff;background:rgba(226,58,62,.14)}
/* Deux mots côte à côte : le même terme dans la langue de la page et dans celle qu'on a choisie. */
.terme.double{display:grid;grid-template-columns:1fr 1fr;column-gap:1.8rem;row-gap:.2rem}
.terme.double .col h3{margin-top:0}
.terme.double .vers{grid-column:1 / -1}
@media (max-width:700px){.terme.double{grid-template-columns:1fr;column-gap:0}
  .terme.double .col+.col{margin-top:.4rem;padding-top:.6rem;border-top:1px solid rgba(255,255,255,.07)}}
a{color:#fff;text-decoration:none}
:focus-visible{outline:2px solid #fff;outline-offset:2px}

.panneau{background:#0a1f33;border:1px solid rgba(255,255,255,.09);border-radius:2px;
  padding:0 1.2rem 1.4rem;margin:0 0 1rem;box-shadow:0 18px 50px rgba(0,0,0,.35)}
.recherche{position:sticky;top:0;z-index:20;background:#0a1f33;
  padding:.9rem 1.2rem 1rem;margin:0 -1.2rem .4rem}
.champ{display:flex;align-items:center;gap:.6rem;background:var(--panneau);
  border:1px solid rgba(255,255,255,.13);border-radius:3px;padding:.62rem .8rem}
.champ:focus-within{border-color:rgba(226,58,62,.7)}
.champ input{flex:1;background:none;border:0;color:var(--ivoire);font-size:.95rem;outline:none;
  font-family:inherit;min-width:0}
.champ input::placeholder{color:#6f8598}
.champ svg{flex:0 0 auto;opacity:.55}
.filtres{display:flex;flex-wrap:wrap;gap:.35rem;align-items:center;margin-top:.7rem}
.filtres .etiq{font-size:.58rem;letter-spacing:.18em;text-transform:uppercase;color:#6f8598;
  margin-right:.2rem}
.puce{font:inherit;font-size:.72rem;letter-spacing:.04em;color:var(--gris);background:none;
  border:1px solid rgba(255,255,255,.16);border-radius:2px;padding:.28rem .6rem;cursor:pointer}
.puce:hover{color:#fff;border-color:rgba(255,255,255,.4)}
.puce[aria-pressed="true"]{color:#fff;border-color:var(--rouge);background:rgba(226,58,62,.14)}
@media (prefers-reduced-motion:no-preference){
  .puce{transition:color .15s,border-color .15s,background .15s}}
.compte{color:var(--gris);font-size:.72rem;letter-spacing:.06em;margin:.9rem 0 .2rem}
.compte b{color:#fff;font-weight:500}

.theme{margin:0 0 2.2rem}
.theme h2{font-size:.64rem;letter-spacing:.22em;text-transform:uppercase;color:var(--gris);
  font-weight:500;margin:0 0 .2rem;padding-top:1rem;border-top:1px solid rgba(226,58,62,.22)}
.theme h2 span{color:#6f8598;letter-spacing:.1em;margin-left:.5rem}
.terme{padding:.95rem 0 .9rem .9rem;border-bottom:1px solid rgba(255,255,255,.07);
  border-left:3px solid transparent;scroll-margin-top:9rem}
.terme:hover{background:rgba(255,255,255,.025)}
.terme:target{border-left-color:var(--rouge);background:rgba(226,58,62,.06)}
.terme h3{margin:0;font-size:1.05rem;font-weight:500;color:#fff;line-height:1.35}
.terme h3 a:hover{text-decoration:underline;text-decoration-color:rgba(226,58,62,.7);
  text-underline-offset:.25em}
.terme .def{margin:.25rem 0 0;color:#c9d6e2;font-size:.92rem;max-width:44rem}
.terme .autres{margin:.45rem 0 0;color:#6f8598;font-size:.7rem;letter-spacing:.04em;
  display:flex;flex-wrap:wrap;gap:.25rem .8rem}
/* `nowrap` seul laissait la ligne des cinq équivalents déborder de la page sur un écran étroit
   (scrollWidth 1042 pour 780 px de fenêtre, 21/11/2026) : le flex-wrap garantit le repli. */
.terme .autres span{white-space:nowrap;min-width:0;overflow-wrap:anywhere}
.terme .autres b{color:var(--gris);font-weight:500}
.terme .autres .manque{opacity:.75}
.terme .autres .manque i{font-style:italic;color:#8fa3b5}
.terme .autres .manque sup{font-size:.85em;vertical-align:.2em}
.terme .vers{margin:.55rem 0 0;display:flex;gap:1rem;flex-wrap:wrap;font-size:.7rem;
  letter-spacing:.04em;text-transform:uppercase}
.terme .vers a{color:#9db2c6;border-bottom:1px solid rgba(226,58,62,.45);padding-bottom:1px}
.terme .vers a:hover{color:#fff;border-bottom-color:var(--rouge)}
.vide{padding:3rem 0;color:var(--gris);font-size:.9rem}
.pied{margin-top:3.6rem;padding-top:1.2rem;border-top:1px solid rgba(255,255,255,.09);
  color:#6f8598;font-size:.72rem;line-height:1.8}

@media (max-width:640px){
  .page{padding:2.4rem 1rem 4rem}
  .recherche{padding:.7rem 0 .8rem}
  .filtres .etiq{width:100%}
  .terme{padding-left:.6rem;scroll-margin-top:11rem}
}
"""

JS = r"""
(function(){
  var data = JSON.parse(document.getElementById('donnees-lexique').textContent);
  var UI = data.ui, LANGUES = data.langues;
  var champ = document.getElementById('champ-q');
  var liste = document.getElementById('liste-termes');
  var compte = document.getElementById('compte-termes');
  var zoneThemes = document.getElementById('themes');
  var etat = {theme:'tous', texte:''};

  // Même choix de langue que l'accueil (clé « sm-langue », « auto » = langue du navigateur) :
  // le code de l'accueil est dans un gabarit de page, on ne peut pas l'importer — voir le rapport.
  function stocke(){ try{ return localStorage.getItem('sm-langue') || 'auto'; }catch(e){ return 'auto'; } }
  /* La langue est choisie une seule fois, dans le <head> (24/11/2026). On lit le résultat. */
  function choisir(){
    var l = (typeof window.smLangue === 'function') ? window.smLangue() : 'en';
    if(l === 'bzh') l = 'fr';
    return UI[l] ? l : 'en';
  }
  var lang = choisir();
  // Le deuxième mot : la langue choisie dans la barre « Deuxième mot ». Tant qu'elle vaut null,
  // la page s'affiche normalement ; dès qu'elle diffère de `lang`, chaque terme montre les deux.
  var langB = (function(){ try{ return localStorage.getItem('sm-lexique-b') || null; }catch(e){ return null; } })();
  if (langB && langB === 'bzh') langB = null;

  function normalise(s){return (s||'').toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g,'');}
  function esc(s){return String(s).replace(/[&<>"]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];});}

  // Un thème sans terme ne s'affiche pas (ni section, ni bouton).
  var themes = data.themes.filter(function(t){ return t.termes && t.termes.length; });
  themes.forEach(function(t){
    t.termes.forEach(function(x){ x._foin = {}; LANGUES.forEach(function(l){
      x._foin[l] = normalise(x.mot[l] + ' ' + x.def[l]); }); });
  });

  function boutonsThemes(){
    var u = UI[lang];
    var h = '<span class="etiq">' + esc(u.theme) + '</span>'
      + '<button class="puce" type="button" data-theme="tous" aria-pressed="' + (etat.theme==='tous') + '">' + esc(u.tous) + '</button>';
    themes.forEach(function(t){
      h += '<button class="puce" type="button" data-theme="' + esc(t.cle) + '" aria-pressed="' + (etat.theme===t.cle) + '">' + esc(t.nom[lang]) + '</button>';
    });
    zoneThemes.innerHTML = h;
  }

  function carte(x, t){
    var u = UI[lang], autres = LANGUES.filter(function(l){return l!==lang && l!==langB;}).map(function(l){
      return '<span lang="' + l + '">' + l + ' <b>' + esc(x.mot[l]) + '</b></span>'; }).join('');
    // Le breton : le mot s'il est attesté, sinon le français avec le petit mot d'excuse (Nicolas,
    // 24/11/2026 : « ceux que t'as pas, tu les fais en français […] désolé pour le français »).
    if (lang !== 'bzh') {
      autres += x.mot.bzh
        ? '<span lang="br">br <b>' + esc(x.mot.bzh) + '</b></span>'
        : '<span lang="br" class="manque" title="' + esc(UI.fr.desole) + '">br <i>' + esc(x.mot.fr)
          + '</i> <sup aria-hidden="true">☺</sup></span>';
    }
    var liens = '<p class="vers"><a href="lexique/' + encodeURIComponent(x.cle) + '.html">'
      + esc(u.detail) + '</a><a href="cours.html#ch' + (data.cours[t.cle] || data.cours_defaut)
      + '-' + (lang === 'bzh' ? 'fr' : lang) + '">'
      + esc(u.cours) + '</a><a href="stages.html?q=' + encodeURIComponent(x.mot.fr) + '">'
      + esc(u.stage) + '</a></p>';
    if (langB && langB !== lang) {   // deux mots : le terme dans les deux langues, l'un à côté de l'autre
      return '<article class="terme double" id="' + esc(x.cle) + '">'
        + '<div class="col"><h3 lang="' + lang + '"><a href="#' + esc(x.cle) + '">'
        + esc(x.mot[lang]) + '</a></h3><p class="def" lang="' + lang + '">' + esc(x.def[lang]) + '</p></div>'
        + '<div class="col"><h3 lang="' + langB + '">' + esc(x.mot[langB]) + '</h3>'
        + '<p class="def" lang="' + langB + '">' + esc(x.def[langB]) + '</p></div>'
        + '<p class="autres">' + autres + '</p>' + liens + '</article>';
    }
    return '<article class="terme" id="' + esc(x.cle) + '">'
      + '<h3><a href="#' + esc(x.cle) + '">' + esc(x.mot[lang]) + '</a></h3>'
      + '<p class="def">' + esc(x.def[lang]) + '</p>'
      + '<p class="autres">' + autres + '</p>' + liens + '</article>';
  }

  function dessine(){
    var u = UI[lang], q = normalise(etat.texte).trim(), total = 0, h = '';
    themes.forEach(function(t){
      if(etat.theme !== 'tous' && etat.theme !== t.cle) return;
      var gardes = t.termes.filter(function(x){
        if (!q) return true;
        if (x._foin[lang].indexOf(q) !== -1) return true;
        return !!(langB && langB !== lang && x._foin[langB] && x._foin[langB].indexOf(q) !== -1);
      });
      if(!gardes.length) return;
      gardes.sort(function(a,b){ return a.mot[lang].localeCompare(b.mot[lang], lang); });
      total += gardes.length;
      h += '<section class="theme"><h2>' + esc(t.nom[lang]) + '<span>' + gardes.length + '</span></h2>'
        + gardes.map(function(x){ return carte(x, t); }).join('') + '</section>';
    });
    liste.innerHTML = h || '<p class="vide">' + esc(u.aucun) + '</p>';
    compte.innerHTML = '<b>' + total + '</b> ' + (total > 1 ? u.n : u.un);
  }

  function traduit(){
    var u = UI[lang];
    document.documentElement.lang = lang;
    document.title = u.titre + ' — Sailing More';
    document.querySelectorAll('[data-t]').forEach(function(el){ el.textContent = u[el.dataset.t]; });
    champ.placeholder = u.placeholder;
    champ.setAttribute('aria-label', u.aria);
    // L'état affiché suit les langues réellement en cours, pas le stockage local.
    document.querySelectorAll('#langues button').forEach(function(b){
      b.setAttribute('aria-pressed', String(b.dataset.lang === lang)); });
    document.querySelectorAll('#trad button').forEach(function(b){
      b.setAttribute('aria-pressed', String(b.dataset.lang === langB)); });
    boutonsThemes();
    dessine();
  }

  function versLAncre(){
    var id = decodeURIComponent((location.hash||'').slice(1));
    if(!id) return;
    var el = document.getElementById(id);
    // Le terme est filtré par la recherche ou le thème : on lève les filtres pour qu'un lien direct marche.
    if(!el && (etat.texte || etat.theme !== 'tous')){
      etat = {theme:'tous', texte:''}; champ.value = ''; boutonsThemes(); dessine();
      el = document.getElementById(id);
    }
    if(el) el.scrollIntoView();
  }

  document.querySelectorAll('#langues button').forEach(function(b){
    b.addEventListener('click', function(){
      try{ localStorage.setItem('sm-langue', b.dataset.lang); }catch(e){}
      lang = choisir(); traduit();
    });
  });
  // La barre de traduction commande directement la langue : passer par `choisir()` la faisait
  // dépendre du stockage local, qui lève sur certains navigateurs en aperçu local.
  document.querySelectorAll('#trad button').forEach(function(b){
    b.addEventListener('click', function(){
      try{ localStorage.setItem('sm-langue', b.dataset.lang); }catch(e){}
      // Deuxième mot : cliquer la langue déjà choisie la retire et revient à l'affichage simple.
      langB = (b.dataset.lang === langB) ? null : b.dataset.lang;
      try{ localStorage.setItem('sm-lexique-b', langB || ''); }catch(e){}
      traduit();
    });
  });
  zoneThemes.addEventListener('click', function(ev){
    var b = ev.target.closest('.puce'); if(!b) return;
    etat.theme = b.dataset.theme; boutonsThemes(); dessine();
  });
  champ.addEventListener('input', function(){ etat.texte = champ.value; dessine(); });
  window.addEventListener('hashchange', versLAncre);

  traduit();
  versLAncre();
})();
"""


def charger() -> dict:
    if not JSON.exists():
        raise SystemExit(f"{JSON} absent")
    return json.loads(JSON.read_text(encoding="utf-8"))


def sans_accent(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", s.lower()) if not unicodedata.combining(c))


def themes_affichables(d: dict) -> list[dict]:
    """Un thème sans terme ne s'affiche pas."""
    return [t for t in d["themes"] if t.get("termes")]


def liste_statique(d: dict, lang: str = "fr") -> str:
    """La liste en français écrite dans le HTML : ce que voit une page sans JavaScript, ou le temps
    que le script démarre. Même balisage que `carte()` / `dessine()` dans le JS."""
    e = _html.escape
    sortie = []
    for t in themes_affichables(d):
        termes = sorted(t["termes"], key=lambda x: sans_accent(x["mot"][lang]))
        cartes = []
        for x in termes:
            autres = "".join(
                f'<span lang="{l}">{l} <b>{e(x["mot"][l])}</b></span>' for l in LANGUES if l != lang)
            if lang != "bzh":
                autres += (f'<span lang="br">br <b>{e(x["mot"]["bzh"])}</b></span>'
                           if x["mot"].get("bzh") else
                           f'<span lang="br" class="manque" title="{e(UI["fr"]["desole"])}">br '
                           f'<i>{e(x["mot"][lang])}</i> <sup aria-hidden="true">☺</sup></span>')
            cartes.append(
                f'<article class="terme" id="{e(x["cle"])}">'
                f'<h3><a href="#{e(x["cle"])}">{e(x["mot"][lang])}</a></h3>'
                f'<p class="def">{e(x["def"][lang])}</p><p class="autres">{autres}</p>'
                + liens_vers(x, t["cle"], lang) + '</article>')
        sortie.append(f'<section class="theme"><h2>{e(t["nom"][lang])}<span>{len(termes)}</span></h2>'
                      + "".join(cartes) + "</section>")
    return "".join(sortie)


def _ld_lexique(themes: list[dict]) -> str:
    """JSON-LD : fil d'Ariane + DefinedTermSet + un DefinedTerm par mot (mot et définition français, mécanique)."""
    import jsonld
    url = f"{jsonld.SITE}/lexique.html"
    ens = f"{url}#lexique"
    termes = [{"@type": "DefinedTerm", "@id": f"{url}#{x['cle']}", "name": x["mot"]["fr"],
               "description": x["def"]["fr"], "url": f"{url}#{x['cle']}", "inDefinedTermSet": {"@id": ens}}
              for t in themes for x in t["termes"]]
    jeu = {"@type": "DefinedTermSet", "@id": ens, "name": "Lexique de voile", "url": url,
           "inLanguage": "fr", "hasDefinedTerm": [{"@id": x["@id"]} for x in termes]}
    return jsonld.bloc(jsonld.fil("lexique.html", "Lexique de voile"), jeu, *termes)


def page_lexique(d: dict | None = None) -> str:
    d = d or charger()
    themes = themes_affichables(d)
    total = sum(len(t["termes"]) for t in themes)
    ui = UI["fr"]
    donnees = {"langues": LANGUES, "ui": UI, "themes": themes,
               "cours": {c: numero_chapitre().get(a, 1) for c, a in COURS_PAR_THEME.items()},
               "cours_defaut": numero_chapitre().get(COURS_DEFAUT, 1)}
    # `</` dans un JSON embarqué fermerait le <script> : on l'échappe.
    brut = json.dumps(donnees, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    # La barre du site (nom, menu, langues) vient d'un seul endroit : site_blocks (23/11/2026).
    import site_blocks as _sb  # noqa: PLC0415
    themes_html = (
        f'<span class="etiq">{ui["theme"]}</span>'
        '<button class="puce" type="button" data-theme="tous" aria-pressed="true">'
        f'{ui["tous"]}</button>'
        + "".join(f'<button class="puce" type="button" data-theme="{_html.escape(t["cle"])}" '
                  f'aria-pressed="false">{_html.escape(t["nom"]["fr"])}</button>' for t in themes))
    # Audit SEO du 24/11/2026, correction 4 : textes de l'audit, le compteur vient de `total` (les termes).
    seo_titre = f"Lexique de la voile : {total} mots définis | Sailing More"
    seo_desc = (f"Bôme, choquer, lofer, empanner : {total} mots de la voile définis en une phrase, classés par "
                "thème, en six langues, chacune avec le chapitre du cours et le stage qui vont avec.")
    return (
        '<!doctype html>\n<html lang="fr"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        f"<title>{seo_titre}</title>"
        '<link rel="canonical" href="https://sailingmore.fr/lexique.html">'
        + _ld_lexique(themes) +
        f'<meta name="description" content="{seo_desc}">'
        + __import__("jsonld").social("lexique.html", seo_titre, seo_desc) +
        "<style>" + CSS + "</style></head><body>"
        + _sb.barre_autonome("lexique.html", LANGUES) +
        '<main class="page">'
        '<h1 data-t="titre">' + ui["titre"] + "</h1>"
        '<p class="chapo" data-t="chapo">' + ui["chapo"] + "</p>"
        '<nav class="trad" id="trad" aria-label="' + ui["mot2"] + '">'
        '<span class="dit" data-t="mot2">' + ui["mot2"] + "</span>"
        + "".join(f'<button type="button" data-lang="{l}">{NOMS_LANGUES[l]}</button>' for l in LANGUES)
        + "</nav>"
        '<div class="panneau">'
        '<div class="recherche"><div class="champ">'
        '<svg width="15" height="15" viewBox="0 0 16 16" fill="none" aria-hidden="true">'
        '<circle cx="7" cy="7" r="5" stroke="#eef3f7" stroke-width="1.4"/>'
        '<path d="M10.6 10.6 14 14" stroke="#eef3f7" stroke-width="1.4"/></svg>'
        f'<input id="champ-q" type="search" placeholder="{ui["placeholder"]}" '
        f'aria-label="{ui["aria"]}" autocomplete="off"></div>'
        '<div class="filtres" id="themes">' + themes_html + "</div></div>"
        f'<div class="compte" id="compte-termes" role="status" aria-live="polite">'
        f'<b>{total}</b> {ui["n"] if total > 1 else ui["un"]}</div>'
        '<div id="liste-termes">' + liste_statique(d) + "</div>"
        "</div></main>"
        '<script type="application/json" id="donnees-lexique">' + brut + "</script>"
        "<script>" + JS + "</script>"
        "</body></html>\n"
    )


def verifier(d: dict) -> list[str]:
    """Contrôle en lecture seule : six langues partout, définitions de 12 à 25 mots, clés uniques."""
    problemes: list[str] = []
    if d.get("langues") != LANGUES:
        problemes.append(f"« langues » vaut {d.get('langues')}, attendu {LANGUES}")
    vues: set[str] = set()
    for t in d.get("themes", []):
        for l in LANGUES:
            if not t.get("nom", {}).get(l):
                problemes.append(f"thème {t.get('cle')} : nom {l} absent")
        for x in t.get("termes", []):
            cle = x.get("cle", "?")
            if cle in vues:
                problemes.append(f"clé en double : {cle}")
            vues.add(cle)
            for l in LANGUES:
                if not x.get("mot", {}).get(l):
                    problemes.append(f"{cle} : mot {l} absent")
                phrase = x.get("def", {}).get(l, "")
                n = len(phrase.split())
                if not 12 <= n <= 25:
                    problemes.append(f"{cle} : définition {l} de {n} mots (12 à 25 attendus)")
    return problemes


def main() -> int:
    if not any(a in sys.argv for a in ("--site", "--publier", "--verifier")):
        print("Rien à faire : --verifier (lecture seule), --site (écrit la page) ou --publier.",
              file=sys.stderr)
        return 2
    d = charger()
    problemes = verifier(d)
    n = sum(len(t["termes"]) for t in d["themes"])
    if "--verifier" in sys.argv:
        for p in problemes:
            print("ÉCHEC · " + p)
        print(("ÉCHEC" if problemes else "OK") + f" · {n} termes, {len(d['themes'])} thème(s)")
        return 1 if problemes else 0
    if problemes:
        for p in problemes:
            print("ÉCHEC · " + p)
        return 1
    if "--site" in sys.argv:
        SITE.mkdir(parents=True, exist_ok=True)
        page = page_lexique(d)
        (SITE / "lexique.html").write_text(page, encoding="utf-8")
        print(f"{SITE / 'lexique.html'} · {len(page):,} car · {n} termes".replace(",", " "))
    if "--publier" in sys.argv:
        # La mer et l'équilibre sont posés par `accueil_site.py --site` sur toutes les pages de site/ :
        # on n'envoie pas une page nue. Cette ligne n'envoie qu'elle, en ajout au dépôt existant.
        # --publier ne réécrit pas la page : réécrire effacerait la mer posée par la construction.
        if not (SITE / "lexique.html").exists() or \
                "<!--mer-debut-->" not in (SITE / "lexique.html").read_text(encoding="utf-8"):
            print("page sans mer : lancer d'abord `accueil_site.py --site`, puis `--publier`.")
            return 1
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        import accueil_site
        accueil_site.miroir_vers_sortie(["lexique.html"])
        accueil_site.publier_en_un_seul_envoi(["lexique.html"], "site : lexique de voile")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
