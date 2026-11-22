#!/usr/bin/env python3
"""Les quatre blocs « vitrine » de la page d'accueil : stories, reels, carte, kit.

Ce module ne fabrique que des morceaux : les vignettes (avec PIL et ffmpeg) et le HTML d'un bloc.
`accueil_site.py` l'appelle, garde la main sur les textes traduits et sur la publication.

D'où viennent les données — rien n'est saisi à la main :
  · stories : `cache/rhum/feuilles-hebergees.jsonl`, le journal écrit par `publier_feuilles.py`
    à chaque feuille poussée dans `/story/` du dépôt Pages. Le préfixe du dossier distant porte
    l'heure (`pub-story-2026-11-18-1702`), le dossier local non (`pub-story-2026-11-18`).
  · reels : `cache/rhum/file-videos.json`, filtré sur celles réellement publiées (`publiee` non nul),
    avec la durée lue dans le fichier et le compte crédité tel qu'il est noté.
  · pays : `cache/rhum/audience-pays.json` (relevé Instagram du jour).
"""
from __future__ import annotations

import json
import math
import os
import subprocess
import urllib.parse
from datetime import datetime
from pathlib import Path

from PIL import Image

RACINE = Path(os.environ.get("SITE_ROOT", "/opt/data"))
RHUM = RACINE / "cache" / "rhum"
JOURNAL_STORY = RHUM / "feuilles-hebergees.jsonl"
VIDEOS = RHUM / "file-videos.json"
MOIS_FR = {"01": "janvier", "02": "février", "03": "mars", "04": "avril", "05": "mai", "06": "juin",
           "07": "juillet", "08": "août", "09": "septembre", "10": "octobre", "11": "novembre",
           "12": "décembre"}
PAYS = RHUM / "audience-pays.json"
VILLES = RHUM / "villes-geo.json"
BOURSES = RACINE / "projets" / "sailingmore" / "bourses.json"

# Six premiers pays d'abonnés, positions réelles sur la projection équirectangulaire de la carte,
# et côté où poser l'étiquette : l'Europe est un peloton serré, quatre libellés au même endroit
# se chevauchent.
COORDONNEES = {
    "US": (37.0, -95.0, "bas"), "FR": (46.6, 2.4, "gauche"), "IT": (42.8, 12.5, "droite"),
    "ES": (40.4, -3.7, "bas"), "BR": (-10.0, -52.0, "bas"), "DE": (51.0, 10.4, "haut"),
    "GB": (54.0, -2.0, "gauche"), "CH": (46.8, 8.2, "haut"), "PT": (39.5, -8.0, "bas"),
    "CA": (56.0, -106.0, "bas"), "AU": (-25.0, 134.0, "bas"), "NL": (52.2, 5.3, "haut"),
}


def _duree(fichier: Path) -> float:
    try:
        r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                            "-of", "csv=p=0", str(fichier)], capture_output=True, text=True, timeout=30)
        return float(r.stdout.strip())
    except Exception:  # noqa: BLE001
        return 0.0


def _image_story(chemin_distant: str) -> Path | None:
    """Le fichier local d'une feuille poussée, ou None s'il a été rangé ailleurs."""
    morceaux = chemin_distant.split("/")
    if len(morceaux) < 3:
        return None
    dossier, nom = morceaux[1], morceaux[2]
    local = RHUM / dossier.rsplit("-", 1)[0] / nom
    if local.exists():
        return local
    autre = local.with_suffix(".png")
    return autre if autre.exists() else None


def tuiles_site(site: Path) -> list[dict]:
    """Les tuiles déjà écrites dans `<site>/stories/d-AAAA-MM-JJ.jpg`, la plus récente d'abord.

    Une tuile est une feuille du jour, posée par `site_story_du_jour.py` : un fichier présent a
    déjà été publié avec sa page `stories/<jour>.html`, donc il peut s'afficher ; un fichier absent
    n'efface rien. La bande de l'accueil montre ainsi toujours une story, même un jour sans lot.
    """
    dossier = site / "stories"
    if not dossier.exists():
        return []
    return [{"vignette": f"stories/{p.name}", "grand": f"stories/{p.name}",
             "jour": p.stem.replace("d-", ""), "lien": f"stories/{p.stem.replace('d-', '')}.html"}
            for p in sorted(dossier.glob("d-*.jpg"), reverse=True)]


def stories(site: Path, combien: int = 6) -> list[dict]:
    """Les dernières feuilles de stories, en vignette et en grand.

    La story de la veille ne s'affiche pas (Nicolas, 19/11/2026) : quand le dernier jour publié
    n'a aucune feuille — journée sans story — on remonte jusqu'au dernier jour qui en a une, et
    la bande commence là. Aucune journée vide au bout, aucune story d'hier.

    Depuis le 20/11/2026, les tuiles déjà posées par `site_story_du_jour.py` (`stories/d-<jour>.jpg`)
    passent en tête, la plus récente d'abord, et chacune ouvre sa page `stories/<jour>.html` :
    la story du soir arrive sur le site dès sa publication, sans attendre une reconstruction.
    """
    tuiles = tuiles_site(site)
    deja = {t["jour"] for t in tuiles}
    if not JOURNAL_STORY.exists():
        return tuiles[:combien]
    lignes = [json.loads(l) for l in JOURNAL_STORY.read_text(encoding="utf-8").splitlines() if l.strip()]

    def jour_de(ligne: dict) -> str:
        return ligne.get("chemin", "").split("/")[1].replace("pub-story-", "")[:10]

    (site / "stories").mkdir(parents=True, exist_ok=True)
    garde, vus = list(tuiles), set()
    for ligne in reversed(lignes):
        if len(garde) >= combien:
            break
        # Une seule vignette par journée : chaque jour a sa page (ou son lien Instagram), mais chaque
        # feuille d'un même lot n'a pas à occuper trois places de la bande (vu le 20/11 : cinq fois
        # « 18.11 » de suite à côté de la tuile du 19).
        if jour_de(ligne) in deja:
            continue
        chemin = ligne.get("chemin", "")
        if chemin in vus:
            continue
        vus.add(chemin)
        source = _image_story(chemin)
        if not source:
            continue
        try:
            im = Image.open(source).convert("RGB")
        except Exception:  # noqa: BLE001
            continue
        i = len(garde) + 1
        petit = im.copy()
        petit.thumbnail((320, 700), Image.LANCZOS)
        petit.save(site / "stories" / f"s{i}.jpg", quality=82, optimize=True)
        grand = im.copy()
        grand.thumbnail((720, 1500), Image.LANCZOS)
        grand.save(site / "stories" / f"g{i}.jpg", quality=80, optimize=True)
        jour = jour_de(ligne)
        deja.add(jour)
        garde.append({"vignette": f"stories/s{i}.jpg", "grand": f"stories/g{i}.jpg",
                      "jour": jour, "quand": ligne.get("quand", "")})
    # Le plus ancien des six à gauche, le plus récent à droite : on lit la semaine dans l'ordre du
    # calendrier. Les tuiles du jour, déjà en tête dans le bon ordre, ne se retournent pas.
    recentes = [x for x in garde if x not in tuiles]
    recentes.reverse()
    return (tuiles + recentes)[:combien]


def reels(site: Path, combien: int = 3) -> list[dict]:
    """Les derniers reels publiés, avec leur durée et le compte crédité."""
    if not VIDEOS.exists():
        return []
    donnees = json.loads(VIDEOS.read_text(encoding="utf-8"))
    liste = donnees.get("videos", donnees)
    publiees = [x for x in liste if x.get("publiee")]
    publiees.sort(key=lambda x: str(x["publiee"]), reverse=True)
    (site / "reels").mkdir(parents=True, exist_ok=True)
    garde = []
    for x in publiees:
        fichier = Path(x["fichier"]) if x.get("fichier") else None
        if not fichier or not fichier.exists():
            # Le fichier peut avoir été déposé sous un autre nom : on le retrouve par le nom du lot.
            for essai in (RHUM / "videos" / f"{x.get('nom')}-h264.mp4", RHUM / "videos" / f"{x.get('nom')}.mp4"):
                if essai.exists():
                    fichier = essai
                    break
        if not fichier or not fichier.exists():
            continue
        duree = _duree(fichier)
        if duree <= 0:
            continue
        brut = site / "reels" / f"t{x['id']}.png"
        # Une image à 40 % du reel : à une seconde, c'est souvent un fondu au blanc ou un carton.
        subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{duree * 0.4:.2f}", "-i", str(fichier),
                        "-frames:v", "1", "-y", str(brut)], capture_output=True, timeout=90)
        if not brut.exists():
            continue
        im = Image.open(brut).convert("RGB")
        l, h = im.size
        largeur = min(l, int(h * 9 / 16))
        hauteur = int(largeur * 16 / 9)
        gauche, haut = (l - largeur) // 2, (h - hauteur) // 2
        im = im.crop((gauche, haut, gauche + largeur, haut + hauteur)).resize((270, 480), Image.LANCZOS)
        im.save(site / "reels" / f"r{x['id']}.jpg", quality=82, optimize=True)
        brut.unlink(missing_ok=True)
        credit = (x.get("credits") or "").replace("Video:", "").strip()
        garde.append({"vignette": f"reels/r{x['id']}.jpg", "duree": duree, "credit": credit,
                      "lien": x.get("lien") or "", "nom": x.get("nom", "")})
    # Le plus ancien des six à gauche, le plus récent à droite : on lit la semaine dans l'ordre du
    # calendrier. Les tuiles du jour, déjà en tête dans le bon ordre, ne se retournent pas.
    recentes = [x for x in garde if x not in tuiles]
    recentes.reverse()
    return (tuiles + recentes)[:combien]


def villes(combien: int = 50) -> list[dict]:
    """Les premières villes d'abonnés de la page Facebook, positionnées sur la carte.

    Meta ne donne que les 45 premières villes : au-delà, la liste s'arrête. Le relevé et les
    coordonnées sont figés dans `villes-geo.json` (Nominatim, une requête par ville).
    """
    if not VILLES.exists():
        return []
    brut = json.loads(VILLES.read_text(encoding="utf-8"))
    brut = brut[:combien]
    if not brut:
        return []
    plus_grand = max(x["n"] for x in brut)
    for i, x in enumerate(brut):
        x["x"] = (x["lon"] + 180) / 360 * 100
        x["y"] = (90 - x["lat"]) / 180 * 100
        # la pastille grandit comme la racine du nombre : la surface reste proportionnelle
        # « mets en tout petit les villes » (Nicolas, 19/11/2026) : les bateaux des bourses doivent
        # dominer la carte, les villes ne sont qu'un fond. Le plus gros point fait 3,4 px, pas 6,4.
        x["r"] = round(0.6 + 1.1 * (x["n"] / plus_grand) ** 0.5, 2)
        x["rang"] = i + 1
    return brut


IG_PROFIL = "https://www.instagram.com/sailingmorehere/"


def html_stories(items: list[dict]) -> str:
    """Bande de stories : six feuilles en carrousel, de la plus ancienne (à gauche) à la plus récente."""
    if not items:
        return ""
    vignettes = "".join(
        f'<a class="vignette" href="{x.get("lien") or IG_PROFIL}" target="_blank" rel="noopener" '
        f'aria-label="Story du {x["jour"]} — {"ouvrir la story" if x.get("lien") else "voir sur notre Instagram"}">'
        f'<span class="anneau"><img src="{x["vignette"]}" alt="Story du {x["jour"]}"></span>'
        '</a>'
        for x in items)
    return ('<section class="stories"><h2 data-t="stories_titre">Nos informations quotidiennes</h2>'
            f'<div class="pelli">{vignettes}</div></section>'
            + ESQUIF)


# La bande de stories tenue en main, qui suit le doigt et la molette (Nicolas, 20/11/2026 : « il faut
# qu'on puisse slider à droite à gauche et que du coup ça les fait bouger »). Chaque vignette est
# inclinée selon sa distance au centre de la bande : dix degrés au bord, rien au milieu, jamais de
# secousse — la même formule que le tirage de site_story_du_jour, à l'écran au lieu du JPEG.
ESQUIF = """
<script>
(() => {
  const bande = document.querySelector('.pelli');
  if (!bande) return;
  const cartes = [...bande.querySelectorAll('.vignette')];
  const doit = matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (doit) return;
  let glisse = null, dernier = 0, vise = 0;
  const dessiner = () => {
    const milieu = bande.getBoundingClientRect();
    const axe = milieu.left + milieu.width / 2;
    const portee = Math.max(1, milieu.width / 2);
    cartes.forEach((c) => {
      const r = c.getBoundingClientRect();
      // position au repos : on retire l'inclinaison en cours pour ne pas la cumuler d'une image à l'autre
      const x = r.left + r.width / 2;
      const part = Math.max(-1, Math.min(1, (x - axe) / portee));
      c.style.transform = 'rotate(' + (part * 10).toFixed(2) + 'deg) translateY('
        + (Math.abs(part) * 7).toFixed(2) + '%)';
    });
  };
  bande.style.justifyContent = 'center';
  dessiner();
  addEventListener('resize', dessiner);
  bande.addEventListener('scroll', () => requestAnimationFrame(dessiner), {passive: true});
  // molette horizontale, et verticale quand la bande est déjà en vue
  bande.addEventListener('wheel', (e) => {
    const d = Math.abs(e.deltaX) > Math.abs(e.deltaY) ? e.deltaX : e.deltaY;
    if (!d) return;
    e.preventDefault();
    bande.scrollLeft += d;
  }, {passive: false});
  // glisser-saisir à la souris (au doigt, le navigateur le fait seul)
  bande.addEventListener('pointerdown', (e) => {
    if (e.pointerType === 'touch') return;
    glisse = {x: e.clientX, g: bande.scrollLeft};
    dernier = e.clientX; vise = 0;
    bande.classList.add('saisie');
    bande.setPointerCapture(e.pointerId);
  });
  bande.addEventListener('pointermove', (e) => {
    if (!glisse) return;
    const d = e.clientX - glisse.x;
    vise = (e.clientX - dernier) * 1.6;
    dernier = e.clientX;
    bande.scrollLeft = glisse.g - d;
    requestAnimationFrame(dessiner);
  });
  const lacher = () => { glisse = null; bande.classList.remove('saisie'); dessiner(); };
  bande.addEventListener('pointerup', lacher);
  bande.addEventListener('pointercancel', lacher);
  // les liens ne se déclenchent pas après un glissement
  bande.addEventListener('click', (e) => {
    if (Math.abs(vise) > 6) { e.preventDefault(); e.stopPropagation(); }
  }, true);
})();
</script>
"""


def html_reels(items: list[dict]) -> str:
    if not items:
        return ""
    cartes = []
    for x in items:
        duree = f"{x['duree']:.1f}".replace(".", ",") + " s"
        vignette = (f'<img src="{x["vignette"]}" alt="Reel {x["nom"]}">'
                    f'<span class="duree">{duree}</span>'
                    '<span class="ig" aria-hidden="true"><svg viewBox="0 0 24 24">'
                    '<rect x="2.6" y="2.6" width="18.8" height="18.8" rx="5.4" fill="none" stroke="#fff" stroke-width="1.9"/>'
                    '<circle cx="12" cy="12" r="4.3" fill="none" stroke="#fff" stroke-width="1.9"/>'
                    '<circle cx="17.4" cy="6.6" r="1.35" fill="#fff"/></svg></span>')
        if x["lien"]:
            cadre = f'<a class="reel" href="{x["lien"]}" target="_blank" rel="noopener">{vignette}</a>'
        else:
            cadre = (f'<a class="reel" href="{IG_PROFIL}" target="_blank" rel="noopener">'
                     f'{vignette}</a>')
        cartes.append(f'<figure class="carte-reel">{cadre}</figure>')
    return ('<section class="reels"><h2 data-t="reels_titre">Les trois derniers reels du blog</h2>'
            f'<div class="trois">{"".join(cartes)}</div></section>')


PAYS = {
    "Argentina": ("ARG", "Argentine"), "Australia": ("AUS", "Australie"),
    "Austria": ("AUT", "Autriche"), "Brazil": ("BRA", "Brésil"),
    "Bulgaria": ("BUL", "Bulgarie"), "Canada": ("CAN", "Canada"),
    "Chile": ("CHI", "Chili"), "Czech Republic": ("CZE", "Tchéquie"),
    "Egypt": ("EGY", "Égypte"), "France": ("FRA", "France"),
    "Germany": ("GER", "Allemagne"), "Greece": ("GRE", "Grèce"),
    "Hong Kong": ("HKG", "Hong Kong"), "Hungary": ("HUN", "Hongrie"),
    "Ireland": ("IRL", "Irlande"), "Italy": ("ITA", "Italie"),
    "Mexico": ("MEX", "Mexique"), "NY": ("US", "États-Unis"),
    "New Zealand": ("NZL", "Nouvelle-Zélande"), "Peru": ("PER", "Pérou"),
    "Poland": ("POL", "Pologne"), "Porto Alegre": ("BRA", "Brésil"),
    "Portugal": ("POR", "Portugal"), "Romania": ("ROM", "Roumanie"),
    "Russia": ("RUS", "Russie"), "South Africa": ("RSA", "Afrique du Sud"),
    "Spain": ("ESP", "Espagne"), "Sweden": ("SWE", "Suède"),
    "Thailand": ("THA", "Thaïlande"), "Turkey": ("TUR", "Turquie"),
    "UK": ("GBR", "Royaume-Uni"), "Ukraine": ("UKR", "Ukraine"),
}


def codes_drapeaux(items=None):
    """Les codes pays réellement présents sur la carte — pour ne générer que ceux-là."""
    items = villes() if items is None else items
    return sorted({PAYS.get(x.get("pays", ""), ("", x.get("pays", "")))[0]
                   for x in items} - {""})


CARTE_CSS = """
<style>
.planisphere .pt-v{position:absolute;transform:translate(-50%,-50%);background:none;border:0;
  padding:0;margin:0;width:26px;height:26px;display:flex;align-items:center;justify-content:center;
  cursor:pointer;border-radius:50%;line-height:0}
.planisphere .pt-v i{display:block;border-radius:50%;background:#e23a3e;transition:transform .18s}
.planisphere .pt-v:hover i,.planisphere .pt-v:focus-visible i{transform:scale(1.8)}
.planisphere .pt-v:focus-visible{outline:1px solid rgba(238,243,247,.7);outline-offset:4px}
.planisphere .pt-v[aria-pressed="true"] i{transform:scale(4.2);box-shadow:0 0 0 3px rgba(238,243,247,.3)}
.planisphere .pt-b.icone{width:20px;height:20px;border-radius:50%;overflow:hidden;
  box-shadow:0 0 0 1.5px rgba(238,243,247,.9),0 1px 4px rgba(0,0,0,.75)}
.planisphere .pt-b.icone img{width:100%;height:100%;object-fit:cover;display:block}
.planisphere .pt-b{position:absolute;transform:translate(-50%,-50%);width:22px;height:22px;
  display:block;line-height:0;filter:drop-shadow(0 1px 2px rgba(0,0,0,.7));transition:transform .18s;
  z-index:5;text-decoration:none}
.planisphere .pt-b svg{width:22px;height:22px;display:block}
.planisphere .pt-b.robot{border-radius:0;background:none;padding:0}
.planisphere .pt-b{z-index:7}   /* au-dessus des pastilles : un doigt sur le bateau ouvre le groupe */
@media(hover:none){.planisphere .pt-b{width:32px;height:32px}}
.planisphere .pt-b:hover,.planisphere .pt-b:focus-visible{transform:translate(-50%,-50%) scale(1.35)}
.legende-carte .hors-carte{display:block;margin-top:.35rem;color:var(--gris)}
.legende-carte .lien-hors-carte{color:var(--toile);text-decoration:underline;text-underline-offset:.18em}
.planisphere .pt-b:focus-visible{outline:1px solid rgba(238,243,247,.7);outline-offset:3px}
.planisphere .liens-bourses{position:absolute;inset:0;width:100%;height:100%;pointer-events:none;z-index:6}
.planisphere .liens-bourses .lien-fond{stroke:rgba(6,16,27,.75);stroke-width:3;fill:none;
  vector-effect:non-scaling-stroke}
.planisphere .liens-bourses .lien-trait{stroke:#f2f5f8;stroke-width:1.4;fill:none;
  stroke-dasharray:3.2 2.4;stroke-linecap:round;vector-effect:non-scaling-stroke}
.planisphere .liens-bourses circle{fill:#f2f5f8;stroke:#08131f;stroke-width:1;
  vector-effect:non-scaling-stroke}
.planisphere .encart-france{position:absolute;left:1.2%;bottom:3.2%;width:23%;min-width:126px;
  aspect-ratio:1000/662;background:#06121f;border:1px solid rgba(238,243,247,.22);border-radius:7px;
  overflow:hidden;z-index:8;box-shadow:0 6px 18px rgba(3,8,14,.45)}
.planisphere .encart-france .fond{position:absolute;inset:0;width:100%;height:100%}
.planisphere .encart-france .fond path{fill:#27576f;fill-opacity:.92;stroke:#5b8aa8;stroke-width:2.5;
  vector-effect:non-scaling-stroke;stroke-linejoin:round}
.planisphere .encart-france .pt-b{width:16px;height:16px;z-index:2}
.planisphere .encart-france .pt-b svg{width:16px;height:16px}
.planisphere .encart-france .pt-b:hover,.planisphere .encart-france .pt-b:focus-visible{
  transform:translate(-50%,-50%) scale(1.4)}
.planisphere .encart-france .titre-fr{position:absolute;right:6px;bottom:3px;font-size:8px;line-height:1;
  letter-spacing:.16em;text-transform:uppercase;color:#a9c2d6;opacity:.75}
@media(max-width:640px){.planisphere .encart-france{width:34%;min-width:104px}}
.planisphere .pt-b .bulle{position:absolute;left:50%;bottom:calc(100% + 11px);transform:translate(-50%,5px);
  display:grid;gap:2px;padding:7px 11px 8px;border-radius:10px;white-space:nowrap;
  line-height:1.25;
  background:linear-gradient(180deg,rgba(12,27,44,.97),rgba(7,17,29,.97));
  border:1px solid rgba(238,243,247,.14);border-top:2px solid #e23a3e;
  box-shadow:0 14px 30px -12px rgba(0,0,0,.95),inset 0 1px 0 rgba(255,255,255,.05);
  opacity:0;pointer-events:none;transition:opacity .15s ease,transform .15s ease}
.planisphere .pt-b .bulle::after{content:"";position:absolute;top:100%;left:50%;transform:translateX(-50%);
  border:5px solid transparent;border-top-color:rgba(7,17,29,.97)}
.planisphere .pt-b .bulle b{font-size:11px;font-weight:700;letter-spacing:.015em;color:#f2f5f8}
.planisphere .pt-b .bulle span.zone{font-size:9.5px;font-weight:600;letter-spacing:.13em;
  text-transform:uppercase;color:rgba(238,243,247,.5)}
.planisphere .pt-b .bulle i{font-style:normal;font-size:10px;font-weight:700;letter-spacing:.05em;
  color:#e23a3e;font-variant-numeric:tabular-nums}
.planisphere .pt-b:hover .bulle,.planisphere .pt-b:focus-visible .bulle{opacity:1;transform:translate(-50%,0)}
.planisphere .pt-b.bord-g .bulle{left:0;transform:translate(0,5px)}
.planisphere .pt-b.bord-g:hover .bulle,.planisphere .pt-b.bord-g:focus-visible .bulle{transform:translate(0,0)}
.planisphere .pt-b.bord-g .bulle::after{left:15px;transform:none}
.planisphere .pt-b.bord-d .bulle{left:auto;right:0;transform:translate(0,5px)}
.planisphere .pt-b.bord-d:hover .bulle,.planisphere .pt-b.bord-d:focus-visible .bulle{transform:translate(0,0)}
.planisphere .pt-b.bord-d .bulle::after{left:auto;right:15px;transform:none}
.planisphere .pt-b.bas .bulle{top:calc(100% + 11px);bottom:auto;transform:translate(-50%,-5px)}
.planisphere .pt-b.bas:hover .bulle,.planisphere .pt-b.bas:focus-visible .bulle{transform:translate(-50%,0)}
.planisphere .pt-b.bas .bulle::after{top:auto;bottom:100%;border-top-color:transparent;border-bottom-color:rgba(7,17,29,.97)}
.planisphere .pt-b.bas.bord-g .bulle{transform:translate(0,-5px)}
.planisphere .pt-b.bas.bord-g:hover .bulle,.planisphere .pt-b.bas.bord-g:focus-visible .bulle{transform:translate(0,0)}
.planisphere .pt-b.bas.bord-d .bulle{transform:translate(0,-5px)}
.planisphere .pt-b.bas.bord-d:hover .bulle,.planisphere .pt-b.bas.bord-d:focus-visible .bulle{transform:translate(0,0)}
.planisphere .pt-b.errant{transition:left 8s cubic-bezier(.45,.05,.55,.95),
  top 8s cubic-bezier(.45,.05,.55,.95),transform .18s ease}
.planisphere .pt-b.derive{transition:left 20s ease-in-out,top 20s ease-in-out,transform .18s ease}
/* La promenade d'un océan : un pas toutes les ~28 s et un glissement de 22 s — plus lent que le bateau
   qui fait le monde (8 s de glissement), pour qu'on voie qu'il se promène et non qu'il saute. */
/* Il bouge tout le temps, doucement : 22 s de glissement, et le pas suivant part aussitôt — plus de
   longue attente où le bateau semble posé (Nicolas, 19/11/2026). */
.planisphere .pt-b.promenade{transition:left 22s linear,top 22s linear,transform .18s ease}
/* Lui fait le monde : même avec ses points sûrs, il garde son allure de course. */
.planisphere .pt-b.promenade.vif{transition:left 9s linear,top 9s linear,transform .18s ease}
.planisphere .pt-b.errant.promenade{transition:left 8s cubic-bezier(.45,.05,.55,.95),top 8s cubic-bezier(.45,.05,.55,.95),transform .18s ease}
.legende-carte{display:flex;align-items:center;gap:9px;margin:16px 0 0;font-size:12px;
  letter-spacing:.04em;color:rgba(238,243,247,.62)}
.legende-carte .mini{flex:0 0 auto;line-height:0}
.legende-carte .mini svg{width:19px;height:19px;display:block}
.etiquette-v{position:absolute;z-index:4;display:flex;align-items:center;gap:8px;
  padding:6px 11px 6px 8px;background:#e23a3e;border:0;border-radius:0;
  color:#fff;font-size:12px;font-weight:700;letter-spacing:.1em;text-transform:uppercase;white-space:nowrap;
  transform:translate(-50%,calc(-100% - 10px));pointer-events:none}
.etiquette-v[hidden]{display:none}
.etiquette-v .drapeau{width:22px;height:auto;display:block;
  box-shadow:0 0 0 1px rgba(255,255,255,.5)}
.etiquette-v .nb{display:none}
@media(max-width:600px){.etiquette-v{font-size:11px;padding:5px 9px 5px 7px}}
</style>
"""

CARTE_JS = """
<script>
(function(){
  document.querySelectorAll('.planisphere').forEach(function(carte){
    var bulle = carte.querySelector('.etiquette-v');
    if(!bulle) return;
    var epingle = null;                     /* la pastille cliquée reste ouverte sous le curseur */
    function placer(b){
      var d = carte.getBoundingClientRect(), r = b.getBoundingClientRect();
      var x = r.left - d.left + r.width / 2;
      var y = r.top - d.top;
      var dr = bulle.querySelector('.drapeau');
      if(b.dataset.d){ dr.src = 'drapeaux/' + b.dataset.d + '.png'; dr.hidden = false; } else { dr.hidden = true; }
      bulle.querySelector('.nom').textContent = b.dataset.n || '';
      bulle.querySelector('.nb').textContent = '';   /* le nombre d'abonnés ne s'affiche pas (Nicolas, 19/11/2026) */
      bulle.hidden = false;
      var bas = y < 44;                      /* pastille trop haut : la bulle passe dessous */
      bulle.style.left = Math.min(Math.max(x, 52), d.width - 52) + 'px';
      bulle.style.top = y + 'px';
      bulle.style.transform = bas ? 'translate(-50%, 16px)' : 'translate(-50%, calc(-100% - 11px))';
    }
    function marquer(b){
      carte.querySelectorAll('.pt-v').forEach(function(o){ o.setAttribute('aria-pressed','false'); });
      if(b){ b.setAttribute('aria-pressed','true'); }
    }
    function fermer(){ bulle.hidden = true; epingle = null; marquer(null); }
    function ouvrir(b){ epingle = b; marquer(b); placer(b); }
    /* au survol et au focus, la ville se nomme sans s'épingler (Nicolas, 19/11/2026) */
    carte.querySelectorAll('.pt-v').forEach(function(b){
      b.addEventListener('mouseenter', function(){ if(!epingle){ placer(b); } });
      b.addEventListener('focus', function(){ if(!epingle){ placer(b); } });
      b.addEventListener('mouseleave', function(){ if(epingle){ placer(epingle); } else { bulle.hidden = true; } });
      b.addEventListener('blur', function(){ if(epingle){ placer(epingle); } else { bulle.hidden = true; } });
    });
    carte.addEventListener('click', function(e){
      /* les pastilles se touchent : c'est la plus proche du clic qui gagne, pas la plus haute */
      var b = null;
      if(e.detail === 0 && document.activeElement && document.activeElement.classList.contains('pt-v')){
        b = document.activeElement;                       /* au clavier, la pastille qui a le focus */
      } else {
        var d = carte.getBoundingClientRect();
        var px = e.clientX - d.left, py = e.clientY - d.top, bd = 1e9;
        carte.querySelectorAll('.pt-v').forEach(function(o){
          var r = o.getBoundingClientRect();
          var cx = r.left - d.left + r.width / 2, cy = r.top - d.top + r.height / 2;
          var dd = (cx - px) * (cx - px) + (cy - py) * (cy - py);
          if(dd < bd){ bd = dd; b = o; }
        });
        if(b && bd > 26 * 26){ b = null; }                 /* trop loin d'une pastille : on ferme */
      }
      if(!b){ fermer(); return; }
      if(b.getAttribute('aria-pressed') === 'true'){ fermer(); } else { ouvrir(b); }
    });
    carte.addEventListener('keydown', function(e){ if(e.key === 'Escape') fermer(); });
  });
  /* La bourse mondiale se promène : « c'est partout dans le monde, tu pourrais le faire bouger
     aléatoirement dans le monde ? » (Nicolas, 19/11/2026). Elle s'immobilise sous le curseur, sinon
     on ne peut ni la lire ni cliquer dessus, et elle ne bouge pas du tout si le visiteur a demandé
     moins d'animation. */
  if(!window.matchMedia('(prefers-reduced-motion: reduce)').matches){
    document.querySelectorAll('.planisphere .pt-b[data-errant],.planisphere .pt-b[data-derive],.planisphere .pt-b[data-pts]')
      .forEach(function(a){
      var errant = a.hasAttribute('data-errant');
      var bx = parseFloat(a.dataset.bx), by = parseFloat(a.dataset.by), amp = parseFloat(a.dataset.amp);
      /* Promenade : les points sont calculés sur la carte (promenade_oceans.py), tous au large.
         On les enchaîne — jamais de tirage au hasard, donc jamais de bateau sur la terre. */
      var pts = null;
      if(a.dataset.pts){ try { pts = JSON.parse(a.dataset.pts); } catch(e){ pts = null; } }
      var i = 0;
      if(pts && pts.length > 1){ a.style.left = pts[0][0] + '%'; a.style.top = pts[0][1] + '%'; }
      /* Sans promenade : l'ancien rythme. Avec : le bateau repart dès qu'il arrive, il ne s'arrête
         jamais — c'est le glissement de 30 s qui donne la lenteur, pas une pause. */
      /* Le pas suivant part quand le glissement s'achève : aucune halte, jamais de saut. Le rythme
         est donc celui de la transition — 30 s pour un bateau d'océan, 8 s pour celui du monde. */
      var vif = a.hasAttribute('data-vif');
      var pause = pts ? ((errant ? 8000 : (vif ? 9000 : 22000)) + 150) : (errant ? 9000 : 16000);
      var hasard = pts ? 300 : (errant ? 5000 : 8000);
      function ailleurs(){
        var x, y;
        if(pts && pts.length > 1){                    /* le point suivant de sa promenade */
          i = (i + 1) % pts.length;
          a.style.left = pts[i][0].toFixed(2) + '%';
          a.style.top = pts[i][1].toFixed(2) + '%';
          return;
        }
        if(errant){                                   /* n'importe où dans le monde */
          x = 6 + Math.random() * 88;
          y = 13 + Math.random() * 74;
        } else {                                      /* à petite distance de son large, pour rester dans l'eau */
          x = Math.min(94, Math.max(6, bx + (Math.random() * 2 - 1) * amp));
          y = Math.min(87, Math.max(13, by + (Math.random() * 2 - 1) * amp * 0.7));
        }
        a.style.left = x.toFixed(2) + '%';
        a.style.top = y.toFixed(2) + '%';
      }
      var t = setInterval(ailleurs, pause + Math.random() * hasard);
      /* Il part dès le chargement, pas quand on arrive sur la carte : au défilement, il est déjà en
         route (Nicolas, 19/11/2026 : « faut qu'il bouge avant que ça scroll dessus »). */
      if(pts){ setTimeout(ailleurs, 150); }
      /* Sur un téléphone il n'y a pas de survol : le bateau continuait de glisser pendant que le
         doigt descendait, et le clic tombait à côté. On l'immobilise au premier contact. */
      a.addEventListener('pointerdown', figer, {passive:true});
      a.addEventListener('touchstart', figer, {passive:true});
      /* On la fige là où elle est : sans ça elle finit son glissement pendant qu'on la vise. */
      function figer(){
        clearInterval(t);
        var r = a.getBoundingClientRect(), m = a.parentElement.getBoundingClientRect();
        a.style.transition = 'none';
        a.style.left = ((r.left - m.left + r.width / 2) / m.width * 100).toFixed(2) + '%';
        a.style.top = ((r.top - m.top + r.height / 2) / m.height * 100).toFixed(2) + '%';
        requestAnimationFrame(function(){ a.style.transition = ''; });
      }
      a.addEventListener('mouseenter', figer);
      a.addEventListener('mouseleave', function(){
        clearInterval(t); t = setInterval(ailleurs, pause + hasard / 2);
      });
      a.addEventListener('focus', function(){ clearInterval(t); });
    });
  }
  document.addEventListener('click', function(e){
    if(!e.target.closest('.planisphere')){
      document.querySelectorAll('.planisphere .etiquette-v').forEach(function(b){ b.hidden = true; });
    }
  });
})();
</script>
"""


def bourses() -> list[dict]:
    """Les bourses aux équipiers, placées par `scripts/bourses_carte.py`.

    Nicolas, 19/11/2026 : ce sont des groupes Facebook, et « quand c'est au nom d'un océan ou plan
    d'eau, mets-le au milieu de celui-ci ». Le fichier est vide tant qu'il n'a pas envoyé sa liste :
    la carte ne change pas d'un pixel.
    """
    try:
        return json.loads(BOURSES.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []


BATEAU_ROBOT = ('<svg viewBox="0 0 32 32" aria-hidden="true">'
               # Un drone de régate : coque large et blanche, flotteurs rouges, cabine ardoise,
               # un gros œil rouge et une aile rigide — la silhouette du jeu, montée comme une machine.
               '<g stroke="#08131f" stroke-width="1.2" stroke-linejoin="round">'
               '<path d="M.8 20.4h30.4L28 26.4H4z" fill="#f2f5f8"/>'
               '<path d="M.8 20.4h6.2l-1.6 6H2.2z" fill="#e23a3e"/>'
               '<path d="M25 20.4h6.2l-1.4 6h-3.2z" fill="#e23a3e"/>'
               '<path d="M11.2 20.4 13 12.6h6.6l1.8 7.8z" fill="#9db2c6"/>'
               '</g>'
               # l'aile rigide, rouge, à bord franc : la marque du jeu
               '<path d="M16.4 2.6 27 13.6h-10.6z" fill="#e23a3e" stroke="#08131f" stroke-width="1.2"/>'
               '<path d="M15.8 13.6V2.4" stroke="#08131f" stroke-width="1.8"/>'
               # l'œil et le radar : ce qui fait le robot
               '<circle cx="11.6" cy="17.2" r="1.7" fill="#e23a3e" stroke="#08131f" stroke-width=".9"/>'
               '<circle cx="11.6" cy="17.2" r=".6" fill="#08131f"/>'
               '<circle cx="15.6" cy="17.2" r="1.7" fill="#e23a3e" stroke="#08131f" stroke-width=".9"/>'
               '<circle cx="15.6" cy="17.2" r=".6" fill="#08131f"/>'
               '<path d="M15.8 2.4 18.6.9" stroke="#08131f" stroke-width="1.2"/>'
               '<circle cx="19.2" cy=".7" r="1.1" fill="#9db2c6" stroke="#08131f" stroke-width=".8"/>'
               '</svg>')
BATEAU = ('<svg viewBox="0 0 32 32" aria-hidden="true">'
          '<g stroke="#08131f" stroke-width="1" stroke-linejoin="round">'
          '<path d="M16.4 3.4v17.2h8.4z" fill="#f2f5f8"/>'
          '<path d="M14.2 8.4 7.4 20.6h6.8z" fill="#d9e0e7"/>'
          '<path d="M2.6 22.6h26.8l-4.1 5.8H6.7z" fill="#e23a3e"/>'
          '</g>'
          '<path d="M16 2.4v20.2" stroke="#08131f" stroke-width="1.5"/>'
          '</svg>')

# Un groupe de vente n'est pas un équipage : on ne cherche pas à embarquer, on vend du matériel ou
# un bateau, et ça s'expédie. Même coque que la charte, mais un colis arrimé sur le pont à la place
# des voiles (Nicolas, 22/11/2026 : « mets plutôt un logo d'un bateau qui transporte un colis »).
BATEAU_COLIS = ('<svg viewBox="0 0 32 32" aria-hidden="true">'
                '<path d="M16 3.4v8.2" stroke="#08131f" stroke-width="1.6" stroke-linecap="round"/>'
                '<g stroke="#08131f" stroke-width="1" stroke-linejoin="round">'
                '<path d="M2.6 22.6h26.8l-4.1 5.8H6.7z" fill="#e23a3e"/>'
                '<rect x="8.4" y="11.6" width="15.2" height="10.6" rx=".7" fill="#c8873f"/>'
                '<path d="M8.4 15.2h15.2" stroke-width=".8"/>'
                '</g>'
                '<path d="M14.9 11.6h2.4v10.6h-2.4z" fill="#f2f5f8"/>'
                '</svg>')

def _participants(n) -> str:
    """« ≈ 138 K », ou rien quand le nombre n'est pas connu (Facebook ne le donne pas).

    Nicolas, 19/11/2026 : « mets un ≈ à chaque fois car ça bouge » — le chiffre n'est jamais exact.
    Nicolas, 20/11/2026 : « on va faire un M pour millions et K pour les milliers » — sur la carte, où
    l'espace est compté, un groupé de 181 000 se lit « 181 K » et se pose en pastille ; « 181 000 »
    débordait du bateau.
    """
    try:
        v = int(n)
    except (TypeError, ValueError):
        return ""
    if v >= 1_000_000:
        return f"\u2248 {v / 1_000_000:.1f}".replace(".0", "").replace(".", ",") + " M "
    if v >= 1_000:
        return f"\u2248 {v / 1_000:.0f} K "
    return f"\u2248 {v} "


def _zone(b: dict) -> str:
    """La zone affichée, ou rien quand elle est déjà dans le nom du groupe.

    Nicolas, 19/11/2026 : « dans le nom tu mets bourse aux équipier france simplement » — un groupe qui
    s'appelle « Bourse aux équipiers France » n'a pas besoin qu'on répète « national » derrière. Une zone
    ne s'affiche que si elle apprend quelque chose : « Méditerranée », « Golfe de Gascogne », « La Rochelle ».
    """
    if b.get("jeu") or b.get("logo"):
        # un groupe de jeu n'a pas de zone : sa place sur la carte est symbolique, l'écrire serait un
        # mensonge (et « océan indien » n'était plus vrai depuis qu'il se promène partout, 19/11/2026).
        return ""
    zone = (b.get("ou") or "").strip()
    if zone.lower() in ("national", "toute la france", "france"):
        return ""
    if zone and zone.lower() in (b.get("groupe") or "").lower():
        return ""
    return zone


# Le tour de la France, tiré de Natural Earth (`assets/cartes/ne_110m_land.geojson`, domaine public)
# et projeté dans la boîte de l'encart : même projection que la carte du monde, un point tous les
# 7/1000 de largeur. Il voyage dans la page plutôt qu'en image — 13 Ko, et rien de plus à publier.
FRANCE_BOITE = (-5.8, 9.9, 41.0, 51.4)          # ouest, est, sud, nord
FRANCE_VUE = (1000, 662)
FRANCE_PATH = (
    'M956 649 994 694 985 778 956 774 930 795 906 778 904 702 889 665 924 668 956 649ZM978 589 957 638 928 625 914 '
    '582 926 558 968 534 978 589ZM178 -461 110 -392 175 -400 245 -400 228 -348 171 -291 237 -287 298 -205 342 -195 '
    '381 -123 399 -97 477 -85 469 -45 436 -26 462 7 404 40 319 40 211 57 181 45 139 75 80 67 35 92 1 79 95 12 152 -'
    '2 52 -12 34 -38 100 -57 66 -92 78 -133 172 -128 182 -165 138 -205 61 -216 46 -233 69 -262 48 -279 14 -249 10 -'
    '310 -22 -343 1 -409 50 -460 101 -455 178 -461ZM7183 -1628 7200 -1596 7258 -1612 7444 -1611 7588 -1580 7639 -15'
    '56 7623 -1523 7553 -1504 7385 -1469 7338 -1450 7417 -1441 7511 -1425 7568 -1437 7601 -1396 7629 -1413 7730 -14'
    '23 7935 -1412 7950 -1383 8217 -1373 8220 -1422 8355 -1411 8457 -1411 8560 -1377 8589 -1337 8552 -1310 8632 -12'
    '60 8732 -1234 8793 -1301 8895 -1272 9004 -1289 9127 -1270 9174 -1288 9278 -1279 9232 -1338 9316 -1365 9892 -13'
    '24 9946 -1286 10113 -1238 10370 -1250 10497 -1239 10550 -1213 10542 -1166 10620 -1148 10706 -1161 10819 -1163 '
    '10939 -1150 11060 -1157 11171 -1101 11249 -1121 11198 -1162 11226 -1190 11430 -1172 11562 -1176 11745 -1146 11'
    '834 -1118 11834 -864 11752 -836 11670 -841 11727 -807 11765 -754 11794 -737 11802 -711 11785 -694 11667 -708 1'
    '1488 -660 11432 -653 11334 -608 11242 -569 11219 -540 11127 -584 10961 -534 10932 -558 10871 -530 10786 -539 1'
    '0765 -497 10689 -436 10691 -410 10764 -396 10755 -303 10696 -301 10669 -247 10695 -220 10584 -187 10562 -115 1'
    '0467 -99 10448 -35 10356 25 10332 -19 10305 -112 10270 -253 10300 -342 10354 -380 10357 -409 10456 -424 10570 '
    '-504 10680 -569 10794 -620 10845 -710 10768 -704 10730 -652 10568 -582 10516 -660 10352 -639 10192 -532 10245 '
    '-493 10103 -476 10004 -470 10009 -516 9910 -526 9831 -494 9636 -505 9427 -486 9220 -362 8976 -212 9077 -204 91'
    '08 -164 9170 -150 9210 -182 9280 -178 9372 -108 9374 -53 9325 10 9319 86 9291 188 9195 280 9173 324 9087 398 9'
    '001 472 8960 509 8875 547 8835 548 8795 517 8709 563 8699 584 8675 581 8648 602 8629 624 8631 669 8598 684 858'
    '7 695 8563 714 8520 724 8493 741 8491 769 8483 776 8508 786 8545 814 8600 889 8615 930 8616 1004 8592 1039 853'
    '4 1051 8483 1077 8426 1083 8419 1048 8431 1000 8402 934 8450 923 8406 869 8375 857 8367 869 8349 874 8347 862 '
    '8330 856 8313 846 8330 818 8345 811 8340 799 8356 765 8352 754 8314 747 8284 730 8195 749 8149 778 8080 796 81'
    '14 766 8100 742 8151 699 8117 665 8062 688 7990 732 7951 773 7888 776 7856 806 7889 849 7941 860 7943 888 7994'
    ' 907 8065 861 8122 886 8163 888 8173 921 8083 939 8053 973 7991 1005 7959 1050 8027 1085 8052 1147 8091 1206 8'
    '134 1254 8133 1302 8093 1319 8109 1353 8146 1373 8136 1425 8120 1475 8084 1481 8038 1550 7986 1633 7927 1709 7'
    '840 1768 7751 1822 7679 1829 7640 1857 7618 1837 7582 1868 7493 1900 7426 1910 7404 1977 7369 1981 7352 1935 7'
    '367 1910 7282 1890 7252 1900 7167 1954 7113 2015 7099 2059 7148 2126 7208 2209 7266 2248 7304 2299 7333 2417 7'
    '325 2529 7272 2571 7199 2612 7147 2665 7067 2724 7044 2684 7062 2640 7015 2604 6962 2595 6936 2562 6904 2496 6'
    '846 2467 6792 2468 6801 2418 6745 2418 6740 2488 6706 2581 6685 2638 6689 2684 6731 2686 6757 2744 6768 2799 6'
    '804 2835 6842 2843 6875 2876 6890 2882 6927 2920 6954 2963 6958 3006 6951 3035 6957 3056 6962 3094 6984 3112 7'
    '009 3168 7008 3189 6963 3194 6903 3147 6827 3096 6820 3064 6783 3021 6774 2968 6751 2934 6758 2887 6744 2860 6'
    '719 2836 6708 2804 6674 2768 6644 2738 6633 2776 6621 2740 6628 2701 6647 2640 6641 2592 6660 2544 6639 2506 6'
    '644 2437 6618 2404 6597 2327 6586 2247 6558 2194 6516 2226 6444 2272 6408 2266 6369 2251 6391 2172 6377 2112 6'
    '327 2039 6335 2016 6298 2008 6253 1956 6235 1923 6231 1890 6219 1860 6192 1823 6134 1820 6139 1846 6119 1882 6'
    '092 1869 6083 1881 6065 1874 6040 1868 6031 1891 5988 1890 5909 1904 5913 1951 5879 1989 5787 2032 5716 2107 5'
    '668 2147 5605 2189 5605 2218 5573 2234 5515 2256 5486 2260 5467 2308 5480 2391 5483 2444 5456 2504 5456 2613 5'
    '423 2616 5394 2664 5413 2685 5355 2703 5334 2746 5308 2765 5248 2705 5218 2616 5194 2552 5172 2522 5138 2461 5'
    '122 2381 5111 2341 5053 2254 5027 2131 5008 2049 5008 1972 4996 1912 4903 1951 4858 1943 4775 1866 4805 1843 4'
    '787 1818 4712 1764 4665 1748 4646 1702 4597 1653 4480 1665 4376 1667 4286 1675 4167 1656 4097 1642 4025 1633 3'
    '998 1555 3968 1544 3919 1555 3854 1586 3777 1565 3712 1516 3651 1498 3608 1438 3561 1353 3527 1363 3487 1342 3'
    '463 1367 3425 1364 3438 1392 3433 1406 3453 1454 3478 1509 3510 1524 3520 1546 3564 1573 3568 1599 3561 1620 3'
    '569 1642 3588 1660 3596 1680 3606 1696 3602 1650 3619 1616 3636 1610 3655 1629 3656 1667 3643 1704 3655 1728 3'
    '666 1725 3668 1743 3718 1733 3771 1734 3809 1736 3853 1693 3901 1653 3941 1613 3959 1592 3967 1597 3961 1623 3'
    '953 1635 3962 1685 3990 1729 4026 1752 4072 1760 4110 1772 4139 1808 4156 1829 4179 1837 4179 1852 4156 1890 4'
    '145 1907 4119 1928 4095 1971 4066 1968 4053 1983 4042 2016 4050 2058 4044 2066 4015 2066 3975 2089 3969 2120 3'
    '954 2134 3915 2133 3890 2149 3890 2175 3859 2193 3824 2187 3782 2208 3752 2212 3706 2229 3694 2257 3692 2279 3'
    '629 2306 3527 2336 3470 2380 3442 2384 3423 2380 3386 2407 3345 2419 3292 2422 3275 2426 3262 2443 3245 2447 3'
    '235 2463 3203 2462 3183 2471 3139 2467 3122 2430 3124 2395 3114 2377 3101 2330 3083 2303 3096 2300 3089 2271 3'
    '097 2259 3094 2231 3086 2204 3067 2185 3062 2159 3029 2137 2995 2083 2977 2031 2933 1988 2905 1977 2862 1916 2'
    '855 1872 2858 1835 2821 1764 2791 1739 2757 1726 2736 1689 2739 1675 2722 1642 2703 1628 2678 1581 2640 1529 2'
    '607 1485 2575 1486 2585 1451 2588 1429 2596 1403 2594 1394 2576 1420 2562 1468 2545 1501 2530 1512 2509 1491 2'
    '480 1463 2435 1372 2428 1377 2454 1445 2494 1509 2542 1608 2565 1642 2586 1678 2643 1749 2630 1760 2632 1801 2'
    '706 1858 2718 1871 2738 1934 2724 1945 2733 2011 2757 2087 2781 2103 2816 2126 2853 2200 2870 2258 2905 2289 2'
    '992 2349 3028 2386 3062 2422 3082 2444 3113 2463 3129 2483 3127 2510 3090 2525 3118 2542 3138 2554 3151 2580 3'
    '179 2607 3211 2607 3271 2591 3340 2583 3397 2564 3428 2559 3451 2548 3487 2545 3508 2544 3537 2535 3571 2528 3'
    '601 2507 3625 2506 3626 2524 3620 2561 3621 2594 3607 2617 3589 2686 3559 2757 3519 2839 3465 2932 3410 3003 3'
    '335 3090 3272 3142 3176 3205 3117 3253 3047 3330 3033 3364 3018 3379 2974 3404 2958 3431 2934 3436 2925 3480 2'
    '904 3506 2892 3548 2866 3569 2837 3648 2841 3684 2882 3707 2883 3724 2866 3762 2870 3782 2865 3812 2888 3852 2'
    '914 3915 2937 3929 2948 3957 2945 4020 2953 4076 2955 4176 2967 4207 2948 4252 2923 4297 2882 4336 2824 4360 2'
    '752 4391 2680 4460 2656 4471 2611 4516 2585 4531 2580 4577 2610 4625 2623 4662 2623 4681 2635 4678 2633 4740 2'
    '622 4770 2637 4781 2628 4807 2601 4830 2549 4851 2472 4886 2444 4909 2450 4936 2466 4941 2461 4974 2445 5020 2'
    '437 5073 2421 5102 2377 5134 2365 5143 2338 5176 2320 5208 2284 5254 2212 5320 2167 5358 2119 5387 2052 5412 2'
    '020 5415 2012 5433 1973 5423 1941 5435 1872 5423 1834 5431 1807 5427 1742 5453 1687 5463 1648 5487 1619 5488 1'
    '592 5465 1570 5464 1543 5436 1540 5445 1531 5428 1532 5390 1511 5348 1532 5336 1530 5287 1488 5228 1456 5174 1'
    '411 5091 1363 5043 1338 4996 1324 4934 1308 4888 1287 4790 1286 4714 1278 4679 1253 4653 1220 4600 1186 4524 1'
    '173 4484 1121 4422 1117 4373 1111 4333 1120 4277 1142 4219 1145 4192 1166 4134 1181 4108 1217 4066 1238 4038 1'
    '245 3991 1241 3955 1222 3932 1205 3894 1190 3855 1193 3842 1213 3817 1193 3755 1180 3713 1148 3672 1154 3660 1'
    '145 3640 1128 3592 1076 3525 1011 3461 968 3408 930 3343 932 3321 946 3301 961 3255 974 3208 962 3198 984 3126'
    ' 993 3076 968 3034 939 3023 926 2995 910 2986 911 2968 845 2991 821 2988 796 3002 745 3000 711 2961 690 2915 6'
    '45 2873 597 2873 541 2873 488 2881 437 2894 337 2932 302 2954 244 2972 188 2954 159 2955 114 2942 73 2943 -2 2'
    '954 -46 2972 -109 2996 -122 2994 -138 2995 -204 2964 -262 2916 -316 2881 -359 2840 -376 2835 -422 2809 -455 27'
    '75 -466 2752 -474 2705 -502 2667 -527 2643 -543 2634 -559 2622 -566 2593 -576 2579 -594 2569 -628 2542 -655 25'
    '38 -670 2520 -669 2511 -689 2497 -693 2483 -703 2435 -695 2406 -721 2357 -753 2334 -725 2322 -694 2277 -679 22'
    '45 -685 2210 -667 2179 -659 2119 -666 2056 -674 2025 -667 1993 -684 1963 -717 1935 -715 1908 -712 1879 -687 18'
    '61 -666 1828 -670 1807 -649 1762 -613 1721 -592 1711 -575 1674 -573 1640 -550 1601 -508 1577 -468 1512 -434 14'
    '87 -375 1480 -325 1437 -293 1420 -240 1366 -256 1287 -232 1232 -223 1199 -182 1156 -118 1127 -71 1101 -28 1035'
    ' -8 996 39 996 77 1023 138 1018 204 1033 231 1033 292 998 361 987 402 961 463 942 571 930 676 925 708 935 768 '
    '910 836 909 862 924 906 920 975 894 1020 902 1018 934 1072 911 1076 923 1045 954 1044 984 1066 999 1058 1055 1'
    '016 1087 1028 1121 1061 1122 1077 1153 1101 1163 1176 1184 1203 1179 1256 1190 1340 1218 1370 1275 1427 1287 1'
    '517 1314 1585 1345 1616 1329 1647 1299 1632 1251 1652 1220 1698 1190 1742 1181 1828 1194 1849 1223 1873 1223 1'
    '893 1234 1957 1241 1972 1262 2057 1261 2118 1278 2182 1297 2211 1307 2260 1287 2286 1268 2342 1263 2388 1271 2'
    '405 1303 2420 1282 2471 1297 2521 1301 2552 1285 2570 1264 2583 1230 2596 1182 2605 1166 2629 1114 2661 1069 2'
    '656 1018 2672 992 2649 963 2673 939 2634 944 2581 930 2537 966 2440 973 2389 939 2320 937 2305 964 2261 971 22'
    '00 937 2130 938 2092 875 2046 840 2077 790 2036 760 2107 699 2205 696 2232 648 2353 656 2430 615 2504 597 2609'
    ' 596 2721 641 2812 665 2886 655 2941 661 3016 628 3026 601 3010 557 2973 534 2938 526 2914 507 2833 453 2760 4'
    '29 2705 392 2752 382 2805 328 2769 303 2863 277 2861 263 2804 274 2753 279 2711 299 2651 303 2596 326 2600 366'
    ' 2631 381 2696 377 2684 400 2614 411 2528 448 2492 435 2506 405 2437 387 2448 374 2509 353 2490 339 2391 323 2'
    '387 299 2328 307 2304 342 2255 389 2256 405 2226 419 2206 413 2188 490 2155 516 2132 562 2153 598 2160 622 221'
    '6 643 2204 659 2129 662 2101 682 2048 716 2028 686 2029 673 1990 671 1957 665 1880 682 1924 718 1892 728 1856 '
    '728 1823 695 1811 709 1825 747 1857 777 1833 791 1868 820 1900 839 1901 875 1842 858 1861 891 1820 897 1844 95'
    '3 1802 954 1750 926 1726 876 1715 833 1690 804 1657 768 1653 750 1642 745 1641 731 1605 710 1600 679 1605 636 '
    '1614 616 1603 606 1590 601 1572 580 1545 568 1485 544 1448 521 1390 502 1336 456 1349 451 1320 424 1319 403 12'
    '78 392 1258 420 1239 399 1241 377 1257 370 1206 360 1155 383 1158 415 1150 433 1171 465 1231 497 1263 550 1334'
    ' 601 1384 601 1399 615 1381 628 1439 651 1485 670 1540 703 1547 715 1535 738 1499 708 1444 697 1417 739 1463 7'
    '62 1456 795 1429 799 1395 854 1368 859 1369 839 1382 805 1395 792 1371 755 1351 723 1325 715 1306 687 1265 676'
    ' 1237 650 1190 646 1141 617 1082 576 1039 539 1019 476 987 469 936 448 906 456 869 486 843 491 785 526 660 509'
    ' 567 530 560 568 563 605 503 648 421 661 415 682 376 718 352 770 377 806 340 834 326 876 278 888 233 937 152 9'
    '38 91 937 51 960 27 984 -4 978 -28 957 -46 920 -105 910 -131 927 -165 918 -197 925 -188 875 -194 836 -222 830 '
    '-237 806 -232 764 -207 741 -202 716 -189 677 -190 650 -203 627 -206 606 -203 561 -229 533 -139 487 -61 499 25 '
    '498 92 509 145 506 248 508 281 470 293 343 228 276 181 244 83 219 77 173 160 159 266 175 246 103 306 131 455 8'
    '1 474 29 530 16 581 3 613 -14 669 -108 756 -134 809 -133 822 -146 875 -149 887 -135 930 -167 915 -191 913 -227'
    ' 887 -262 885 -327 895 -344 914 -363 970 -367 992 -385 1043 -403 1041 -370 1022 -349 1030 -332 1064 -322 1049 '
    '-298 1030 -305 984 -259 1001 -228 1003 -203 1067 -189 1066 -166 1131 -178 1167 -195 1239 -170 1269 -150 1312 -'
    '169 1412 -198 1492 -220 1555 -209 1560 -193 1622 -193 1636 -221 1724 -241 1711 -295 1713 -343 1744 -383 1804 -'
    '404 1855 -357 1906 -358 1918 -407 1925 -445 1902 -437 1862 -459 1856 -496 1937 -513 2017 -523 2086 -512 2152 -'
    '514 2224 -549 2157 -579 2042 -574 1930 -551 1826 -538 1789 -572 1728 -593 1742 -656 1711 -713 1741 -750 1799 -'
    '790 1945 -859 1987 -873 1981 -900 1892 -930 1782 -912 1721 -867 1731 -828 1629 -777 1506 -722 1460 -633 1505 -'
    '588 1566 -553 1508 -481 1441 -466 1417 -359 1381 -299 1304 -306 1268 -255 1194 -252 1174 -312 1120 -385 1072 -'
    '475 1029 -514 903 -440 818 -425 730 -458 708 -526 687 -673 746 -714 914 -767 1040 -833 1157 -922 1310 -1045 14'
    '16 -1093 1591 -1172 1731 -1200 1836 -1197 1933 -1250 2049 -1247 2163 -1259 2363 -1213 2281 -1196 2350 -1156 24'
    '16 -1178 2521 -1140 2695 -1124 2936 -1052 2985 -1022 2989 -980 2918 -946 2814 -929 2530 -978 2483 -970 2587 -9'
    '23 2595 -828 2677 -809 2727 -792 2735 -823 2695 -852 2737 -875 2891 -835 2945 -851 2902 -897 3051 -960 3109 -9'
    '56 3169 -934 3206 -977 3153 -1015 3184 -1054 3137 -1093 3315 -1073 3352 -1037 3271 -1029 3271 -994 3322 -972 3'
    '420 -986 3436 -1026 3569 -1057 3791 -1111 3839 -1108 3776 -1069 3855 -1063 3901 -1085 4020 -1086 4115 -1113 41'
    '87 -1074 4260 -1117 4193 -1153 4226 -1174 4414 -1155 4502 -1135 4733 -1063 4776 -1096 4711 -1129 4709 -1143 46'
    '32 -1149 4653 -1179 4619 -1229 4617 -1249 4735 -1307 4777 -1365 4824 -1377 4993 -1361 5006 -1325 4946 -1274 49'
    '85 -1253 5006 -1209 4991 -1122 5062 -1083 5034 -1040 4910 -950 4982 -940 5008 -963 5078 -980 5095 -1011 5150 -'
    '1041 5113 -1078 5142 -1120 5073 -1125 5057 -1160 5108 -1224 5026 -1276 5140 -1319 5125 -1364 5157 -1366 5190 -'
    '1330 5165 -1269 5233 -1257 5204 -1303 5311 -1328 5443 -1332 5561 -1295 5504 -1348 5498 -1416 5608 -1429 5761 -'
    '1426 5900 -1435 5848 -1468 5921 -1510 5995 -1511 6118 -1543 6287 -1551 6308 -1569 6475 -1575 6527 -1561 6670 -'
    '1594 6787 -1593 6805 -1621 6866 -1648 7016 -1674 7125 -1653 7039 -1638 7183 -1628Z'
)


def encart_france(items: list[dict] | None = None) -> str:
    """Le dézoom sur la France : six groupes y tiennent en trois pixels sur la carte du monde.

    Un encadré en bas à gauche reprend la France à sa vraie forme (`FRANCE_PATH`, Natural Earth
    projeté) et y pose les groupes français à leur point, écartés juste assez pour se lire.
    (Nicolas, 22/11/2026 : « tu pourrais pas faire un bout de carte qui zoom sur la France pour
    afficher tous les groupes en fr ? »)
    """
    items = bourses() if items is None else items
    lon0, lon1, lat0, lat1 = FRANCE_BOITE
    dedans = [b for b in items if b.get("lat") is not None and b.get("lon") is not None
              and lon0 <= float(b["lon"]) <= lon1 and lat0 <= float(b["lat"]) <= lat1
              and b.get("carte") is not False]
    if not dedans:
        return ""
    place: list[tuple[float, float]] = []
    marques = []
    for b in dedans:
        x = (float(b["lon"]) - lon0) / (lon1 - lon0) * 100
        y = (lat1 - float(b["lat"])) / (lat1 - lat0) * 100
        bx, by = x, y
        # même principe que la grande carte : le point exact d'abord, puis des anneaux serrés. Sur
        # 130 px de large, deux groupes à trois kilomètres l'un de l'autre se recouvrent.
        for r in (0.0, 10.0, 17.0, 24.0):
            libre = False
            for k in range(1 if not r else 12):
                a = math.radians(30 * k)
                cx = min(max(x + r * math.cos(a), 4.0), 96.0)
                cy = min(max(y + r * math.sin(a) * 0.66, 5.0), 95.0)
                if all((cx - px) ** 2 + (cy - py) ** 2 >= 14.0 ** 2 for px, py in place):
                    bx, by, libre = cx, cy, True
                    break
            if libre:
                break
        place.append((bx, by))
        icone = BATEAU_COLIS if b.get("colis") else BATEAU
        gens = _participants(b.get("membres"))
        titre = " — ".join(m for m in (b["groupe"], _zone(b), (gens + "participants") if gens else "") if m)
        mot = "groupe de vente" if b.get("colis") else "bourse aux équipiers"
        marques.append(
            f'<a class="pt-b" href="{b["lien"]}" target="_blank" rel="noopener" title="{titre}" '
            f'aria-label="{titre}, {mot}" style="left:{bx:.1f}%;top:{by:.1f}%">{icone}</a>')
    return ('<div class="encart-france" role="group" aria-label="Zoom sur la France">'
            f'<svg class="fond" viewBox="0 0 {FRANCE_VUE[0]} {FRANCE_VUE[1]}" '
            'preserveAspectRatio="none" aria-hidden="true">'
            f'<path d="{FRANCE_PATH}"/></svg>' + "".join(marques)
            + '<span class="titre-fr">France</span></div>')


def _espace(items: list[dict]) -> list[tuple[dict, float, float, float, float]]:
    """Écarte les bateaux qui se chevauchent, sans mentir sur leur position.

    Le Léman tient en 8 px sur une carte du monde : posé à sa vraie place, son bateau recouvre celui de
    France. Le bateau est donc décalé et relié à son point exact par un fin trait pointillé — le point
    reste juste, le bateau reste lisible. Unités : celles de la carte, 1000 × 500.

    Un bateau posé sur un port ou un pays (`port`, `vif`) ne bouge pas d'un pixel : c'est lui qui donne
    la géographie, et un trait de rappel s'y lisait comme une flèche vers la côte (Nicolas, 19/11/2026).
    Ce sont donc les autres qui s'écartent, par anneaux de plus en plus larges — une grille de neuf
    places ne suffisait pas à séparer six bourses entassées sur la France (22/11/2026).
    """
    MINIMUM, PRES, MIN_SERRE = 34.0, 17.0, 26.0
    RAYONS = (30.0, 42.0, 58.0, 76.0, 96.0)
    # Un port reste à sa place : il est la référence des autres.
    items = sorted(items, key=lambda b: 0 if (b.get("port") or b.get("vif")) else 1)
    place: list[tuple[float, float]] = []
    sortie = []
    for b in items:
        if b.get("x") is None or b.get("y") is None:
            continue
        px, py = float(b["x"]) * 10, float(b["y"]) * 5      # % → unités de carte
        px = min(max(px, 16.0), 984.0)
        ancre = bool(b.get("port") or b.get("vif"))
        serre = any((px - qx) ** 2 + (py - qy) ** 2 < PRES ** 2 for qx, qy in place)
        minimum = MIN_SERRE if serre else MINIMUM
        if ancre:
            candidats = [(0.0, 0.0)]
        else:
            candidats = [(0.0, 0.0)]
            for r in RAYONS:
                for k in range(12):
                    a = math.radians(30 * k)
                    candidats.append((round(r * math.cos(a), 2), round(r * math.sin(a), 2)))
        dx = dy = 0.0
        for ox, oy in candidats:
            # un bateau au bord de la carte (le pôle Nord) serait coupé par le cadre : on le rentre juste assez
            ty = min(max(py + oy, 16.0), 484.0)
            bx = min(max(px + ox, 16.0), 984.0)
            if all((bx - qx) ** 2 + (ty - qy) ** 2 >= minimum ** 2 for qx, qy in place):
                dx, dy = bx - px, ty - py
                break
        ty = min(max(py + dy, 16.0), 484.0)
        if not b.get("errant"):
            place.append((px + dx, ty))       # un bateau qui se promène ne réserve aucune place
        sortie.append((b, px, py, dx, ty))
    return sortie


def marques_bourses(items: list[dict] | None = None) -> str:
    """Un petit bateau par bourse, cliquable vers le groupe ; le nombre de participants au survol."""
    items = bourses() if items is None else items
    # Une bourse peut être retirée de la carte (Virtual Regatta, jeu en ligne sans mer) : elle garde
    # alors son lien dans la légende, sous la carte.
    items = [b for b in items if b.get("carte") is not False]
    sortie, liens = [], []
    for b, px, py, dx, ty in _espace(items):
        gens = _participants(b.get("membres"))
        mot = '<span data-t="bulle_participants">participants</span>' if gens else ""
        zone = _zone(b)
        titre = " — ".join(x.strip() for x in (b["groupe"], zone,
                                               (gens + "participants") if gens else "") if x)
        # la carte se lit au survol : le nom, la zone s'il y en a une, puis le nombre — jamais sur une
        # seule ligne (Nicolas, 19/11/2026 : « c'est dégueulasse le fond du titre, fais mieux »)
        morceaux = ['<b>' + b["groupe"] + '</b>']
        if zone:
            morceaux.append('<span class="zone">' + zone + '</span>')
        if gens:
            morceaux.append('<i>' + gens + mot + '</i>')
        bulle = '<span class="bulle">' + "".join(morceaux) + '</span>'

        # Un bateau écarté se dessine écarté : le décalage calculé par _espace() servait au trait mais
        # pas au bateau lui-même, si bien que deux bourses au même point restaient l'une sur l'autre
        # (Le Bon Coin Voile tombait exactement sur la bourse France, 22/11/2026).
        bx = min(max(px + dx, 16.0), 984.0)
        # Pas de trait de rappel pour une bourse posée sur un port ou un pays (Léman, Marseille,
        # France) : le trait se lisait comme une flèche vers la côte (Nicolas, 19/11/2026).
        if (abs(ty - py) > 0.5 or abs(dx) > 0.5) and not (b.get("vif") or b.get("port")):
            d = f"M{px:.1f} {py:.1f}L{bx:.1f} {ty:.1f}"
            # deux traits superposés : un fond sombre pour tenir sur la terre claire, puis le pointillé ivoire
            liens.append(f'<path class="lien-fond" d="{d}"/><path class="lien-trait" d="{d}"/>'
                         f'<circle cx="{px:.1f}" cy="{py:.1f}" r="3.4"/>')
        # un groupe de jeu porte son propre logo (« mets le logo de Virtual Regatta Inshore », 19/11/2026) ;
        # les autres gardent le bateau de la charte.
        if b.get("jeu"):
            # Virtual Regatta : plus l'icône de l'application mais un bateau de robot, celui d'une
            # régate sans équipage (Nicolas, 19/11/2026).
            icone, classe = BATEAU_ROBOT, "pt-b robot"
        elif b.get("logo"):
            icone = f'<img src="{b["logo"]}" alt="{b["groupe"]}" width="20" height="20" loading="lazy">'
            classe = "pt-b icone"
        elif b.get("colis"):
            # Un groupe de vente : la coque de la charte, un colis arrimé sur le pont à la place des voiles.
            icone, classe = BATEAU_COLIS, "pt-b"
        else:
            icone, classe = BATEAU, "pt-b"
        if px < 260:
            classe += " bord-g"          # près du bord gauche, l'infobulle s'aligne à gauche
        elif px > 740:
            classe += " bord-d"
        if ty < 170:
            classe += " bas"             # trop haut sur la carte : l'infobulle passe sous le bateau
        # Une bourse sans lieu fixe : « c'est partout dans le monde » (errant) ou « bouge doucement sur
        # l'océan » (dérive, Nicolas, 19/11/2026). Aucune des deux n'a de point ni de trait de rappel.
        anime = ""
        if b.get("errant"):
            classe += " errant"
            anime = ' data-errant="1"'
            # Son tour du monde est aussi fait de points d'eau : il ne traverse plus les continents.
            pts = b.get("promenade")
            if pts:
                classe += " promenade"
                anime += ' data-pts="' + json.dumps(pts, separators=(",", ":")) + '"'
        elif b.get("derive"):
            amp = float(b.get("amplitude") or 5.0)
            classe += " derive"
            anime = (f' data-derive="1" data-bx="{px / 10:.2f}" data-by="{ty / 5:.2f}" '
                     f'data-amp="{amp:.2f}"')
            # Des points d'eau sûrs, calculés par promenade_oceans.py : le bateau longe son océan
            # sans jamais toucher la terre (Nicolas, 19/11/2026).
            pts = b.get("promenade")
            if pts:
                classe += " promenade"
                anime += ' data-pts="' + json.dumps(pts, separators=(",", ":")) + '"'
        else:
            # Plan d'eau étroit (Léman, Marseille, côtes françaises) : un souffle de quelques pixels,
            # donc le repère n'est plus figé — calculé par promenade_oceans.py, jamais hors du bassin.
            pts = b.get("promenade")
            if pts:
                classe += " promenade" + (" vif" if b.get("vif") else "")
                anime = ' data-pts="' + json.dumps(pts, separators=(",", ":")) + '"'
                if b.get("vif"):
                    anime += ' data-vif="1"'
        type_mot = "groupe de vente" if b.get("colis") else "bourse aux équipiers"
        if anime:
            sortie.append(
                f'<a class="{classe}"{anime} href="{b["lien"]}" target="_blank" rel="noopener" '
                f'title="{titre}" aria-label="{titre}, {type_mot}" '
                f'style="left:{bx / 10:.2f}%;top:{ty / 5:.2f}%">{icone}{bulle}</a>')
            continue
        sortie.append(
            f'<a class="{classe}" href="{b["lien"]}" target="_blank" rel="noopener" title="{titre}" '
            f'aria-label="{titre}, {type_mot}" '
            f'style="left:{bx / 10:.2f}%;top:{ty / 5:.2f}%">{icone}{bulle}</a>')
    if liens:
        sortie.insert(0, '<svg class="liens-bourses" viewBox="0 0 1000 500" '
                         'preserveAspectRatio="none" aria-hidden="true">'
                         + "".join(liens) + "</svg>")
    return "".join(sortie)


def legende_bourses(items: list[dict] | None = None) -> str:
    """Aucune légende sous la carte (Nicolas, deux fois : 19/11 puis 20/11/2026 — « il y a juste la
    carte et puis il n'y a pas de légende en dessous qui parle de bourses aux équipiers »).

    La fonction reste parce que quatre points d'appel la citent, mais elle ne rend plus rien : ni la
    ligne « Bourses aux équipiers — un bateau par groupe », ni le « Hors carte » qui la suivait. Ce qui
    reste lisible, c'est la carte elle-même : chaque bateau porte son nom et son chiffre dans son
    `aria-label`, et le survol affiche le nombre de participants."""
    return ""


def html_carte(items: list[dict] | None = None) -> str:
    """La carte de nuit : une pastille par ville d'abonnés ; au clic, le drapeau et le nom."""
    items = villes() if items is None else items
    if not items:
        return ""
    def espaces(n: int) -> str:
        """Le même K/M que les grands chiffres (Nicolas, 20/11/2026) : « 2 460 » se lit « 2,5 K »,
        et la carte parle la même langue que le bloc « en chiffres » posé juste au-dessus."""
        v = float(n)
        if abs(v) < 1000:
            return f"{int(round(v)):,}".replace(",", "\u00a0")
        unite, part = ("M", 1_000_000) if abs(v) >= 1_000_000 else ("K", 1_000)
        val = v / part
        texte = f"{val:.1f}".rstrip("0").rstrip(".") if abs(val) < 10 else f"{val:.0f}"
        return texte.replace(".", ",") + "\u00a0" + unite
    points = []
    for x in items:
        iso, pays = PAYS.get(x.get("pays", ""), ("", x.get("pays", "")))
        points.append(
            f'<button class="pt-v" type="button" aria-pressed="false" '
            f'aria-label="{x["ville"]}, {pays} — {espaces(x["n"])} abonnés" '
            f'data-n="{x["ville"]}" data-d="{iso}" data-c="{espaces(x["n"])}" '
            f'style="left:{x["x"]:.2f}%;top:{x["y"]:.2f}%">'
            f'<i style="width:{max(1.8, x["r"]*2):.1f}px;height:{max(1.8, x["r"]*2):.1f}px"></i></button>')
    return ('<section class="monde"><h2 data-t="carte_titre">Nos concentrations de voileux</h2>'
            + CARTE_CSS +
            '<div class="planisphere"><img src="carte-monde.png" alt="Carte du monde">'
            + "".join(points)
            + marques_bourses()
            + encart_france()
            + '<div class="etiquette-v" hidden aria-live="polite">'
              '<img class="drapeau" alt="" width="22" height="15">'
              '<span class="nom"></span><span class="nb"></span></div>'
            '</div>'
            + legende_bourses()
            + '</section>'
            + CARTE_JS)


def formulaire_kit(adresse: str = "hello.sailingmore@gmail.com") -> str:
    """Le formulaire, seul — l'accueil et la page annonceurs partagent ce même bloc."""
    local, _, domaine = adresse.partition("@")
    return (f'<form class="kit-form" method="POST" action="https://formsubmit.co/{adresse}" '
            f'data-a="{local}" data-b="{domaine}">'
            '<input type="hidden" name="_subject" value="Demande de grille — Sailing More">'
            '<input type="hidden" name="_template" value="table">'
            '<input type="hidden" name="_captcha" value="false">'
            '<input type="hidden" name="_next" value="https://sailingmore.fr/merci.html">'
            '<input class="miel" type="text" name="_honey" tabindex="-1" autocomplete="off" aria-hidden="true">'
            '<label><span data-t="kit_nom">Votre nom</span>'
            '<input name="nom" required autocomplete="name"></label>'
            '<label><span data-t="kit_marque">Marque ou activité</span>'
            '<input name="marque" required autocomplete="organization"></label>'
            '<label><span data-t="kit_email">Email</span>'
            '<input name="email" type="email" required autocomplete="email" inputmode="email"></label>'
            '<button class="bouton" type="submit"><span data-t="kit_bouton">Recevoir la grille</span> <span class="fleche" aria-hidden="true">→</span></button>'
            '</form>'
            '<p class="kit-note" data-t="kit_note">Vos données servent seulement à vous répondre. '
            'Suppression sur demande.</p>'
            f'<p class="kit-ou"><span data-t="kit_ou">Ou écrivez à</span> '
            f'<a class="courriel" href="mailto:{adresse}" data-a="{local}" data-b="{domaine}" '
            f'data-t="kit_lien">notre adresse</a>.</p>'
            "<noscript><p class=\"kit-ou\">Sans JavaScript, écrivez à "
            "<a href=\"mailto:hello.sailingmore@gmail.com\">hello.sailingmore@gmail.com</a> — "
            "la grille part le jour même.</p></noscript>"
            "<script>(function(){"
            "document.querySelectorAll('form.kit-form').forEach(function(f){"
            "if(f.dataset.a&&f.dataset.b)f.action='https://formsubmit.co/'+f.dataset.a+'@'+f.dataset.b;});"
            "document.querySelectorAll('a.courriel').forEach(function(a){"
            "if(a.dataset.a&&a.dataset.b){var ad=a.dataset.a+'@'+a.dataset.b;"
            "a.href='mailto:'+ad;a.textContent=ad;a.removeAttribute('data-t');}"
            "});})();</script>")


PACKS = (
    ("p1_nom", "p1_ce", "440 €", "Essai une semaine", "2 publications · 1 concours", 2, 1, "7 j"),
    ("p2_nom", "p2_ce", "890 €", "Présence un mois", "4 publications · 2 concours", 4, 2, "30 j"),
    ("p3_nom", "p3_ce", "1 390 €", "Parité un mois", "5 publications · 2 concours", 5, 2, "30 j"),
    ("p4_nom", "p4_ce", "3 900 €", "Trimestre", "12 publications · 6 concours", 12, 6, "90 j"),
)
"""
Les quatre blocs de la grille (Nicolas, 20/11/2026, 21 h 40 : « 1 » — les quatre blocs aux prix du
document, le bloc à 500 € disparaît). Le bloc unique de lancement est donc retiré, pas complété :
`blocs-parite-2026-11-20.md` fait foi pour les prix et les contenus.

Le cinquième champ de chaque ligne est le texte français écrit dans la page, pour qu'elle reste lisible
quand le script de traduction ne tourne pas. Les mêmes contenus vivent dans `accueil_site.py` pour les
six langues, sous les clés `p1_nom` à `p4_ce`.
"""


def detail_packs(fr: dict | None = None) -> str:
    """Ce que chaque formule contient, ligne par ligne (Nicolas, 20/11/2026 : « détaillé plus »).

    Les quantités viennent de `PACKS` et du document `3-offre/blocs-parite-2026-11-20.md`. Les cellules
    qui ne dépendent d'aucune langue restent des nombres, un ✓ ou un tiret : seuls les intitulés de
    ligne passent par le dictionnaire (`d1` … `d8`, `d_legende`).
    """
    P, C, D = 5, 6, 7
    fr = fr or {}
    lignes = [
        ("d1", "Publications dédiées, Facebook et Instagram",
         [str(p[P]) for p in PACKS]),
        ("d2", "Jeux concours de 7 jours, avec votre lot et votre logo sur l'affiche",
         [str(p[C]) for p in PACKS]),
        ("d3", "Stories pour annoncer le concours", [str(p[C]) for p in PACKS]),
        ("d4", "Tirage au sort, et le gagnant annoncé", ["oui"] * 4),
        ("d5", "Rapport de portée sous 72 h, chiffres Meta", ["oui"] * 4),
        ("d6", "La mention « partenariat rémunéré »", ["oui"] * 4),
        ("d7", "Durée du pack", [p[D] for p in PACKS]),
        ("d8", "Une parution en plus, à l'unité", ["", "150 €", "200 €", ""]),
    ]
    tete = "".join(f'<th data-t="{p[0]}">{p[3]}</th>' for p in PACKS)
    corps = ""
    for cle, intitule, cellules in lignes:
        tds = ""
        for v in cellules:
            if v == "oui":
                tds += '<td class="det-oui">✓</td>'
            elif v == "":
                tds += '<td class="det-vide">—</td>'
            else:
                tds += f"<td>{v}</td>"
        corps += f'<tr><td class="det-intitule" data-t="{cle}">{intitule}</td>{tds}</tr>'
    return ('<details class="plis plis-detail"><summary data-t="det_titre">Le détail, formule par '
            'formule</summary>'
            '<table class="detail-packs"><thead><tr><th></th>' + tete + '</tr></thead>'
            '<tbody>' + corps + '</tbody></table>'
            '<p class="tarif-notes" data-t="d_legende">Une publication dédiée, c\'est un post '
            'Facebook et un post Instagram sur votre marque, avec votre visuel et le lien que vous '
            'voulez. Le concours met votre lot en jeu, sur une affiche qui porte votre logo. La coche '
            'veut dire que c\'est compris. Les images sont les nôtres ou les vôtres ; celle d\'un '
            'tiers, seulement avec son accord écrit. Et le lot du concours vient de vous.</p>'
            '</details>')


# Nicolas, 21/11/2026 : l'engagement six mois disparaît, et l'année passe de 8 900 à 6 000 €.
HORS_GRILLE = (
    ("h2_nom", "h2_ce", "6 000 €", "Douze mois",
     "l'année entière, concours et publications répartis"),
    ("h3_nom", "h3_ce", "sur devis", "Sur mesure",
     "un budget plus gros, ou un événement : on écrit la formule ensemble"),
    ("h4_nom", "h4_ce", "sur devis", "Sponsoring d'un format",
     "votre nom sur une série qu'on produit, avec nos images ou les vôtres"),
)
"""Au-delà de la grille (Nicolas, 20/11/2026 : « ou genre des partenaires de long terme ou sponsors ? »).

Les engagements 6 et 12 mois reprennent les prix déjà écrits dans `blocs-parite-2026-11-20.md` (4 700 €
et 8 900 €, inchangés) : on n'invente aucun tarif, et le sur-mesure reste « sur devis » plutôt que
chiffré au hasard. Le contenu exact d'un engagement se cale avec l'annonceur — la page le dit.
"""


def hors_grille(fr: dict | None = None) -> str:
    """La porte ouverte au-dessus des quatre formules : engagement long, sur-mesure, sponsoring."""
    lignes = "".join(
        f'<div class="tarif-ligne"><span class="tarif-nom" data-t="{kn}">'
        f'{(fr or {}).get(kn, fr_nom)}</span>'
        f'<span class="tarif-ce" data-t="{kc}">{(fr or {}).get(kc, fr_ce)}</span>'
        f'<span class="tarif-prix">{prix}</span></div>'
        for kn, kc, prix, fr_nom, fr_ce in HORS_GRILLE
    )
    fr = fr or {}
    return ('<h2 class="hors-titre" data-t="h_titre">'
            + fr.get("h_titre", "Au-delà des quatre formules") + '</h2>'
            '<p class="hors-intro" data-t="h_intro">'
            + fr.get("h_intro", "Plus gros budget, saison entière, ou votre nom sur une série.") +
            '</p>'
            '<div class="tarifs hors">' + lignes + '</div>'
            '<p class="tarif-notes" data-t="h_note">'
            + fr.get("h_note", "Prix avant signature. Prix HT.") + '</p>')


def tarifs(fr: dict | None = None) -> str:
    """La bande des prix : quatre formules, un filet rouge ouvert et refermé par un filet blanc."""
    lignes = "".join(
        f'<div class="tarif-ligne"><span class="tarif-nom" data-t="{cle_nom}">{fr_nom}</span>'
        f'<span class="tarif-ce" data-t="{cle_ce}">{fr_ce}</span>'
        f'<span class="tarif-prix">{prix}</span></div>'
        for cle_nom, cle_ce, prix, fr_nom, fr_ce, *_ in PACKS
    )
    return ('<div class="tarifs">'
            + lignes +
            '</div>'
            '<p class="tarif-notes" data-t="tarif_notes">Prix HT. Aucune portée garantie : on la '
            'mesure, et on l\'écrit avant de signer.</p>'
            + detail_packs(fr))


def html_kit(adresse: str = "hello.sailingmore@gmail.com", fr: dict | None = None) -> str:
    """Le bloc annonceurs de l'accueil : la promesse, les prix, puis le formulaire."""
    local, _, domaine = adresse.partition("@")
    return ('<section class="kit-bloc" id="annonceurs"><div class="carte-kit">'
            '<h3 data-t="kit_titre">Annonceurs</h3>'
            '<p data-t="kit_texte">Quatre formules, du test d\'une semaine au trimestre. Prix HT.</p>'
            '<p class="kit-preuve" data-t="kit_preuve">Ces chiffres viennent de Meta, relevés ce '
            'mois-ci.</p>'
            + tarifs(fr) +
            formulaire_kit(adresse) +
            '</div></section>')




def html_rappel_kit() -> str:
    """Le rappel du bas de page : une ligne qui remonte au formulaire, pas un second formulaire."""
    return ('<section class="kit-rappel"><a class="bouton" href="#annonceurs">'
            '<span data-t="kit_rappel">Annonceurs — recevoir la grille des tarifs</span> →</a></section>')


CSS = """
  .stories,.reels,.monde{max-width:62rem;margin:0 auto 6.5rem;padding:0 1.4rem}
  /* Nicolas, 20/11/2026 : « d'un coup il y a un grand espace, d'un coup moins ». Un seul rythme entre
     deux sections : 6,5 rem. Les vieilles surcharges de maquette (104 px → 5,5 rem, 88 px) sont
     neutralisées plus bas, pas ici, pour ne pas casser les peaux qui suivent. */
  .stories h2,.reels h2,.monde h2{white-space:nowrap;font-size:clamp(.98rem,3.05vw,1.62rem);
    letter-spacing:-.012em;margin:0 0 1.5rem;line-height:1.15;color:var(--toile);
    font-weight:700}
  .pelli{position:relative;height:clamp(22rem,52vw,30rem);
    display:flex;align-items:center;justify-content:center;overflow-x:auto;overflow-y:hidden;
    user-select:none;-webkit-user-select:none;
    padding:1.2rem .2rem 0;-webkit-overflow-scrolling:touch;scrollbar-width:none;
    scroll-snap-type:x proximity;cursor:grab}
  .pelli.saisie{cursor:grabbing;scroll-snap-type:none}
  .pelli::-webkit-scrollbar{display:none}
  .pelli>*{scroll-snap-align:center}
  /* Les stories tenues en éventail, comme un jeu de cartes (Nicolas, 20/11/2026). C'est la présentation
     de la bande sur le site, rien d'autre : ni les fiches publiées, ni leur ordre ne changent. Chaque
     vignette est inclinée depuis son bas (transform-origin) et décalée par son rang. */
  /* L'inclinaison n'est plus fixée par le rang : elle suit la main, calculée par ESQUIF ci-dessous.
     La règle de secours ci-dessous vaut quand le script ne tourne pas (JS coupé). */
  .pelli .vignette:nth-child(1){transform:rotate(-8deg) translate(-30%,7%)}
  .pelli .vignette:nth-child(2){transform:rotate(-4deg) translate(-15%,2%)}
  .pelli .vignette:nth-child(4){transform:rotate(4deg) translate(15%,2%)}
  .pelli .vignette:nth-child(5){transform:rotate(8deg) translate(30%,7%)}
  .pelli .vignette:nth-child(n+6){display:none}
  .vignette{flex:none;width:clamp(7.4rem,25vw,12rem);
    transform-origin:50% 100%;position:relative;text-decoration:none;
    transition:transform .22s ease}
  .vignette .anneau{display:block;padding:3px;border-radius:1.15rem;
    background:linear-gradient(150deg,#f9ce34,#ee2a7b 46%,#6228d7)}
  .vignette:hover{transform:rotate(0deg) translate(0,-6%);z-index:9}
  .vignette img{display:block;width:100%;height:auto;aspect-ratio:9/16;object-fit:cover;
    border-radius:.95rem;border:3px solid var(--nuit)}
  .trois{display:grid;grid-template-columns:repeat(3,1fr);gap:1.1rem}
  .carte-reel{margin:0}
  .carte-reel .ig{position:absolute;top:.5rem;left:.5rem;width:1.55rem;height:1.55rem;
    border-radius:50%;background:rgba(8,22,42,.66);display:flex;align-items:center;
    justify-content:center;pointer-events:none}
  .carte-reel .ig svg{width:1rem;height:1rem}
  .carte-reel .credit{margin-top:.4rem}
  .reel{position:relative;display:block;border-radius:.9rem;overflow:hidden;
    border:1px solid rgba(126,214,214,.22);background:#0a1a2e}
  .reel img{display:block;width:100%;height:auto}
  .duree{position:absolute;right:.5rem;bottom:.5rem;font-size:.72rem;font-weight:700;
    padding:.16rem .45rem;border-radius:.35rem;background:rgba(6,16,32,.82);color:var(--creme)}
  .credit{display:block;margin:.45rem 0 0;font-size:.74rem;letter-spacing:.04em;color:var(--gris)}
  .planisphere{position:relative;border-radius:1.1rem;overflow:hidden;
    border:1px solid rgba(126,214,214,.18);background:#08162a}
  .planisphere img{display:block;width:100%;height:auto;opacity:.92}
  .pt-v{position:absolute;transform:translate(-50%,-50%);display:block}
  .pt-v i{display:block;border-radius:50%;background:var(--eau);
    box-shadow:0 0 0 .18rem rgba(126,214,214,.16),0 0 12px 2px rgba(126,214,214,.45);
    opacity:.92}
  .pt-v:nth-child(-n+5) i{opacity:1;background:#a8ecec}
  .legende{margin:.85rem 0 0;text-align:center;font-size:.74rem;letter-spacing:.03em;
    color:#c3d6e6;line-height:1.6}
  .note{margin:.9rem 0 0;text-align:center;font-size:.78rem;color:var(--gris)}
  .kit-bloc{max-width:62rem;margin:0 auto 6.5rem;padding:0 1.4rem}
  .carte-kit{border:1px solid rgba(126,214,214,.28);border-radius:1.1rem;padding:2rem 1.7rem;
    background:radial-gradient(120% 150% at 15% 0%,rgba(126,214,214,.12),rgba(13,36,64,.55) 60%,rgba(8,22,42,.9));
    box-shadow:0 18px 40px -28px rgba(0,0,0,.9)}
  .carte-kit h3{margin:0 0 .5rem;font-size:clamp(1.25rem,2.6vw,1.7rem);letter-spacing:-.01em}
  .carte-kit p{margin:0 0 1.3rem;color:#cfe0ee;max-width:34rem}
  /* Le bouton du formulaire suit le style commun (`.bouton`) : filet rouge, capitales espacées, et le
     rouge qui monte au survol. Ne garder ici que la pose. */
  .carte-kit .bouton{padding:1rem 1.7rem;text-decoration:none}
  @media (max-width:900px){
    .vignette{width:clamp(6.6rem,24vw,8.6rem)}
    .pelli{height:clamp(15rem,54vw,18rem)}
    .pelli .vignette:nth-child(1){transform:rotate(-7deg) translate(-24%,7%)}
    .pelli .vignette:nth-child(2){transform:rotate(-3.5deg) translate(-12%,2%)}
    .pelli .vignette:nth-child(4){transform:rotate(3.5deg) translate(12%,2%)}
    .pelli .vignette:nth-child(5){transform:rotate(7deg) translate(24%,7%)}
    .pelli{justify-content:flex-start}
    .trois{grid-template-columns:repeat(3,1fr);gap:.6rem}
    .legende{font-size:.68rem}
  }

/* Le formulaire annonceurs (Nicolas, 19/11/2026) : trois champs, pas d'arrondi, le rouge au focus. */
.kit-form{display:grid;gap:.75rem;margin:1.6rem 0 1rem;max-width:30rem;text-align:left}
.kit-form label{display:grid;gap:.32rem}
.kit-form label span{font-size:.6rem;letter-spacing:.16em;text-transform:uppercase;
  color:rgba(238,241,244,.6);font-weight:500}
.kit-form input{background:rgba(7,28,49,.55);border:1px solid rgba(255,255,255,.22);color:#eef1f4;
  padding:.72rem .8rem;font:inherit;font-size:.9rem;border-radius:0;outline:none;width:100%}
.kit-form input:focus{border-color:#e23a3e;background:rgba(7,28,49,.85)}
.kit-form input.miel{position:absolute;left:-9999px;width:1px;height:1px;opacity:0;pointer-events:none}
/* Le bouton du formulaire ne redéfinit rien : il hérite de `.bouton` (rectangle à filet, rouge qui monte
   au survol). Seule la pose reste — c'est ici que le bouton était encore un aplat plein carré. */
.carte-kit .kit-form button{justify-self:start;margin-top:.5rem;cursor:pointer}
/* La bande des prix (Nicolas, 19/11/2026) : une bande, filet rouge dessus, filet blanc dessous. */
.tarifs{margin:1.6rem 0 .4rem;border-top:3px solid #e23a3e;border-bottom:1px solid rgba(255,255,255,.30)}
.tarif-ligne{display:grid;grid-template-columns:1fr auto;gap:.15rem 1.1rem;padding:.85rem 0;
  border-top:1px solid rgba(255,255,255,.10);text-align:left;align-items:baseline}
.tarif-ligne:first-child{border-top:0}
.tarif-nom{font-size:.94rem;font-weight:600;color:#fff}
.tarif-ce{grid-column:1;font-size:.74rem;color:rgba(238,241,244,.58);line-height:1.45}
.tarif-prix{grid-row:1 / span 2;grid-column:2;font-size:1.18rem;font-weight:300;
  color:#fff;font-variant-numeric:tabular-nums;white-space:nowrap}
.tarif-long .tarif-prix{font-size:1rem}
.tarif-notes{margin:1rem 0 0;font-size:.72rem;line-height:1.6;color:rgba(238,241,244,.55);text-align:left}
.detail-packs{width:100%;border-collapse:collapse;margin:1.5rem 0 0;font-size:.76rem;color:#fff}
.detail-packs th{padding:.5rem .35rem;font-size:.6rem;letter-spacing:.1em;text-transform:uppercase;
  color:#9db2c6;font-weight:400;text-align:center;line-height:1.3}
.detail-packs th:first-child{text-align:left}
.detail-packs td{padding:.62rem .35rem;border-top:1px solid rgba(255,255,255,.10);text-align:center;
  font-weight:300}
.detail-packs .det-intitule{text-align:left;color:rgba(238,241,244,.8);line-height:1.45;
  font-size:.74rem;padding-right:.8rem}
.detail-packs .det-oui{color:#e23a3e;font-weight:600}
.detail-packs .det-vide{color:rgba(238,241,244,.22)}
@media (max-width:520px){.detail-packs{font-size:.7rem}.detail-packs td{padding:.5rem .2rem}
  .detail-packs th{font-size:.55rem}.detail-packs .det-intitule{font-size:.68rem}}
.plis{margin:1.2rem 0 0;border-top:1px solid rgba(255,255,255,.14)}
.plis>summary{cursor:pointer;list-style:none;padding:.9rem 0;font-size:.7rem;letter-spacing:.14em;
  text-transform:uppercase;color:rgba(238,241,244,.72)}
.plis>summary::-webkit-details-marker{display:none}
.plis>summary::after{content:"+";float:right;color:#e23a3e;font-size:.9rem;letter-spacing:0}
.plis[open]>summary::after{content:"–"}
.plis>summary:hover{color:#fff}
.hors-titre{margin:2rem 0 .4rem;font-size:.9rem;letter-spacing:.14em;text-transform:uppercase;
  color:#fff;font-weight:400}
.hors-intro{margin:0;font-size:.78rem;line-height:1.6;color:rgba(238,241,244,.7)}
.tarifs.hors{border-bottom:0;margin-top:1.1rem}
.tarifs.hors .tarif-prix{font-size:1rem;color:#fff}
@media (max-width:520px){.tarif-prix{font-size:1.02rem}.tarif-long .tarif-prix{font-size:.9rem}}

.tarifs{margin:1.6rem 0 .4rem;border-top:3px solid #e23a3e;border-bottom:1px solid rgba(255,255,255,.30)}
.tarif-ligne{display:grid;grid-template-columns:1fr auto;gap:.15rem 1.1rem;padding:.85rem 0;
  border-top:1px solid rgba(255,255,255,.10);text-align:left;align-items:baseline}
.tarif-ligne:first-child{border-top:0}
.tarif-nom{font-size:.94rem;font-weight:600;color:#fff}
.tarif-ce{grid-column:1;font-size:.74rem;color:rgba(238,241,244,.58);line-height:1.45}
.tarif-prix{grid-row:1 / span 2;grid-column:2;font-size:1.18rem;font-weight:300;
  color:#fff;font-variant-numeric:tabular-nums;white-space:nowrap}
.tarif-long .tarif-prix{font-size:1rem}
.tarif-notes{margin:1rem 0 0;font-size:.72rem;line-height:1.6;color:rgba(238,241,244,.55);text-align:left}
.detail-packs{width:100%;border-collapse:collapse;margin:1.5rem 0 0;font-size:.76rem;color:#fff}
.detail-packs th{padding:.5rem .35rem;font-size:.6rem;letter-spacing:.1em;text-transform:uppercase;
  color:#9db2c6;font-weight:400;text-align:center;line-height:1.3}
.detail-packs th:first-child{text-align:left}
.detail-packs td{padding:.62rem .35rem;border-top:1px solid rgba(255,255,255,.10);text-align:center;
  font-weight:300}
.detail-packs .det-intitule{text-align:left;color:rgba(238,241,244,.8);line-height:1.45;
  font-size:.74rem;padding-right:.8rem}
.detail-packs .det-oui{color:#e23a3e;font-weight:600}
.detail-packs .det-vide{color:rgba(238,241,244,.22)}
@media (max-width:520px){.detail-packs{font-size:.7rem}.detail-packs td{padding:.5rem .2rem}
  .detail-packs th{font-size:.55rem}.detail-packs .det-intitule{font-size:.68rem}}
.plis{margin:1.2rem 0 0;border-top:1px solid rgba(255,255,255,.14)}
.plis>summary{cursor:pointer;list-style:none;padding:.9rem 0;font-size:.7rem;letter-spacing:.14em;
  text-transform:uppercase;color:rgba(238,241,244,.72)}
.plis>summary::-webkit-details-marker{display:none}
.plis>summary::after{content:"+";float:right;color:#e23a3e;font-size:.9rem;letter-spacing:0}
.plis[open]>summary::after{content:"–"}
.plis>summary:hover{color:#fff}
.hors-titre{margin:2rem 0 .4rem;font-size:.9rem;letter-spacing:.14em;text-transform:uppercase;
  color:#fff;font-weight:400}
.hors-intro{margin:0;font-size:.78rem;line-height:1.6;color:rgba(238,241,244,.7)}
.tarifs.hors{border-bottom:0;margin-top:1.1rem}
.tarifs.hors .tarif-prix{font-size:1rem;color:#fff}
@media (max-width:520px){.tarif-prix{font-size:1.02rem}.tarif-long .tarif-prix{font-size:.9rem}}

.carte-kit .kit-preuve{font-size:.86rem;color:rgba(238,241,244,.86);margin:.2rem 0 0}
.carte-kit .kit-note{font-size:.7rem;color:rgba(238,241,244,.52);margin:.2rem 0 0;line-height:1.55}
.carte-kit .kit-ou{font-size:.76rem;color:rgba(238,241,244,.6);margin:.9rem 0 0}
.kit-rappel{max-width:1180px;margin:0 auto;padding:0 1.4rem 4.5rem;text-align:left}
.kit-rappel .bouton{margin:0}

/* Le bouton du héros : le seul pas vers le formulaire depuis le haut de page (Nicolas, 19/11/2026). */
/* Nicolas, 20/11/2026 : les boutons passent au rectangle à filet — plus d'aplat plein, un trait rouge,
   un mot en capitales espacées, et le rouge qui monte du bas au survol. Cette règle ne garde que la
   pose du bouton dans le héros : couleur, bordure et rayon viennent de `.bouton` (accueil_site.py). */
.hero .bouton-hero{margin:5rem 0 0;text-decoration:none;pointer-events:auto}
@media(max-width:640px){.hero .bouton-hero{margin-top:2.6rem}}
"""
