#!/usr/bin/env python3
"""Page d'essai « vidéo + schéma » sur trois règles (22/11/2026).

Le but n'est pas de publier la page des règles : c'est de montrer à Nicolas, sur trois cas, ce que
donne une carte de règle avec une vidéo (chargée seulement au clic, donc aucun cookie avant) et un
schéma dessiné par nous. Les trois règles servent de test avant généralisation.

    python3 scripts/regles_video_test.py            # écrit projets/sailingmore/site/regles-video-test.html
    python3 scripts/regles_video_test.py --apercu   # écrit le même fichier et affiche son chemin

Rien n'est copié d'un tiers : la vidéo reste chez YouTube (iframe youtube-nocookie insérée au clic),
le schéma est du SVG écrit ici, le texte vient de `regles.json`.
"""
from __future__ import annotations

import html as _html
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import regles_page as R  # noqa: E402  (CSS et lecture de regles.json : une seule source)

SITE = Path("/opt/data/projets/sailingmore/site")

# Vidéos retenues : édition 2025-2028 uniquement, courtes, une règle par vidéo.
# Vérifiées le 22/11/2026 (oEmbed 200, date de publication et édition lues sur la page YouTube).
VIDEOS = {
    "10": {"id": "5rS5GpzEOYY", "chaine": "Sailing Kiwi", "date": "2026", "duree": "1 min",
           "titre": "Don't Get Penalized — The Sailing Rule Most Beginners Get Wrong"},
    "18": {"id": "AiLKmHfAYiE", "chaine": "Sailing Kiwi", "date": "2026", "duree": "1 min 15",
           "titre": "You Rounded the Mark Wrong: Room to Round vs Room to Sail"},
    "44": {"id": "Tlk798UfvVo", "chaine": "Sailing Kiwi", "date": "2026", "duree": "1 min 29",
           "titre": "How to Correctly Execute a One-Turn Penalty (Step-by-Step)"},
}

VOILE = 'M0,-15 L4.5,5 L0,11 L-4.5,5 Z'
GRAND_VOILE = 'M0,-13 L0,3 L9,3 Z'

CSS_EN_PLUS = """
.video{margin:1rem 0 .2rem;border:1px solid rgba(255,255,255,.12);background:#08192b}
.video iframe{display:block;width:100%;aspect-ratio:16/9;border:0}
.lecture{position:relative;display:flex;align-items:center;justify-content:center;gap:.75rem;
  width:100%;aspect-ratio:16/9;background:
    repeating-linear-gradient(115deg,rgba(255,255,255,.035) 0 2px,transparent 2px 11px),
    radial-gradient(120% 120% at 30% 20%,#12344f 0%,#08192b 70%);
  border:0;color:#fff;font:inherit;cursor:pointer}
.lecture .rond{width:3.2rem;height:3.2rem;border-radius:50%;background:rgba(226,58,62,.92);
  display:flex;align-items:center;justify-content:center;flex:0 0 auto}
.lecture:hover .rond{background:#e23a3e;transform:scale(1.04)}
.lecture .txt{text-align:left;font-size:.7rem;letter-spacing:.1em;text-transform:uppercase;
  color:#d6e5f1;line-height:1.5}
.lecture .txt small{display:block;letter-spacing:.04em;text-transform:none;color:#8aa0b4;font-size:.68rem}
.credit{font-size:.67rem;color:#7d92a6;margin:.45rem 0 0;letter-spacing:.02em}
.credit a{color:#cfe0ee;text-decoration:underline;text-decoration-color:rgba(226,58,62,.6)}
.schema{margin:1.1rem 0 .3rem;background:#0a1f33;border:1px solid rgba(255,255,255,.08);padding:.7rem}
.schema svg{display:block;width:100%;height:auto}
.schema figcaption{font-size:.66rem;color:#8aa0b4;margin-top:.55rem;line-height:1.5}
.note{font-size:.72rem;color:#8aa0b4;border-left:3px solid rgba(226,58,62,.5);padding:.1rem 0 .1rem .8rem;
  margin:2rem 0 0;max-width:42rem}
.regle{background:#0a1f33;border:1px solid rgba(255,255,255,.09);padding:1.1rem 1.2rem 1.3rem;
  margin:0 0 1.2rem;border-left:3px solid rgba(226,58,62,.55)}
.regle h3{font-size:1.25rem}
.regle .num{color:#8aa0b4;font-size:.78rem;letter-spacing:.14em;text-transform:uppercase;display:block;
  margin-bottom:.15rem}
"""


def _e(s: str) -> str:
    return _html.escape(str(s), quote=True)


def carte_video(cle: str) -> str:
    v = VIDEOS[cle]
    url = f"https://www.youtube.com/watch?v={v['id']}"
    return (
        f'<div class="video" data-video="{_e(v["id"])}">'
        f'<button type="button" class="lecture" aria-label="Lire la vidéo de la règle {_e(cle)} '
        f'({_e(v["duree"])}, en anglais)">'
        '<span class="rond" aria-hidden="true"><svg width="16" height="18" viewBox="0 0 16 18" '
        'fill="#fff"><path d="M1 1.2v15.6L15 9z"/></svg></span>'
        f'<span class="txt">Voir la vidéo<small>{_e(v["duree"])} · en anglais</small></span>'
        "</button></div>"
        f'<p class="credit">{_e(v["chaine"])}, {_e(v["date"])} · « {_e(v["titre"])} » · '
        f'<a href="{_e(url)}" rel="noopener nofollow">ouvrir sur YouTube</a> · '
        "chargée seulement au clic</p>"
    )


def _badge(x: float, y: float, lettre: str, fond: str = "#eef3f7", texte: str = "#08192b") -> str:
    return (f'<circle cx="{x}" cy="{y}" r="13" fill="{fond}"/>'
            f'<text x="{x}" y="{y + 4.8}" fill="{texte}" font-size="14" font-weight="700" '
            f'text-anchor="middle">{lettre}</text>')


def _bateau(x: float, y: float, angle: float, coque: str, v1: str, v2: str,
            bord: str = "none") -> str:
    """Bateau vu de dessus, assez gros pour rester lisible sur un téléphone."""
    return (f'<g transform="translate({x},{y}) rotate({angle}) scale(1.9)">'
            # coque vue de dessus : étrave pointue, tableau arrière droit
            f'<path d="M0,-16 L3.6,-7 L3.6,11 L-3.6,11 L-3.6,-7 Z" fill="{coque}" stroke="{bord}" '
            f'stroke-width=".7"/>'
            # grand-voile et foc, de part et d'autre du mât
            f'<path d="M0,-13 C 8,-6 9,4 3,10 Z" fill="{v1}"/>'
            f'<path d="M0,-9 C -4,-3 -4,4 0,9 Z" fill="{v2}"/>'
            "</g>")


def schema_10() -> str:
    return f"""
<svg viewBox="0 0 480 250" role="img" aria-labelledby="s10t">
  <title id="s10t">Règle 10 : sur des amures opposées, le bateau bâbord amures s'écarte.</title>
  <defs>
    <marker id="a10" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto">
      <path d="M0,0 L10,5 L0,10 z" fill="#8aa0b4"/>
    </marker>
    <marker id="a10r" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto">
      <path d="M0,0 L10,5 L0,10 z" fill="#e23a3e"/>
    </marker>
  </defs>
  <g stroke="#8aa0b4" stroke-width="1.6" marker-end="url(#a10)" opacity=".7">
    <line x1="60" y1="22" x2="60" y2="54"/><line x1="240" y1="22" x2="240" y2="54"/>
    <line x1="420" y1="22" x2="420" y2="54"/>
  </g>
  <text x="240" y="14" fill="#8aa0b4" font-size="12" text-anchor="middle" letter-spacing="3">VENT</text>

  <line x1="306" y1="100" x2="135" y2="100" stroke="#eef3f7" stroke-width="2"
        marker-end="url(#a10)" opacity=".85"/>
  {_bateau(330, 100, -90, "#eef3f7", "#b9cad8", "#cfe0ee")}
  {_badge(330, 58, "A")}

  <path d="M150,190 C 215,208 275,204 315,214" fill="none" stroke="#e23a3e" stroke-width="2"
        stroke-dasharray="6 5" marker-end="url(#a10r)"/>
  {_bateau(120, 200, 45, "#e23a3e", "#c94346", "#a32024")}
  {_badge(120, 158, "B", "#e23a3e", "#ffffff")}
</svg>"""


def schema_18() -> str:
    return f"""
<svg viewBox="0 0 480 240" role="img" aria-labelledby="s18t">
  <defs>
    <marker id="a18" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto">
      <path d="M0,0 L10,5 L0,10 z" fill="#8aa0b4"/>
    </marker>
  </defs>
  <title id="s18t">Règle 18 : dans la zone, l'extérieur laisse la place à la marque à l'intérieur.</title>
  <text x="8" y="24" fill="#8aa0b4" font-size="12">zone = 3 longueurs de coque</text>
  <circle cx="240" cy="90" r="68" fill="rgba(238,243,247,.03)" stroke="#8aa0b4" stroke-width="1.4"
          stroke-dasharray="7 6"/>
  <circle cx="240" cy="90" r="9" fill="#e23a3e"/>
  <text x="258" y="94" fill="#8aa0b4" font-size="12">la marque</text>

  {_bateau(214, 126, 4, "#eef3f7", "#b9cad8", "#cfe0ee")}
  {_badge(176, 126, "A")}

  <path d="M318,182 C 306,168 300,150 296,140" fill="none" stroke="#8aa0b4" stroke-width="1.8"
        stroke-dasharray="5 5" marker-end="url(#a18)"/>
  {_bateau(334,198, -28, "#8aa0b4", "#9db2c6", "#6f8ba1")}
  {_badge(374, 198, "B", "#8aa0b4", "#08192b")}
</svg>"""


def schema_44() -> str:
    return f"""
<svg viewBox="0 0 480 250" role="img" aria-labelledby="s44t">
  <title id="s44t">Règle 44 : un tour complet compte un virement et un empannage.</title>
  <defs>
    <marker id="a44" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto">
      <path d="M0,0 L10,5 L0,10 z" fill="#e23a3e"/>
    </marker>
  </defs>
  <g fill="#8aa0b4" font-size="12.5" text-anchor="end">
    <text x="168" y="112">deux tours</text><text x="168" y="130">pour la partie 2</text>
    <text x="168" y="158">un seul tour</text><text x="168" y="176">pour la règle 31</text>
  </g>
  <circle cx="250" cy="128" r="70" fill="none" stroke="#8aa0b4" stroke-width="1.4"
          stroke-dasharray="7 6" opacity=".8"/>
  <path d="M250,58 A70,70 0 1,1 246,58" fill="none" stroke="#e23a3e" stroke-width="2.2"
        marker-end="url(#a44)"/>
  <text x="250" y="34" fill="#e23a3e" font-size="13" text-anchor="middle">virement</text>
  <text x="250" y="226" fill="#e23a3e" font-size="13" text-anchor="middle">empannage</text>

  {_bateau(322,128, 90, "#eef3f7", "#b9cad8", "#cfe0ee")}
  <text x="352" y="124" fill="#eef3f7" font-size="13">départ</text>
  <text x="352" y="142" fill="#8aa0b4" font-size="11.5">le bateau pénalisé</text>
</svg>"""


SCHEMAS = {
    "10": (schema_10(), "A, tribord amures, garde sa route ; B, bâbord amures, doit s'écarter — il vire "
                        "ou passe derrière. Personne n'est dispensé d'éviter l'abordage (règles 10 et 14)."),
    "18": (schema_18(), "A est à l'intérieur : B, à l'extérieur, doit lui laisser la place de passer la "
                        "marque. La zone se mesure à trois longueurs de coque, et c'est la situation au "
                        "moment où le premier bateau y entre qui compte."),
    "44": (schema_44(), "Un tour = un virement et un empannage, dans le même sens et sans s'arrêter. "
                        "Deux tours pour une règle de la partie 2, un seul pour avoir touché une marque."),
}

JS = """
document.querySelectorAll('.video').forEach(function(v){
  var b = v.querySelector('.lecture'); if(!b) return;
  b.addEventListener('click', function(){
    var f = document.createElement('iframe');
    f.src = 'https://www.youtube-nocookie.com/embed/' + v.dataset.video + '?autoplay=1&rel=0&modestbranding=1';
    f.title = b.getAttribute('aria-label') || 'Vidéo';
    f.allow = 'accelerometer; autoplay; encrypted-media; picture-in-picture; fullscreen';
    f.allowFullscreen = true;
    f.setAttribute('referrerpolicy', 'strict-origin-when-cross-origin');
    v.replaceChildren(f);
  });
});
"""


def page() -> str:
    d = R.charger()
    par_cle = {(r.get("num") or r["cle"]): r for r in d["regles"]}
    e = _e
    cartes = []
    for cle in ("10", "18", "44"):
        r = par_cle[cle]
        svg, legende = SCHEMAS[cle]
        ex = (r.get("exemples") or [{}])[0]
        bloc_ex = ""
        if ex.get("situation"):
            bloc_ex = (f'<details><summary>Exemple</summary><p>{e(ex["situation"]["fr"])}</p>'
                       f'<p><b>Issue :</b> {e(ex["issue"]["fr"])}</p></details>')
        cartes.append(
            f'<article class="regle" id="r{cle}">'
            f'<h3><span class="num">Règle {cle}</span>{e(r["titre"]["fr"])}</h3>'
            f'<p class="resume">{e(r["resume"]["fr"])}</p>'
            f"{carte_video(cle)}"
            f'<figure class="schema">{svg}<figcaption>{e(legende)}</figcaption></figure>'
            f"{bloc_ex}"
            "</article>")

    return (
        '<!doctype html>\n<html lang="fr"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        '<meta name="robots" content="noindex,nofollow">'
        "<title>Essai — vidéo et schéma sur trois règles — Sailing More</title>"
        "<style>" + R.CSS + CSS_EN_PLUS + "</style></head><body>"
        '<div class="page">'
        '<div class="haut"><a class="retour" href="regles-de-course.html">Règles de course</a></div>'
        "<h1>Essai : vidéo et schéma</h1>"
        '<p class="chapo">Trois règles, trois cartes complètes : le texte, une vidéo de moins de deux '
        "minutes, un schéma, un exemple. La vidéo ne se charge qu'au clic — avant, aucune requête ne part "
        "vers YouTube. Page d'essai, non indexée : elle ne remplace pas la page des règles.</p>"
        + "".join(cartes) +
        '<p class="note">Les vidéos appartiennent à leurs auteurs et restent chez YouTube : la page les '
        "affiche, elle ne les héberge pas. Elles expliquent la règle en anglais ; seule l'édition "
        "2025-2028 du texte officiel fait foi. Les schémas sont dessinés par Sailing More.</p>"
        "</div><script>" + JS + "</script></body></html>\n"
    )


def main() -> int:
    SITE.mkdir(parents=True, exist_ok=True)
    cible = SITE / "regles-video-test.html"
    cible.write_text(page(), encoding="utf-8")
    print(f"{cible} ({cible.stat().st_size} octets)")
    return len(VIDEOS)


if __name__ == "__main__":
    sys.exit(main())
