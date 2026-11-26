#!/usr/bin/env python3
"""Seul écrivain des fiches bateaux (tâche 58, Nicolas 26/11/2026).

Source unique : site/bateaux-fiches.json. Appelé par `accueil_site.sortir_le_site` ; aucun HTML de fiche
n'est écrit à la main. Écrit :
  site/bateaux/<slug>.html            les fiches qui passent le seuil
  site/bateaux/index.html             le sommaire, par chantier puis par taille
  site/sitemap-bateaux.xml            une <loc> par fiche publiée (le sommaire est dans sitemap.xml)
  site/bateaux-file-attente.json      les fiches sous le seuil : non publiées, hors sitemap
  un bloc « fiches bateaux » (balisé, idempotent) dans lexique/<mot>.html et cours-*.html (fr)

SEUIL : 8 champs sur 10 remplis (nom, constructeur, architecte, loa_m, beam_m, draft_min_m,
deplacement_kg, production_debut — les 8 champs nommés par Nicolas), au moins 5 sources distinctes
(couples URL + citation, avec date) et confiance différente de « basse ».
IMAGES : 0 à 2 par fiche, jamais bloquant (champ images[] = {fichier, auteur, licence, url_source, date}).

    python3 scripts/fiches_bateaux.py           # écrit dans la copie
"""
from __future__ import annotations

import html
import json
import os
import re
import sys
from pathlib import Path

RACINE = Path(os.environ.get("SITE_ROOT") or Path(__file__).resolve().parent.parent)
SITE = RACINE / "projets" / "sailingmore" / "site"
URL = "https://sailingmore.fr"
DATE = "2026-11-26"
CHAMPS = ["nom", "constructeur", "architecte", "loa_m", "beam_m", "draft_min_m", "deplacement_kg", "production_debut"]
CHAMPS_MIN = 8
SOURCES_MIN = 5
LICENCES = {"CC0", "CC-BY", "CC-BY-SA", "presse-autorisee", "photo-maison"}
COURSE = {"jeanneau-sun-fast-3200", "jeanneau-sun-fast-3600", "beneteau-first-31-7", "beneteau-first-34-7",
          "beneteau-first-36-7", "x-332", "x-35"}   # classes et séries qui courent (ORC/IRC, monotypes)
MARQUE = re.compile(r"<!--fiches-bateaux-->.*?<!--/fiches-bateaux-->", re.S)

# lexique (pages par mot), cours : chemins relatifs à site/
LEX = {"quille": "lexique/quille.html", "lest": "lexique/lest.html", "deplacement": "lexique/deplacement.html",
       "tirant": "lexique/tirant-d-eau.html", "stabilite": "lexique/stabilite.html", "gite": "lexique/gite.html",
       "croisiere": "lexique/voilier-de-croisiere.html", "course": "lexique/voilier-de-course.html",
       "monocoque": "lexique/monocoque.html"}
C_BATEAU = "cours-le-bateau-et-son-vocabulaire.html"
C_REGLER = "cours-regler-les-voiles-et-man-uvrer.html"
C_METEO = "cours-la-meteo.html"


# ───────────────────────────────────────────────────────── données
def normaliser(b: dict) -> dict:
    b = dict(b)
    b["architecte"] = b.get("architecte") or b.get("architect")
    if b.get("production_debut") is None:
        b["production_debut"] = b.get("production_start_year")
    if b.get("production_fin") is None:
        b["production_fin"] = b.get("production_end_year")
    return b


def sources_distinctes(b: dict) -> list[dict]:
    vus, out = set(), []
    for s in b.get("sources", []):
        if s.get("url") and s.get("citation") and s.get("consulte_le") and (s["url"], s["citation"]) not in vus:
            vus.add((s["url"], s["citation"]))
            out.append(s)
    return out


def evaluer(b: dict) -> tuple[bool, str]:
    n = sum(1 for c in CHAMPS if b.get(c) not in (None, ""))
    s = len(sources_distinctes(b))
    if n < CHAMPS_MIN:
        return False, f"{n} champs sur 10 (seuil {CHAMPS_MIN})"
    if s < SOURCES_MIN:
        return False, f"{s} sources distinctes (seuil {SOURCES_MIN})"
    if (b.get("confiance") or "basse") == "basse":
        return False, "confiance basse"
    return True, ""


def images_valides(b: dict) -> list[dict]:
    """0 à 2 images, jamais bloquant : une entrée incomplète ou sous licence refusée est écartée."""
    out = []
    for im in (b.get("images") or [])[:2]:
        if all(im.get(k) for k in ("fichier", "auteur", "licence", "url_source", "date")) \
                and im["licence"] in LICENCES and (SITE / im["fichier"]).exists():
            out.append(im)
    return out


def charger() -> tuple[list[dict], list[dict]]:
    d = json.loads((SITE / "bateaux-fiches.json").read_text(encoding="utf-8"))
    pub, att = [], []
    for b in map(normaliser, d["bateaux"]):
        ok, raison = evaluer(b)
        (pub if ok else att).append(b if ok else {**b, "raison_file_attente": raison})
    return pub, att


# ───────────────────────────────────────────────────────── mise en forme
def e(x) -> str:
    return html.escape(str(x), quote=True)


def m(x: float) -> str:
    return f"{x:.2f}".replace(".", ",") + " m"


def ft(x: float) -> str:
    return f"{x / 0.3048:.1f}".replace(".", ",") + " ft"


def kg(x: float) -> str:
    return f"{int(round(x)):,}".replace(",", " ") + " kg"


def lien(chemin: str, texte: str, prefixe: str = "../") -> str:
    return f'<a href="{prefixe}{chemin}">{texte}</a>'


def domaine(u: str) -> str:
    return re.sub(r"^https?://(www\.)?", "", u).split("/")[0]


def ligne_source(s: dict) -> str:
    wiki = " — texte Wikipédia, CC-BY-SA" if "wikipedia.org" in s["url"] else ""
    return (f'<li><a href="{e(s["url"])}" rel="nofollow noopener">{e(domaine(s["url"]))}</a> '
            f'« {e(s["citation"])} » <span class="d">({e(s["consulte_le"])}{wiki})</span></li>')


def cellule(b: dict, champ: str, valeur: str) -> str:
    src = [s for s in sources_distinctes(b) if s.get("champ") == champ]
    ul = f'<ul class="src">{"".join(ligne_source(s) for s in src)}</ul>' if src else ""
    return f"<td>{valeur}{ul}</td>"


def phrase_prod(b: dict) -> str:
    d, f = b["production_debut"], b.get("production_fin")
    if f and f != d:
        return f"produit de {d} à {f}"
    if f:
        return f"produit en {d}"
    return f"produit à partir de {d} (fin de production non publiée)"


def phrase_tirant(b: dict) -> str:
    lo, hi = b["draft_min_m"], b.get("draft_max_m")
    if hi and abs(hi - lo) > 0.004:
        return f"son tirant d’eau est de {m(lo)} à {m(hi)} selon la quille choisie"
    return f"son tirant d’eau est de {m(lo)}"


def kg_par_m(b: dict) -> int:
    return int(round(b["deplacement_kg"] / b["loa_m"]))


def texte(b: dict) -> str:
    course = b["slug"] in COURSE
    genre = (lien(LEX["course"], "voilier de course-croisière") if course else lien(LEX["croisiere"], "voilier de croisière"))
    p = [f'<p>Le {e(b["nom"])} est un {genre} de {m(b["loa_m"])} hors-tout dessiné par {e(b["architecte"])}, '
         f'construit par {e(b["constructeur"])} et {phrase_prod(b)}. Sa largeur maximale est de {m(b["beam_m"])}.</p>',
         f'<p>Côté {lien(LEX["tirant"], "tirant d’eau")}, {phrase_tirant(b)} : c’est ce chiffre qui décide des fonds où l’on peut '
         f'mouiller ou entrer au port. Son {lien(LEX["deplacement"], "déplacement")} annoncé est de {kg(b["deplacement_kg"])}, '
         f'soit {kg_par_m(b)} kg par mètre de longueur hors-tout (calcul simple sur les cotes ci-dessous, sans longueur de flottaison).</p>',
         f'<p>La {lien(LEX["quille"], "quille")} et son lest fournissent la stabilité : plus le lest est bas, moins le bateau '
         f'gîte sous la risée (voir {lien(C_BATEAU, "Le bateau et son vocabulaire")}). Pour la conduite, le cours '
         f'{lien(C_REGLER, "Régler les voiles et manœuvrer")} dit quand choquer ou prendre un ris, et '
         + ("le cours sur la météo" if course else lien(C_METEO, "La météo")) + ' comment lire le vent avant de sortir.</p>']
    if course:
        p.append(f'<p>Ce modèle se retrouve en régate : voir le calendrier des {lien("regates.html", "régates")} et les '
                 f'{lien("regles-de-course.html", "règles de course")} qui s’y appliquent.</p>')
    return "".join(p)


CSS = """*{box-sizing:border-box}body{margin:0;background:#071c31;color:#eef3f7;font-family:system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;line-height:1.7}
.page{max-width:46rem;margin:0 auto;padding:3.6rem 1.4rem 5rem}a.retour{color:#9db2c6;text-decoration:none;font-size:12px;letter-spacing:.14em;text-transform:uppercase}
h1{font-size:clamp(1.9rem,6vw,2.7rem);line-height:1.1;margin:1.6rem 0 1rem;color:#fff;font-weight:300;text-transform:uppercase}
h1::after{content:"";display:block;width:3.4rem;height:3px;background:#e23a3e;margin:1.2rem 0 1.6rem}
h2{font-size:12px;margin:2.6rem 0 .9rem;letter-spacing:.22em;text-transform:uppercase;color:#9db2c6;font-weight:500;padding-top:1.1rem;border-top:1px solid rgba(226,58,62,.22)}
p,li,td,th{font-size:.95rem}a{color:#fff;text-decoration:underline;text-decoration-color:rgba(226,58,62,.7);text-underline-offset:3px}
table{width:100%;border-collapse:collapse}th,td{text-align:left;padding:.7rem .6rem .7rem 0;border-bottom:1px solid rgba(255,255,255,.09);vertical-align:top}th{color:#9db2c6;font-weight:500;width:34%}
.src,.d{color:#9db2c6;font-size:12px;line-height:1.5}ul.src{list-style:none;padding:0;margin:.4rem 0 0}ul.src li{font-size:12px;color:#9db2c6}
figure{margin:1.4rem 0}figure img{max-width:100%;height:auto}figcaption{color:#9db2c6;font-size:12px}
hr{border:0;border-top:1px solid rgba(255,255,255,.09);margin:3rem 0}"""
FIN = ('<script src="/js/config.js"></script><script src="/js/favoris.js"></script>'
       '<script src="/js/favoris-ui.js"></script>\n</body></html>\n')


def tete(titre: str, desc: str, chemin: str, fil: list[tuple[str, str]]) -> str:
    ld = {"@context": "https://schema.org", "@type": "WebPage", "name": titre, "url": f"{URL}/{chemin}", "inLanguage": "fr",
          "dateModified": DATE,
          "breadcrumb": {"@type": "BreadcrumbList", "itemListElement": [
              {"@type": "ListItem", "position": i + 1, "name": n, "item": u} for i, (n, u) in enumerate(fil)]}}
    return ('<!doctype html>\n<html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">\n'
            f'<title>{e(titre)}</title><link rel="canonical" href="{URL}/{chemin}">\n<meta name="description" content="{e(desc)}">\n'
            f'<meta property="og:type" content="website"><meta property="og:site_name" content="Sailing More">'
            f'<meta property="og:title" content="{e(titre)}"><meta property="og:description" content="{e(desc)}">'
            f'<meta property="og:url" content="{URL}/{chemin}">\n<link rel="icon" href="../favicon-32.png" sizes="32x32">\n'
            f'<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>\n<style>{CSS}</style></head><body><div class="page">\n')


def fiche(b: dict, tous: list[dict]) -> str:
    nom = b["nom"]
    titre = f"{nom} : fiche technique, cotes et dimensions — SailingMore"
    desc = (f"{nom} ({b['constructeur']}) : longueur {m(b['loa_m'])}, largeur {m(b['beam_m'])}, "
            f"déplacement {kg(b['deplacement_kg'])}. Chaque cote est sourcée et datée.")
    lignes = [("Constructeur", e(b["constructeur"]), None), ("Architecte", e(b["architecte"]), "architecte"),
              ("Longueur hors-tout", f"{m(b['loa_m'])} · {ft(b['loa_m'])}", "loa_m"),
              ("Largeur (bau maxi)", f"{m(b['beam_m'])} · {ft(b['beam_m'])}", "beam_m"),
              ("Tirant d’eau mini", f"{m(b['draft_min_m'])} · {ft(b['draft_min_m'])}", "draft_min_m")]
    if b.get("draft_max_m"):
        lignes.append(("Tirant d’eau maxi", f"{m(b['draft_max_m'])} · {ft(b['draft_max_m'])}", "draft_max_m"))
    lignes += [("Déplacement", kg(b["deplacement_kg"]), "deplacement_kg"),
               ("Début de production", str(b["production_debut"]), "production_debut"),
               ("Fin de production", str(b["production_fin"]) if b.get("production_fin") else "non publié", None)]
    tab = "".join(f'<tr><th scope="row">{k}</th>{cellule(b, c, v) if c else f"<td>{v}</td>"}</tr>' for k, v, c in lignes)
    div = ""
    if b.get("divergences"):
        div = "<h2>Écarts entre les sources</h2><ul>" + "".join(f"<li>{e(x if isinstance(x, str) else json.dumps(x, ensure_ascii=False))}</li>"
                                                            for x in b["divergences"]) + "</ul>"
    ims = "".join(f'<figure><img src="../{e(i["fichier"])}" alt="{e(nom)}" loading="lazy">'
                  f'<figcaption>{e(i["auteur"])}, {e(i["licence"])} — <a href="{e(i["url_source"])}" rel="nofollow noopener">source</a>, {e(i["date"])}</figcaption></figure>'
                  for i in images_valides(b))
    meme = [x for x in tous if x["constructeur"] == b["constructeur"] and x["slug"] != b["slug"]]
    voisins = sorted((x for x in tous if x["slug"] != b["slug"]), key=lambda x: abs(x["loa_m"] - b["loa_m"]))[:4]
    def li(x): return f'<li><a href="{x["slug"]}.html">{e(x["nom"])}</a> <span class="d">{m(x["loa_m"])}</span></li>'
    suite = ""
    if meme:
        suite += "<h2>Même chantier</h2><ul>" + "".join(li(x) for x in meme) + "</ul>"
    suite += "<h2>Tailles voisines</h2><ul>" + "".join(li(x) for x in voisins) + "</ul>"
    return (tete(titre, desc, f"bateaux/{b['slug']}.html",
                 [("SailingMore", f"{URL}/"), ("Fiches bateaux", f"{URL}/bateaux/"), (nom, f"{URL}/bateaux/{b['slug']}.html")])
            + f'<a class="retour" href="./">← Toutes les fiches bateaux</a>\n<h1>{e(nom)}</h1>\n{texte(b)}{ims}\n'
            + f"<h2>Cotes</h2><table>{tab}</table>{div}"
            + f'<p class="src">Fiabilité de la relève : {e(b["confiance"])}.</p>{suite}\n'
            + f'<hr><p class="src">Relevé du {e(b.get("releve_le", "2026-11-23"))} · valeurs reprises telles que publiées, jamais estimées · '
              f'<a href="../mentions-legales.html">Mentions légales</a></p>\n</div>' + FIN)


def taille(x: dict) -> str:
    return "Moins de 10 m" if x["loa_m"] < 10 else ("10 à 11 m" if x["loa_m"] < 11 else "11 m et plus")


def sommaire(pub: list[dict]) -> str:
    out = []
    for ch in sorted({x["constructeur"] for x in pub}):
        out.append(f"<h2>{e(ch)}</h2>")
        for t in ("Moins de 10 m", "10 à 11 m", "11 m et plus"):
            g = sorted((x for x in pub if x["constructeur"] == ch and taille(x) == t), key=lambda x: x["loa_m"])
            if g:
                out.append(f'<p class="d">{t}</p><ul>' + "".join(
                    f'<li><a href="{x["slug"]}.html">{e(x["nom"])}</a> <span class="d">{m(x["loa_m"])} · {kg(x["deplacement_kg"])}</span></li>'
                    for x in g) + "</ul>")
    return (tete("Fiches bateaux : cotes et dimensions des croiseurs de 9 à 11 m — SailingMore",
                 f"{len(pub)} fiches techniques de voiliers de croisière : longueur, largeur, tirant d’eau, déplacement, chaque cote sourcée.",
                 "bateaux/", [("SailingMore", f"{URL}/"), ("Fiches bateaux", f"{URL}/bateaux/")])
            + f'<a class="retour" href="../bateaux.html">← Nomenclature des bateaux</a>\n<h1>Fiches bateaux</h1>\n'
              f'<p>{len(pub)} croiseurs de 9 à 11 m, rangés par chantier puis par taille. Chaque cote porte sa source, sa citation et sa date. '
              f'Les mots techniques renvoient au {lien("lexique.html", "lexique")} et au {lien("cours.html", "cours")}.</p>\n'
            + "".join(out) + '\n</div>' + FIN)


def sitemap(pub: list[dict]) -> str:
    u = "".join(f"  <url><loc>{URL}/bateaux/{b['slug']}.html</loc><lastmod>{DATE}</lastmod></url>\n" for b in pub)
    return ('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + u + "</urlset>\n")


# ───────────────────────────────────────────────────────── lien retour : lexique et cours
def _li(b: dict, prefixe: str, fait: str) -> str:
    return f'<a href="{prefixe}bateaux/{b["slug"]}.html">{e(b["nom"])}</a> ({fait})'


def retours(pub: list[dict]) -> dict[str, str]:
    """chemin relatif (site/) -> phrase. Les fiches choisies illustrent le terme par une cote réelle, jamais au hasard."""
    ext = lambda cle, rev=False: sorted(pub, key=cle, reverse=rev)
    lo_t, hi_t = ext(lambda x: x["draft_min_m"])[0], ext(lambda x: x.get("draft_max_m") or x["draft_min_m"], True)[0]
    lo_d, hi_d = ext(lambda x: x["deplacement_kg"])[0], ext(lambda x: x["deplacement_kg"], True)[0]
    deux = [x for x in pub if x.get("draft_max_m") and x["draft_max_m"] - x["draft_min_m"] > 0.004]
    lq = sorted(deux, key=lambda x: x["draft_max_m"] - x["draft_min_m"], reverse=True)[0] if deux else None
    lx = ext(lambda x: kg_par_m(x))
    cr = [x for x in pub if x["slug"] not in COURSE]
    co = [x for x in pub if x["slug"] in COURSE]
    def p(t, *items, pre="../"): return f'<p class="fiches-bateaux">{t} ' + " ; ".join(items) + ".</p>"
    R = {}
    for pre, base in (("../", "lexique/"), ("", "")):
        pass
    L = lambda k, t, *it: R.__setitem__(LEX[k], p(t, *it))
    L("tirant", "Sur nos fiches bateaux :", _li(lo_t, "../", f"tirant d’eau mini {m(lo_t['draft_min_m'])}"),
      _li(hi_t, "../", f"jusqu’à {m(hi_t.get('draft_max_m') or hi_t['draft_min_m'])}"))
    L("deplacement", "Sur nos fiches bateaux :", _li(lo_d, "../", kg(lo_d["deplacement_kg"])), _li(hi_d, "../", kg(hi_d["deplacement_kg"])))
    if lq:
        L("quille", "Sur nos fiches bateaux, un modèle à quille au choix :", _li(lq, "../", f"{m(lq['draft_min_m'])} ou {m(lq['draft_max_m'])}"))
    L("lest", "Sur nos fiches bateaux :", _li(lx[0], "../", f"{kg_par_m(lx[0])} kg par mètre"), _li(lx[-1], "../", f"{kg_par_m(lx[-1])} kg par mètre"))
    L("stabilite", "Sur nos fiches bateaux :", _li(lx[0], "../", f"{kg_par_m(lx[0])} kg par mètre"), _li(lx[-1], "../", f"{kg_par_m(lx[-1])} kg par mètre"))
    if cr:
        L("croisiere", "Sur nos fiches bateaux :", _li(cr[0], "../", m(cr[0]["loa_m"])), _li(cr[-1], "../", m(cr[-1]["loa_m"])))
    if co:
        L("course", "Sur nos fiches bateaux :", _li(co[0], "../", m(co[0]["loa_m"])), _li(co[-1], "../", m(co[-1]["loa_m"])))
    if co:
        R[C_REGLER] = p("Des bateaux qui se règlent à la régate, sur nos fiches :", _li(co[0], "", m(co[0]["loa_m"])), _li(co[-1], "", m(co[-1]["loa_m"])))
    R[C_BATEAU] = p("Quille, lest et déplacement en chiffres, sur nos fiches :", _li(lo_d, "", kg(lo_d["deplacement_kg"])), _li(hi_d, "", kg(hi_d["deplacement_kg"])))
    R[C_METEO] = p("Le même vent ne pèse pas pareil sur un bateau léger et sur un lourd, sur nos fiches :",
                   _li(lx[0], "", f"{kg_par_m(lx[0])} kg par mètre"), _li(lx[-1], "", f"{kg_par_m(lx[-1])} kg par mètre"))
    return R


def poser_retours(pub: list[dict], site: Path) -> int:
    n = 0
    for chemin, bloc in retours(pub).items():
        f = site / chemin
        if not f.exists():
            continue
        src = f.read_text(encoding="utf-8")
        src = MARQUE.sub("", src)
        marque = f"<!--fiches-bateaux-->{bloc}<!--/fiches-bateaux-->"
        if chemin.startswith("lexique/"):
            if "</main>" not in src:
                continue
            nouveau = src.replace("</main>", marque + "</main>", 1)
        else:
            cle = '<nav class="cours-nav"'
            if cle not in src:
                continue
            nouveau = src.replace(cle, marque + cle, 1)
        f.write_text(nouveau, encoding="utf-8")
        n += 1
    return n


# ───────────────────────────────────────────────────────── point d'entrée
def ecrire_page(site: Path = SITE) -> str:
    global SITE
    SITE = site
    pub, att = charger()
    dossier = site / "bateaux"
    dossier.mkdir(exist_ok=True)
    for b in pub:
        (dossier / f"{b['slug']}.html").write_text(fiche(b, pub), encoding="utf-8")
    (dossier / "index.html").write_text(sommaire(pub), encoding="utf-8")
    (site / "sitemap-bateaux.xml").write_text(sitemap(pub), encoding="utf-8")
    (site / "bateaux-file-attente.json").write_text(json.dumps(
        [{"slug": b["slug"], "nom": b["nom"], "raison": b["raison_file_attente"]} for b in att], ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    r = poser_retours(pub, site)
    return f"{len(pub)} fiches publiées, {len(att)} en file d’attente, {r} pages lexique/cours avec lien retour"


if __name__ == "__main__":
    print(ecrire_page())
    sys.exit(0)
