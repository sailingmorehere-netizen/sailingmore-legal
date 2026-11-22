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
  aspect-ratio:1000/934;background:#06121f;border:1px solid rgba(238,243,247,.22);border-radius:7px;
  overflow:hidden;z-index:8;box-shadow:0 6px 18px rgba(3,8,14,.45)}
.planisphere .encart-france .fond{position:absolute;inset:0;width:100%;height:100%}
.planisphere .encart-france .fond path.cote{fill:none;stroke:#6fa8c8;stroke-width:6;stroke-linejoin:round;opacity:.55}
.planisphere .encart-france .fond path.terre{fill:none;stroke:#2f6d90;stroke-width:11;
  stroke-linecap:round;vector-effect:none;opacity:.9}
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
FRANCE_BOITE = (-12.0, 10.0, 40.5, 54.4)          # ouest, est, sud, nord
FRANCE_VUE = (1000, 934)
FRANCE_COTE = (
    'M964 886 991 934 985 1023 964 1019 946 1041 929 1023 927 942 916 904 941 907 964 886ZM980 823 965 875 944 861 '
    '934 816 943 791 972 765 980 823ZM237 144 156 183 92 173 129 103 105 35 167 -18 201 -49 239 -52 288 -10 264 36 '
    '271 84 237 144ZM1122 -81 1095 -27 1047 -65 1041 -93 1108 -115 1122 -81ZM409 -285 360 -212 407 -221 456 -221 44'
    '5 -166 404 -106 451 -101 495 -15 526 -4 554 72 567 99 622 112 616 155 593 174 611 209 570 244 510 244 432 262 '
    '411 249 381 280 339 273 307 298 283 285 350 214 390 200 319 189 306 162 354 141 329 105 337 61 405 67 412 28 3'
    '80 -14 325 -26 314 -44 331 -74 316 -93 292 -61 289 -126 266 -160 282 -230 318 -284 354 -279 409 -285ZM5408 -15'
    '17 5420 -1484 5462 -1500 5594 -1499 5697 -1466 5733 -1441 5722 -1406 5672 -1386 5552 -1349 5518 -1329 5575 -13'
    '20 5642 -1303 5683 -1315 5706 -1272 5726 -1290 5799 -1300 5944 -1289 5955 -1258 6145 -1248 6148 -1299 6245 -12'
    '87 6317 -1288 6391 -1252 6411 -1209 6385 -1181 6442 -1128 6513 -1101 6557 -1172 6630 -1141 6707 -1159 6795 -11'
    '39 6829 -1158 6903 -1148 6870 -1211 6930 -1240 7341 -1196 7380 -1156 7499 -1105 7682 -1118 7773 -1106 7810 -10'
    '79 7805 -1030 7861 -1010 7922 -1024 8002 -1026 8088 -1013 8174 -1020 8254 -960 8310 -982 8273 -1025 8293 -1055'
    ' 8438 -1036 8533 -1040 8664 -1008 8727 -979 8727 -711 8669 -681 8610 -686 8651 -650 8678 -595 8699 -577 8704 -'
    '549 8692 -531 8607 -546 8480 -495 8440 -487 8370 -440 8304 -399 8288 -368 8223 -415 8104 -362 8084 -387 8040 -'
    '358 7979 -367 7964 -323 7910 -258 7912 -231 7963 -216 7957 -118 7915 -116 7896 -60 7914 -31 7835 4 7819 80 775'
    '1 97 7738 165 7672 228 7655 181 7636 83 7611 -66 7632 -159 7671 -199 7673 -231 7744 -246 7825 -330 7903 -399 7'
    '985 -453 8022 -548 7966 -542 7939 -487 7824 -413 7786 -495 7669 -473 7555 -360 7593 -319 7491 -301 7421 -294 7'
    '424 -343 7354 -353 7297 -320 7159 -332 7009 -312 6862 -181 6688 -22 6759 -14 6782 28 6826 43 6855 10 6905 14 6'
    '970 88 6972 145 6936 212 6932 293 6912 400 6843 497 6828 544 6766 622 6705 700 6676 739 6615 779 6587 780 6558'
    ' 747 6497 796 6490 818 6473 814 6453 837 6439 860 6441 908 6418 923 6410 935 6392 955 6362 966 6342 984 6341 1'
    '013 6354 1031 6380 1061 6419 1140 6430 1184 6430 1261 6413 1298 6372 1311 6336 1339 6295 1345 6290 1308 6298 1'
    '258 6278 1188 6312 1176 6281 1119 6259 1106 6253 1119 6240 1124 6238 1112 6226 1105 6214 1095 6227 1065 6237 1'
    '057 6233 1045 6245 1009 6215 990 6194 972 6130 992 6097 1023 6048 1042 6072 1011 6063 984 6099 939 6075 904 60'
    '35 928 5984 974 5956 1018 5911 1021 5888 1052 5912 1098 5949 1109 5951 1139 5986 1159 6037 1111 6078 1137 6107'
    ' 1139 6115 1174 6050 1193 6029 1229 5985 1263 5961 1310 6010 1347 6028 1413 6056 1474 6087 1526 6086 1576 6057'
    ' 1594 6068 1630 6095 1651 6088 1706 6077 1759 6051 1765 6018 1838 5981 1926 5939 2006 5876 2068 5813 2124 5762'
    ' 2132 5734 2162 5718 2140 5693 2174 5629 2207 5581 2218 5566 2289 5540 2293 5529 2244 5539 2218 5478 2196 5457'
    ' 2207 5396 2265 5358 2328 5348 2375 5383 2446 5426 2533 5467 2575 5494 2629 5515 2753 5509 2871 5471 2916 5419'
    ' 2959 5382 3015 5325 3078 5309 3034 5322 2989 5288 2951 5250 2941 5231 2906 5208 2836 5168 2806 5129 2807 5135'
    ' 2754 5095 2754 5092 2828 5067 2927 5052 2986 5056 3035 5085 3037 5104 3098 5112 3156 5137 3195 5165 3202 5188'
    ' 3237 5199 3244 5226 3284 5245 3329 5247 3374 5242 3405 5247 3428 5250 3468 5266 3486 5284 3546 5283 3568 5251'
    ' 3573 5208 3523 5154 3470 5149 3436 5123 3391 5116 3335 5100 3298 5105 3249 5095 3221 5077 3195 5069 3162 5045'
    ' 3124 5023 3092 5015 3132 5007 3094 5012 3052 5025 2988 5021 2938 5035 2887 5019 2847 5023 2774 5005 2739 4990'
    ' 2658 4982 2573 4962 2518 4932 2552 4880 2599 4855 2593 4827 2578 4842 2494 4833 2432 4797 2354 4803 2330 4776'
    ' 2321 4744 2266 4731 2231 4728 2197 4720 2165 4701 2126 4659 2123 4663 2151 4649 2188 4629 2174 4623 2187 4610'
    ' 2179 4592 2173 4586 2198 4555 2197 4499 2211 4502 2262 4477 2301 4412 2347 4361 2426 4327 2468 4281 2512 4281'
    ' 2543 4259 2559 4218 2583 4197 2587 4183 2638 4192 2726 4195 2781 4176 2845 4175 2959 4152 2963 4131 3014 4145'
    ' 3036 4104 3055 4088 3101 4070 3120 4027 3057 4006 2963 3988 2896 3973 2864 3948 2799 3937 2715 3929 2673 3888'
    ' 2581 3869 2451 3855 2365 3856 2283 3847 2220 3781 2261 3749 2253 3689 2171 3711 2147 3698 2120 3644 2063 3611'
    ' 2046 3598 1998 3562 1947 3479 1960 3405 1961 3341 1970 3255 1950 3206 1935 3154 1926 3135 1843 3113 1831 3078'
    ' 1843 3033 1876 2977 1854 2931 1802 2887 1783 2857 1719 2823 1630 2799 1640 2770 1618 2753 1644 2726 1641 2736'
    ' 1671 2732 1686 2746 1737 2764 1795 2786 1810 2794 1834 2825 1862 2828 1890 2823 1912 2829 1935 2842 1953 2848'
    ' 1976 2855 1992 2852 1943 2864 1908 2877 1901 2890 1922 2891 1961 2881 2001 2890 2026 2900 2041 2935 2031 2973'
    ' 2033 3000 2035 3032 1989 3065 1946 3094 1905 3107 1882 3109 1915 3103 1927 3109 1981 3129 2026 3155 2051 3188'
    ' 2060 3215 2072 3235 2110 3248 2133 3264 2141 3264 2156 3247 2196 3240 2215 3221 2237 3204 2283 3183 2279 3174'
    ' 2295 3167 2329 3172 2374 3147 2382 3119 2407 3114 2440 3104 2454 3076 2454 3058 2471 3058 2498 3036 2516 3011'
    ' 2510 2980 2533 2959 2537 2927 2555 2918 2584 2917 2607 2871 2636 2799 2667 2758 2714 2738 2718 2724 2714 2698'
    ' 2742 2669 2755 2631 2758 2619 2762 2609 2780 2597 2785 2590 2802 2568 2801 2553 2810 2522 2806 2510 2767 2511'
    ' 2730 2504 2710 2495 2661 2482 2633 2486 2599 2492 2586 2490 2557 2484 2528 2470 2508 2467 2481 2443 2457 2419'
    ' 2401 2406 2346 2375 2300 2355 2289 2325 2225 2319 2178 2321 2138 2295 2064 2274 2037 2249 2024 2234 1985 2237'
    ' 1970 2224 1935 2211 1920 2193 1870 2165 1816 2142 1770 2120 1770 2127 1733 2129 1710 2134 1683 2120 1700 2110'
    ' 1751 2098 1786 2087 1798 2072 1776 2052 1746 2019 1650 2033 1727 2061 1794 2096 1899 2112 1935 2127 1973 2168'
    ' 2048 2159 2059 2160 2103 2213 2163 2221 2177 2236 2243 2226 2255 2232 2324 2249 2405 2266 2421 2291 2446 2318'
    ' 2524 2330 2585 2355 2618 2417 2682 2442 2720 2467 2759 2481 2782 2504 2802 2514 2823 2513 2851 2487 2867 2507'
    ' 2885 2521 2898 2530 2925 2551 2953 2573 2954 2616 2937 2666 2929 2706 2908 2728 2903 2744 2891 2770 2889 2785'
    ' 2887 2806 2877 2830 2871 2851 2848 2869 2847 2870 2866 2866 2905 2866 2940 2856 2965 2843 3037 2821 3112 2793'
    ' 3198 2754 3297 2715 3372 2662 3464 2617 3518 2549 3585 2506 3636 2456 3717 2446 3753 2436 3768 2404 3795 2393'
    ' 3823 2376 3828 2369 3876 2355 3903 2346 3947 2327 3970 2306 4052 2309 4090 2338 4115 2340 4132 2327 4173 2330'
    ' 4193 2327 4226 2343 4268 2361 4334 2378 4349 2385 4379 2384 4446 2389 4505 2391 4610 2399 4643 2385 4691 2368'
    ' 4737 2339 4779 2297 4804 2246 4837 2195 4909 2177 4921 2145 4969 2127 4985 2123 5033 2144 5084 2153 5123 2154'
    ' 5143 2161 5206 2153 5237 2164 5248 2157 5276 2138 5300 2101 5323 2046 5359 2026 5384 2030 5412 2042 5417 2038'
    ' 5452 2026 5501 2021 5557 2009 5587 1978 5621 1969 5631 1950 5665 1937 5700 1912 5748 1860 5817 1828 5857 1794'
    ' 5888 1746 5914 1723 5918 1717 5936 1690 5926 1667 5939 1618 5926 1590 5934 1572 5931 1525 5957 1486 5968 1458'
    ' 5993 1437 5995 1418 5971 1403 5970 1383 5940 1375 5892 1360 5847 1375 5834 1374 5783 1344 5720 1321 5663 1288'
    ' 5576 1255 5525 1237 5476 1227 5410 1216 5362 1200 5258 1199 5178 1194 5141 1176 5113 1152 5058 1128 4977 1119'
    ' 4935 1082 4870 1079 4818 1075 4776 1081 4717 1097 4655 1099 4626 1114 4566 1124 4538 1151 4494 1165 4464 1170'
    ' 4415 1168 4376 1154 4352 1142 4312 1131 4271 1133 4257 1147 4231 1133 4166 1124 4121 1101 4078 1106 4065 1099'
    ' 4044 1087 3994 1050 3923 1003 3855 973 3799 945 3730 947 3708 957 3686 968 3637 977 3587 968 3577 984 3502 99'
    '1 3449 973 3404 952 3393 943 3363 931 3353 932 3335 885 3359 867 3355 850 3370 814 3369 789 3327 774 3278 742 '
    '3234 708 3235 668 3235 630 3243 594 3257 522 3296 497 3319 456 3339 416 3320 395 3320 363 3307 334 3308 280 33'
    '20 249 3339 204 3364 183 3363 136 3331 95 3280 56 3243 26 3199 13 3194 -19 3167 -43 3131 -51 3107 -57 3057 -77'
    ' 3017 -94 2991 -106 2982 -117 2969 -122 2939 -129 2925 -142 2914 -167 2885 -186 2881 -196 2862 -210 2838 -213 '
    '2823 -220 2772 -214 2742 -233 2690 -256 2666 -236 2653 -214 2606 -203 2571 -207 2535 -194 2502 -188 2439 -193 '
    '2372 -199 2339 -194 2305 -206 2273 -230 2244 -228 2216 -226 2185 -209 2166 -194 2131 -197 2109 -181 2061 -156 '
    '2019 -140 2008 -128 1969 -127 1933 -111 1891 -81 1867 -52 1798 -28 1771 14 1764 50 1718 73 1700 111 1644 99 15'
    '60 117 1503 123 1467 152 1422 198 1391 231 1363 262 1294 276 1252 309 1253 337 1281 380 1277 427 1292 447 1292'
    ' 491 1256 540 1244 568 1216 612 1196 689 1184 764 1178 787 1188 830 1162 879 1161 897 1177 928 1173 978 1146 1'
    '010 1154 1008 1188 1047 1163 1050 1176 1027 1209 1027 1240 1043 1257 1037 1315 1007 1349 1015 1385 1039 1386 1'
    '050 1418 1068 1429 1121 1452 1140 1446 1178 1457 1238 1487 1260 1547 1301 1560 1365 1588 1413 1622 1435 1604 1'
    '457 1573 1446 1522 1461 1489 1493 1458 1525 1448 1586 1462 1602 1492 1619 1493 1633 1504 1678 1512 1689 1534 1'
    '750 1533 1794 1551 1839 1571 1860 1581 1895 1560 1913 1541 1953 1535 1986 1543 1998 1577 2009 1555 2045 1571 2'
    '081 1575 2103 1558 2116 1535 2125 1500 2134 1450 2141 1433 2158 1377 2181 1330 2178 1276 2189 1248 2172 1218 2'
    '189 1193 2161 1198 2123 1183 2092 1222 2023 1229 1986 1193 1937 1191 1927 1219 1895 1227 1851 1191 1802 1192 1'
    '775 1125 1742 1088 1764 1036 1735 1004 1785 939 1855 937 1875 886 1961 895 2016 851 2069 832 2144 831 2223 878'
    ' 2289 904 2341 893 2381 899 2434 864 2441 836 2430 790 2403 765 2378 757 2362 737 2304 680 2252 655 2213 615 2'
    '246 604 2283 548 2258 522 2325 494 2324 480 2283 490 2247 496 2216 517 2174 521 2135 546 2137 588 2160 604 220'
    '6 600 2197 624 2147 636 2086 675 2060 661 2070 629 2021 610 2029 597 2072 574 2059 559 1988 542 1985 517 1943 '
    '525 1926 562 1891 612 1892 629 1870 644 1856 637 1844 718 1820 746 1803 794 1818 833 1823 859 1863 880 1855 89'
    '7 1801 900 1781 921 1744 957 1729 926 1730 912 1702 910 1678 904 1623 921 1655 959 1632 970 1607 970 1582 936 '
    '1574 950 1584 990 1607 1022 1590 1037 1615 1068 1638 1087 1638 1125 1596 1107 1610 1142 1581 1149 1598 1208 15'
    '68 1209 1530 1180 1513 1126 1505 1081 1488 1050 1464 1012 1461 993 1453 973 1428 951 1424 919 1427 873 1434 85'
    '2 1426 841 1404 814 1384 801 1341 776 1315 752 1273 732 1235 682 1224 649 1223 627 1194 616 1180 645 1166 622 '
    '1167 599 1179 592 1143 582 1106 606 1108 639 1103 658 1118 693 1160 727 1183 782 1234 836 1269 836 1280 851 12'
    '68 864 1308 888 1342 909 1381 944 1385 956 1377 980 1352 949 1312 938 1293 981 1326 1006 1321 1041 1302 1045 1'
    '277 1103 1258 1108 1259 1088 1268 1052 1278 1037 1260 998 1246 964 1227 956 1214 927 1185 915 1165 888 1131 88'
    '3 1096 853 1054 809 1023 771 1009 704 986 696 949 674 929 683 902 714 883 719 842 757 753 739 686 761 681 801 '
    '684 840 641 885 582 899 578 922 550 959 533 1014 551 1052 524 1082 514 1126 480 1139 448 1191 390 1192 347 119'
    '1 318 1215 301 1240 279 1234 262 1212 249 1173 207 1163 188 1180 164 1171 141 1178 148 1125 144 1084 123 1078 '
    '112 1052 116 1008 134 984 137 957 147 916 146 888 137 864 135 841 137 793 119 764 183 716 238 728 299 727 348 '
    '739 386 735 459 738 483 697 491 563 444 493 411 459 341 433 337 384 396 369 472 387 458 311 500 340 606 287 62'
    '0 232 660 218 696 205 720 187 759 88 822 60 859 62 868 47 906 44 915 59 945 25 935 0 933 -38 915 -75 913 -144 '
    '921 -162 934 -182 974 -186 990 -205 1026 -224 1025 -189 1011 -167 1017 -149 1041 -138 1030 -113 1017 -120 984 '
    '-72 996 -39 997 -13 1043 2 1043 26 1089 14 1114 -5 1166 22 1187 43 1218 23 1289 -8 1346 -30 1392 -19 1395 -3 1'
    '439 -2 1449 -31 1512 -53 1503 -110 1504 -160 1526 -202 1569 -225 1605 -175 1642 -176 1651 -228 1656 -268 1639 '
    '-259 1610 -283 1606 -322 1664 -340 1721 -350 1770 -339 1817 -341 1869 -378 1821 -410 1739 -405 1659 -380 1585 '
    '-366 1559 -403 1515 -425 1525 -491 1503 -551 1524 -591 1566 -633 1670 -706 1700 -720 1695 -748 1632 -780 1554 '
    '-761 1510 -714 1517 -673 1444 -619 1357 -561 1324 -466 1356 -419 1399 -382 1358 -306 1310 -290 1293 -177 1267 '
    '-115 1212 -121 1186 -68 1134 -65 1119 -128 1081 -204 1047 -299 1016 -341 926 -263 866 -247 803 -281 787 -354 7'
    '72 -509 814 -552 934 -608 1024 -678 1107 -771 1216 -901 1293 -952 1417 -1036 1517 -1065 1592 -1062 1661 -1117 '
    '1744 -1115 1826 -1128 1968 -1079 1909 -1061 1959 -1019 2006 -1042 2081 -1001 2205 -985 2377 -909 2412 -877 241'
    '5 -833 2364 -797 2290 -779 2087 -831 2054 -822 2128 -773 2134 -673 2192 -652 2228 -635 2234 -668 2205 -697 223'
    '5 -722 2345 -680 2383 -696 2353 -746 2459 -811 2501 -808 2543 -784 2570 -830 2532 -870 2554 -911 2521 -952 264'
    '8 -931 2674 -893 2616 -885 2616 -847 2652 -824 2722 -839 2734 -882 2829 -914 2987 -971 3021 -968 2977 -927 303'
    '3 -920 3066 -943 3151 -945 3218 -973 3270 -933 3322 -977 3274 -1016 3298 -1038 3432 -1018 3495 -997 3660 -920 '
    '3690 -955 3644 -991 3643 -1005 3588 -1012 3603 -1043 3578 -1096 3577 -1117 3661 -1178 3691 -1239 3725 -1253 38'
    '45 -1235 3854 -1197 3811 -1143 3840 -1121 3854 -1075 3844 -982 3894 -941 3874 -896 3785 -801 3837 -791 3855 -8'
    '15 3906 -833 3918 -866 3957 -898 3930 -936 3952 -980 3902 -986 3891 -1023 3927 -1091 3868 -1145 3950 -1191 393'
    '9 -1239 3962 -1240 3986 -1203 3968 -1138 4016 -1126 3996 -1174 4072 -1201 4166 -1204 4250 -1166 4210 -1222 420'
    '5 -1293 4284 -1307 4393 -1304 4492 -1313 4455 -1348 4508 -1392 4560 -1394 4648 -1427 4768 -1436 4783 -1455 490'
    '3 -1461 4940 -1446 5042 -1481 5125 -1480 5138 -1509 5181 -1538 5289 -1565 5367 -1544 5305 -1527 5408 -1517Z'
)


FRANCE_DOTS = (
    'M143 13h.1M169 13h.1M195 13h.1M221 13h.1M247 13h.1M273 13h.1M403 13h.1M429 13h.1M455 13h.1M481 13h.1M507 13h.1'
    'M949 13h.1M975 13h.1M117 39h.1M143 39h.1M169 39h.1M195 39h.1M221 39h.1M247 39h.1M429 39h.1M455 39h.1M481 39h.1'
    'M507 39h.1M533 39h.1M949 39h.1M975 39h.1M117 65h.1M143 65h.1M169 65h.1M195 65h.1M221 65h.1M247 65h.1M351 65h.1'
    'M377 65h.1M429 65h.1M455 65h.1M481 65h.1M507 65h.1M533 65h.1M819 65h.1M845 65h.1M871 65h.1M897 65h.1M923 65h.1'
    'M949 65h.1M975 65h.1M143 91h.1M169 91h.1M195 91h.1M221 91h.1M247 91h.1M351 91h.1M377 91h.1M403 91h.1M429 91h.1'
    'M455 91h.1M481 91h.1M507 91h.1M533 91h.1M559 91h.1M767 91h.1M793 91h.1M819 91h.1M845 91h.1M871 91h.1M897 91h.1'
    'M923 91h.1M949 91h.1M975 91h.1M143 117h.1M169 117h.1M195 117h.1M221 117h.1M247 117h.1M351 117h.1M377 117h.1M40'
    '3 117h.1M429 117h.1M455 117h.1M481 117h.1M507 117h.1M533 117h.1M559 117h.1M585 117h.1M611 117h.1M767 117h.1M79'
    '3 117h.1M819 117h.1M845 117h.1M871 117h.1M897 117h.1M923 117h.1M949 117h.1M975 117h.1M117 143h.1M143 143h.1M16'
    '9 143h.1M195 143h.1M221 143h.1M351 143h.1M377 143h.1M403 143h.1M429 143h.1M455 143h.1M481 143h.1M507 143h.1M53'
    '3 143h.1M559 143h.1M585 143h.1M611 143h.1M741 143h.1M767 143h.1M793 143h.1M819 143h.1M845 143h.1M871 143h.1M89'
    '7 143h.1M923 143h.1M949 143h.1M975 143h.1M117 169h.1M143 169h.1M169 169h.1M325 169h.1M351 169h.1M377 169h.1M40'
    '3 169h.1M429 169h.1M455 169h.1M481 169h.1M507 169h.1M533 169h.1M559 169h.1M585 169h.1M741 169h.1M767 169h.1M79'
    '3 169h.1M819 169h.1M845 169h.1M871 169h.1M897 169h.1M923 169h.1M949 169h.1M975 169h.1M377 195h.1M403 195h.1M42'
    '9 195h.1M455 195h.1M481 195h.1M507 195h.1M533 195h.1M559 195h.1M585 195h.1M715 195h.1M741 195h.1M767 195h.1M79'
    '3 195h.1M819 195h.1M845 195h.1M871 195h.1M897 195h.1M923 195h.1M949 195h.1M975 195h.1M351 221h.1M377 221h.1M40'
    '3 221h.1M429 221h.1M455 221h.1M481 221h.1M507 221h.1M533 221h.1M559 221h.1M585 221h.1M663 221h.1M689 221h.1M71'
    '5 221h.1M741 221h.1M767 221h.1M793 221h.1M819 221h.1M845 221h.1M871 221h.1M897 221h.1M923 221h.1M949 221h.1M97'
    '5 221h.1M325 247h.1M351 247h.1M377 247h.1M403 247h.1M429 247h.1M455 247h.1M481 247h.1M637 247h.1M663 247h.1M68'
    '9 247h.1M715 247h.1M741 247h.1M767 247h.1M793 247h.1M819 247h.1M845 247h.1M871 247h.1M897 247h.1M923 247h.1M94'
    '9 247h.1M975 247h.1M299 273h.1M325 273h.1M351 273h.1M377 273h.1M611 273h.1M637 273h.1M663 273h.1M689 273h.1M71'
    '5 273h.1M741 273h.1M767 273h.1M793 273h.1M819 273h.1M845 273h.1M871 273h.1M897 273h.1M923 273h.1M949 273h.1M97'
    '5 273h.1M585 299h.1M611 299h.1M637 299h.1M663 299h.1M689 299h.1M715 299h.1M741 299h.1M767 299h.1M793 299h.1M81'
    '9 299h.1M845 299h.1M871 299h.1M897 299h.1M923 299h.1M949 299h.1M975 299h.1M533 325h.1M559 325h.1M585 325h.1M61'
    '1 325h.1M637 325h.1M663 325h.1M689 325h.1M715 325h.1M741 325h.1M767 325h.1M793 325h.1M819 325h.1M845 325h.1M87'
    '1 325h.1M897 325h.1M923 325h.1M949 325h.1M975 325h.1M481 351h.1M507 351h.1M533 351h.1M559 351h.1M585 351h.1M61'
    '1 351h.1M637 351h.1M663 351h.1M689 351h.1M715 351h.1M741 351h.1M767 351h.1M793 351h.1M819 351h.1M845 351h.1M87'
    '1 351h.1M897 351h.1M923 351h.1M949 351h.1M975 351h.1M377 377h.1M403 377h.1M481 377h.1M507 377h.1M533 377h.1M55'
    '9 377h.1M585 377h.1M611 377h.1M637 377h.1M663 377h.1M689 377h.1M715 377h.1M741 377h.1M767 377h.1M793 377h.1M81'
    '9 377h.1M845 377h.1M871 377h.1M897 377h.1M923 377h.1M949 377h.1M975 377h.1M351 403h.1M377 403h.1M403 403h.1M42'
    '9 403h.1M455 403h.1M481 403h.1M507 403h.1M533 403h.1M559 403h.1M585 403h.1M611 403h.1M637 403h.1M663 403h.1M68'
    '9 403h.1M715 403h.1M741 403h.1M767 403h.1M793 403h.1M819 403h.1M845 403h.1M871 403h.1M897 403h.1M923 403h.1M94'
    '9 403h.1M975 403h.1M351 429h.1M377 429h.1M403 429h.1M429 429h.1M455 429h.1M481 429h.1M507 429h.1M533 429h.1M55'
    '9 429h.1M585 429h.1M611 429h.1M637 429h.1M663 429h.1M689 429h.1M715 429h.1M741 429h.1M767 429h.1M793 429h.1M81'
    '9 429h.1M845 429h.1M871 429h.1M897 429h.1M923 429h.1M949 429h.1M975 429h.1M403 455h.1M429 455h.1M455 455h.1M48'
    '1 455h.1M507 455h.1M533 455h.1M559 455h.1M585 455h.1M611 455h.1M637 455h.1M663 455h.1M689 455h.1M715 455h.1M74'
    '1 455h.1M767 455h.1M793 455h.1M819 455h.1M845 455h.1M871 455h.1M897 455h.1M923 455h.1M949 455h.1M975 455h.1M45'
    '5 481h.1M481 481h.1M507 481h.1M533 481h.1M559 481h.1M585 481h.1M611 481h.1M637 481h.1M663 481h.1M689 481h.1M71'
    '5 481h.1M741 481h.1M767 481h.1M793 481h.1M819 481h.1M845 481h.1M871 481h.1M897 481h.1M923 481h.1M949 481h.1M97'
    '5 481h.1M455 507h.1M481 507h.1M507 507h.1M533 507h.1M559 507h.1M585 507h.1M611 507h.1M637 507h.1M663 507h.1M68'
    '9 507h.1M715 507h.1M741 507h.1M767 507h.1M793 507h.1M819 507h.1M845 507h.1M871 507h.1M897 507h.1M923 507h.1M94'
    '9 507h.1M975 507h.1M481 533h.1M507 533h.1M533 533h.1M559 533h.1M585 533h.1M611 533h.1M637 533h.1M663 533h.1M68'
    '9 533h.1M715 533h.1M741 533h.1M767 533h.1M793 533h.1M819 533h.1M845 533h.1M871 533h.1M897 533h.1M923 533h.1M94'
    '9 533h.1M975 533h.1M507 559h.1M533 559h.1M559 559h.1M585 559h.1M611 559h.1M637 559h.1M663 559h.1M689 559h.1M71'
    '5 559h.1M741 559h.1M767 559h.1M793 559h.1M819 559h.1M845 559h.1M871 559h.1M897 559h.1M923 559h.1M949 559h.1M97'
    '5 559h.1M507 585h.1M533 585h.1M559 585h.1M585 585h.1M611 585h.1M637 585h.1M663 585h.1M689 585h.1M715 585h.1M74'
    '1 585h.1M767 585h.1M793 585h.1M819 585h.1M845 585h.1M871 585h.1M897 585h.1M923 585h.1M949 585h.1M975 585h.1M50'
    '7 611h.1M533 611h.1M559 611h.1M585 611h.1M611 611h.1M637 611h.1M663 611h.1M689 611h.1M715 611h.1M741 611h.1M76'
    '7 611h.1M793 611h.1M819 611h.1M845 611h.1M871 611h.1M897 611h.1M923 611h.1M949 611h.1M975 611h.1M507 637h.1M53'
    '3 637h.1M559 637h.1M585 637h.1M611 637h.1M637 637h.1M663 637h.1M689 637h.1M715 637h.1M741 637h.1M767 637h.1M79'
    '3 637h.1M819 637h.1M845 637h.1M871 637h.1M897 637h.1M923 637h.1M949 637h.1M975 637h.1M507 663h.1M533 663h.1M55'
    '9 663h.1M585 663h.1M611 663h.1M637 663h.1M663 663h.1M689 663h.1M715 663h.1M741 663h.1M767 663h.1M793 663h.1M81'
    '9 663h.1M845 663h.1M871 663h.1M897 663h.1M923 663h.1M949 663h.1M975 663h.1M507 689h.1M533 689h.1M559 689h.1M58'
    '5 689h.1M611 689h.1M637 689h.1M663 689h.1M689 689h.1M715 689h.1M741 689h.1M767 689h.1M793 689h.1M819 689h.1M84'
    '5 689h.1M871 689h.1M897 689h.1M923 689h.1M975 689h.1M481 715h.1M507 715h.1M533 715h.1M559 715h.1M585 715h.1M61'
    '1 715h.1M637 715h.1M663 715h.1M689 715h.1M715 715h.1M741 715h.1M767 715h.1M793 715h.1M819 715h.1M845 715h.1M87'
    '1 715h.1M897 715h.1M169 741h.1M195 741h.1M221 741h.1M247 741h.1M273 741h.1M299 741h.1M325 741h.1M351 741h.1M37'
    '7 741h.1M403 741h.1M429 741h.1M455 741h.1M481 741h.1M507 741h.1M533 741h.1M559 741h.1M585 741h.1M611 741h.1M63'
    '7 741h.1M663 741h.1M689 741h.1M715 741h.1M741 741h.1M767 741h.1M793 741h.1M819 741h.1M845 741h.1M143 767h.1M16'
    '9 767h.1M195 767h.1M221 767h.1M247 767h.1M273 767h.1M299 767h.1M325 767h.1M351 767h.1M377 767h.1M403 767h.1M42'
    '9 767h.1M455 767h.1M481 767h.1M507 767h.1M533 767h.1M559 767h.1M585 767h.1M611 767h.1M637 767h.1M663 767h.1M14'
    '3 793h.1M169 793h.1M195 793h.1M221 793h.1M247 793h.1M273 793h.1M299 793h.1M325 793h.1M351 793h.1M377 793h.1M40'
    '3 793h.1M429 793h.1M455 793h.1M481 793h.1M507 793h.1M533 793h.1M559 793h.1M585 793h.1M611 793h.1M637 793h.1M66'
    '3 793h.1M949 793h.1M975 793h.1M143 819h.1M169 819h.1M195 819h.1M221 819h.1M247 819h.1M273 819h.1M299 819h.1M32'
    '5 819h.1M351 819h.1M377 819h.1M403 819h.1M429 819h.1M455 819h.1M481 819h.1M507 819h.1M533 819h.1M559 819h.1M58'
    '5 819h.1M611 819h.1M637 819h.1M663 819h.1M949 819h.1M975 819h.1M143 845h.1M169 845h.1M195 845h.1M221 845h.1M24'
    '7 845h.1M273 845h.1M299 845h.1M325 845h.1M351 845h.1M377 845h.1M403 845h.1M429 845h.1M455 845h.1M481 845h.1M50'
    '7 845h.1M533 845h.1M559 845h.1M585 845h.1M611 845h.1M637 845h.1M663 845h.1M949 845h.1M143 871h.1M169 871h.1M19'
    '5 871h.1M221 871h.1M247 871h.1M273 871h.1M299 871h.1M325 871h.1M351 871h.1M377 871h.1M403 871h.1M429 871h.1M45'
    '5 871h.1M481 871h.1M507 871h.1M533 871h.1M559 871h.1M585 871h.1M611 871h.1M637 871h.1M169 897h.1M195 897h.1M22'
    '1 897h.1M247 897h.1M273 897h.1M299 897h.1M325 897h.1M351 897h.1M377 897h.1M403 897h.1M429 897h.1M455 897h.1M48'
    '1 897h.1M507 897h.1M533 897h.1M559 897h.1M585 897h.1M169 923h.1M195 923h.1M221 923h.1M247 923h.1M273 923h.1M29'
    '9 923h.1M325 923h.1M351 923h.1M377 923h.1M403 923h.1M429 923h.1M455 923h.1M481 923h.1M507 923h.1M533 923h.1M55'
    '9 923h.1M923 923h.1M949 923h.1M975 923h.1'
)


def encart_france(items: list[dict] | None = None) -> str:
    """Le dézoom sur la France : six groupes y tiennent en trois pixels sur la carte du monde.

    Un encadré en bas à gauche reprend la France en points (`FRANCE_DOTS`, Natural Earth projeté),
    du même dessin que la grande carte, et y pose les groupes français à leur point, écartés juste
    assez pour se lire.
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
    # Un repère immobile garde son point exact ; ceux qui se promènent s'écartent, sinon deux d'entre
    # eux — la bourse France et Le Bon Coin, même centre du pays — se posent l'un sur l'autre.
    dedans = sorted(dedans, key=lambda b: (1 if b.get("promenade") else 0, -(b.get("membres") or 0)))
    place: list[tuple[float, float]] = []
    marques = []
    for b in dedans:
        x = (float(b["lon"]) - lon0) / (lon1 - lon0) * 100
        y = (lat1 - float(b["lat"])) / (lat1 - lat0) * 100
        bx, by = x, y
        # même principe que la grande carte : le point exact d'abord, puis des anneaux. Sur 170 px de
        # large, deux groupes à trois kilomètres l'un de l'autre se recouvrent.
        ancre = not b.get("promenade")
        for r in ((0.0,) if ancre else (0.0, 15.0, 22.0, 30.0)):
            libre = False
            for k in range(1 if not r else 16):
                a = math.radians(22.5 * k)
                cx = min(max(x + r * math.cos(a), 5.0), 95.0)
                cy = min(max(y + r * math.sin(a) * 0.66, 6.0), 94.0)
                if all((cx - px) ** 2 + (cy - py) ** 2 >= 13.0 ** 2 for px, py in place):
                    bx, by, libre = cx, cy, True
                    break
            if libre:
                break
        place.append((bx, by))
        icone = BATEAU_COLIS if b.get("colis") else BATEAU
        gens = _participants(b.get("membres"))
        titre = " — ".join(m for m in (b["groupe"], _zone(b), (gens + "participants") if gens else "") if m)
        mot = "groupe de vente" if b.get("colis") else "bourse aux équipiers"
        # Un groupe qui se promène sur la grande carte se promène aussi ici : la bourse France navigue
        # autour des côtes, Le Bon Coin traverse la France par la terre (Nicolas, 22/11/2026).
        anime = ""
        prom = b.get("promenade") or []
        if len(prom) > 1:
            X0, X1 = (lon0 + 180) / 3.6, (lon1 + 180) / 3.6
            Y0, Y1 = (90 - lat1) / 1.8, (90 - lat0) / 1.8
            pts = [[round(min(max((x - X0) / (X1 - X0) * 100, 2), 98), 1),
                    round(min(max((y - Y0) / (Y1 - Y0) * 100, 2), 98), 1)] for x, y in prom]
            anime = ' data-pts="' + json.dumps(pts, separators=(",", ":")) + '" data-vif="1"'
            bx, by = pts[0][0], pts[0][1]
        marques.append(
            f'<a class="pt-b"{anime} href="{b["lien"]}" target="_blank" rel="noopener" title="{titre}" '
            f'aria-label="{titre}, {mot}" style="left:{bx:.1f}%;top:{by:.1f}%">{icone}</a>')
    return ('<div class="encart-france" role="group" aria-label="Zoom sur la France">'
            f'<svg class="fond" viewBox="0 0 {FRANCE_VUE[0]} {FRANCE_VUE[1]}" '
            'preserveAspectRatio="none" aria-hidden="true">'
            f'<path class="cote" d="{FRANCE_COTE}"/>'
            f'<path class="terre" d="{FRANCE_DOTS}"/></svg>' + "".join(marques)
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
        ancre = not b.get("promenade")
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
