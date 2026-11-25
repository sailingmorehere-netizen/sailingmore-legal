#!/usr/bin/env python3
"""Construit la page `regles-de-course.html` : les règles de course à la voile (RRS 2025-2028), avec
recherche (numéro, titre, résumé, situation vécue) et filtres (partie, thème).

Entrée  : `regles.json`, à côté de ce script — la seule source (six langues par règle).
Contrôle: le texte officiel extrait du PDF, `regles/rrs-2025-2028.txt` (racine du projet).
Sortie  : `projets/sailingmore/site/regles-de-course.html`.

    python3 scripts/regles_page.py --verifier   # contrôle le JSON et sa couverture du PDF — lecture seule
    python3 scripts/regles_page.py --site       # écrit la page dans projets/sailingmore/site
    python3 scripts/regles_page.py --apercu     # écrit `regles-apercu.html` sans exiger la couverture complète
    python3 scripts/regles_page.py --publier    # envoie la page déjà habillée de la mer, sans la réécrire

Ce qu'on publie : le numéro, l'intitulé officiel, NOTRE résumé, NOS exemples, les renvois, le lien vers le
PDF officiel. Jamais le texte des règles, jamais la traduction FFVoile, jamais un cas du Case Book recopié
(copyright World Sailing, 22/11/2026 — voir projets/sailingmore/brief-page-regles.md).

Même construction que `lexique_page.py` : toutes les règles sont embarquées dans un
`<script type="application/json">`, rien n'est chargé par `fetch`, et la liste française est aussi écrite
dans le HTML (la page se lit sans JavaScript). La mer est posée plus tard par `accueil_site.py`.

Garde-fou : tant que `regles.json` porte `"complet": false`, `--site` et `ecrire_page()` refusent d'écrire
la page publiable (une page à moitié pleine ne part pas en ligne). `--apercu` sert à la relire.
"""
from __future__ import annotations

import html as _html
import json
import os
import re
import sys
import unicodedata
from pathlib import Path

ICI = Path(os.environ.get("SAILINGMORE_RACINE", "/opt/data"))
JSON = Path(__file__).resolve().parent / "regles.json"
TXT = ICI / "regles/rrs-2025-2028.txt"
PDF = ICI / "regles/RRS-2025-2028.pdf"
SITE = ICI / "projets/sailingmore/site"
sys.path.insert(0, str(Path(__file__).resolve().parent))
from site_blocks import LANGUES  # noqa: E402  (une seule liste pour toutes les pages)
APPENDICES = list("ABCDEFGHJMNPRST")  # vérifié dans le PDF : ni I, ni K, ni L, ni O, ni Q
DEUX_EXEMPLES = {str(n) for n in range(10, 20)} | {"31", "42", "44", "61"}
MIN_MOTS_RESUME = 25

UI = {
    "fr": {"titre": "Règles de course à la voile (RCV)",
           "chapo": "Les règles de course à la voile (RCV 2025-2028) expliquées avec nos mots, un exemple concret pour chacune. "
                    "Cherchez par numéro, par titre ou par situation vécue.",
           "retour": "← Sailing More", "placeholder": "Un numéro (10), un mot (bâbord), une situation (collision)…",
           "aria": "Rechercher dans les règles", "tous": "Toutes", "tous_m": "Tous",
           "partie": "Partie", "themes_lib": "Ce que je cherche", "regles_lib": "Numéro de règle", "toutes_regles": "Toutes les règles",
           "sommaire": "Sommaire",
           "un": "règle", "n": "règles", "aucun": "Aucune règle ne correspond à cette recherche.",
           "defs": "Définitions", "app": "Appendices", "regle": "Règle", "def": "Définition",
           "appendice": "Appendice", "exemple": "Exemple", "issue": "Issue", "voir": "Voir aussi",
           "sanction": "Sanction", "actifs": "Filtres actifs", "retirer": "Retirer le filtre",
           "effacer": "Tout effacer", "pdf": "Texte officiel (PDF gratuit)",
           "source": "Source officielle : Racing Rules of Sailing 2025-2028, © World Sailing Limited. "
                     "Résumés et exemples écrits par Sailing More ; en cas de doute, le texte officiel fait foi.",
           "edition": "Édition", "corr": "corrections du",
           "schema": "Schéma de la règle", "video_lire": "Lire la vidéo",
           "video_tiers": "Vidéo d'un tiers, lue chez YouTube : rien n'est chargé avant votre clic."},
    "en": {"titre": "Sailing racing rules",
           "chapo": "The racing rules (RRS 2025-2028) explained in our own words, with a concrete example for each. "
                    "Search by number, by title or by a situation you lived.",
           "retour": "← Sailing More", "placeholder": "A number (10), a word (port), a situation (collision)…",
           "aria": "Search the rules", "tous": "All", "tous_m": "All",
           "partie": "Part", "themes_lib": "What I am looking for", "regles_lib": "Rule number", "toutes_regles": "All rules",
           "sommaire": "Contents",
           "un": "rule", "n": "rules", "aucun": "No rule matches this search.",
           "defs": "Definitions", "app": "Appendices", "regle": "Rule", "def": "Definition",
           "appendice": "Appendix", "exemple": "Example", "issue": "Outcome", "voir": "See also",
           "sanction": "Penalty", "actifs": "Active filters", "retirer": "Remove the filter",
           "effacer": "Clear all", "pdf": "Official text (free PDF)",
           "source": "Official source: Racing Rules of Sailing 2025-2028, © World Sailing Limited. "
                     "Summaries and examples written by Sailing More; in case of doubt, the official text prevails.",
           "edition": "Edition", "corr": "corrections of",
           "schema": "Diagram of the rule", "video_lire": "Play the video",
           "video_tiers": "Third-party video, played by YouTube: nothing is loaded before you click."},
    "it": {"titre": "Regole di regata a vela",
           "chapo": "Le regole di regata (RRS 2025-2028) spiegate con parole nostre, con un esempio concreto per ciascuna. "
                    "Cerca per numero, per titolo o per situazione vissuta.",
           "retour": "← Sailing More", "placeholder": "Un numero (10), una parola (mura a sinistra), una situazione (collisione)…",
           "aria": "Cerca nelle regole", "tous": "Tutte", "tous_m": "Tutti",
           "partie": "Parte", "themes_lib": "Cosa cerco", "regles_lib": "Numero di regola", "toutes_regles": "Tutte le regole",
           "sommaire": "Indice",
           "un": "regola", "n": "regole", "aucun": "Nessuna regola corrisponde a questa ricerca.",
           "defs": "Definizioni", "app": "Appendici", "regle": "Regola", "def": "Definizione",
           "appendice": "Appendice", "exemple": "Esempio", "issue": "Esito", "voir": "Vedi anche",
           "sanction": "Penalità", "actifs": "Filtri attivi", "retirer": "Rimuovi il filtro",
           "effacer": "Cancella tutto", "pdf": "Testo ufficiale (PDF gratuito)",
           "source": "Fonte ufficiale: Racing Rules of Sailing 2025-2028, © World Sailing Limited. "
                     "Riassunti ed esempi scritti da Sailing More; in caso di dubbio fa fede il testo ufficiale.",
           "edition": "Edizione", "corr": "correzioni del",
           "schema": "Schema della regola", "video_lire": "Guarda il video",
           "video_tiers": "Video di terzi, riprodotto da YouTube: nulla viene caricato prima del tuo clic."},
    "es": {"titre": "Reglas de regata a vela",
           "chapo": "Las reglas de regata (RRS 2025-2028) explicadas con nuestras palabras, con un ejemplo concreto para cada una. "
                    "Busca por número, por título o por una situación vivida.",
           "retour": "← Sailing More", "placeholder": "Un número (10), una palabra (babor), una situación (colisión)…",
           "aria": "Buscar en las reglas", "tous": "Todas", "tous_m": "Todos",
           "partie": "Parte", "themes_lib": "Lo que busco", "regles_lib": "Número de regla", "toutes_regles": "Todas las reglas",
           "sommaire": "Índice",
           "un": "regla", "n": "reglas", "aucun": "Ninguna regla coincide con esta búsqueda.",
           "defs": "Definiciones", "app": "Apéndices", "regle": "Regla", "def": "Definición",
           "appendice": "Apéndice", "exemple": "Ejemplo", "issue": "Resultado", "voir": "Ver también",
           "sanction": "Penalización", "actifs": "Filtros activos", "retirer": "Quitar el filtro",
           "effacer": "Borrar todo", "pdf": "Texto oficial (PDF gratuito)",
           "source": "Fuente oficial: Racing Rules of Sailing 2025-2028, © World Sailing Limited. "
                     "Resúmenes y ejemplos escritos por Sailing More; en caso de duda, prevalece el texto oficial.",
           "edition": "Edición", "corr": "correcciones del",
           "schema": "Esquema de la regla", "video_lire": "Ver el vídeo",
           "video_tiers": "Vídeo de un tercero, reproducido por YouTube: no se carga nada antes de tu clic."},
    "pt": {"titre": "Regras de regata à vela",
           "chapo": "As regras de regata (RRS 2025-2028) explicadas com as nossas palavras, com um exemplo concreto para cada uma. "
                    "Pesquise por número, por título ou por uma situação vivida.",
           "retour": "← Sailing More", "placeholder": "Um número (10), uma palavra (bombordo), uma situação (colisão)…",
           "aria": "Pesquisar nas regras", "tous": "Todas", "tous_m": "Todos",
           "partie": "Parte", "themes_lib": "O que procuro", "regles_lib": "Número de regra", "toutes_regles": "Todas as regras",
           "sommaire": "Índice",
           "un": "regra", "n": "regras", "aucun": "Nenhuma regra corresponde a esta pesquisa.",
           "defs": "Definições", "app": "Apêndices", "regle": "Regra", "def": "Definição",
           "appendice": "Apêndice", "exemple": "Exemplo", "issue": "Resultado", "voir": "Ver também",
           "sanction": "Penalização", "actifs": "Filtros ativos", "retirer": "Remover o filtro",
           "effacer": "Limpar tudo", "pdf": "Texto oficial (PDF gratuito)",
           "source": "Fonte oficial: Racing Rules of Sailing 2025-2028, © World Sailing Limited. "
                     "Resumos e exemplos escritos pela Sailing More; em caso de dúvida, o texto oficial prevalece.",
           "edition": "Edição", "corr": "correções de",
           "schema": "Esquema da regra", "video_lire": "Ver o vídeo",
           "video_tiers": "Vídeo de terceiros, reproduzido pelo YouTube: nada é carregado antes do seu clique."},
    "de": {"titre": "Wettfahrtregeln im Segeln",
           "chapo": "Die Wettfahrtregeln (RRS 2025-2028) in eigenen Worten erklärt, mit einem konkreten Beispiel für jede. "
                    "Suche nach Nummer, Titel oder erlebter Situation.",
           "retour": "← Sailing More", "placeholder": "Eine Nummer (10), ein Wort (Backbord), eine Situation (Kollision)…",
           "aria": "In den Regeln suchen", "tous": "Alle", "tous_m": "Alle",
           "partie": "Teil", "themes_lib": "Was ich suche", "regles_lib": "Regelnummer", "toutes_regles": "Alle Regeln",
           "sommaire": "Inhalt",
           "un": "Regel", "n": "Regeln", "aucun": "Keine Regel passt zu dieser Suche.",
           "defs": "Definitionen", "app": "Anhänge", "regle": "Regel", "def": "Definition",
           "appendice": "Anhang", "exemple": "Beispiel", "issue": "Ergebnis", "voir": "Siehe auch",
           "sanction": "Strafe", "actifs": "Aktive Filter", "retirer": "Filter entfernen",
           "effacer": "Alles löschen", "pdf": "Offizieller Text (kostenloses PDF)",
           "source": "Offizielle Quelle: Racing Rules of Sailing 2025-2028, © World Sailing Limited. "
                     "Zusammenfassungen und Beispiele von Sailing More; im Zweifel gilt der offizielle Text.",
           "edition": "Ausgabe", "corr": "Berichtigungen vom",
           "schema": "Schema der Regel", "video_lire": "Video abspielen",
           "video_tiers": "Video eines Dritten, von YouTube abgespielt: Vor Ihrem Klick wird nichts geladen."},
}

# Même charte que `lexique_page.py` : palette Signal B, rouge qui souligne et n'écrit pas ; ici aucune
# information ne passe par la couleur seule (coche devant le filtre actif, libellés écrits).
CSS = """
:root{--nuit:#0a1a2b;--panneau:#0f2438;--ivoire:#eef3f7;--gris:#9db2c6;--rouge:#e23a3e}
*{box-sizing:border-box}
@media (prefers-reduced-motion:no-preference){html{scroll-behavior:smooth}}
body{margin:0;background:#071c31;color:var(--ivoire);
  font-family:ui-sans-serif,system-ui,-apple-system,"Helvetica Neue",Arial,sans-serif;
  line-height:1.6;-webkit-font-smoothing:antialiased}
.page{max-width:64rem;margin:0 auto;padding:2rem 1.4rem 5rem}
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
.chapo{color:var(--gris);font-size:.95rem;max-width:38rem;margin:0 0 2.2rem}
a{color:#fff;text-decoration:none}
:focus-visible{outline:2px solid #fff;outline-offset:2px}

.panneau{background:#0a1f33;border:1px solid rgba(255,255,255,.09);border-radius:2px;
  padding:0 1.2rem 1.4rem;margin:0 0 1rem;box-shadow:0 18px 50px rgba(0,0,0,.35)}
.recherche{position:sticky;top:var(--h-entete);z-index:20;background:#0a1f33;
  padding:.9rem 1.2rem 1rem;margin:0 -1.2rem .4rem}
.champ{display:flex;align-items:center;gap:.6rem;background:var(--panneau);
  border:1px solid rgba(255,255,255,.13);border-radius:3px;padding:.62rem .8rem}
.champ:focus-within{border-color:rgba(226,58,62,.7)}
.champ input{flex:1;background:none;border:0;color:var(--ivoire);font-size:.95rem;outline:none;
  font-family:inherit;min-width:0}
.champ input::placeholder{color:#7d92a6}
.champ svg{flex:0 0 auto;opacity:.55}
.filtres{position:relative;display:flex;flex-wrap:wrap;gap:.35rem;align-items:center;margin-top:.7rem}
/* Le sommaire : la même idée que le « Table of Contents » du site officiel — on montre les parties,
   on ne cache pas les règles. Un bouton, une liste de neuf lignes, un saut. (23/11/2026) */
.som-p{position:absolute;left:0;top:calc(100% + .3rem);z-index:45;min-width:min(22rem,92vw);
  background:#0a1f33;border:1px solid rgba(255,255,255,.16);border-radius:3px;padding:.35rem;
  box-shadow:0 18px 40px rgba(0,0,0,.45);display:grid;gap:.1rem}
.som-p a{display:flex;justify-content:space-between;gap:1rem;color:#dbe6ef;font-size:.8rem;
  padding:.42rem .5rem;border-radius:2px}
.som-p a:hover,.som-p a:focus-visible{background:rgba(255,255,255,.08);color:#fff}
.som-p a b{font-weight:500}
.som-p a span{color:#8aa0b4;font-variant-numeric:tabular-nums;font-size:.74rem}
.puce.som{border-color:rgba(226,58,62,.55);color:#fff}
.puce.som[aria-expanded="true"]{background:rgba(226,58,62,.18);border-color:var(--rouge)}
.filtres .etiq{font-size:.58rem;letter-spacing:.18em;text-transform:uppercase;color:#8aa0b4;
  margin-right:.2rem}
.filtres select{font:inherit;font-size:.78rem;color:#eef3f7;background:#0a1f33;
  border:1px solid rgba(255,255,255,.16);border-radius:2px;padding:.3rem .5rem;width:auto;max-width:100%}
.filtres select:focus{border-color:rgba(226,58,62,.7);outline:none}
.puce{font:inherit;font-size:.72rem;letter-spacing:.04em;color:var(--gris);background:none;
  border:1px solid rgba(255,255,255,.16);border-radius:2px;padding:.28rem .6rem;cursor:pointer}
.puce:hover{color:#fff;border-color:rgba(255,255,255,.4)}
.puce[aria-pressed="true"]{color:#fff;border-color:var(--rouge);background:rgba(226,58,62,.14);
  font-weight:600}
.puce[aria-pressed="true"]::before{content:"\\2713\\00a0"}
@media (prefers-reduced-motion:no-preference){
  .puce{transition:color .15s,border-color .15s,background .15s}}
.actifs{display:none;flex-wrap:wrap;gap:.35rem;align-items:center;margin-top:.7rem;font-size:.72rem;
  color:var(--gris)}
.actifs.on{display:flex}
.actifs button{font:inherit;font-size:.72rem;color:#fff;background:rgba(255,255,255,.06);
  border:1px solid rgba(255,255,255,.3);border-radius:2px;padding:.2rem .5rem;cursor:pointer}
.actifs button::after{content:"\\00a0\\00d7"}
.actifs button.tout{border-style:dashed}
.actifs button.tout::after{content:""}
.compte{color:var(--gris);font-size:.72rem;letter-spacing:.06em;margin:.9rem 0 .2rem}
.compte b{color:#fff;font-weight:500}

.groupe{margin:0 0 2.2rem;scroll-margin-top:calc(var(--h-entete) + 8.5rem)}
.groupe h2{font-size:.64rem;letter-spacing:.22em;text-transform:uppercase;color:var(--gris);
  font-weight:500;margin:0 0 .2rem;padding-top:1rem;border-top:1px solid rgba(226,58,62,.22)}
.groupe h2 span{color:#8aa0b4;letter-spacing:.1em;margin-left:.5rem}
.regle{padding:.95rem 0 .9rem .9rem;border-bottom:1px solid rgba(255,255,255,.07);
  border-left:3px solid transparent;scroll-margin-top:calc(var(--h-entete) + 9rem)}
.regle:hover{background:rgba(255,255,255,.025)}
.regle:target{border-left-color:var(--rouge);background:rgba(226,58,62,.06)}
.regle h3{margin:0;font-size:1.05rem;font-weight:500;color:#fff;line-height:1.35}
.regle h3 a:hover{text-decoration:underline;text-decoration-color:rgba(226,58,62,.7);
  text-underline-offset:.25em}
.regle .num{display:inline-block;min-width:4.6rem;color:var(--gris);font-size:.72rem;
  letter-spacing:.08em;text-transform:uppercase;font-weight:600}
.regle .resume{margin:.3rem 0 0;color:#c9d6e2;font-size:.92rem;max-width:44rem}
.regle details{margin:.55rem 0 0;max-width:44rem;border-left:2px solid rgba(255,255,255,.14);
  padding:0 0 0 .8rem}
.regle summary{cursor:pointer;color:var(--gris);font-size:.78rem;letter-spacing:.04em}
.regle summary:hover{color:#fff}
.regle details p{margin:.35rem 0 0;color:#c9d6e2;font-size:.88rem}
.regle details b{color:#fff;font-weight:600}
.regle .renvois,.regle .sanction{margin:.5rem 0 0;color:#8aa0b4;font-size:.74rem;letter-spacing:.03em}
.regle .renvois a{color:var(--gris);text-decoration:underline;text-underline-offset:.2em;
  margin-right:.6rem}
.regle .renvois a:hover{color:#fff}
.regle .sanction b{color:var(--gris);font-weight:600}
/* Schémas : un à cinq temps, le nombre dépend de la règle. Les formes se lisent sans la couleur :
   trait plein = garde sa route, pointillés = s'écarte, bateau pâle = où il serait allé. */
.regle .schema{margin:.7rem 0 0;max-width:44rem;padding:0;list-style:none}
ol.schema{display:flex;flex-wrap:wrap;gap:1.3rem}
ol.schema>li{position:relative;flex:1 1 11rem;max-width:15rem;margin:0}
ol.schema>li:not(:last-child)::after{content:"\\2192" / "";position:absolute;right:-1.15rem;top:30%;
  width:1rem;text-align:center;color:var(--gris);font-size:1rem}
figure.schema{margin:.7rem 0 0;max-width:16rem}
.schema figure{margin:0}
.schema figcaption{margin:.35rem 0 0;color:#c9d6e2;font-size:.76rem;line-height:1.45}
.schema .n{display:inline-block;min-width:1.15rem;text-align:center;margin-right:.2rem;color:#fff;
  background:rgba(255,255,255,.12);border-radius:50%;font-size:.7rem;font-weight:600}
svg.sc{display:block;width:100%;height:auto;background:#071c31;border:1px solid rgba(255,255,255,.12)}
.sc .sc-t{fill:none;stroke:#eef3f7;stroke-width:1.6}
.sc .sc-td{fill:none;stroke:#9db2c6;stroke-width:1.6;stroke-dasharray:4 3}
.sc .sc-f{opacity:.4}
.sc .sc-lien{fill:none;stroke:#9db2c6;stroke-width:1;stroke-dasharray:1 3}
.sc .sc-z{fill:none;stroke:#9db2c6;stroke-width:1;stroke-dasharray:2 4;opacity:.6}
.sc .sc-m{fill:#0a1f33;stroke:#e23a3e;stroke-width:2.4}
.sc .sc-x{fill:none;stroke:#e23a3e;stroke-width:2.4;stroke-linecap:round}
.sc-v{fill:none;stroke:#9db2c6;stroke-width:1.5;stroke-linecap:round;stroke-linejoin:round}
.sc .sc-pri{color:#eef3f7}
.sc .sc-ev{color:#9db2c6}
.sc .sc-fant{color:#9db2c6;opacity:.35}
.video{margin:.7rem 0 0;max-width:44rem}
.video-lire{font:inherit;font-size:.78rem;letter-spacing:.04em;color:#fff;background:rgba(255,255,255,.06);
  border:1px solid rgba(255,255,255,.3);border-radius:2px;padding:.4rem .8rem;cursor:pointer}
.video-lire:hover{border-color:#fff}
.video-lire::before{content:"\\25B6\\00a0"}
.video-tiers{margin:.3rem 0 0;color:#8aa0b4;font-size:.72rem}
.video iframe{display:block;width:100%;max-width:32rem;aspect-ratio:16/9;border:0;background:#000}
.vide{padding:3rem 0;color:var(--gris);font-size:.9rem}
.pied{margin-top:3.6rem;padding-top:1.2rem;border-top:1px solid rgba(255,255,255,.09);
  color:#8aa0b4;font-size:.72rem;line-height:1.8}
.pied a{color:var(--gris);text-decoration:underline;text-underline-offset:.2em}

@media (prefers-color-scheme:light){
  /* La page garde sa nuit : le contraste est tenu par les couleurs ci-dessus (>= 4,5:1 sur #0a1f33). */
  :root{color-scheme:dark}
}
@media (max-width:640px){
  .page{padding:2.4rem 1rem 4rem}
  .recherche{padding:.7rem 0 .8rem}
  .filtres .etiq{width:100%}
  .filtres select{width:100%}
  .regle{padding-left:.6rem;scroll-margin-top:calc(var(--h-entete) + 12rem)}
  .regle .num{display:block;min-width:0}
}
"""

JS = r"""
(function(){
  var data = JSON.parse(document.getElementById('donnees-regles').textContent);
  var UI = data.ui, LANGUES = data.langues, PARTIES = data.parties, THEMES = data.themes, REGLES = data.regles;
  var champ = document.getElementById('champ-q');
  var liste = document.getElementById('liste-regles');
  var compte = document.getElementById('compte-regles');
  var zoneThemes = document.getElementById('themes');
  var zoneActifs = document.getElementById('actifs');
  var etat = {regle:'', theme:'tous', texte:''};
  var ORDRE = ['defs','1','2','3','4','5','6','7','app'];

  function stocke(){ try{ return localStorage.getItem('sm-langue') || 'auto'; }catch(e){ return 'auto'; } }
  /* La langue est choisie une seule fois, dans le <head> (24/11/2026). On lit le résultat. */
  function choisir(){
    var l = (typeof window.smLangue === 'function') ? window.smLangue() : 'en';
    if(l === 'bzh') l = 'fr';
    return UI[l] ? l : 'en';
  }
  var lang = choisir();

  function normalise(s){return (s||'').toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g,'');}
  function esc(s){return String(s).replace(/[&<>"]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];});}
  var parParCle = {}; PARTIES.forEach(function(p){ parParCle[p.cle] = p; });
  var parRegle = {}; REGLES.forEach(function(r){ parRegle[r.cle] = r; });

  // Le foin de recherche : numéro, titre (langue + intitulé officiel anglais), résumé, situations, issues.
  REGLES.forEach(function(r){
    r._foin = {};
    LANGUES.forEach(function(l){
      var t = [r.num || '', r.titre[l], r.titre.en, r.resume[l], (r.sanction && r.sanction[l]) || ''];
      (r.exemples || []).forEach(function(x){ t.push(x.situation[l], x.issue[l]); });
      r._foin[l] = normalise(t.join(' '));
    });
  });

  function etiquette(r){
    var u = UI[lang];
    if(r.partie === 'defs') return u.def;
    if(r.appendice && r.num === r.appendice) return u.appendice + ' ' + r.num;
    return u.regle + ' ' + r.num;
  }
  function nomPartie(k){
    var u = UI[lang];
    if(k === 'defs') return u.defs;
    if(k === 'app') return u.app;
    return u.partie + ' ' + k + ' · ' + parParCle[k].nom[lang];
  }

  function opt(val, texte, sel){
    return '<option value="' + esc(val) + '"' + (sel ? ' selected' : '') + '>' + esc(texte) + '</option>';
  }
  function libRegle(r){ return r.partie === 'defs' ? r.titre[lang] : r.titre[lang] + ' — ' + r.num; }
  // Les thèmes en pastilles : le texte de chaque pastille suit la langue de la page.
  function remplirThemes(){
    var u = UI[lang];
    document.getElementById('lib-theme').textContent = u.themes_lib;
    zoneThemes.setAttribute('aria-label', u.themes_lib);
    var bs = zoneThemes.querySelectorAll('button[data-theme]');
    for(var i = 0; i < bs.length; i++){
      var cle = bs[i].getAttribute('data-theme');
      if(cle === 'tous'){ bs[i].textContent = u.tous_m; }
      else {
        var th = THEMES.filter(function(x){ return x.cle === cle; })[0];
        if(th) bs[i].textContent = th.nom[lang];
      }
    }
    majThemes();
  }
  // Le sommaire : neuf entrées, la partie et ses numéros, un saut — rien à dérouler.
  var somB = document.getElementById('som-b'), somP = document.getElementById('som-p');
  function remplirSom(){
    if(!somB || !somP) return;
    var h = '';
    ORDRE.forEach(function(k){
      var rs = REGLES.filter(function(r){ return r.partie === k; });
      if(!rs.length) return;
      var bornes = (k === 'defs' || k === 'app') ? String(rs.length)
                 : (rs[0].num + '–' + rs[rs.length - 1].num);
      h += '<a href="#p' + esc(k) + '"><b>' + esc(nomPartie(k)) + '</b><span>' + esc(bornes) + '</span></a>';
    });
    somP.innerHTML = h;
    somB.textContent = UI[lang].sommaire;
    somB.setAttribute('aria-label', UI[lang].sommaire);
  }
  function fermerSom(){ if(somP){ somP.hidden = true; somB.setAttribute('aria-expanded', 'false'); } }

  function majThemes(){
    var bs = zoneThemes.querySelectorAll('button[data-theme]');
    for(var i = 0; i < bs.length; i++){
      bs[i].setAttribute('aria-pressed', bs[i].getAttribute('data-theme') === etat.theme ? 'true' : 'false');
    }
  }
  function selectsDefaut(){ etat.regle = ''; etat.theme = 'tous'; majThemes(); }

  function actifs(){
    var u = UI[lang], h = '';
    if(etat.regle && parRegle[etat.regle]){
      var rs = parRegle[etat.regle];
      var tx = rs.partie === 'defs' ? rs.titre[lang] : u.regle + ' ' + rs.num + ' · ' + rs.titre[lang];
      h += '<button type="button" data-retire="regle" aria-label="' + esc(u.retirer) + ' : ' + esc(tx) + '">' + esc(tx) + '</button>';
    }
    if(etat.theme !== 'tous'){
      var th = THEMES.filter(function(x){return x.cle===etat.theme;})[0];
      h += '<button type="button" data-retire="theme" aria-label="' + esc(u.retirer) + ' : ' + esc(th.nom[lang]) + '">' + esc(th.nom[lang]) + '</button>';
    }
    if(etat.texte.trim()) h += '<button type="button" data-retire="texte" aria-label="' + esc(u.retirer) + ' : ' + esc(etat.texte) + '">« ' + esc(etat.texte.trim()) + ' »</button>';
    zoneActifs.className = 'actifs' + (h ? ' on' : '');
    zoneActifs.innerHTML = h ? '<span>' + esc(u.actifs) + ' :</span>' + h
      + '<button type="button" class="tout" data-retire="tout">' + esc(u.effacer) + '</button>' : '';
  }

  // Le schéma : une étape = le dessin seul, sans numéro ; deux à cinq = étapes numérotées, une flèche entre elles.
  // Les SVG viennent de regles.json (notre texte, jamais de l'extérieur).
  function schemaHtml(r){
    var s = r.schema; if(!s || !s.length) return '';
    var u = UI[lang];
    if(s.length === 1) return '<figure class="schema" aria-label="' + esc(u.schema) + '">' + s[0].svg
      + '<figcaption>' + esc(s[0].legende[lang]) + '</figcaption></figure>';
    return '<ol class="schema" aria-label="' + esc(u.schema) + '">' + s.map(function(e, i){
      return '<li><figure>' + e.svg + '<figcaption><b class="n">' + (i+1) + '</b> ' + esc(e.legende[lang])
        + '</figcaption></figure></li>'; }).join('') + '</ol>';
  }
  // La vidéo : un bouton, aucune requête avant le clic (l'iframe youtube-nocookie naît du clic).
  function videoHtml(r){
    var v = r.video; if(!v) return '';
    var u = UI[lang];
    return '<div class="video"><button type="button" class="video-lire" data-yt="' + esc(v.id) + '" data-titre="' + esc(v.titre) + '">'
      + esc(u.video_lire) + ' (' + esc(v.chaine) + ')</button><p class="video-tiers">' + esc(u.video_tiers) + '</p></div>';
  }

  function carte(r){
    var u = UI[lang];
    var h = '<article class="regle" id="r' + esc(r.cle) + '">'
      + '<h3><a href="#r' + esc(r.cle) + '"><span class="num">' + esc(etiquette(r)) + '</span> ' + esc(r.titre[lang]) + '</a></h3>'
      + '<p class="resume">' + esc(r.resume[lang]) + '</p>'
      + schemaHtml(r) + videoHtml(r);
    (r.exemples || []).forEach(function(x, i){
      var n = (r.exemples.length > 1) ? ' ' + (i+1) : '';
      h += '<details><summary>' + esc(u.exemple) + n + '</summary><p>' + esc(x.situation[lang]) + '</p>'
        + '<p><b>' + esc(u.issue) + ' :</b> ' + esc(x.issue[lang]) + '</p></details>';
    });
    var renvois = [];
    (r.exemples || []).forEach(function(x){ (x.renvois || []).forEach(function(c){ if(renvois.indexOf(c) < 0) renvois.push(c); }); });
    if(renvois.length) h += '<p class="renvois">' + esc(u.voir) + ' : ' + renvois.map(function(c){
      var cible = parRegle[c]; return cible ? '<a href="#r' + esc(c) + '">' + esc(etiquette(cible)) + '</a>' : ''; }).join('') + '</p>';
    if(r.sanction && r.sanction[lang]) h += '<p class="sanction"><b>' + esc(u.sanction) + ' :</b> ' + esc(r.sanction[lang]) + '</p>';
    return h + '</article>';
  }

  // Une requête qui ressemble à un numéro (« 10 », « règle 10 », « rule 10 », « 10.1 », « C2.1 »).
  function numeroDemande(q){
    var m = q.match(/^(?:[a-z]+\.?\s*)?([a-z]?\d+(?:\.\d+)*)$/);
    return m ? m[1] : null;
  }
  function garde(r, q){
    if(etat.regle && r.cle !== etat.regle) return false;
    if(etat.theme !== 'tous' && (r.themes || []).indexOf(etat.theme) < 0) return false;
    return true;
  }
  function cherche(q){
    var base = REGLES.filter(function(r){ return garde(r); });
    if(!q) return base;
    var n = numeroDemande(q);
    if(n){
      var par = base.filter(function(r){ var x = (r.num || '').toLowerCase();
        return x === n || x.indexOf(n + '.') === 0; });
      if(par.length) return par;
    }
    var mots = q.split(/\s+/).filter(Boolean);
    return base.filter(function(r){ return mots.every(function(m){ return r._foin[lang].indexOf(m) !== -1; }); });
  }

  function dessine(){
    majThemes();                     /* la pastille active reste la bonne */
    var u = UI[lang], q = normalise(etat.texte).trim(), total = 0, h = '';
    var trouvees = cherche(q);
    ORDRE.forEach(function(k){
      var g = trouvees.filter(function(r){ return r.partie === k; });
      if(!g.length) return;
      total += g.length;
      h += '<section class="groupe" id="p' + esc(k) + '"><h2>' + esc(nomPartie(k)) + '<span>' + g.length + '</span></h2>'
        + g.map(carte).join('') + '</section>';
    });
    liste.innerHTML = h || '<p class="vide">' + esc(u.aucun) + '</p>';
    compte.innerHTML = '<b>' + total + '</b> ' + (total > 1 ? u.n : u.un);
    actifs();
  }

  function traduit(){
    var u = UI[lang];
    document.documentElement.lang = lang;
    document.title = u.titre + ' — Sailing More';
    document.querySelectorAll('[data-t]').forEach(function(el){ el.textContent = u[el.dataset.t]; });
    champ.placeholder = u.placeholder;
    champ.setAttribute('aria-label', u.aria);
    var actif = stocke();
    document.querySelectorAll('#langues button').forEach(function(b){
      b.setAttribute('aria-pressed', String(b.dataset.lang === actif)); });
    remplirThemes();
    remplirSom();
    dessine();
  }

  function versLAncre(){
    var id = decodeURIComponent((location.hash||'').slice(1));
    if(!id) return;
    var el = document.getElementById(id);
    if(!el && (etat.texte || etat.regle || etat.theme !== 'tous')){
      etat = {regle:'', theme:'tous', texte:''}; champ.value = ''; selectsDefaut(); dessine();
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
  if(somB) somB.addEventListener('click', function(){
    var ouvert = somP.hidden;
    somP.hidden = !ouvert;
    somB.setAttribute('aria-expanded', ouvert ? 'true' : 'false');
  });
  if(somP) somP.addEventListener('click', function(e){ if(e.target.closest('a')) fermerSom(); });
  document.addEventListener('keydown', function(e){ if(e.key === 'Escape') fermerSom(); });
  document.addEventListener('click', function(e){ if(!e.target.closest('#som-b') && !e.target.closest('#som-p')) fermerSom(); });
  zoneThemes.addEventListener('click', function(e){
    var b = e.target.closest('button[data-theme]');
    if(!b) return;
    var cle = b.getAttribute('data-theme');
    etat.theme = (cle === 'tous' || etat.theme === cle) ? 'tous' : cle;   // retoucher la même pastille l'éteint
    dessine();
  });
  zoneActifs.addEventListener('click', function(ev){
    var b = ev.target.closest('button'); if(!b) return;
    var k = b.dataset.retire;
    if(k === 'regle' || k === 'tout'){ etat.regle = ''; }
    if(k === 'theme' || k === 'tout'){ etat.theme = 'tous'; majThemes(); }
    if(k === 'texte' || k === 'tout'){ etat.texte = ''; champ.value = ''; }
    dessine();
  });
  liste.addEventListener('click', function(ev){
    var b = ev.target.closest('.video-lire'); if(!b) return;
    var f = document.createElement('iframe');
    f.src = 'https://www.youtube-nocookie.com/embed/' + encodeURIComponent(b.dataset.yt) + '?autoplay=1&rel=0';
    f.title = b.dataset.titre;
    f.allow = 'autoplay; encrypted-media; picture-in-picture; fullscreen';
    f.allowFullscreen = true;
    f.referrerPolicy = 'strict-origin-when-cross-origin';
    b.parentNode.insertBefore(f, b); b.parentNode.removeChild(b);
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
    d = json.loads(JSON.read_text(encoding="utf-8"))
    # L'ordre du fichier n'a pas d'importance : on trie par partie puis par numéro du livre (tri stable,
    # donc les définitions, qui n'ont pas de numéro, gardent l'ordre où elles sont écrites).
    d["regles"] = sorted(d.get("regles", []), key=_cle_tri)
    return d


def _cle_tri(r: dict):
    ordre = ["defs", "1", "2", "3", "4", "5", "6", "7", "app"]
    p = ordre.index(r["partie"]) if r.get("partie") in ordre else len(ordre)
    morceaux = [(0, int(x), "") if x.isdigit() else (1, 0, x) for x in re.findall(r"\d+|\D+", r.get("num") or "")]
    return (p, morceaux)


# --------------------------------------------------------------------------------------------------
# Le texte officiel : source de vérité des numéros et des intitulés
# --------------------------------------------------------------------------------------------------

def texte_officiel() -> str | None:
    """L'extraction du PDF. À défaut du .txt, extraction pypdf du PDF ; à défaut des deux, None."""
    if TXT.exists():
        return TXT.read_text(encoding="utf-8", errors="replace")
    if PDF.exists():
        try:
            from pypdf import PdfReader  # type: ignore
            return "\n".join((p.extract_text() or "") for p in PdfReader(str(PDF)).pages)
        except Exception:
            return None
    return None


def _maj(s: str) -> str:
    return s.replace("’", "'").replace(" ", " ").strip().upper()


def titres_officiels(texte: str) -> dict[str, str]:
    """{numéro: début de l'intitulé en majuscules} pour les règles 1 à 92 des Parties 1 à 7.
    La zone va de la ligne « PART 1 » à la ligne « APPENDIX A » ; un intitulé est une ligne
    « <nombre> <MOTS EN MAJUSCULES> » (les tableaux de signaux, « 4 P, I, U… », n'en sont pas)."""
    lignes = [l.strip() for l in texte.splitlines()]
    try:
        debut = lignes.index("PART 1")
        fin = lignes.index("APPENDIX A", debut)
    except ValueError:
        return {}
    titres: dict[str, str] = {}
    for l in lignes[debut:fin]:
        m = re.match(r"^(\d{1,2}) ([A-Z]{2,}.*)$", l)  # {2,} : « 10 ON OPPOSITE TACKS », « 11 ON THE SAME TACK… »
        if m and m.group(2) == m.group(2).upper():
            titres.setdefault(m.group(1), _maj(m.group(2)))
    return titres


def appendices_officiels(texte: str) -> set[str]:
    return {m.group(1) for l in texte.splitlines() if (m := re.match(r"^APPENDIX ([A-Z])$", l.strip()))}


def zone_definitions(texte: str) -> str:
    lignes = [l.strip() for l in texte.splitlines()]
    try:
        debut = lignes.index("DEFINITIONS")
        fin = lignes.index("BASIC PRINCIPLES", debut)
    except ValueError:
        return ""
    return "\n".join(lignes[debut:fin]).upper().replace("’", "'")


# --------------------------------------------------------------------------------------------------
# Contrôles
# --------------------------------------------------------------------------------------------------

def _mots(s: str) -> int:
    return len((s or "").split())


def verifier(d: dict) -> list[str]:
    """Contrôle de structure, en lecture seule : six langues partout, résumés de 25 mots ou plus, une règle
    numérotée = au moins un exemple (deux pour 10 à 19, 31, 42, 44, 61), pas de doublon, renvois existants."""
    pb: list[str] = []
    if d.get("langues") != LANGUES:
        pb.append(f"« langues » vaut {d.get('langues')}, attendu {LANGUES}")
    for k in ("libelle", "corrections", "pdf", "consulte_le"):
        if not d.get("edition", {}).get(k):
            pb.append(f"édition : « {k} » absent")
    parties = {p.get("cle") for p in d.get("parties", [])}
    for p in d.get("parties", []):
        for l in LANGUES:
            if not p.get("nom", {}).get(l):
                pb.append(f"partie {p.get('cle')} : nom {l} absent")
    themes = {t.get("cle") for t in d.get("themes", [])}
    for t in d.get("themes", []):
        for l in LANGUES:
            if not t.get("nom", {}).get(l):
                pb.append(f"thème {t.get('cle')} : nom {l} absent")
    cles: set[str] = set()
    nums: set[str] = set()
    regles = d.get("regles", [])
    for r in regles:
        cle = r.get("cle", "?")
        if cle in cles:
            pb.append(f"clé en double : {cle}")
        cles.add(cle)
        num = r.get("num")
        if num:
            if num in nums:
                pb.append(f"numéro en double : {num}")
            nums.add(num)
        if r.get("partie") not in parties:
            pb.append(f"{cle} : partie « {r.get('partie')} » inconnue")
        ap = r.get("appendice")
        if r.get("partie") == "app" and ap not in APPENDICES:
            pb.append(f"{cle} : appendice « {ap} » inexistant (A B C D E F G H J M N P R S T seulement)")
        if r.get("partie") != "app" and ap:
            pb.append(f"{cle} : appendice renseigné hors de la partie « app »")
        for l in LANGUES:
            if not r.get("titre", {}).get(l):
                pb.append(f"{cle} : titre {l} absent")
            n = _mots(r.get("resume", {}).get(l, ""))
            if n < MIN_MOTS_RESUME:
                pb.append(f"{cle} : résumé {l} de {n} mots ({MIN_MOTS_RESUME} au moins)")
        ths = r.get("themes", [])
        if not 1 <= len(ths) <= 2 or any(t not in themes for t in ths):
            pb.append(f"{cle} : thèmes {ths} (un ou deux, pris dans la liste)")
        ex = r.get("exemples", [])
        if num:
            mini = 2 if num in DEUX_EXEMPLES else 1
            if len(ex) < mini:
                pb.append(f"{cle} : {len(ex)} exemple(s), {mini} attendu(s)")
        for i, x in enumerate(ex, 1):
            for champ in ("situation", "issue"):
                for l in LANGUES:
                    if not x.get(champ, {}).get(l):
                        pb.append(f"{cle} : exemple {i}, {champ} {l} absent")
        pb += verifier_schema(r)
        sa = r.get("sanction")
        if sa is not None:
            for l in LANGUES:
                if not sa.get(l):
                    pb.append(f"{cle} : sanction {l} absente")
    for r in regles:
        for x in r.get("exemples", []):
            for c in x.get("renvois", []):
                if c not in cles:
                    pb.append(f"{r.get('cle')} : renvoi vers « {c} », absent du JSON")
    return pb


def completude(d: dict) -> list[str]:
    """Couverture contre le texte officiel : un numéro dans l'un et pas dans l'autre est un échec ; un
    intitulé anglais qui ne commence pas comme celui du livre aussi ; idem pour les appendices."""
    texte = texte_officiel()
    if texte is None:
        return ["NON CONTRÔLÉ · texte officiel introuvable (regles/rrs-2025-2028.txt ni le PDF)"]
    pb: list[str] = []
    officiels = titres_officiels(texte)
    if not officiels:
        return ["NON CONTRÔLÉ · zone des Parties 1 à 7 introuvable dans l'extraction du PDF"]
    json_nums = {r["num"]: r for r in d.get("regles", [])
                 if r.get("num") and r.get("partie") in {str(i) for i in range(1, 8)}}
    for n in sorted(officiels, key=int):
        if n not in json_nums:
            pb.append(f"règle {n} ({officiels[n].title()}) : dans le PDF, absente du JSON")
    for n, r in json_nums.items():
        if n not in officiels:
            pb.append(f"règle {n} : dans le JSON, absente du PDF")
            continue
        titre = _maj(r["titre"].get("en", ""))
        if not titre.startswith(officiels[n]):
            pb.append(f"règle {n} : titre anglais « {r['titre'].get('en')} » ≠ intitulé officiel « {officiels[n]} »")
    lettres = appendices_officiels(texte)
    en_json = {r["appendice"] for r in d.get("regles", []) if r.get("appendice")}
    for a in sorted(lettres - en_json):
        pb.append(f"appendice {a} : dans le PDF, absent du JSON")
    for a in sorted(en_json - lettres):
        pb.append(f"appendice {a} : dans le JSON, absent du PDF")
    zone = zone_definitions(texte)
    for r in d.get("regles", []):
        if r.get("partie") == "defs" and _maj(r["titre"].get("en", "")) not in zone:
            pb.append(f"définition {r.get('cle')} : « {r['titre'].get('en')} » introuvable dans les Définitions du PDF")
    return pb


def comptes(d: dict) -> str:
    texte = texte_officiel()
    n_json = sum(1 for r in d.get("regles", []) if r.get("num") and r.get("partie") in {str(i) for i in range(1, 8)})
    n_pdf = len(titres_officiels(texte)) if texte else "?"
    defs = sum(1 for r in d.get("regles", []) if r.get("partie") == "defs")
    apps = len({r["appendice"] for r in d.get("regles", []) if r.get("appendice")})
    return (f"{n_json} règles numérotées sur {n_pdf} dans le PDF (parties 1 à 7), {defs} définition(s), "
            f"{apps} appendice(s) sur {len(APPENDICES)}")


# --------------------------------------------------------------------------------------------------
# La page
# --------------------------------------------------------------------------------------------------

ORDRE_PARTIES = ["defs", "1", "2", "3", "4", "5", "6", "7", "app"]


def etiquette(r: dict, lang: str = "fr") -> str:
    u = UI[lang]
    if r.get("partie") == "defs":
        return u["def"]
    if r.get("appendice") and r.get("num") == r["appendice"]:
        return f'{u["appendice"]} {r["num"]}'
    return f'{u["regle"]} {r["num"]}'


def nom_partie(d: dict, cle: str, lang: str = "fr") -> str:
    u = UI[lang]
    if cle == "defs":
        return u["defs"]
    if cle == "app":
        return u["app"]
    nom = next(p["nom"][lang] for p in d["parties"] if p["cle"] == cle)
    return f'{u["partie"]} {cle} · {nom}'


SPRITE = (
    "<svg width='0' height='0' style='position:absolute' aria-hidden='true' focusable='false'><defs>"
    # Un bateau, étrave en haut, à l'origine ; la couleur vient de `color` sur le <use>.
    "<g id='sc-bat'><path d='M0,-10 C5,-4 5,6 3,10 L-3,10 C-5,6 -5,-4 0,-10Z' fill='currentColor'/>"
    "<path d='M0,-6 L0,7' stroke='#0a1f33' stroke-width='1.2'/></g>"
    # Le vent, flèche vers le bas, en haut à gauche de chaque dessin.
    "<g id='sc-vent'><path class='sc-v' d='M22,10 L22,38 M16,31 L22,38 L28,31'/></g>"
    "</defs></svg>"
)


def schema_statique(r: dict, lang: str = "fr") -> str:
    """Même balisage que `schemaHtml()` dans le JS : une étape = dessin seul ; deux à cinq = numérotées."""
    s = r.get("schema") or []
    if not s:
        return ""
    e = _html.escape
    lib = e(UI[lang]["schema"])
    if len(s) == 1:
        return (f'<figure class="schema" aria-label="{lib}">{s[0]["svg"]}'
                f'<figcaption>{e(s[0]["legende"][lang])}</figcaption></figure>')
    items = "".join(f'<li><figure>{x["svg"]}<figcaption><b class="n">{i}</b> {e(x["legende"][lang])}'
                    f'</figcaption></figure></li>' for i, x in enumerate(s, 1))
    return f'<ol class="schema" aria-label="{lib}">{items}</ol>'


def video_statique(r: dict, lang: str = "fr") -> str:
    """Sans JavaScript : un simple lien vers YouTube (rien n'est chargé avant le clic), avec la mention."""
    v = r.get("video")
    if not v:
        return ""
    e = _html.escape
    u = UI[lang]
    return (f'<div class="video"><a href="https://www.youtube.com/watch?v={e(v["id"])}" rel="noopener">'
            f'{e(u["video_lire"])} ({e(v["chaine"])})</a><p class="video-tiers">{e(u["video_tiers"])}</p></div>')


def verifier_schema(r: dict) -> list[str]:
    """Un à cinq temps, une légende en six langues par temps, SVG sobre (pas de script, pas de lien
    sortant) ; une vidéo = identifiant YouTube de 11 caractères, titre, chaîne."""
    pb: list[str] = []
    cle = r.get("cle", "?")
    s = r.get("schema")
    if s is not None:
        if not isinstance(s, list) or not 1 <= len(s) <= 5:
            pb.append(f"{cle} : schéma de {len(s) if isinstance(s, list) else '?'} étape(s), 1 à 5 attendues")
        else:
            for i, x in enumerate(s, 1):
                svg = x.get("svg", "")
                if not svg.startswith("<svg") or not svg.endswith("</svg>"):
                    pb.append(f"{cle} : schéma, étape {i} n'est pas un <svg>")
                if re.search(r"<script|<foreignobject|<image|\son\w+\s*=|javascript:|href\s*=\s*['\"](?!#sc-)", svg, re.I):
                    pb.append(f"{cle} : schéma, étape {i} contient un élément non permis (script, image, lien sortant)")
                for l in LANGUES:
                    if not x.get("legende", {}).get(l):
                        pb.append(f"{cle} : schéma, étape {i}, légende {l} absente")
    v = r.get("video")
    if v is not None:
        if not re.fullmatch(r"[A-Za-z0-9_-]{11}", v.get("id", "")):
            pb.append(f"{cle} : vidéo, identifiant YouTube invalide")
        for k in ("titre", "chaine"):
            if not v.get(k):
                pb.append(f"{cle} : vidéo, « {k} » absent")
    return pb


def carte_statique(d: dict, r: dict, par_cle: dict, lang: str = "fr") -> str:
    """Même balisage que `carte()` dans le JS."""
    e = _html.escape
    u = UI[lang]
    h = (f'<article class="regle" id="r{e(r["cle"])}"><h3><a href="#r{e(r["cle"])}">'
         f'<span class="num">{e(etiquette(r, lang))}</span> {e(r["titre"][lang])}</a></h3>'
         f'<p class="resume">{e(r["resume"][lang])}</p>')
    h += schema_statique(r, lang) + video_statique(r, lang)
    ex = r.get("exemples", [])
    for i, x in enumerate(ex, 1):
        n = f" {i}" if len(ex) > 1 else ""
        h += (f'<details><summary>{e(u["exemple"])}{n}</summary><p>{e(x["situation"][lang])}</p>'
              f'<p><b>{e(u["issue"])} :</b> {e(x["issue"][lang])}</p></details>')
    renvois: list[str] = []
    for x in ex:
        for c in x.get("renvois", []):
            if c not in renvois:
                renvois.append(c)
    if renvois:
        liens = "".join(f'<a href="#r{e(c)}">{e(etiquette(par_cle[c], lang))}</a>' for c in renvois if c in par_cle)
        h += f'<p class="renvois">{e(u["voir"])} : {liens}</p>'
    if r.get("sanction") and r["sanction"].get(lang):
        h += f'<p class="sanction"><b>{e(u["sanction"])} :</b> {e(r["sanction"][lang])}</p>'
    return h + "</article>"


def liste_statique(d: dict, lang: str = "fr") -> str:
    par_cle = {r["cle"]: r for r in d["regles"]}
    sortie = []
    for k in ORDRE_PARTIES:
        groupe = [r for r in d["regles"] if r["partie"] == k]
        if not groupe:
            continue
        sortie.append(f'<section class="groupe" id="p{k}"><h2>{_html.escape(nom_partie(d, k, lang))}'
                      f'<span>{len(groupe)}</span></h2>'
                      + "".join(carte_statique(d, r, par_cle, lang) for r in groupe) + "</section>")
    return "".join(sortie)


def _ld_regles(d: dict) -> str:
    """JSON-LD : fil d'Ariane + Article. Pas de FAQPage : regles.json n'a aucune question/réponse
    (les questions de révision sont sur cours.html, pas ici)."""
    import jsonld
    url = f"{jsonld.SITE}/regles-de-course.html"
    article = {"@type": "Article", "headline": "Règles de course à la voile", "inLanguage": "fr",
               "description": f"Les règles de course à la voile (RCV {d['edition']['libelle']}) : numéro, "
                              "intitulé, résumé et exemple concret pour chaque règle.",
               "mainEntityOfPage": url, "url": url,
               "author": {"@id": jsonld.ORG_ID}, "publisher": {"@id": jsonld.ORG_ID}}
    return jsonld.bloc(jsonld.fil("regles-de-course.html", "Règles de course"), article, jsonld.organisation())


def page_regles(d: dict | None = None) -> str:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import site_blocks  # la barre du site : un seul endroit
    d = d or charger()
    e = _html.escape
    ui = UI["fr"]
    total = len(d["regles"])
    donnees = {"langues": LANGUES, "ui": UI, "parties": d["parties"], "themes": d["themes"],
               "regles": d["regles"]}
    brut = json.dumps(donnees, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    boutons_langue = '<button data-lang="auto" aria-pressed="true">Auto</button>' + "".join(
        f'<button data-lang="{l}" aria-pressed="false">{l.upper()}</button>' for l in LANGUES)
    ed = d["edition"]

    def opt(val: str, texte: str) -> str:
        return f'<option value="{e(val)}">{e(texte)}</option>'

    # Deux filtres, et rien de plus : la recherche (qui prend un numéro, un mot, une situation) et
    # six thèmes en pastilles, tous visibles sur une ligne. Le menu déroulant des 113 numéros a été
    # retiré le 23/11/2026 : « c'est compliqué encore » (Nicolas).
    f_themes = (f'<span class="etiq" id="lib-theme">{e(ui["themes_lib"])}</span>'
                f'<button type="button" class="puce" data-theme="tous" aria-pressed="true">'
                f'{e(ui["tous_m"])}</button>'
                + "".join(f'<button type="button" class="puce" data-theme="{e(th["cle"])}" '
                          f'aria-pressed="false">{e(th["nom"]["fr"])}</button>' for th in d["themes"]))
    # Audit SEO du 24/11/2026, correction 4 : textes de l'audit ; l'édition vient des données.
    seo_titre = f"Règles de course à la voile (RCV {ed['libelle']}) | Sailing More"
    seo_desc = (f"Toutes les règles de course à la voile {ed['libelle']} résumées en clair, avec un exemple "
                "pour chaque règle. Cherchez une règle par numéro ou par mot.")
    return (
        '<!doctype html>\n<html lang="fr"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        f"<title>{seo_titre}</title>"
        '<link rel="canonical" href="https://sailingmore.fr/regles-de-course.html">'
        + _ld_regles(d) +
        f'<meta name="description" content="{seo_desc}">'
        + __import__("jsonld").social("regles-de-course.html", seo_titre, seo_desc) +
        "<style>" + site_blocks.ENTETE_CSS + CSS + "</style>"
        "<noscript><style>.recherche{display:none}</style></noscript></head><body>"
        + site_blocks.entete_site("regles-de-course.html", LANGUES) + SPRITE +
        '<main class="page">'
        '<h1 data-t="titre">' + ui["titre"] + "</h1>"
        '<p class="chapo" data-t="chapo">' + ui["chapo"] + "</p>"
        '<div class="panneau">'
        '<div class="recherche"><div class="champ">'
        '<svg width="15" height="15" viewBox="0 0 16 16" fill="none" aria-hidden="true">'
        '<circle cx="7" cy="7" r="5" stroke="#eef3f7" stroke-width="1.4"/>'
        '<path d="M10.6 10.6 14 14" stroke="#eef3f7" stroke-width="1.4"/></svg>'
        f'<input id="champ-q" type="search" placeholder="{e(ui["placeholder"])}" '
        f'aria-label="{e(ui["aria"])}" autocomplete="off"></div>'
        '<div class="filtres" id="themes">'
        '<button type="button" class="puce som" id="som-b" aria-expanded="false" '
        f'aria-controls="som-p">{e(ui["sommaire"])}</button>'
        '<div class="som-p" id="som-p" hidden></div>' + f_themes + "</div>"
        '<div class="actifs" id="actifs"></div></div>'
        f'<div class="compte" id="compte-regles" role="status" aria-live="polite">'
        f'<b>{total}</b> {ui["n"] if total > 1 else ui["un"]}</div>'
        '<div id="liste-regles">' + liste_statique(d) + "</div>"
        "</div>"
        '<p class="pied"><span data-t="source">' + e(ui["source"]) + "</span> "
        f'<a href="{e(ed["pdf"])}" rel="noopener" data-t="pdf">{e(ui["pdf"])}</a><br>'
        f'<span data-t="edition">{e(ui["edition"])}</span> {e(ed["libelle"])} · '
        f'<span data-t="corr">{e(ui["corr"])}</span> {e(ed["corrections"])}</p>'
        "</main>"
        '<script type="application/json" id="donnees-regles">' + brut + "</script>"
        "<script>" + JS + "</script>"
        "</body></html>\n"
    )


def ecrire_page(dossier: Path) -> int:
    """Appelée par `accueil_site.py` à côté de `regates_page.ecrire_page(SITE)` : écrit la page et rend le
    nombre de règles, ou 0 sans rien écrire si le JSON est refusé (incomplet, ou contrôle en échec)."""
    try:
        d = charger()
    except (ValueError, OSError, SystemExit) as e:  # JSON invalide : on n'écrit rien, on ne casse pas le build
        print(f"page des règles non écrite : regles.json illisible ({e})", file=sys.stderr)
        return 0
    pb = verifier(d)
    if d.get("complet") is not True:
        pb.append("regles.json porte « complet »: false — la page n'est pas publiable")
    pb += [p for p in completude(d) if not p.startswith("NON CONTRÔLÉ")]
    if pb:
        print(f"page des règles non écrite : {len(pb)} point(s) à régler (python3 scripts/regles_page.py --verifier)",
              file=sys.stderr)
        return 0
    dossier.mkdir(parents=True, exist_ok=True)
    (dossier / "regles-de-course.html").write_text(page_regles(d), encoding="utf-8")
    return len(d["regles"])


def main() -> int:
    if not any(a in sys.argv for a in ("--site", "--publier", "--verifier", "--apercu")):
        print("Rien à faire : --verifier (lecture seule), --apercu, --site (écrit la page) ou --publier.",
              file=sys.stderr)
        return 2
    d = charger()
    structure = verifier(d)
    couverture = completude(d)
    if "--verifier" in sys.argv:
        for p in structure:
            print("ÉCHEC · " + p)
        for p in couverture:
            print("ÉCHEC · " + p)
        if d.get("complet") is not True:
            print("ÉCHEC · regles.json porte « complet »: false")
        ok = not structure and not couverture and d.get("complet") is True
        print(("OK" if ok else "ÉCHEC") + " · " + comptes(d))
        return 0 if ok else 1
    if "--apercu" in sys.argv:
        if structure:
            for p in structure:
                print("ÉCHEC · " + p)
            return 1
        SITE.mkdir(parents=True, exist_ok=True)
        page = page_regles(d)
        (SITE / "regles-apercu.html").write_text(page, encoding="utf-8")
        print(f"{SITE / 'regles-apercu.html'} · {len(page):,} car · {len(d['regles'])} entrées (aperçu, non publiable)"
              .replace(",", " "))
        return 0
    refus = structure + [p for p in couverture if not p.startswith("NON CONTRÔLÉ")]
    if d.get("complet") is not True:
        refus.append("regles.json porte « complet »: false")
    if refus:
        for p in refus:
            print("ÉCHEC · " + p)
        return 1
    if "--site" in sys.argv:
        SITE.mkdir(parents=True, exist_ok=True)
        page = page_regles(d)
        (SITE / "regles-de-course.html").write_text(page, encoding="utf-8")
        print(f"{SITE / 'regles-de-course.html'} · {len(page):,} car · {comptes(d)}".replace(",", " "))
    if "--publier" in sys.argv:
        # Comme lexique_page : on n'envoie pas une page nue ; la mer est posée par `accueil_site.py --site`.
        if not (SITE / "regles-de-course.html").exists() or \
                "<!--mer-debut-->" not in (SITE / "regles-de-course.html").read_text(encoding="utf-8"):
            print("page sans mer : lancer d'abord `accueil_site.py --site`, puis `--publier`.")
            return 1
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        import accueil_site
        accueil_site.miroir_vers_sortie(["regles-de-course.html"])
        accueil_site.publier_en_un_seul_envoi(["regles-de-course.html"], "site : règles de course")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
