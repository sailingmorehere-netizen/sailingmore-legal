#!/usr/bin/env python3
"""Construit la page `cours.html` : quelques cours théoriques, chacun adossé à un texte officiel.

Source unique du contenu : le dictionnaire COURS ci-dessous (six langues). Rien n'est écrit à la main
dans cours.html. Règle de la page : une affirmation = une règle citée (RRS 2025-2028, COLREG).
Ce dont on n'est pas sûr n'est pas écrit (voir RAPPORT.md).

    python3 scripts/cours_page.py --ecrire    # écrit projets/sailingmore/site/cours.html
"""
from __future__ import annotations

import html as _html
import os
import sys
from pathlib import Path

RACINE = Path(os.environ.get("SITE_ROOT", "/opt/data"))
SITE = RACINE / "projets" / "sailingmore" / "site"

LANGUES = ["fr", "en", "it", "es", "pt", "de"]
URL_RRS = "https://sailing.org/inside-world-sailing/rules-regulations/racingrules/"

# Chaque cours : (titre, [(phrase, règle), ...]). Les règles sont citées dans la forme de la langue.
# Même structure dans les six langues : 3 cours RRS, puis 3 cours COLREG (le deuxième a deux phrases).
COURS = {
    "fr": {
        "h1": "Cours théoriques",
        "intro": "Peu de cours, mais chacun s'appuie sur un texte officiel dont la règle est citée. Ces résumés ne remplacent pas le texte : en cas de doute, c'est le texte qui fait foi.",
        "h_rrs": "En régate — Règles de course à la voile (RRS 2025-2028)",
        "h_col": "En mer, hors course — Règlement international pour prévenir les abordages (COLREG / RIPAM)",
        "rrs": [
            ("Tribord et bâbord", [("Quand deux bateaux sont sur des amures opposées, le bateau bâbord amures s'écarte du bateau tribord amures.", "RRS 10")]),
            ("Même amure, bateaux engagés", [("Quand deux bateaux sont sur la même amure et engagés, le bateau au vent s'écarte du bateau sous le vent.", "RRS 11")]),
            ("Même amure, non engagés", [("Quand deux bateaux sont sur la même amure et non engagés, le bateau qui est derrière s'écarte du bateau qui est devant.", "RRS 12")]),
        ],
        "col": [
            ("Deux voiliers", [("Quand chacun reçoit le vent d'un bord différent, celui qui reçoit le vent par bâbord s'écarte de la route de l'autre.", "COLREG 12 a) i)"),
                               ("Quand les deux reçoivent le vent du même bord, le voilier au vent s'écarte de la route du voilier sous le vent.", "COLREG 12 a) ii)")]),
            ("Le rattrapage", [("Tout navire qui en rattrape un autre s'écarte de sa route.", "COLREG 13 a)")]),
            ("Moteur et voile", [("Un navire à propulsion mécanique faisant route s'écarte de la route d'un navire à voile.", "COLREG 18 a) iv)")]),
        ],
        "note": "Sources : Racing Rules of Sailing 2025-2028 (World Sailing, {lien}) ; COLREG 1972 (OMI), appliqué en France sous le nom de RIPAM. Les cas particuliers (virement de bord, marques, obstructions, navires à capacité de manœuvre restreinte, etc.) ne sont pas traités ici.",
    },
    "en": {
        "h1": "Theory courses",
        "intro": "Few courses, but each rests on an official text and cites the rule. These summaries do not replace the text: if in doubt, the text prevails.",
        "h_rrs": "Racing — Racing Rules of Sailing (RRS 2025-2028)",
        "h_col": "At sea, outside a race — International Regulations for Preventing Collisions at Sea (COLREG)",
        "rrs": [
            ("Port and starboard", [("When boats are on opposite tacks, a port-tack boat keeps clear of a starboard-tack boat.", "RRS 10")]),
            ("Same tack, overlapped", [("When boats are on the same tack and overlapped, a windward boat keeps clear of a leeward boat.", "RRS 11")]),
            ("Same tack, not overlapped", [("When boats are on the same tack and not overlapped, a boat clear astern keeps clear of a boat clear ahead.", "RRS 12")]),
        ],
        "col": [
            ("Two sailing vessels", [("When each has the wind on a different side, the vessel with the wind on the port side keeps out of the way of the other.", "COLREG 12(a)(i)"),
                                     ("When both have the wind on the same side, the windward vessel keeps out of the way of the leeward vessel.", "COLREG 12(a)(ii)")]),
            ("Overtaking", [("Any vessel overtaking any other keeps out of the way of the vessel being overtaken.", "COLREG 13(a)")]),
            ("Power and sail", [("A power-driven vessel underway keeps out of the way of a sailing vessel.", "COLREG 18(a)(iv)")]),
        ],
        "note": "Sources: Racing Rules of Sailing 2025-2028 (World Sailing, {lien}); COLREG 1972 (IMO). Special cases (tacking, marks, obstructions, vessels restricted in their ability to manoeuvre, etc.) are not covered here.",
    },
    "it": {
        "h1": "Corsi teorici",
        "intro": "Pochi corsi, ma ognuno poggia su un testo ufficiale e cita la regola. Questi riassunti non sostituiscono il testo: in caso di dubbio fa fede il testo.",
        "h_rrs": "In regata — Regole di Regata a Vela (RRS 2025-2028)",
        "h_col": "In mare, fuori regata — Regolamento internazionale per prevenire gli abbordi in mare (COLREG)",
        "rrs": [
            ("Mure a sinistra e a dritta", [("Quando due barche sono con mure opposte, la barca con mure a sinistra lascia strada alla barca con mure a dritta.", "RRS 10")]),
            ("Stessa mura, in contatto di ingaggio", [("Quando due barche sono con la stessa mura e in ingaggio, la barca sopravento lascia strada a quella sottovento.", "RRS 11")]),
            ("Stessa mura, senza ingaggio", [("Quando due barche sono con la stessa mura e non in ingaggio, la barca che è a poppavia lascia strada a quella che è a prua.", "RRS 12")]),
        ],
        "col": [
            ("Due barche a vela", [("Quando ciascuna riceve il vento da lati diversi, quella che lo riceve da sinistra si tiene fuori rotta dall'altra.", "COLREG 12 a) i)"),
                                   ("Quando entrambe ricevono il vento dallo stesso lato, quella sopravento si tiene fuori rotta da quella sottovento.", "COLREG 12 a) ii)")]),
            ("Il sorpasso", [("Ogni nave che ne raggiunge un'altra si tiene fuori rotta da quella che sta raggiungendo.", "COLREG 13 a)")]),
            ("Motore e vela", [("Una nave a propulsione meccanica in navigazione si tiene fuori rotta da una nave a vela.", "COLREG 18 a) iv)")]),
        ],
        "note": "Fonti: Racing Rules of Sailing 2025-2028 (World Sailing, {lien}); COLREG 1972 (IMO). I casi particolari (virata, boe, ostacoli, navi con manovrabilità limitata, ecc.) non sono trattati qui.",
    },
    "es": {
        "h1": "Cursos teóricos",
        "intro": "Pocos cursos, pero cada uno se apoya en un texto oficial y cita la regla. Estos resúmenes no sustituyen al texto: en caso de duda, prevalece el texto.",
        "h_rrs": "En regata — Reglas de Regata a Vela (RRS 2025-2028)",
        "h_col": "En el mar, fuera de regata — Reglamento internacional para prevenir los abordajes (RIPA / COLREG)",
        "rrs": [
            ("Babor y estribor", [("Cuando dos barcos están en amuras opuestas, el barco de amura de babor se mantiene separado del barco de amura de estribor.", "RRS 10")]),
            ("Misma amura, con solape", [("Cuando dos barcos están en la misma amura y con solape, el barco de barlovento se mantiene separado del de sotavento.", "RRS 11")]),
            ("Misma amura, sin solape", [("Cuando dos barcos están en la misma amura y sin solape, el barco que está por la popa se mantiene separado del que está por delante.", "RRS 12")]),
        ],
        "col": [
            ("Dos veleros", [("Cuando cada uno recibe el viento por una banda distinta, el que lo recibe por babor se mantiene apartado de la derrota del otro.", "COLREG 12 a) i)"),
                             ("Cuando ambos reciben el viento por la misma banda, el de barlovento se mantiene apartado de la derrota del de sotavento.", "COLREG 12 a) ii)")]),
            ("Alcance", [("Todo buque que alcance a otro se mantendrá apartado de la derrota de este.", "COLREG 13 a)")]),
            ("Motor y vela", [("Un buque de propulsión mecánica en navegación se mantiene apartado de la derrota de un buque de vela.", "COLREG 18 a) iv)")]),
        ],
        "note": "Fuentes: Racing Rules of Sailing 2025-2028 (World Sailing, {lien}); COLREG 1972 (OMI). Los casos particulares (virada, marcas, obstrucciones, buques con capacidad de maniobra restringida, etc.) no se tratan aquí.",
    },
    "pt": {
        "h1": "Cursos teóricos",
        "intro": "Poucos cursos, mas cada um assenta num texto oficial e cita a regra. Estes resumos não substituem o texto: em caso de dúvida, prevalece o texto.",
        "h_rrs": "Em regata — Regras de Regata à Vela (RRS 2025-2028)",
        "h_col": "No mar, fora de regata — Regulamento Internacional para Evitar Abalroamentos no Mar (RIEAM / COLREG)",
        "rrs": [
            ("Bombordo e estibordo", [("Quando dois barcos estão em amuras opostas, o barco com amura a bombordo mantém-se afastado do barco com amura a estibordo.", "RRS 10")]),
            ("Mesma amura, com sobreposição", [("Quando dois barcos estão na mesma amura e sobrepostos, o barco de barlavento mantém-se afastado do de sotavento.", "RRS 11")]),
            ("Mesma amura, sem sobreposição", [("Quando dois barcos estão na mesma amura e sem sobreposição, o barco que está atrás mantém-se afastado do que está à frente.", "RRS 12")]),
        ],
        "col": [
            ("Dois veleiros", [("Quando cada um recebe o vento por um bordo diferente, o que o recebe por bombordo afasta-se da rota do outro.", "COLREG 12 a) i)"),
                               ("Quando ambos recebem o vento pelo mesmo bordo, o de barlavento afasta-se da rota do de sotavento.", "COLREG 12 a) ii)")]),
            ("Ultrapassagem", [("Qualquer embarcação que alcance outra afasta-se da rota desta.", "COLREG 13 a)")]),
            ("Motor e vela", [("Uma embarcação de propulsão mecânica em marcha afasta-se da rota de uma embarcação à vela.", "COLREG 18 a) iv)")]),
        ],
        "note": "Fontes: Racing Rules of Sailing 2025-2028 (World Sailing, {lien}); COLREG 1972 (OMI). Os casos particulares (viragem, marcas, obstruções, embarcações com capacidade de manobra restrita, etc.) não são tratados aqui.",
    },
    "de": {
        "h1": "Theoriekurse",
        "intro": "Wenige Kurse, aber jeder stützt sich auf einen offiziellen Text und nennt die Regel. Diese Zusammenfassungen ersetzen den Text nicht: im Zweifel gilt der Text.",
        "h_rrs": "Im Rennen — Wettsegelbestimmungen (RRS 2025-2028)",
        "h_col": "Auf See, außerhalb von Wettfahrten — Kollisionsverhütungsregeln (KVR / COLREG)",
        "rrs": [
            ("Backbord und Steuerbord", [("Wenn Boote auf entgegengesetzten Bugen segeln, muss ein Boot auf Backbordbug einem Boot auf Steuerbordbug ausweichen.", "RRS 10")]),
            ("Gleicher Bug, überlappend", [("Wenn Boote auf gleichem Bug und überlappend segeln, muss das Luvboot dem Leeboot ausweichen.", "RRS 11")]),
            ("Gleicher Bug, nicht überlappend", [("Wenn Boote auf gleichem Bug und nicht überlappend segeln, muss das achtern befindliche Boot dem voraus befindlichen Boot ausweichen.", "RRS 12")]),
        ],
        "col": [
            ("Zwei Segelfahrzeuge", [("Hat jedes den Wind von einer anderen Seite, muss das Fahrzeug mit Wind von Backbord dem anderen ausweichen.", "COLREG 12 a) i)"),
                                     ("Haben beide den Wind von derselben Seite, muss das Luvfahrzeug dem Leefahrzeug ausweichen.", "COLREG 12 a) ii)")]),
            ("Überholen", [("Jedes Fahrzeug, das ein anderes überholt, muss dem überholten Fahrzeug aus dem Weg gehen.", "COLREG 13 a)")]),
            ("Maschine und Segel", [("Ein Maschinenfahrzeug in Fahrt muss einem Segelfahrzeug aus dem Weg gehen.", "COLREG 18 a) iv)")]),
        ],
        "note": "Quellen: Racing Rules of Sailing 2025-2028 (World Sailing, {lien}); COLREG 1972 (IMO). Sonderfälle (Wenden, Marken, Hindernisse, manövrierbehinderte Fahrzeuge usw.) werden hier nicht behandelt.",
    },
}

TITRE = {"fr": "Cours théoriques de voile", "en": "Sailing theory courses", "it": "Corsi teorici di vela",
         "es": "Cursos teóricos de vela", "pt": "Cursos teóricos de vela", "de": "Segel-Theoriekurse"}

CSS = """
:root{--nuit:#0a1a2b;--panneau:#0f2438;--ivoire:#eef3f7;--gris:#9db2c6;--rouge:#e23a3e}
*{box-sizing:border-box}
body{margin:0;background:#071c31;color:var(--ivoire);font-family:ui-sans-serif,system-ui,-apple-system,"Helvetica Neue",Arial,sans-serif;line-height:1.6;-webkit-font-smoothing:antialiased}
.page{max-width:48rem;margin:0 auto;padding:3.6rem 1.4rem 5rem}
.haut{display:flex;justify-content:space-between;align-items:center;gap:1rem;flex-wrap:wrap}
a.retour{color:var(--gris);text-decoration:none;font-size:.64rem;letter-spacing:.14em;text-transform:uppercase;font-weight:500}
.langues button{background:none;border:1px solid #27425b;color:var(--gris);font-size:.64rem;padding:.25rem .5rem;margin-left:.2rem;cursor:pointer;border-radius:3px}
.langues button[aria-pressed=true]{color:var(--ivoire);border-color:var(--rouge)}
h1{font-size:2rem;margin:2rem 0 .4rem}
h2{font-size:1.15rem;margin:0 0 .6rem}
.intro{color:var(--gris)}
.cours{background:var(--panneau);border-left:3px solid var(--rouge);padding:1rem 1.2rem;margin:1.2rem 0;border-radius:3px}
.cours p{margin:.3rem 0}
.regle{display:inline-block;font-size:.72rem;letter-spacing:.06em;color:var(--gris);border:1px solid #27425b;border-radius:3px;padding:0 .4rem;margin-left:.3rem;white-space:nowrap}
.note{color:var(--gris);font-size:.85rem;margin-top:2rem}
a{color:var(--ivoire)}
"""

JS = """
(function(){
  var L=["fr","en","it","es","pt","de"],s=null;
  try{s=localStorage.getItem("sm-langue")}catch(e){}
  if(L.indexOf(s)<0){var n=(navigator.language||"fr").slice(0,2);s=L.indexOf(n)>=0?n:"en"}
  function set(l,save){
    document.documentElement.lang=l;
    [].forEach.call(document.querySelectorAll("[data-l]"),function(e){e.hidden=e.getAttribute("data-l")!==l});
    [].forEach.call(document.querySelectorAll("#langues button"),function(b){b.setAttribute("aria-pressed",b.getAttribute("data-lang")===l)});
    if(save){try{localStorage.setItem("sm-langue",l)}catch(e){}}
  }
  [].forEach.call(document.querySelectorAll("#langues button"),function(b){b.addEventListener("click",function(){set(b.getAttribute("data-lang"),true)})});
  set(s,false);
})();
"""


def _e(s: str) -> str:
    return _html.escape(s, quote=False)


def _cours(blocs) -> str:
    sortie = []
    for titre, phrases in blocs:
        ps = "".join(f'<p>{_e(t)}<span class="regle">{_e(r)}</span></p>' for t, r in phrases)
        sortie.append(f'<div class="cours"><h2>{_e(titre)}</h2>{ps}</div>')
    return "\n".join(sortie)


def _langue(lang: str) -> str:
    c = COURS[lang]
    lien = f'<a href="{URL_RRS}" rel="noopener">sailing.org</a>'
    cache = "" if lang == "fr" else " hidden"
    return (f'<div data-l="{lang}"{cache}>\n<h1>{_e(c["h1"])}</h1>\n<p class="intro">{_e(c["intro"])}</p>\n'
            f'<h2>{_e(c["h_rrs"])}</h2>\n{_cours(c["rrs"])}\n<h2>{_e(c["h_col"])}</h2>\n{_cours(c["col"])}\n'
            f'<p class="note">{_e(c["note"]).replace("{lien}", lien)}</p>\n</div>')


def page_cours() -> str:
    boutons = "".join(f'<button data-lang="{l}">{l.upper()}</button>' for l in LANGUES)
    corps = "\n\n".join(_langue(l) for l in LANGUES)
    desc = ("Quelques cours théoriques de voile, adossés aux textes officiels : priorités en régate "
            "(RRS 2025-2028) et règles de barre et de route (COLREG/RIPAM), règle citée sous chaque affirmation.")
    return (f'<!doctype html>\n<html lang="fr"><head><meta charset="utf-8">'
            f'<meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<title>{TITRE["fr"]} — Sailing More</title>'
            f'<link rel="canonical" href="https://sailingmore.fr/cours.html">'
            f'<meta name="description" content="{_html.escape(desc)}"><style>{CSS}</style></head><body><div class="page">\n'
            f'<div class="haut"><a class="retour" href="index.html">← Sailing More</a>\n'
            f'<div class="langues" id="langues">{boutons}</div></div>\n\n{corps}\n</div>\n'
            f'<script>{JS}</script>\n</body></html>\n')


def ecrire_page(dossier: Path = SITE) -> str:
    """Écrit `cours.html` dans `dossier` — appelé par `accueil_site.sortir_le_site`."""
    dossier.mkdir(parents=True, exist_ok=True)
    (dossier / "cours.html").write_text(page_cours(), encoding="utf-8")
    return "cours.html"


def main() -> int:
    if "--ecrire" not in sys.argv:
        print(__doc__)
        return 0
    SITE.mkdir(parents=True, exist_ok=True)
    (SITE / "cours.html").write_text(page_cours(), encoding="utf-8")
    print(f"{SITE / 'cours.html'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
