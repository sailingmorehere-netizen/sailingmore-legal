#!/usr/bin/env python3
"""Schémas « avant / pendant / après » et vidéo, posés sous chaque règle de la page des règles.

Rien n'est hébergé ici : la vidéo reste chez YouTube et n'est chargée qu'au clic (aucune requête vers
Google avant, la promesse du bandeau tient). Les schémas sont du SVG écrit ici, quelques centaines
d'octets chacun, sans texte : les mots qui les accompagnent sont traduits dans le bloc JavaScript.

Le bloc est injecté dans la page que Claude construit (`regles-de-course.html`), juste avant
`</body>`, par `publier_atelier.py` — un seul chemin de publication, rien à modifier dans ses scripts.
Il pose le schéma sous le résumé de chaque règle, et le repose quand la page se filtre ou change de
langue, puisque les cartes sont reconstruites en JavaScript.

    python3 scripts/regles_schemas.py                  # aperçu local (trois cartes)
    python3 scripts/regles_schemas.py --injecter PAGE  # injecte dans la page construite
"""
from __future__ import annotations

import itertools
import json
import os
import sys
from pathlib import Path

SITE = Path(os.environ.get("SITE_ROOT", "/opt/data")) / "projets/sailingmore/site"
DEPART = "<!-- schemas avant pendant apres -->"
FIN = "<!-- /schemas avant pendant apres -->"

# Vidéos retenues : édition 2025-2028 uniquement, courtes, une règle par vidéo.
# Aucune n'est copiée : le lecteur est celui de YouTube, sans cookie tant qu'on n'a pas cliqué.
VIDEOS = {
    "10": {"id": "5rS5GpzEOYY", "chaine": "Sailing Kiwi", "duree": "1 min",
           "titre": "Don't Get Penalized — The Sailing Rule Most Beginners Get Wrong"},
    "18": {"id": "AiLKmHfAYiE", "chaine": "Sailing Kiwi", "duree": "1 min 15",
           "titre": "You Rounded the Mark Wrong: Room to Round vs Room to Sail"},
    "44": {"id": "Tlk798UfvVo", "chaine": "Sailing Kiwi", "duree": "1 min 29",
           "titre": "How to Correctly Execute a One-Turn Penalty (Step-by-Step)"},
}

COQUE_A, GV_A, FOC_A = "#eef3f7", "#b9cad8", "#cfe0ee"
COQUE_B, GV_B, FOC_B = "#e23a3e", "#f08b8d", "#c94346"
COQUE_G, GV_G, FOC_G = "#8aa0b4", "#c3d3df", "#9db2c6"
JAUNE, GRIS = "#ffd166", "#8aa0b4"

_IDS = itertools.count(1)


def _bateau(x: float, y: float, coque: str, gv: str, foc: str, echelle: float = 1.45) -> str:
    """Voilier de profil : à cette taille, c'est la seule silhouette qui se lit comme un bateau."""
    return (
        f'<g transform="translate({x},{y}) scale({echelle})">'
        f'<path d="M-11,3 Q0,12 11,3 L8.5,-1 L-8.5,-1 Z" fill="{coque}"/>'
        f'<line x1="0" y1="-1" x2="0" y2="-15" stroke="{coque}" stroke-width="1.1"/>'
        f'<path d="M0.8,-14 L0.8,-2.5 L9,-2.5 Z" fill="{gv}"/>'
        f'<path d="M-1,-12 L-1,-2.5 L-7.5,-2.5 Z" fill="{foc}"/>'
        "</g>"
    )


def _badge(x: float, y: float, lettre: str, fond: str, texte: str = "#08192b") -> str:
    return (f'<circle cx="{x}" cy="{y}" r="9" fill="{fond}"/>'
            f'<text x="{x}" y="{y + 3.4}" text-anchor="middle" font-size="11" font-weight="700" '
            f'fill="{texte}">{lettre}</text>')


def _fleche(d: str, couleur: str, cle: str, pointilles: bool = False) -> str:
    tirets = ' stroke-dasharray="5 4"' if pointilles else ""
    return (f'<path d="{d}" fill="none" stroke="{couleur}" stroke-width="1.7"{tirets} '
            f'marker-end="url(#{cle})"/>'.replace(f"#{cle}", f"#{{M{cle}}}"))


def _panneau(corps: str, couleurs: dict[str, str]) -> str:
    """Un pas de la séquence : même cadre, même échelle pour les trois."""
    defs = []
    for cle, couleur in couleurs.items():
        ident = f"mk{next(_IDS)}"
        corps = corps.replace(f"{{M{cle}}}", ident)
        defs.append(f'<marker id="{ident}" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" '
                    f'markerHeight="6" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="{couleur}"/>'
                    "</marker>")
    return ('<svg viewBox="0 0 320 140" role="img" class="seq-svg"><defs>' + "".join(defs) + "</defs>"
            '<rect x="0" y="0" width="320" height="140" rx="10" fill="#0d2338"/>'
            + corps + "</svg>")


def _zone(cx: float = 205, cy: float = 74, r: float = 40) -> str:
    return (f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{GRIS}" stroke-width="1.4" '
            'stroke-dasharray="6 6"/>'
            f'<circle cx="{cx}" cy="{cy}" r="4" fill="{JAUNE}"/>')


def etapes_10() -> list[str]:
    """Règle 10 — amures opposées : B, bâbord amures, s'écarte."""
    fleches = {"A": COQUE_A, "B": COQUE_B}
    avant = (
        _fleche("M300,66 L220,66", COQUE_A, "A", True)
        + _fleche("M36,96 L140,96", COQUE_B, "B", True)
        + _bateau(266, 66, COQUE_A, GV_A, FOC_A) + _badge(294, 46, "A", COQUE_A)
        + _bateau(48, 96, COQUE_B, GV_B, FOC_B) + _badge(24, 116, "B", COQUE_B, "#fff")
    )
    pendant = (
        _fleche("M112,106 C 158,124 202,120 226,108", COQUE_B, "B")
        + _fleche("M300,52 L215,52", COQUE_A, "A", True)
        + _bateau(266, 52, COQUE_A, GV_A, FOC_A) + _badge(294, 32, "A", COQUE_A)
        + _bateau(96, 102, COQUE_B, GV_B, FOC_B) + _badge(72, 122, "B", COQUE_B, "#fff")
    )
    apres = (
        _fleche("M96,64 L16,64", COQUE_A, "A", True)
        + _bateau(112, 64, COQUE_A, GV_A, FOC_A) + _badge(140, 44, "A", COQUE_A)
        + _fleche("M196,112 L300,112", COQUE_B, "B", True)
        + _bateau(178, 112, COQUE_B, GV_B, FOC_B) + _badge(154, 130, "B", COQUE_B, "#fff")
    )
    return [_panneau(x, fleches) for x in (avant, pendant, apres)]


def etapes_18() -> list[str]:
    """Règle 18 — place à la marque : A à l'intérieur a droit à la place, B à l'extérieur s'écarte."""
    fleches = {"A": COQUE_A, "G": GRIS}
    avant = (_zone()
             + _fleche("M40,104 L120,96", GRIS, "G", True)
             + _bateau(186, 68, COQUE_A, GV_A, FOC_A) + _badge(162, 50, "A", COQUE_A)
             + _bateau(50, 104, COQUE_G, GV_G, FOC_G) + _badge(26, 124, "B", GRIS))
    pendant = (_zone()
               + _fleche("M228,42 C 258,56 266,86 244,100", COQUE_A, "A")
               + _bateau(222, 36, COQUE_A, GV_A, FOC_A) + _badge(198, 18, "A", COQUE_A)
               + _bateau(58, 62, COQUE_G, GV_G, FOC_G) + _badge(34, 82, "B", GRIS)
               + _fleche("M82,70 L104,74", GRIS, "G"))
    apres = (_zone()
             + _bateau(272, 100, COQUE_A, GV_A, FOC_A) + _badge(296, 80, "A", COQUE_A)
             + _fleche("M118,118 L186,118", GRIS, "G", True)
             + _bateau(196, 114, COQUE_G, GV_G, FOC_G) + _badge(172, 132, "B", GRIS))
    return [_panneau(x, fleches) for x in (avant, pendant, apres)]


def etapes_44() -> list[str]:
    """Règle 44 — pénalité d'un tour, effectuée dès que possible après l'incident."""
    fleches = {"B": COQUE_B, "A": COQUE_A}
    avant = (_bateau(148, 62, COQUE_A, GV_A, FOC_A) + _badge(124, 42, "A", COQUE_A)
             + _bateau(196, 74, COQUE_B, GV_B, FOC_B) + _badge(222, 94, "B", COQUE_B, "#fff")
             + f'<circle cx="172" cy="68" r="10" fill="none" stroke="{JAUNE}" stroke-width="1.6"/>')
    pendant = (f'<circle cx="160" cy="70" r="32" fill="none" stroke="{JAUNE}" stroke-width="1.5" '
               'stroke-dasharray="7 6"/>'
               + _fleche("M160,38 C 198,46 206,86 176,100", COQUE_B, "B")
               + _bateau(160, 70, COQUE_B, GV_B, FOC_B) + _badge(160, 22, "B", COQUE_B, "#fff"))
    apres = (_bateau(118, 66, COQUE_B, GV_B, FOC_B) + _badge(94, 46, "B", COQUE_B, "#fff")
             + _fleche("M148,74 L256,88", COQUE_B, "B", True)
             + _bateau(264, 90, COQUE_A, GV_A, FOC_A) + _badge(290, 70, "A", COQUE_A))
    return [_panneau(x, fleches) for x in (avant, pendant, apres)]


SEQUENCES = {"10": etapes_10(), "18": etapes_18(), "44": etapes_44()}


CSS = """
.regle .seq{margin:.9rem 0 .2rem;display:grid;gap:.1rem}
.regle .seq-etape{display:grid;grid-template-columns:4.4rem minmax(0,1fr);align-items:center;gap:.6rem}
.regle .seq-etape span{font-size:.64rem;letter-spacing:.08em;text-transform:uppercase;color:#8aa0b4}
.regle .seq-svg{width:100%;max-width:320px;height:auto;display:block;border-radius:10px}
.regle .seq-fleche{color:#3d5a75;font-size:.75rem;line-height:1;padding-left:5rem}
.regle .video{margin:.85rem 0 0}
.regle .lecture{display:inline-flex;align-items:center;gap:.5rem;background:#12314d;color:#eef3f7;
 border:1px solid #23496b;border-radius:999px;padding:.48rem .95rem;font:inherit;font-size:.78rem;
 cursor:pointer}
.regle .lecture:hover{border-color:#eef3f7}
.regle .lecture b{color:#ffd166;font-weight:700}
.regle .cadre{position:relative;padding-top:56.25%;margin-top:.6rem;border-radius:10px;
 overflow:hidden;background:#000}
.regle .cadre iframe{position:absolute;inset:0;width:100%;height:100%;border:0}
.regle .credit{color:#8aa0b4;font-size:.66rem;margin:.4rem 0 0;line-height:1.35}
"""

JS = """
(function(){
  var SEQ = window.__SEQ || {}, VIDEO = window.__VIDEO || {};
  var UI = {
    fr:{a:"avant",p:"pendant",r:"après",l:"Voir la vidéo",c:"Vidéo d'un tiers, lue chez YouTube. Rien n'est chargé avant votre clic."},
    en:{a:"before",p:"during",r:"after",l:"Watch the video",c:"Third-party video, played on YouTube. Nothing loads before you click."},
    it:{a:"prima",p:"durante",r:"dopo",l:"Guarda il video",c:"Video di terzi, letta su YouTube. Nulla si carica prima del clic."},
    es:{a:"antes",p:"durante",r:"después",l:"Ver el vídeo",c:"Vídeo de un tercero, leído en YouTube. Nada se carga antes del clic."},
    pt:{a:"antes",p:"durante",r:"depois",l:"Ver o vídeo",c:"Vídeo de terceiros, lido no YouTube. Nada carrega antes do clique."},
    de:{a:"vorher",p:"während",r:"nachher",l:"Video ansehen",c:"Video eines Dritten, auf YouTube. Vor dem Klick wird nichts geladen."}
  };
  function langue(){ var l=(document.documentElement.lang||"fr").slice(0,2); return UI[l]?l:"fr"; }
  function esc(s){ return String(s).replace(/[&<>]/g,function(c){return {"&":"&amp;","<":"&lt;",">":"&gt;"}[c];}); }

  function poser(){
    var u = UI[langue()];
    Object.keys(SEQ).forEach(function(cle){
      var carte = document.getElementById("r"+cle);
      if(!carte || carte.querySelector(".seq")) return;
      var cible = carte.querySelector(".resume");
      if(!cible) return;
      var etapes = SEQ[cle], h = '<div class="seq">';
      [["a",0],["p",1],["r",2]].forEach(function(x,i){
        h += '<div class="seq-etape"><span>'+esc(u[x[0]])+'</span>'+etapes[x[1]]+'</div>';
        if(i<2) h += '<div class="seq-fleche">↓</div>';
      });
      if(VIDEO[cle]){
        h += '<div class="video"><button class="lecture" type="button" data-cle="'+cle+'">'
           + '<b>▶</b> '+esc(u.l)+'</button><div class="cadre" hidden></div>'
           + '<p class="credit">'+esc(u.c)+'</p></div>';
      }
      cible.insertAdjacentHTML("afterend", h + '</div>');
    });
  }

  document.addEventListener("click", function(ev){
    var b = ev.target.closest && ev.target.closest(".lecture");
    if(!b) return;
    var cle = b.dataset.cle, cadre = b.nextElementSibling;
    if(!cadre || !cadre.classList.contains("cadre") || !cadre.hidden) return;
    var f = document.createElement("iframe");
    f.src = "https://www.youtube-nocookie.com/embed/" + VIDEO[cle] + "?autoplay=1&rel=0&modestbranding=1";
    f.title = "Vidéo — règle " + cle;
    f.allow = "accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture";
    f.setAttribute("allowfullscreen","");
    f.setAttribute("referrerpolicy","strict-origin-when-cross-origin");
    cadre.appendChild(f); cadre.hidden = false; b.hidden = true;
  });

  var liste = document.getElementById("liste-regles");
  if(liste) new MutationObserver(poser).observe(liste, {childList:true});
  new MutationObserver(poser).observe(document.documentElement,
                                     {attributes:true, attributeFilter:["lang"]});
  if(document.readyState !== "loading") poser();
  else document.addEventListener("DOMContentLoaded", poser);
})();
"""


def fragment() -> str:
    seq = json.dumps(SEQUENCES, ensure_ascii=False)
    vid = json.dumps({k: v["id"] for k, v in VIDEOS.items()}, ensure_ascii=False)
    return (f"{DEPART}\n<style>{CSS}</style>\n"
            f"<script>window.__SEQ = {seq}; window.__VIDEO = {vid};</script>\n"
            f"<script>{JS}</script>\n{FIN}\n")


def injecter(chemin: Path) -> int:
    """Pose le bloc dans la page construite, une seule fois. Rend le nombre de règles servies."""
    html = chemin.read_text(encoding="utf-8")
    i, j = html.find(DEPART), html.find(FIN)
    if 0 <= i < j:
        html = html[:i] + html[j + len(FIN) + 1:]
    if "</body>" not in html:
        raise SystemExit(f"{chemin} : pas de </body>, page inattendue")
    html = html.replace("</body>", fragment() + "</body>", 1)
    chemin.write_text(html, encoding="utf-8")
    return len(SEQUENCES)


def apercu(site: Path) -> Path:
    """Aperçu local : trois cartes, pour regarder avant de toucher à la page des règles."""
    cartes = "".join(
        f'<article class="regle" id="r{cle}"><h3><span class="num">{cle}</span> Règle {cle}</h3>'
        '<p class="resume">Aperçu : le texte vient de la page des règles, pas de ce fichier.</p>'
        "</article>" for cle in SEQUENCES)
    page = f"""<!doctype html><html lang="fr"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex">
<title>Aperçu — schémas avant / pendant / après</title>
<style>body{{background:#08192b;color:#eef3f7;font-family:system-ui,sans-serif;margin:0;padding:1rem}}
.regle{{background:#0b2340;border:1px solid #1c3d5c;border-radius:14px;padding:1rem;margin:0 0 1rem}}
.regle h3{{margin:0 0 .5rem;font-size:.95rem}}.regle .num{{color:#ffd166}}
.regle .resume{{color:#8aa0b4;font-size:.82rem;margin:.2rem 0 .6rem}}</style></head>
<body>{cartes}{fragment()}</body></html>"""
    site.mkdir(parents=True, exist_ok=True)
    cible = site / "apercu-schemas.html"
    cible.write_text(page, encoding="utf-8")
    return cible


def main(argv: list[str]) -> int:
    if len(argv) >= 2 and argv[0] == "--injecter":
        print(f"{argv[1]} : {injecter(Path(argv[1]))} règle(s) servie(s)")
        return 0
    cible = apercu(SITE)
    print(f"{cible} ({cible.stat().st_size} octets)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
