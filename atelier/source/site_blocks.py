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
  aspect-ratio:1000/671;background:#06121f;border:1px solid rgba(238,243,247,.22);border-radius:7px;
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
FRANCE_BOITE = (-5.2, 8.8, 41.8, 51.2)          # ouest, est, sud, nord
FRANCE_VUE = (1000, 671)
FRANCE_COTE = (
    'M1029 713 1072 764 1062 858 1030 854 1000 878 973 859 971 772 954 732 994 735 1029 713ZM1054 646 1031 701 998 '
    '686 982 638 996 612 1042 585 1054 646ZM-113 -76 -240 -34 -341 -44 -283 -119 -321 -191 -223 -247 -169 -281 -110'
    ' -284 -33 -239 -71 -190 -59 -139 -113 -76ZM157 -531 80 -453 153 -463 231 -463 213 -405 149 -341 222 -336 292 -'
    '244 341 -233 385 -152 405 -123 492 -110 483 -64 446 -43 475 -6 411 31 315 30 194 50 160 36 113 69 47 61 -3 89 '
    '-41 74 64 -1 128 -16 15 -28 -5 -56 70 -79 31 -117 44 -164 151 -157 161 -199 112 -244 25 -256 8 -276 34 -308 11'
    ' -327 -28 -293 -32 -362 -68 -399 -42 -472 14 -530 71 -525 157 -531ZM8012 -1840 8031 -1805 8097 -1822 8306 -182'
    '1 8467 -1786 8524 -1759 8506 -1722 8427 -1701 8239 -1662 8186 -1640 8274 -1630 8380 -1612 8444 -1626 8481 -158'
    '0 8512 -1599 8626 -1610 8855 -1598 8873 -1565 9171 -1554 9176 -1609 9327 -1596 9441 -1597 9557 -1559 9589 -151'
    '3 9547 -1483 9637 -1427 9749 -1398 9818 -1473 9933 -1441 10054 -1460 10193 -1438 10245 -1458 10362 -1448 10311'
    ' -1514 10405 -1545 11050 -1499 11111 -1457 11298 -1402 11586 -1416 11728 -1404 11788 -1374 11779 -1322 11867 -'
    '1302 11963 -1316 12089 -1318 12224 -1304 12360 -1312 12484 -1249 12573 -1272 12515 -1317 12547 -1349 12775 -13'
    '29 12923 -1333 13129 -1299 13229 -1268 13229 -984 13136 -952 13044 -957 13108 -919 13151 -860 13184 -841 13192'
    ' -812 13173 -793 13040 -808 12841 -754 12777 -746 12668 -696 12564 -652 12538 -620 12436 -669 12250 -613 12217'
    ' -640 12148 -609 12053 -619 12030 -572 11944 -503 11947 -474 12028 -458 12018 -354 11952 -351 11922 -292 11951'
    ' -261 11826 -224 11802 -143 11695 -126 11674 -53 11571 13 11544 -36 11514 -140 11474 -298 11508 -397 11568 -44'
    '0 11572 -473 11683 -489 11811 -579 11934 -653 12062 -710 12120 -810 12033 -804 11990 -745 11809 -667 11750 -75'
    '5 11566 -731 11387 -611 11446 -567 11287 -549 11176 -541 11181 -593 11070 -604 10982 -569 10763 -581 10528 -56'
    '0 10297 -420 10023 -252 10136 -243 10171 -198 10240 -182 10286 -218 10364 -213 10468 -135 10470 -74 10414 -3 1'
    '0408 82 10376 197 10268 300 10244 349 10147 432 10051 515 10005 557 9910 599 9865 600 9820 565 9724 617 9713 6'
    '41 9686 637 9655 661 9633 685 9636 736 9599 752 9586 765 9560 786 9512 798 9481 817 9479 848 9470 856 9499 867'
    ' 9539 899 9601 983 9619 1029 9619 1111 9592 1151 9528 1164 9470 1194 9406 1200 9398 1161 9411 1108 9380 1033 9'
    '433 1021 9384 960 9349 947 9341 960 9320 966 9317 952 9299 946 9279 935 9299 903 9316 895 9309 882 9328 843 93'
    '23 832 9281 824 9248 805 9148 825 9095 859 9018 878 9056 845 9041 817 9098 769 9060 732 8998 757 8917 807 8873'
    ' 853 8803 856 8767 890 8804 938 8863 950 8865 982 8922 1002 9002 952 9065 979 9111 981 9123 1019 9022 1039 898'
    '8 1077 8919 1113 8882 1163 8959 1202 8987 1272 9031 1338 9079 1393 9078 1446 9033 1465 9050 1503 9092 1525 908'
    '1 1583 9063 1640 9023 1646 8971 1724 8913 1817 8847 1903 8749 1968 8649 2028 8569 2037 8525 2068 8500 2045 846'
    '0 2081 8360 2116 8285 2127 8260 2203 8221 2207 8202 2155 8219 2128 8123 2105 8089 2116 7994 2177 7934 2245 791'
    '9 2294 7973 2370 8040 2463 8105 2507 8148 2564 8181 2696 8171 2822 8112 2869 8030 2915 7972 2974 7883 3041 785'
    '7 2995 7877 2947 7824 2906 7764 2896 7735 2859 7699 2785 7635 2752 7574 2753 7584 2697 7521 2698 7516 2776 747'
    '7 2881 7454 2944 7459 2995 7505 2998 7534 3063 7547 3124 7587 3165 7630 3174 7667 3211 7684 3217 7726 3260 775'
    '6 3308 7760 3356 7752 3389 7759 3413 7764 3456 7790 3475 7818 3538 7816 3563 7766 3567 7698 3514 7614 3458 760'
    '5 3421 7564 3374 7554 3315 7528 3276 7536 3224 7520 3193 7492 3166 7480 3131 7442 3090 7407 3056 7396 3098 738'
    '2 3059 7390 3014 7411 2946 7404 2893 7426 2838 7402 2796 7408 2718 7379 2681 7356 2596 7343 2505 7312 2446 726'
    '5 2482 7184 2533 7143 2527 7099 2510 7124 2422 7109 2355 7053 2272 7062 2247 7020 2237 6969 2179 6949 2142 694'
    '5 2106 6931 2071 6901 2030 6835 2027 6842 2056 6819 2096 6789 2082 6779 2095 6758 2087 6731 2080 6721 2106 667'
    '2 2106 6584 2120 6588 2174 6550 2216 6447 2264 6367 2348 6314 2393 6242 2440 6242 2473 6207 2491 6142 2516 610'
    '9 2520 6088 2574 6102 2667 6106 2726 6076 2794 6076 2915 6039 2919 6006 2973 6028 2997 5963 3017 5939 3066 591'
    '0 3086 5842 3020 5809 2920 5782 2848 5757 2814 5719 2745 5701 2656 5689 2611 5624 2513 5594 2375 5573 2284 557'
    '3 2197 5559 2130 5455 2173 5405 2165 5312 2078 5346 2052 5325 2024 5241 1964 5189 1946 5168 1894 5112 1840 498'
    '1 1853 4865 1855 4764 1865 4630 1843 4552 1827 4471 1817 4441 1730 4407 1717 4352 1730 4280 1765 4192 1741 412'
    '0 1686 4051 1666 4004 1598 3951 1503 3913 1514 3867 1491 3841 1519 3798 1515 3813 1547 3807 1563 3830 1617 385'
    '8 1678 3893 1695 3905 1720 3954 1750 3958 1779 3951 1803 3960 1827 3981 1847 3990 1870 4001 1888 3996 1836 401'
    '5 1798 4035 1791 4056 1813 4058 1855 4042 1897 4056 1924 4068 1921 4071 1940 4127 1929 4186 1931 4229 1933 427'
    '8 1885 4331 1839 4376 1795 4397 1771 4399 1806 4390 1819 4400 1876 4432 1924 4472 1950 4524 1960 4566 1973 459'
    '9 2014 4618 2037 4643 2046 4643 2062 4617 2105 4606 2125 4576 2148 4549 2197 4517 2193 4502 2210 4490 2246 449'
    '9 2294 4492 2302 4460 2302 4415 2329 4408 2364 4392 2379 4347 2378 4319 2396 4320 2425 4285 2445 4246 2438 419'
    '8 2462 4165 2466 4113 2485 4099 2517 4098 2541 4027 2572 3912 2605 3849 2655 3817 2659 3796 2655 3754 2685 370'
    '8 2698 3648 2702 3630 2706 3615 2725 3596 2730 3585 2748 3550 2747 3527 2756 3477 2753 3459 2711 3461 2672 344'
    '9 2651 3435 2598 3415 2569 3429 2565 3422 2533 3430 2519 3427 2488 3418 2457 3396 2436 3391 2407 3354 2382 331'
    '6 2322 3296 2264 3246 2215 3214 2203 3167 2135 3159 2085 3162 2043 3121 1964 3087 1936 3049 1921 3025 1880 302'
    '9 1864 3009 1827 2989 1811 2961 1758 2917 1701 2881 1652 2845 1652 2856 1613 2859 1588 2868 1559 2846 1578 283'
    '0 1632 2811 1669 2794 1681 2771 1658 2738 1626 2687 1524 2710 1606 2753 1678 2807 1789 2834 1827 2857 1868 292'
    '1 1947 2907 1959 2909 2006 2992 2070 3005 2084 3028 2154 3012 2167 3022 2241 3049 2326 3076 2344 3115 2370 315'
    '6 2453 3176 2518 3215 2553 3313 2620 3352 2661 3391 2702 3414 2727 3449 2748 3466 2770 3463 2800 3423 2817 345'
    '3 2837 3476 2850 3490 2879 3523 2909 3558 2909 3625 2891 3703 2883 3766 2861 3802 2856 3827 2843 3868 2840 389'
    '1 2839 3923 2828 3961 2821 3995 2797 4022 2796 4024 2816 4017 2858 4018 2895 4002 2921 3982 2998 3948 3078 390'
    '4 3169 3842 3274 3781 3354 3697 3451 3626 3509 3519 3580 3453 3634 3374 3720 3358 3758 3342 3775 3292 3803 327'
    '4 3833 3247 3838 3237 3889 3214 3918 3200 3965 3172 3989 3139 4077 3143 4117 3189 4143 3191 4162 3171 4205 317'
    '5 4226 3170 4261 3195 4305 3225 4376 3251 4391 3263 4423 3260 4494 3269 4557 3271 4669 3284 4704 3263 4755 323'
    '5 4804 3189 4848 3124 4876 3044 4910 2963 4987 2935 5000 2886 5051 2856 5067 2850 5118 2884 5172 2898 5214 289'
    '9 5235 2912 5232 2910 5302 2898 5335 2915 5347 2904 5377 2874 5402 2815 5426 2730 5465 2698 5491 2704 5521 272'
    '3 5526 2716 5564 2699 5616 2690 5675 2672 5707 2623 5743 2609 5754 2579 5790 2559 5827 2518 5878 2438 5951 238'
    '7 5994 2333 6027 2259 6054 2222 6058 2213 6078 2169 6067 2134 6081 2057 6067 2013 6076 1984 6072 1910 6100 184'
    '9 6112 1805 6139 1773 6140 1742 6115 1718 6114 1687 6082 1675 6072 1675 6031 1652 5983 1675 5970 1673 5915 162'
    '6 5848 1590 5788 1539 5695 1486 5641 1458 5589 1442 5519 1425 5467 1401 5358 1399 5272 1390 5233 1362 5204 132'
    '5 5145 1288 5059 1272 5014 1214 4945 1210 4890 1203 4845 1213 4782 1237 4717 1241 4686 1264 4622 1281 4593 132'
    '2 4546 1345 4514 1353 4461 1349 4421 1328 4395 1309 4352 1291 4309 1295 4294 1317 4266 1295 4197 1281 4149 124'
    '5 4104 1252 4090 1242 4068 1223 4014 1164 3939 1090 3867 1043 3808 1000 3734 1002 3710 1018 3688 1035 3636 104'
    '9 3583 1036 3572 1061 3492 1071 3435 1043 3388 1011 3376 996 3344 978 3334 979 3314 904 3340 877 3336 850 3352'
    ' 793 3351 754 3306 731 3254 680 3207 627 3208 564 3208 505 3216 447 3232 335 3273 295 3298 231 3319 167 3298 1'
    '35 3299 85 3285 39 3286 -45 3298 -95 3319 -166 3345 -179 3343 -198 3344 -272 3310 -337 3256 -398 3216 -446 317'
    '0 -465 3165 -516 3136 -553 3098 -566 3072 -575 3019 -606 2977 -634 2949 -652 2940 -670 2926 -678 2894 -689 287'
    '8 -709 2867 -747 2837 -778 2832 -794 2812 -815 2786 -820 2771 -832 2716 -822 2684 -852 2629 -888 2603 -856 259'
    '0 -821 2540 -805 2503 -811 2465 -791 2429 -782 2362 -790 2292 -798 2256 -791 2221 -810 2187 -847 2156 -844 212'
    '6 -841 2093 -814 2073 -790 2036 -795 2012 -770 1961 -730 1916 -706 1904 -687 1863 -686 1825 -660 1781 -612 175'
    '5 -567 1682 -530 1653 -463 1645 -407 1597 -371 1578 -312 1518 -330 1429 -302 1368 -293 1330 -247 1282 -175 124'
    '9 -122 1220 -75 1146 -52 1102 0 1102 43 1133 111 1128 185 1144 216 1144 285 1105 362 1093 407 1064 476 1042 59'
    '7 1029 715 1023 751 1034 819 1006 895 1005 924 1022 973 1017 1051 989 1101 997 1099 1033 1159 1007 1164 1021 1'
    '129 1056 1128 1089 1153 1107 1143 1168 1096 1204 1110 1243 1147 1244 1165 1278 1192 1289 1276 1314 1306 1308 1'
    '366 1320 1460 1352 1494 1415 1558 1429 1659 1459 1735 1494 1770 1476 1804 1443 1787 1388 1810 1354 1861 1320 1'
    '910 1310 2007 1325 2031 1357 2058 1357 2081 1369 2152 1378 2169 1401 2264 1400 2333 1419 2404 1440 2437 1451 2'
    '492 1429 2521 1408 2584 1402 2635 1411 2654 1447 2671 1423 2728 1440 2784 1444 2819 1426 2840 1403 2854 1365 2'
    '868 1311 2878 1293 2906 1235 2941 1184 2936 1127 2954 1098 2927 1065 2954 1039 2911 1045 2851 1028 2802 1069 2'
    '694 1077 2636 1039 2559 1037 2542 1066 2493 1075 2424 1037 2346 1038 2303 967 2251 927 2286 872 2241 838 2320 '
    '770 2430 767 2460 712 2596 722 2682 676 2765 655 2883 654 3008 704 3111 732 3194 721 3255 727 3340 690 3350 65'
    '9 3332 611 3291 584 3252 576 3225 554 3134 494 3053 467 2991 425 3043 414 3102 354 3062 326 3168 297 3166 281 '
    '3102 293 3045 298 2997 321 2930 325 2869 352 2873 396 2908 413 2981 409 2967 434 2889 447 2792 488 2752 474 27'
    '68 440 2690 419 2702 406 2771 382 2750 365 2639 347 2634 321 2568 330 2541 369 2486 422 2488 440 2453 455 2431'
    ' 449 2411 535 2374 564 2348 615 2371 656 2380 684 2442 707 2429 724 2344 728 2314 750 2254 789 2232 755 2233 7'
    '41 2189 739 2152 732 2065 750 2115 791 2079 802 2039 802 2001 766 1988 781 2004 824 2039 857 2012 873 2052 906'
    ' 2088 927 2089 967 2023 948 2044 984 1998 992 2025 1055 1978 1056 1919 1025 1893 968 1880 920 1852 887 1816 84'
    '7 1811 826 1799 821 1797 806 1758 782 1751 748 1757 699 1767 677 1755 665 1740 660 1720 637 1689 622 1622 596 '
    '1581 570 1515 549 1455 497 1470 491 1437 461 1436 437 1390 426 1368 457 1347 433 1349 408 1367 400 1310 390 12'
    '52 415 1256 451 1247 471 1271 507 1338 543 1374 602 1453 660 1509 659 1526 675 1506 689 1570 715 1623 737 1684'
    ' 774 1691 787 1678 813 1638 780 1576 768 1546 814 1598 841 1589 878 1560 882 1522 943 1492 949 1492 927 1507 8'
    '89 1522 873 1494 832 1472 796 1443 787 1422 756 1376 743 1345 715 1292 710 1236 678 1171 631 1122 590 1100 520'
    ' 1064 511 1006 488 973 497 932 531 903 536 838 576 697 557 593 580 585 623 589 664 521 712 429 727 423 751 379'
    ' 791 352 849 379 890 338 921 323 968 269 982 218 1037 127 1038 59 1037 15 1062 -13 1089 -48 1083 -74 1059 -94 '
    '1018 -161 1007 -190 1025 -227 1015 -264 1023 -253 967 -260 923 -292 917 -309 890 -303 843 -275 817 -270 788 -2'
    '55 745 -256 715 -271 689 -274 665 -270 614 -299 583 -198 532 -111 545 -15 544 61 557 120 553 236 555 273 512 2'
    '86 370 212 295 160 259 51 232 43 180 136 164 256 182 233 102 301 132 467 77 489 18 551 4 608 -10 645 -30 708 -'
    '135 805 -165 865 -163 879 -178 938 -182 952 -166 1000 -201 984 -228 980 -269 951 -308 949 -381 961 -400 982 -4'
    '22 1045 -426 1070 -446 1127 -466 1125 -429 1104 -406 1112 -386 1151 -375 1133 -348 1112 -356 1061 -305 1080 -2'
    '70 1081 -242 1154 -226 1153 -200 1225 -214 1266 -233 1346 -205 1380 -183 1429 -203 1540 -237 1630 -261 1701 -2'
    '49 1707 -231 1776 -230 1792 -262 1891 -285 1875 -345 1878 -399 1913 -443 1980 -468 2037 -414 2094 -416 2108 -4'
    '71 2116 -513 2090 -504 2045 -529 2039 -570 2129 -590 2219 -600 2296 -589 2370 -591 2451 -630 2376 -664 2247 -6'
    '58 2121 -632 2005 -617 1964 -656 1894 -680 1910 -750 1876 -814 1910 -856 1974 -901 2138 -978 2186 -993 2178 -1'
    '023 2079 -1057 1956 -1037 1887 -987 1898 -943 1784 -886 1646 -824 1594 -724 1645 -674 1713 -634 1648 -553 1574'
    ' -537 1546 -417 1506 -350 1419 -357 1379 -300 1296 -297 1273 -365 1213 -446 1159 -547 1111 -590 970 -508 875 -'
    '491 776 -527 751 -604 728 -769 794 -815 982 -875 1123 -948 1254 -1048 1426 -1186 1545 -1239 1742 -1329 1898 -1'
    '360 2016 -1356 2125 -1416 2255 -1412 2383 -1427 2607 -1374 2515 -1355 2593 -1310 2667 -1335 2784 -1292 2980 -1'
    '275 3249 -1194 3304 -1160 3309 -1113 3230 -1075 3113 -1056 2794 -1111 2742 -1102 2858 -1049 2867 -943 2959 -92'
    '2 3015 -903 3024 -938 2980 -969 3027 -995 3200 -951 3260 -968 3212 -1021 3378 -1090 3444 -1086 3511 -1061 3552'
    ' -1110 3493 -1153 3528 -1196 3475 -1240 3675 -1217 3716 -1177 3625 -1168 3626 -1129 3682 -1104 3792 -1120 3810'
    ' -1165 3959 -1199 4208 -1260 4262 -1257 4192 -1214 4280 -1206 4332 -1231 4466 -1233 4572 -1262 4653 -1219 4734'
    ' -1266 4659 -1308 4696 -1331 4907 -1310 5006 -1287 5265 -1206 5313 -1243 5240 -1281 5238 -1296 5152 -1303 5176'
    ' -1337 5137 -1393 5135 -1415 5267 -1480 5314 -1545 5367 -1559 5556 -1540 5571 -1500 5503 -1443 5548 -1420 5571'
    ' -1370 5555 -1272 5633 -1228 5603 -1181 5463 -1079 5545 -1069 5573 -1094 5652 -1113 5670 -1148 5732 -1182 5691'
    ' -1223 5724 -1270 5646 -1276 5629 -1315 5686 -1387 5593 -1445 5721 -1493 5704 -1544 5740 -1546 5777 -1506 5749'
    ' -1437 5826 -1424 5793 -1476 5913 -1504 6061 -1508 6193 -1467 6129 -1526 6122 -1602 6246 -1617 6418 -1614 6573'
    ' -1623 6515 -1660 6598 -1707 6680 -1709 6819 -1745 7007 -1754 7031 -1774 7219 -1780 7277 -1764 7437 -1802 7569'
    ' -1801 7588 -1832 7656 -1862 7825 -1891 7948 -1868 7850 -1851 8012 -1840Z'
)


FRANCE_DOTS = (
    'M60 12h.1M84 12h.1M108 12h.1M132 12h.1M156 12h.1M180 12h.1M204 12h.1M228 12h.1M252 12h.1M276 12h.1M300 12h.1M3'
    '24 12h.1M348 12h.1M372 12h.1M396 12h.1M420 12h.1M516 12h.1M540 12h.1M564 12h.1M588 12h.1M612 12h.1M636 12h.1M6'
    '60 12h.1M684 12h.1M708 12h.1M732 12h.1M756 12h.1M780 12h.1M804 12h.1M828 12h.1M852 12h.1M876 12h.1M900 12h.1M9'
    '24 12h.1M948 12h.1M972 12h.1M996 12h.1M36 36h.1M60 36h.1M84 36h.1M108 36h.1M132 36h.1M156 36h.1M180 36h.1M204 '
    '36h.1M228 36h.1M252 36h.1M276 36h.1M492 36h.1M516 36h.1M540 36h.1M564 36h.1M588 36h.1M612 36h.1M636 36h.1M660 '
    '36h.1M684 36h.1M708 36h.1M732 36h.1M756 36h.1M780 36h.1M804 36h.1M828 36h.1M852 36h.1M876 36h.1M900 36h.1M924 '
    '36h.1M948 36h.1M972 36h.1M996 36h.1M12 60h.1M36 60h.1M60 60h.1M84 60h.1M108 60h.1M492 60h.1M516 60h.1M540 60h.'
    '1M564 60h.1M588 60h.1M612 60h.1M636 60h.1M660 60h.1M684 60h.1M708 60h.1M732 60h.1M756 60h.1M780 60h.1M804 60h.'
    '1M828 60h.1M852 60h.1M876 60h.1M900 60h.1M924 60h.1M948 60h.1M972 60h.1M996 60h.1M468 84h.1M492 84h.1M516 84h.'
    '1M540 84h.1M564 84h.1M588 84h.1M612 84h.1M636 84h.1M660 84h.1M684 84h.1M708 84h.1M732 84h.1M756 84h.1M780 84h.'
    '1M804 84h.1M828 84h.1M852 84h.1M876 84h.1M900 84h.1M924 84h.1M948 84h.1M972 84h.1M996 84h.1M396 108h.1M420 108'
    'h.1M444 108h.1M468 108h.1M492 108h.1M516 108h.1M540 108h.1M564 108h.1M588 108h.1M612 108h.1M636 108h.1M660 108'
    'h.1M684 108h.1M708 108h.1M732 108h.1M756 108h.1M780 108h.1M804 108h.1M828 108h.1M852 108h.1M876 108h.1M900 108'
    'h.1M924 108h.1M948 108h.1M972 108h.1M996 108h.1M252 132h.1M276 132h.1M300 132h.1M324 132h.1M348 132h.1M372 132'
    'h.1M396 132h.1M420 132h.1M444 132h.1M468 132h.1M492 132h.1M516 132h.1M540 132h.1M564 132h.1M588 132h.1M612 132'
    'h.1M636 132h.1M660 132h.1M684 132h.1M708 132h.1M732 132h.1M756 132h.1M780 132h.1M804 132h.1M828 132h.1M852 132'
    'h.1M876 132h.1M900 132h.1M924 132h.1M948 132h.1M972 132h.1M996 132h.1M252 156h.1M276 156h.1M300 156h.1M324 156'
    'h.1M348 156h.1M372 156h.1M396 156h.1M420 156h.1M444 156h.1M468 156h.1M492 156h.1M516 156h.1M540 156h.1M564 156'
    'h.1M588 156h.1M612 156h.1M636 156h.1M660 156h.1M684 156h.1M708 156h.1M732 156h.1M756 156h.1M780 156h.1M804 156'
    'h.1M828 156h.1M852 156h.1M876 156h.1M900 156h.1M924 156h.1M948 156h.1M972 156h.1M996 156h.1M60 180h.1M84 180h.'
    '1M108 180h.1M132 180h.1M156 180h.1M180 180h.1M204 180h.1M228 180h.1M276 180h.1M300 180h.1M324 180h.1M348 180h.'
    '1M372 180h.1M396 180h.1M420 180h.1M444 180h.1M468 180h.1M492 180h.1M516 180h.1M540 180h.1M564 180h.1M588 180h.'
    '1M612 180h.1M636 180h.1M660 180h.1M684 180h.1M708 180h.1M732 180h.1M756 180h.1M780 180h.1M804 180h.1M828 180h.'
    '1M852 180h.1M876 180h.1M900 180h.1M924 180h.1M948 180h.1M972 180h.1M996 180h.1M60 204h.1M84 204h.1M108 204h.1M'
    '132 204h.1M156 204h.1M180 204h.1M204 204h.1M228 204h.1M252 204h.1M276 204h.1M300 204h.1M324 204h.1M348 204h.1M'
    '372 204h.1M396 204h.1M420 204h.1M444 204h.1M468 204h.1M492 204h.1M516 204h.1M540 204h.1M564 204h.1M588 204h.1M'
    '612 204h.1M636 204h.1M660 204h.1M684 204h.1M708 204h.1M732 204h.1M756 204h.1M780 204h.1M804 204h.1M828 204h.1M'
    '852 204h.1M876 204h.1M900 204h.1M924 204h.1M948 204h.1M972 204h.1M996 204h.1M60 228h.1M84 228h.1M108 228h.1M13'
    '2 228h.1M156 228h.1M180 228h.1M204 228h.1M228 228h.1M252 228h.1M276 228h.1M300 228h.1M324 228h.1M348 228h.1M37'
    '2 228h.1M396 228h.1M420 228h.1M444 228h.1M468 228h.1M492 228h.1M516 228h.1M540 228h.1M564 228h.1M588 228h.1M61'
    '2 228h.1M636 228h.1M660 228h.1M684 228h.1M708 228h.1M732 228h.1M756 228h.1M780 228h.1M804 228h.1M828 228h.1M85'
    '2 228h.1M876 228h.1M900 228h.1M924 228h.1M948 228h.1M972 228h.1M996 228h.1M132 252h.1M156 252h.1M180 252h.1M20'
    '4 252h.1M228 252h.1M252 252h.1M276 252h.1M300 252h.1M324 252h.1M348 252h.1M372 252h.1M396 252h.1M420 252h.1M44'
    '4 252h.1M468 252h.1M492 252h.1M516 252h.1M540 252h.1M564 252h.1M588 252h.1M612 252h.1M636 252h.1M660 252h.1M68'
    '4 252h.1M708 252h.1M732 252h.1M756 252h.1M780 252h.1M804 252h.1M828 252h.1M852 252h.1M876 252h.1M900 252h.1M92'
    '4 252h.1M948 252h.1M972 252h.1M996 252h.1M204 276h.1M228 276h.1M252 276h.1M276 276h.1M300 276h.1M324 276h.1M34'
    '8 276h.1M372 276h.1M396 276h.1M420 276h.1M444 276h.1M468 276h.1M492 276h.1M516 276h.1M540 276h.1M564 276h.1M58'
    '8 276h.1M612 276h.1M636 276h.1M660 276h.1M684 276h.1M708 276h.1M732 276h.1M756 276h.1M780 276h.1M804 276h.1M82'
    '8 276h.1M852 276h.1M876 276h.1M900 276h.1M924 276h.1M948 276h.1M972 276h.1M996 276h.1M228 300h.1M252 300h.1M27'
    '6 300h.1M300 300h.1M324 300h.1M348 300h.1M372 300h.1M396 300h.1M420 300h.1M444 300h.1M468 300h.1M492 300h.1M51'
    '6 300h.1M540 300h.1M564 300h.1M588 300h.1M612 300h.1M636 300h.1M660 300h.1M684 300h.1M708 300h.1M732 300h.1M75'
    '6 300h.1M780 300h.1M804 300h.1M828 300h.1M852 300h.1M876 300h.1M900 300h.1M924 300h.1M948 300h.1M972 300h.1M99'
    '6 300h.1M252 324h.1M276 324h.1M300 324h.1M324 324h.1M348 324h.1M372 324h.1M396 324h.1M420 324h.1M444 324h.1M46'
    '8 324h.1M492 324h.1M516 324h.1M540 324h.1M564 324h.1M588 324h.1M612 324h.1M636 324h.1M660 324h.1M684 324h.1M70'
    '8 324h.1M732 324h.1M756 324h.1M780 324h.1M804 324h.1M828 324h.1M852 324h.1M876 324h.1M900 324h.1M924 324h.1M94'
    '8 324h.1M972 324h.1M996 324h.1M276 348h.1M300 348h.1M324 348h.1M348 348h.1M372 348h.1M396 348h.1M420 348h.1M44'
    '4 348h.1M468 348h.1M492 348h.1M516 348h.1M540 348h.1M564 348h.1M588 348h.1M612 348h.1M636 348h.1M660 348h.1M68'
    '4 348h.1M708 348h.1M732 348h.1M756 348h.1M780 348h.1M804 348h.1M828 348h.1M852 348h.1M876 348h.1M900 348h.1M92'
    '4 348h.1M948 348h.1M972 348h.1M996 348h.1M300 372h.1M324 372h.1M348 372h.1M372 372h.1M396 372h.1M420 372h.1M44'
    '4 372h.1M468 372h.1M492 372h.1M516 372h.1M540 372h.1M564 372h.1M588 372h.1M612 372h.1M636 372h.1M660 372h.1M68'
    '4 372h.1M708 372h.1M732 372h.1M756 372h.1M780 372h.1M804 372h.1M828 372h.1M852 372h.1M876 372h.1M900 372h.1M92'
    '4 372h.1M948 372h.1M972 372h.1M996 372h.1M300 396h.1M324 396h.1M348 396h.1M372 396h.1M396 396h.1M420 396h.1M44'
    '4 396h.1M468 396h.1M492 396h.1M516 396h.1M540 396h.1M564 396h.1M588 396h.1M612 396h.1M636 396h.1M660 396h.1M68'
    '4 396h.1M708 396h.1M732 396h.1M756 396h.1M780 396h.1M804 396h.1M828 396h.1M852 396h.1M876 396h.1M900 396h.1M92'
    '4 396h.1M948 396h.1M972 396h.1M996 396h.1M300 420h.1M324 420h.1M348 420h.1M372 420h.1M396 420h.1M420 420h.1M44'
    '4 420h.1M468 420h.1M492 420h.1M516 420h.1M540 420h.1M564 420h.1M588 420h.1M612 420h.1M636 420h.1M660 420h.1M68'
    '4 420h.1M708 420h.1M732 420h.1M756 420h.1M780 420h.1M804 420h.1M828 420h.1M852 420h.1M876 420h.1M900 420h.1M92'
    '4 420h.1M948 420h.1M972 420h.1M996 420h.1M300 444h.1M324 444h.1M348 444h.1M372 444h.1M396 444h.1M420 444h.1M44'
    '4 444h.1M468 444h.1M492 444h.1M516 444h.1M540 444h.1M564 444h.1M588 444h.1M612 444h.1M636 444h.1M660 444h.1M68'
    '4 444h.1M708 444h.1M732 444h.1M756 444h.1M780 444h.1M804 444h.1M828 444h.1M852 444h.1M876 444h.1M900 444h.1M92'
    '4 444h.1M948 444h.1M972 444h.1M996 444h.1M300 468h.1M324 468h.1M348 468h.1M372 468h.1M396 468h.1M420 468h.1M44'
    '4 468h.1M468 468h.1M492 468h.1M516 468h.1M540 468h.1M564 468h.1M588 468h.1M612 468h.1M636 468h.1M660 468h.1M68'
    '4 468h.1M708 468h.1M732 468h.1M756 468h.1M780 468h.1M804 468h.1M828 468h.1M852 468h.1M876 468h.1M900 468h.1M92'
    '4 468h.1M948 468h.1M972 468h.1M996 468h.1M276 492h.1M300 492h.1M324 492h.1M348 492h.1M372 492h.1M396 492h.1M42'
    '0 492h.1M444 492h.1M468 492h.1M492 492h.1M516 492h.1M540 492h.1M564 492h.1M588 492h.1M612 492h.1M636 492h.1M66'
    '0 492h.1M684 492h.1M708 492h.1M732 492h.1M756 492h.1M780 492h.1M804 492h.1M828 492h.1M852 492h.1M876 492h.1M90'
    '0 492h.1M924 492h.1M948 492h.1M972 492h.1M276 516h.1M300 516h.1M324 516h.1M348 516h.1M372 516h.1M396 516h.1M42'
    '0 516h.1M444 516h.1M468 516h.1M492 516h.1M516 516h.1M540 516h.1M564 516h.1M588 516h.1M612 516h.1M636 516h.1M66'
    '0 516h.1M684 516h.1M708 516h.1M732 516h.1M756 516h.1M780 516h.1M804 516h.1M828 516h.1M852 516h.1M876 516h.1M90'
    '0 516h.1M924 516h.1M948 516h.1M252 540h.1M276 540h.1M300 540h.1M324 540h.1M348 540h.1M372 540h.1M396 540h.1M42'
    '0 540h.1M444 540h.1M468 540h.1M492 540h.1M516 540h.1M540 540h.1M564 540h.1M588 540h.1M612 540h.1M636 540h.1M66'
    '0 540h.1M684 540h.1M708 540h.1M732 540h.1M756 540h.1M780 540h.1M804 540h.1M828 540h.1M852 540h.1M876 540h.1M12'
    ' 564h.1M36 564h.1M60 564h.1M84 564h.1M108 564h.1M132 564h.1M156 564h.1M180 564h.1M204 564h.1M228 564h.1M252 56'
    '4h.1M276 564h.1M300 564h.1M324 564h.1M348 564h.1M372 564h.1M396 564h.1M420 564h.1M444 564h.1M468 564h.1M492 56'
    '4h.1M516 564h.1M540 564h.1M564 564h.1M588 564h.1M612 564h.1M636 564h.1M660 564h.1M756 564h.1M780 564h.1M804 56'
    '4h.1M828 564h.1M852 564h.1M12 588h.1M36 588h.1M60 588h.1M84 588h.1M108 588h.1M132 588h.1M156 588h.1M180 588h.1'
    'M204 588h.1M228 588h.1M252 588h.1M276 588h.1M300 588h.1M324 588h.1M348 588h.1M372 588h.1M396 588h.1M420 588h.1'
    'M444 588h.1M468 588h.1M492 588h.1M516 588h.1M540 588h.1M564 588h.1M588 588h.1M12 612h.1M36 612h.1M60 612h.1M84'
    ' 612h.1M108 612h.1M132 612h.1M156 612h.1M180 612h.1M204 612h.1M228 612h.1M252 612h.1M276 612h.1M300 612h.1M324'
    ' 612h.1M348 612h.1M372 612h.1M396 612h.1M420 612h.1M444 612h.1M468 612h.1M492 612h.1M516 612h.1M540 612h.1M564'
    ' 612h.1M12 636h.1M36 636h.1M60 636h.1M84 636h.1M108 636h.1M132 636h.1M156 636h.1M180 636h.1M204 636h.1M228 636'
    'h.1M252 636h.1M276 636h.1M300 636h.1M324 636h.1M348 636h.1M372 636h.1M396 636h.1M420 636h.1M444 636h.1M468 636'
    'h.1M492 636h.1M516 636h.1M540 636h.1M564 636h.1M996 636h.1M12 660h.1M36 660h.1M60 660h.1M84 660h.1M108 660h.1M'
    '132 660h.1M156 660h.1M180 660h.1M204 660h.1M228 660h.1M252 660h.1M276 660h.1M300 660h.1M324 660h.1M348 660h.1M'
    '372 660h.1M396 660h.1M420 660h.1M444 660h.1M468 660h.1M492 660h.1M516 660h.1M540 660h.1M564 660h.1M588 660h.1M'
    '996 660h.1'
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
        marques.append(
            f'<a class="pt-b" href="{b["lien"]}" target="_blank" rel="noopener" title="{titre}" '
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
