# © 2026 Sailing More — tous droits réservés. All rights reserved.
"""Une page par chant de marin, et l'index qui alimente le sous-menu du site.

Nicolas, 26/11/2026 : « il faudrait que les musiques s'affichent en sous menu sur la page. et que
chaque musique ait sa page ». La page `chants-de-marin.html` reste la liste ; chaque chant reçoit
`chant-<id>.html`, avec ses paroles, sa note, son lecteur, et deux liens (précédent / suivant) dans
la même famille.

Un seul chemin : `chants_page.ecrire_page()` écrit la liste, les pages de chant et l'index du
sous-menu. Rien ne s'écrit ici à la main.
"""

from __future__ import annotations

import html as H
import json
import re
import sys
from pathlib import Path

BASE = Path("/opt/data")
SITE = BASE / "projets/sailingmore/site"
INDEX_MENU = BASE / "projets/sailingmore/chants-menu.json"
URL = "https://sailingmore.fr"

sys.path.insert(0, str(Path(__file__).parent))
import chants_page as C  # noqa: E402
import jsonld  # noqa: E402
import site_blocks  # noqa: E402

e = lambda s: H.escape(str(s), quote=True)  # noqa: E731

CSS_PLUS = """
.page-chant{max-width:52rem}
.fil-ariane{font-size:.66rem;letter-spacing:.14em;text-transform:uppercase;color:#6f8598;margin:1.6rem 0 0}
.fil-ariane a{color:#9db2c6}
.fil-ariane span{margin:0 .4rem}
.chapeau-chant{color:#9db2c6;font-size:.95rem;margin:0 0 1.4rem;max-width:38rem}
.bloc-chant{margin:0 0 1.6rem}
.bloc-chant h2{font-size:.62rem;letter-spacing:.2em;text-transform:uppercase;color:#6f8598;font-weight:600;margin:1.8rem 0 .6rem}
.paroles-chant{white-space:pre-line;font-size:1rem;line-height:1.75;color:#eef3f7;border-left:2px solid var(--rouge);padding:.2rem 0 .2rem 1rem}
.note-chant{color:#9db2c6;font-size:.85rem;line-height:1.65;max-width:40rem}
.source-chant{color:#5d7386;font-size:.72rem;letter-spacing:.03em}
.prev-suiv{display:flex;justify-content:space-between;gap:.8rem;margin:2.4rem 0 0;padding-top:1.2rem;border-top:1px solid rgba(255,255,255,.1);font-size:.8rem}
.prev-suiv a{color:#fff;max-width:47%}
.prev-suiv small{display:block;color:#6f8598;font-size:.6rem;letter-spacing:.16em;text-transform:uppercase;margin-bottom:.2rem}
.retour{display:inline-block;margin:2.2rem 0 0;font-size:.78rem;color:#9db2c6;border-bottom:1px solid rgba(157,178,198,.4)}
"""

SCRIPT = """<script>
(function(){
  var l=document.querySelector('.lecteur');if(!l)return;
  var a=new Audio(l.dataset.src),b=l.querySelector('.play'),i=l.querySelector('.barre-t i'),t=l.querySelector('.t'),d=l.querySelector('.d');
  function mm(s){if(!isFinite(s))return '–:––';var m=Math.floor(s/60),r=Math.floor(s%60);return m+':'+(r<10?'0':'')+r}
  b.addEventListener('click',function(){a.paused?a.play():a.pause()});
  a.addEventListener('play',function(){b.textContent='❚❚'});a.addEventListener('pause',function(){b.textContent='▶'});
  a.addEventListener('loadedmetadata',function(){d.textContent=mm(a.duration)});
  a.addEventListener('timeupdate',function(){t.textContent=mm(a.currentTime);i.style.width=(a.currentTime/(a.duration||1)*100)+'%'});
  l.querySelector('.barre-t').addEventListener('click',function(ev){var r=this.getBoundingClientRect();a.currentTime=(ev.clientX-r.left)/r.width*(a.duration||0)});
})();
</script>"""


def nom_page(c: dict) -> str:
    return f"chant-{c['id']}.html"


def _chaine(c: dict, dans: list[dict]) -> tuple[dict | None, dict | None]:
    """Le chant précédent et le suivant, dans la même famille quand elle en compte d'autres."""
    famille = [x for x in dans if x["type"] == c["type"]]
    if len(famille) < 2:
        famille = dans
    i = next((k for k, x in enumerate(famille) if x["id"] == c["id"]), None)
    if i is None:
        return None, None
    return (famille[i - 1] if i > 0 else None), (famille[i + 1] if i + 1 < len(famille) else None)


def page_chanson(c: dict, d: dict, dans: list[dict]) -> str:
    T = d["ui"]["fr"]
    nom_langue = d["langueNoms"]["fr"].get(c["lg"], c["lg"])
    page = nom_page(c)
    resume = c["resume"].get("fr") or c["resume"]["en"]
    titre_seo = f"{c['titre']} — {T[c['type']].lower()} · chant de marin | Sailing More"
    desc = re.sub(r"\s+", " ", resume)[:155].rstrip(" ,;.")
    alternates = (f'<link rel="alternate" hreflang="fr" href="{URL}/{page}">'
                  f'<link rel="alternate" hreflang="x-default" href="{URL}/{page}">')

    oeuvre = {"@type": "MusicComposition", "name": c["titre"], "inLanguage": c["lg"],
              "description": resume, "alternateName": [c["titre"]],
              "isPartOf": {"@type": "CollectionPage", "name": T["titrePage"],
                           "url": f"{URL}/{C.PAGE}"}}
    if c.get("source"):
        oeuvre["creditText"] = c["source"]
    if c.get("audio"):
        a = c["audio"]
        oeuvre["audio"] = {"@type": "AudioObject", "name": a["nom"], "contentUrl": a["src"],
                           "encodingFormat": "audio/wav" if a["src"].endswith(".wav") else "audio/ogg"}
    tete = ('<!doctype html><html lang="fr"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<title>{e(titre_seo)}</title>'
            f'<meta name="description" content="{e(desc)}">'
            f'<link rel="canonical" href="{URL}/{page}">{alternates}'
            + jsonld.bloc({"@type": "BreadcrumbList", "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Accueil", "item": f"{URL}/"},
                {"@type": "ListItem", "position": 2, "name": T["titrePage"], "item": f"{URL}/{C.PAGE}"},
                {"@type": "ListItem", "position": 3, "name": c["titre"], "item": f"{URL}/{page}"}]},
                oeuvre)
            + jsonld.social(page, titre_seo, desc))

    if c.get("audio"):
        a = c["audio"]
        son = (f'<div class="lecteur" data-src="{e(a["src"])}">'
               f'<button class="play" aria-label="{e(T["ecouter"])}">▶</button>'
               f'<div class="rail"><div class="nom">{e(a["nom"])}</div>'
               '<div class="barre-t"><i></i></div>'
               '<div class="ligne"><span class="t">0:00</span><span class="d">–:––</span></div></div></div>'
               f'<p class="source-chant">{e(C._note_audio(a, T))}</p>')
    else:
        son = f'<p class="source-chant">{e(T["aucun"])}</p>'

    liens = "".join(
        f'<a class="son-lien" href="{e(x["u"])}" target="_blank" rel="noopener">{e(x["t"])}<em>↗</em></a>'
        for x in c.get("liens") or [])
    paroles = (f'<h2>{e(T["paroles"])}</h2><div class="paroles-chant" lang="{e(c["lg"])}">'
               f'{e(c["paroles"])}</div>'
               f'<p class="source-chant">{e(c["source"])}</p>') if c.get("paroles") else \
              f'<p class="source-chant">{e(T["sansParoles"])}</p>'
    accords = (f'<h2>{e(T["accords"])}</h2><div class="acords" data-acc>{e(c["accords"])}</div>'
               f'<p class="source-chant">{e(T["tonalite"])}</p>') if c.get("accords") else ""
    badge = "pro" if c.get("prot") else "dp"
    prec, suiv = _chaine(c, dans)
    nav = '<div class="prev-suiv">'
    nav += (f'<a href="{e(nom_page(prec))}"><small>← {e(T["precedent"])}</small>{e(prec["titre"])}</a>'
            if prec else "<span></span>")
    nav += (f'<a href="{e(nom_page(suiv))}" style="text-align:right"><small>{e(T["suivant"])} →</small>'
            f'{e(suiv["titre"])}</a>' if suiv else "<span></span>")
    nav += "</div>"

    corps = (f"<style>{site_blocks.CSS if hasattr(site_blocks, 'CSS') else ''}{C.CSS}{CSS_PLUS}</style>"
             '</head><body><main class="page page-chant">'
             f'<nav class="fil-ariane"><a href="/">Accueil</a><span>›</span>'
             f'<a href="{e(C.PAGE)}">{e(T["titrePage"])}</a><span>›</span>{e(c["titre"])}</nav>'
             f'<h1 id="h1">{e(c["titre"])}</h1>'
             f'<p class="fil-ariane" style="margin:0 0 .8rem">{e(T[c["type"]])} · {e(nom_langue)} · '
             f'<span class="badge {badge}">{e(T[badge])}</span></p>'
             + (f'<figure class="illus"><img src="/{e(c["image"]["fichier"])}" alt="{e(c["titre"])}" '
                f'width="{e(c["image"].get("largeur") or 900)}" decoding="async">'
                f'<figcaption>{e(c["image"]["credit"])}</figcaption></figure>' if c.get("image") else "")
             + f'<p class="chapeau-chant">{e(resume)}</p>'
             f'<p class="source-chant">{e(T["an"]["l"])} : {e(C._annee(c["annees"], T["an"]))} · {e(T["an"]["a"])}</p>'
             f'<div class="bloc-chant">{paroles}{accords}'
             f'<h2>{e(T["ecouter"])}</h2>{son}{liens}</div>'
             + nav
             + f'<a class="retour" href="{e(C.PAGE)}">← {e(T["titrePage"])} ({len(dans)})</a>'
             '</main>' + (SCRIPT if c.get("audio") else "") + '</body></html>\n')
    return tete + corps


def ecrire(dossier: Path = SITE) -> int:
    """Écrit les pages et l'index du sous-menu ; rend le nombre de pages écrites."""
    d = C.charger()
    dossier.mkdir(parents=True, exist_ok=True)
    chants = d["chants"]
    for c in chants:
        (dossier / nom_page(c)).write_text(page_chanson(c, d, chants), encoding="utf-8")
    INDEX_MENU.write_text(json.dumps(
        [{"id": c["id"], "titre": c["titre"], "type": c["type"]} for c in chants],
        ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    return len(chants)


if __name__ == "__main__":
    print(f"{ecrire()} page(s) de chant écrite(s) ; index du sous-menu : {INDEX_MENU.name}")
