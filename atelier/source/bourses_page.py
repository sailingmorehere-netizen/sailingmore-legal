#!/usr/bin/env python3
"""La page « bourse aux équipiers » : la carte de l'accueil, et les groupes Facebook un par un.

Nicolas, 26/11/2026 : « on va faire une page bourse aux équipiers pour afficher la carte qu'on avait
créée pour l'accueil et on présente les différents groupes facebook ».

Une seule source pour la carte : `site_blocks.marques_bourses()` et `site_blocks.encart_france()`,
les mêmes fonctions que l'accueil — c'est la même carte, servie une deuxième fois. Les groupes sont
lus dans `projets/sailingmore/bourses.json`, jamais recopiés ici.

Un seul écrivain : ce module. `accueil_site.py` l'appelle comme les autres pages et publie le fichier.
"""
from __future__ import annotations

import html as H
from pathlib import Path

import clics_sortants
import site_blocks

PAGE = "bourse-equipiers.html"

UI = {
    "fr": {
        "titre": "La bourse aux équipiers",
        "retour": "← Le site",
        "chapo": ("Les groupes Facebook où un bateau cherche un équipier — et où un équipier cherche un "
                  "bateau. Un clic ouvre le groupe : Sailing More ne modère rien, ne prend rien, "
                  "ne s'interpose pas."),
        "carte": "Où sont les groupes",
        "liste": "Les groupes, un par un",
        "membres": "membres",
        "voir": "Ouvrir le groupe",
        "jeu": "jeu en ligne",
        "note": ("Un groupe manque ? Écris à nicolas.baudu@sailingmore.fr et il rejoint la carte."),
        "total": "{n} groupes, {m} membres en tout.",
        "alt": "Carte du monde des bourses aux équipiers : un bateau par groupe",
    },
    "en": {
        "titre": "Crew finder groups",
        "retour": "← The site",
        "chapo": ("The Facebook groups where a boat looks for crew — and where crew look for a boat. "
                  "One click opens the group: Sailing More moderates nothing, takes nothing, "
                  "and does not step in."),
        "carte": "Where the groups are",
        "liste": "The groups, one by one",
        "membres": "members",
        "voir": "Open the group",
        "jeu": "online game",
        "note": "A group missing? Write to nicolas.baudu@sailingmore.fr and it goes on the map.",
        "total": "{n} groups, {m} members in all.",
        "alt": "World map of crew finder groups: one boat per group",
    },
}

CSS = """
:root{--fond:#0a1a2b;--carte:#0f2438;--trait:#1d3549;--encre:#e8eef5;--doux:#9db2c7;--accent:#5fd3c4}
*{box-sizing:border-box}
body{margin:0;background:var(--fond);color:var(--encre);font:16px/1.5 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}
a{color:inherit}
.page{max-width:72rem;margin:0 auto;padding:2rem 1.2rem 5rem}
.page h1{font-size:clamp(1.5rem,3.4vw,2.2rem);margin:.2rem 0 .7rem;letter-spacing:-.01em;
  font-weight:500;text-transform:none;color:var(--encre)}
.chapo{color:var(--doux);max-width:46rem;margin:0 0 .4rem}
.total{color:var(--doux);font-size:.86rem;margin:0 0 1.6rem}
.retour{display:inline-block;color:var(--doux);text-decoration:none;font-size:.9rem;margin-bottom:.6rem}
.bourses{display:grid;gap:.7rem;grid-template-columns:repeat(auto-fill,minmax(15.5rem,1fr));margin:1rem 0 0}
.bourse{display:flex;flex-direction:column;gap:.2rem;padding:.85rem .95rem;background:var(--carte);
  border:1px solid var(--trait);border-radius:12px;text-decoration:none;min-width:0;min-height:6.2rem}
.bourse:hover,.bourse:focus-visible{border-color:var(--accent)}
.bourse strong{font-weight:600;font-size:.98rem;line-height:1.25}
.bourse .ou{color:var(--doux);font-size:.8rem;letter-spacing:.04em;text-transform:uppercase}
.bourse .nb{color:var(--accent);font-size:.86rem}
.bourse .badge{align-self:flex-start;color:var(--doux);border:1px solid var(--trait);border-radius:99px;
  padding:.05rem .5rem;font-size:.72rem;letter-spacing:.04em;text-transform:uppercase}
.note{margin-top:1.6rem;color:var(--doux);font-size:.86rem;border-top:1px solid var(--trait);padding-top:1rem}
/* La carte : même brique que l'accueil, et le titre de section au même réglage que les autres cartes
   du site (.74rem/.06em/400) — seule la couleur reste celle de cet endroit (Nicolas, 26/11/2026). */
.monde{max-width:62rem;margin:0 auto 2.4rem;padding:0 .2rem}
.monde h2{font-size:.74rem;letter-spacing:.06em;font-weight:400;text-transform:uppercase;
  color:var(--doux);margin:1.4rem 0 .5rem}
.planisphere{position:relative;border:1px solid var(--trait);border-radius:12px;overflow:hidden;
  background:#081521}
.planisphere img{display:block;width:100%;height:auto;opacity:.92}
.encart-france{width:min(430px,100%);margin:.9rem 0 0}
"""


JS = """<script>
(function(){
  var U = window.SM_PAGE_UI || {}, L = 'fr';
  try{ if(window.smLangue) L = window.smLangue(); }catch(e){}
  if(!U[L]) L = 'fr';
  function t(k){ return (U[L] && U[L][k]) || (U.fr && U.fr[k]) || k; }
  function textes(){
    document.querySelectorAll('[data-t]').forEach(function(e){
      var v = t(e.dataset.t);
      if(v && e.dataset.n !== undefined) v = v.replace('{n}', e.dataset.n).replace('{m}', e.dataset.m || '');
      if(v) e.textContent = v;
    });
  }
  function choisir(v){
    if(window.smChoisirLangue) window.smChoisirLangue(v);
    L = (v === 'bzh') ? 'fr' : v;
    if(!U[L]) L = 'fr';
    textes();
    document.querySelectorAll('#langues button').forEach(function(b){
      b.setAttribute('aria-pressed', String(b.dataset.lang === v));
    });
  }
  document.querySelectorAll('#langues button').forEach(function(b){
    b.addEventListener('click', function(){ choisir(b.dataset.lang); });
  });
  textes();
})();
</script>"""


def _nombre(n: int) -> str:
    return f"{n:,}".replace(",", "\u00a0")


def _json_script(obj) -> str:
    """JSON posé dans un <script> : jamais échappé en HTML (sinon les guillemets deviennent &quot;
    et le script lit des clés brutes — vu le 26/11/2026), seulement le `</` qui fermerait la balise."""
    import json
    return json.dumps(obj, ensure_ascii=False).replace("</", "<\\/")


def construire(dossier: Path | None = None) -> str:
    import jsonld

    bourses = [b for b in site_blocks.bourses() if b.get("groupe") and b.get("lien")]
    # Les plus gros d'abord : c'est là qu'on a le plus de chances de trouver une place.
    bourses.sort(key=lambda b: (-(int(b.get("membres") or 0)), b.get("groupe") or ""))
    total = sum(int(b.get("membres") or 0) for b in bourses)
    f = UI["fr"]

    cartes = []
    for b in bourses:
        zone = (b.get("ou") or "").strip()
        gens = int(b.get("membres") or 0)
        lien = clics_sortants.lien(b["lien"], "bourse")
        morceaux = [f'<strong>{H.escape(b["groupe"])}</strong>']
        if zone:
            morceaux.append(f'<span class="ou">{H.escape(zone)}</span>')
        if gens:
            morceaux.append(f'<span class="nb">{_nombre(gens)} <span data-t="membres">membres</span></span>')
        if b.get("jeu"):
            morceaux.append('<span class="badge" data-t="jeu">jeu en ligne</span>')
        cartes.append(f'<a class="bourse" href="{H.escape(lien, quote=True)}" rel="nofollow noopener" '
                      f'title="{H.escape(f["voir"])} : {H.escape(b["groupe"], quote=True)}">'
                      + "".join(morceaux) + "</a>")

    seo_titre = (f"Bourse aux équipiers : {len(bourses)} groupes Facebook pour embarquer | Sailing More")
    seo_desc = (f"La carte des groupes Facebook où l'on trouve un équipier ou un bateau : "
                f"{len(bourses)} groupes, {_nombre(total)} membres. Léman, France, Atlantique, Pacifique, "
                "Caraïbes, monde entier.")

    return ("<!doctype html><html lang=\"fr\"><head><meta charset=\"utf-8\">"
            "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">"
            f"<title>{H.escape(seo_titre)}</title>"
            f"<link rel=\"canonical\" href=\"https://sailingmore.fr/{PAGE}\">"
            f"{jsonld.page_simple(PAGE, f['titre'])}"
            f"<meta name=\"description\" content=\"{H.escape(seo_desc, quote=True)}\">"
            f"{jsonld.social(PAGE, seo_titre, seo_desc)}"
            f"<style>{site_blocks.ENTETE_CSS}{CSS}</style>{site_blocks.script_langue()}</head><body>\n"
            f"{site_blocks.entete_site(PAGE, site_blocks.LANGUES)}\n<main class=\"page\">"
            f"<a class=\"retour\" href=\"/\" data-t=\"retour\">{H.escape(f['retour'])}</a>"
            f"<h1 data-t=\"titre\">{H.escape(f['titre'])}</h1>"
            f"<p class=\"chapo\" data-t=\"chapo\">{H.escape(f['chapo'])}</p>"
            f"<p class=\"total\" data-t=\"total\" data-n=\"{len(bourses)}\" data-m=\"{_nombre(total)}\">{H.escape(f['total'].format(n=len(bourses), m=_nombre(total)))}</p>"
            "<section class=\"monde\">"
            f"<h2 data-t=\"carte\">{H.escape(f['carte'])}</h2>"
            "<div class=\"planisphere\">"
            f"<img src=\"carte-monde.png\" alt=\"{H.escape(f['alt'], quote=True)}\">"
            f"{site_blocks.marques_bourses(bourses)}"
            f"{site_blocks.encart_france(bourses)}"
            "</div></section>"
            f"<h2 data-t=\"liste\" style=\"margin-top:2.2rem\">{H.escape(f['liste'])}</h2>"
            f"<div class=\"bourses\">{''.join(cartes)}</div>"
            f"<p class=\"note\" data-t=\"note\">{H.escape(f['note'])}</p>"
            "</main>"
            f"{site_blocks.CARTE_CSS}"
            f"<script>window.SM_PAGE_UI={_json_script(UI)};</script>"
            f"{JS}"
            "</body></html>\n")


def ecrire_page(dossier: Path) -> int:
    dossier.mkdir(parents=True, exist_ok=True)
    (dossier / PAGE).write_text(construire(dossier), encoding="utf-8")
    return len(site_blocks.bourses())


if __name__ == "__main__":
    site = Path("/opt/data/projets/sailingmore/site")
    print(ecrire_page(site), "groupe(s) écrit(s)")
