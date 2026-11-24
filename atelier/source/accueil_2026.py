"""L'accueil 2026 de sailingmore.fr : des cases, deux familles de chiffres, rien d'animé.

Tâche n°47 (Nicolas, 24/11/2026). Une seule source par objet :
  - le gabarit (en-tête, sélecteur de langue) reste celui du site : on le reprend de la page qu'on reçoit ;
  - tout le corps de page est écrit ici ;
  - les chiffres ne sont jamais saisis : ils sortent des fichiers de données (voir `mesures()`).

Deux usages, un seul chemin :
  python3 scripts/accueil_2026.py            réécrit projets/sailingmore/site/index.html en place
  accueil_2026.refondre(html_ancien, racine) appelé par accueil_site.py au moment d'écrire index.html

Ordre des cases de la première rangée : stages · régates · cours (JOB-LIST 2026-11-23 § 5, révisé par Nicolas).
La carte du Léman est dans la seconde rangée, jamais devant.
"""
from __future__ import annotations

import datetime
import json
import re
import sqlite3
import sys
from pathlib import Path

# L'ordre des tableaux de textes de l'accueil n'est pas celui du site : c'est fr en de it es pt.
# Ce n'est pas une seconde liste de langues, mais l'ordre d'écriture des tableaux `P` plus bas ;
# il est confronté à `site_blocks.LANGUES` au chargement, et le module s'arrête si les deux ne
# couvrent pas les mêmes langues — le 24/11/2026, avoir pris l'ordre du site a affiché du portugais
# à un visiteur allemand.
from site_blocks import LANGUES as _LANGUES_SITE
ORDRE_DES_TEXTES = ("fr", "en", "de", "it", "es", "pt")
if set(ORDRE_DES_TEXTES) != set(_LANGUES_SITE):
    raise SystemExit("accueil_2026 : l'ordre des textes de l'accueil (" + str(ORDRE_DES_TEXTES)
                     + ") ne couvre pas les langues du site (" + str(_LANGUES_SITE)
                     + ") — ajouter les textes de la langue manquante avant de publier.")
LANGUES = list(ORDRE_DES_TEXTES)

MOIS = {
    "fr": ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre", "octobre", "novembre", "décembre"],
    "en": ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"],
    "de": ["Januar", "Februar", "März", "April", "Mai", "Juni", "Juli", "August", "September", "Oktober", "November", "Dezember"],
    "it": ["gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno", "luglio", "agosto", "settembre", "ottobre", "novembre", "dicembre"],
    "es": ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"],
    "pt": ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"],
}

assert set(LANGUES) <= set(MOIS), "accueil_2026 : des mois manquent pour une langue"
# séparateur de milliers, séparateur décimal, unité du million
FORMAT = {
    "fr": (" ", ",", "M"), "en": (",", ".", "M"), "de": (".", ",", "Mio."),
    "it": (".", ",", "mln"), "es": (".", ",", "M"), "pt": (".", ",", "M"),
}


# --------------------------------------------------------------------------- mesures
def mesures(racine: Path) -> dict:
    """Tous les nombres de la page, comptés dans les fichiers. Rien n'est écrit à la main."""
    site = racine / "projets/sailingmore"
    rh = json.loads((racine / "cache/rhum/chiffres-stats.json").read_text(encoding="utf-8"))
    par = {c["cle"]: c for c in rh["chiffres"]}
    ab = rh["abonnes"]
    assert ab["total"] == ab["facebook"] + ab["instagram"] + ab["youtube"] + ab["telegram"], "abonnés : la somme ne tombe pas juste"
    assert par["abonnes"]["valeur"] == ab["total"]
    assert par["vues_mesurees"]["valeur"] == par["vues_facebook"]["valeur"] + par["vues_youtube"]["valeur"], "vues mesurées ≠ Facebook + YouTube"

    reg = json.loads((site / "regates.json").read_text(encoding="utf-8"))
    ref = reg["maj"][:10]                                   # la date des données sert de « aujourd'hui »
    avenir = [r for r in reg["regates"] if (r.get("debut") or "") >= ref and not r.get("annulee")]
    sp = json.loads((site / "site/stages-proches.json").read_text(encoding="utf-8"))
    # une offre sans date (champ vide) est permanente ; une offre datée avant le relevé n'est plus une offre
    offres = [o for o in sp["o"] if not o[7] or o[7] >= ref]
    lex = json.loads((site / "lexique.json").read_text(encoding="utf-8"))
    termes = [t for th in lex["themes"] for t in th["termes"]]
    complets = [t for t in termes if all(t["mot"].get(l) for l in lex["langues"])]
    chants = json.loads((site / "chants-de-marin.json").read_text(encoding="utf-8"))["chants"]
    bateaux = json.loads((site / "site/bateaux.json").read_text(encoding="utf-8"))["bateaux"]
    cx = sqlite3.connect(str(site / "ports.sqlite"))
    ports = cx.execute("select count(*) from ports").fetchone()[0]
    cx.close()
    return {
        "reseaux_maj": rh["maj"], "site_maj": max(ref, sp["maj"]),
        "abonnes": ab["total"], "fb": ab["facebook"], "ig": ab["instagram"], "yt": ab["youtube"], "tg": ab["telegram"],
        "vues_mesurees": par["vues_mesurees"]["valeur"], "vues_total": par["vues"]["valeur"],
        "contenus": par["contenus"]["valeur"],
        "offres": len(offres), "offres_toutes": len(sp["o"]),
        "ecoles": len({o[4] for o in offres}), "pays_offres": len({o[6] for o in offres if o[6]}),
        "regates": len(avenir), "pays_regates": len({r["pays"] for r in avenir if r.get("pays")}),
        "regates_annulees": sum(1 for r in reg["regates"] if (r.get("debut") or "") >= ref and r.get("annulee")),
        "termes": len(complets), "termes_tous": len(termes), "langues": len(lex["langues"]),
        "chants": len(chants), "chants_paroles": sum(1 for c in chants if c.get("paroles")),
        "bateaux": len(bateaux), "ports": ports,
    }


def _n(v: int, l: str) -> str:
    return f"{v:,}".replace(",", FORMAT[l][0])


def _m(v: int, l: str) -> str:
    """Millions, une décimale : 39 676 926 -> « 39,7 »."""
    s, d, _ = FORMAT[l]
    return f"{v / 1e6:.1f}".replace(".", d)


def _date(iso: str, l: str) -> str:
    a, m, j = iso[:10].split("-")
    j = int(j)
    if l == "en":
        return f"{MOIS[l][int(m) - 1]} {j}, {a}"
    if l == "de":
        return f"{j}. {MOIS[l][int(m) - 1]} {a}"
    if l in ("es", "pt"):
        return f"{j} de {MOIS[l][int(m) - 1]} de {a}"
    return f"{j}{'er' if (l == 'fr' and j == 1) else ''} {MOIS[l][int(m) - 1]} {a}"


# --------------------------------------------------------------------------- textes
def textes(x: dict) -> dict:
    """Les six langues. Un texte change dans les six le même jour."""
    T: dict = {}
    for l in LANGUES:
        n = lambda k: _n(x[k], l)
        mil = FORMAT[l][2]
        d = {}
        d["rdate"] = _date(x["reseaux_maj"], l)
        d["sdate"] = _date(x["site_maj"], l)
        d["n_abo"] = n("abonnes")
        d["n_vues"] = f"{_m(x['vues_mesurees'], l)} {mil}"
        d["n_cont"] = n("contenus")
        d["n_off"] = n("offres")
        d["n_eco"] = n("ecoles")
        d["n_reg"] = n("regates")
        d["abo_d"] = f"Facebook {n('fb')} · Instagram {n('ig')} · YouTube {n('yt')} · Telegram {n('tg')}"
        tot = f"{_m(x['vues_total'], l)} {mil}"
        T[l] = d
        T[l]["_tot"] = tot
    P = {  # texte par langue, dans l'ordre LANGUES = fr en de it es pt
        "titre": ["Sailing More — stages, régates et cours de voile", "Sailing More — sailing courses, regattas and lessons",
                  "Sailing More — Segelkurse, Regatten und Theorie", "Sailing More — corsi di vela, regate e lezioni",
                  "Sailing More — cursos de vela, regatas y clases", "Sailing More — cursos de vela, regatas e aulas"],
        "h1": ["Stages, régates et cours de voile, en Europe et au-delà.",
               "Sailing courses, regattas and lessons, across Europe and beyond.",
               "Segelkurse, Regatten und Theorie, in Europa und darüber hinaus.",
               "Corsi di vela, regate e lezioni, in Europa e oltre.",
               "Cursos de vela, regatas y clases, en Europa y más allá.",
               "Cursos de vela, regatas e aulas, na Europa e além."],
        "sous": ["Média indépendant de la voile, fait par des passionnés.", "An independent sailing outlet, made by enthusiasts.",
                 "Unabhängiges Segelmedium, von Enthusiasten gemacht.", "Media indipendente di vela, fatto da appassionati.",
                 "Medio independiente de vela, hecho por apasionados.", "Meio independente de vela, feito por apaixonados."],
        "c_stages": ["Stages", "Courses", "Segelkurse", "Corsi", "Cursos", "Cursos"],
        "c_regates": ["Régates", "Regattas", "Regatten", "Regate", "Regatas", "Regatas"],
        "c_cours": ["Cours", "Lessons", "Theorie", "Lezioni", "Clases", "Aulas"],
        "l_stages": ["{o} offres de stage, dans {p} pays.", "{o} course offers in {p} countries.", "{o} Kursangebote in {p} Ländern.",
                     "{o} offerte di corsi in {p} paesi.", "{o} ofertas de cursos en {p} países.", "{o} ofertas de cursos em {p} países."],
        "l_regates": ["{n} régates à venir, dans {p} pays.", "{n} upcoming regattas in {p} countries.", "{n} kommende Regatten in {p} Ländern.",
                      "{n} regate in programma in {p} paesi.", "{n} regatas próximas en {p} países.", "{n} regatas a seguir em {p} países."],
        "l_cours": ["Les cours théoriques de voile, pour préparer la mer.", "Sailing theory lessons, to get ready for the sea.",
                    "Segeltheorie, zur Vorbereitung aufs Wasser.", "Lezioni teoriche di vela, per prepararsi al mare.",
                    "Clases teóricas de vela, para preparar la mar.", "Aulas teóricas de vela, para preparar o mar."],
        "v_stages": ["Voir les stages", "See courses", "Kurse ansehen", "Vedi i corsi", "Ver los cursos", "Ver os cursos"],
        "v_regates": ["Voir les régates", "See regattas", "Regatten ansehen", "Vedi le regate", "Ver las regatas", "Ver as regatas"],
        "v_cours": ["Voir les cours", "See lessons", "Unterricht ansehen", "Vedi le lezioni", "Ver las clases", "Ver as aulas"],
        "c_leman": ["Carte du Léman", "Lake Geneva map", "Karte des Genfersees", "Mappa del Lemano", "Mapa del Lemán", "Mapa do Lemano"],
        "l_leman": ["Préparer une sortie sur le lac.", "Plan an outing on the lake.", "Einen Ausflug auf dem See planen.",
                    "Preparare un'uscita sul lago.", "Preparar una salida en el lago.", "Preparar uma saída no lago."],
        "c_regles": ["Règles de course", "Racing rules", "Wettsegelregeln", "Regole di regata", "Reglas de regata", "Regras de regata"],
        "l_regles": ["Les règles, expliquées en clair.", "The rules, explained plainly.", "Die Regeln, klar erklärt.",
                     "Le regole, spiegate con chiarezza.", "Las reglas, explicadas con claridad.", "As regras, explicadas com clareza."],
        "c_lexique": ["Lexique", "Glossary", "Glossar", "Glossario", "Glosario", "Glossário"],
        "l_lexique": ["{t} termes en {g} langues.", "{t} terms in {g} languages.", "{t} Begriffe in {g} Sprachen.",
                      "{t} termini in {g} lingue.", "{t} términos en {g} idiomas.", "{t} termos em {g} idiomas."],
        "c_ports": ["Carte des ports", "Port map", "Hafenkarte", "Mappa dei porti", "Mapa de puertos", "Mapa de portos"],
        "l_ports": ["{n} ports et marinas.", "{n} ports and marinas.", "{n} Häfen und Marinas.",
                    "{n} porti e marine.", "{n} puertos y marinas.", "{n} portos e marinas."],
        "c_bateaux": ["Bateaux", "Boats", "Boote", "Barche", "Barcos", "Barcos"],
        "l_bateaux": ["{n} bateaux, pièce par pièce.", "{n} boats, part by part.", "{n} Boote, Teil für Teil.",
                      "{n} barche, pezzo per pezzo.", "{n} barcos, pieza a pieza.", "{n} barcos, peça a peça."],
        "c_chants": ["Chants de marins", "Sea shanties", "Seemannslieder", "Canti di marinai", "Cantos de marineros", "Cantos de marinheiros"],
        "l_chants": ["{n} chants de marins, présentés un à un.", "{n} sea shanties, presented one by one.", "{n} Seemannslieder, einzeln vorgestellt.",
                     "{n} canti di marinai, presentati uno a uno.", "{n} cantos de marineros, presentados uno a uno.", "{n} cantos de marinheiros, apresentados um a um."],
        "r_titre": ["Réseaux", "Social networks", "Soziale Netzwerke", "Social", "Redes", "Redes"],
        "r_date": ["relevé le", "as of", "Stand:", "rilevato il", "datos del", "dados de"],
        "r_abo": ["abonnés", "followers", "Follower", "follower", "seguidores", "seguidores"],
        "r_vues": ["vues mesurées", "measured views", "gemessene Aufrufe", "visualizzazioni misurate", "visualizaciones medidas", "visualizações medidas"],
        "r_vues_d": ["≈ {t} au total, Instagram estimé", "≈ {t} in total, Instagram estimated", "≈ {t} insgesamt, Instagram geschätzt",
                     "≈ {t} in totale, Instagram stimato", "≈ {t} en total, Instagram estimado", "≈ {t} no total, Instagram estimado"],
        "r_cont": ["contenus publiés", "posts published", "veröffentlichte Beiträge", "contenuti pubblicati", "contenidos publicados", "conteúdos publicados"],
        "r_cont_d": ["publications Instagram et vidéos YouTube", "Instagram posts and YouTube videos", "Instagram-Beiträge und YouTube-Videos",
                     "post Instagram e video YouTube", "publicaciones de Instagram y vídeos de YouTube", "publicações do Instagram e vídeos do YouTube"],
        "s_titre": ["Site", "Site", "Website", "Sito", "Sitio", "Site"],
        "s_date": ["compté le", "counted on", "gezählt am", "contato il", "contado el", "contado em"],
        "s_off": ["offres de stage", "course offers", "Kursangebote", "offerte di corsi", "ofertas de cursos", "ofertas de cursos"],
        "s_eco": ["écoles, dans {p} pays", "schools, in {p} countries", "Schulen, in {p} Ländern", "scuole, in {p} paesi", "escuelas, en {p} países", "escolas, em {p} países"],
        "s_reg": ["régates à venir", "upcoming regattas", "kommende Regatten", "regate in programma", "regatas próximas", "regatas a seguir"],
        "k_jeux": ["Jeux", "Games", "Spiele", "Giochi", "Juegos", "Jogos"],
        "k_fav": ["Favoris", "Favorites", "Favoriten", "Preferiti", "Favoritos", "Favoritos"],
        "k_compte": ["Mon compte", "My account", "Mein Konto", "Il mio account", "Mi cuenta", "Minha conta"],
        "k_ann": ["Annonceurs", "Advertise", "Werben", "Pubblicità", "Anunciar", "Anunciar"],
        "cook_t": ["Aucun cookie de mesure ni de publicité.", "No analytics or advertising cookies.", "Keine Mess- oder Werbe-Cookies.",
                   "Nessun cookie di misurazione o pubblicità.", "Ninguna cookie de medición ni de publicidad.", "Nenhum cookie de medição ou de publicidade."],
        "cook_l": ["En savoir plus", "Learn more", "Mehr erfahren", "Scopri di più", "Más información", "Saiba mais"],
        "cook_b": ["J'ai compris", "Got it", "Verstanden", "Ho capito", "Entendido", "Entendi"],
    }
    for k, v in P.items():
        for i, l in enumerate(LANGUES):
            s = v[i]
            cle_n = {"l_regates": "regates", "l_bateaux": "bateaux", "l_ports": "ports", "l_chants": "chants"}.get(k)
            s = (s.replace("{o}", _n(x["offres"], l))
                   .replace("{n}", _n(x[cle_n], l) if cle_n else "{n}")
                   .replace("{p}", _n(x["pays_regates"] if k == "l_regates" else x["pays_offres"], l))
                   .replace("{t}", _n(x["termes"], l) if k == "l_lexique" else T[l]["_tot"])
                   .replace("{g}", str(x["langues"])))
            T[l][k] = s
    for l in LANGUES:
        T[l].pop("_tot")
    return T


# --------------------------------------------------------------------------- pictogrammes (24 × 24, trait)
PICTO = {
    "stages": '<path d="M12 3v14M12 4c4 2 6 6 6 11h-6M12 7c-3 2-5 5-5 8h5M4 19h16l-2 2H6z"/>',
    "regates": '<path d="M6 21V4M6 4h11l-2 4 2 4H6"/>',
    "cours": '<path d="M4 5h6a2 2 0 0 1 2 2v13a2 2 0 0 0-2-2H4zM20 5h-6a2 2 0 0 0-2 2v13a2 2 0 0 1 2-2h6z"/>',
    "leman": '<path d="M12 21s-6-5.5-6-10a6 6 0 0 1 12 0c0 4.5-6 10-6 10z"/><circle cx="12" cy="11" r="2"/>',
    "regles": '<path d="M5 4h14v16H5zM9 9h6M9 13h6M9 17h3"/>',
    "lexique": '<path d="M3 19 8 5l5 14M5 14h6M16 8h5M16 12h5M16 16h5"/>',
    "ports": '<circle cx="12" cy="5" r="2"/><path d="M12 7v14M7 11h10M5 15c0 3 3 6 7 6s7-3 7-6"/>',
    "bateaux": '<path d="M3 15h18l-3 5H6zM12 3v12M12 4l6 9h-6"/>',
    "chants": '<path d="M9 18V5l10-2v13"/><circle cx="6.5" cy="18" r="2.5"/><circle cx="16.5" cy="16" r="2.5"/>',
}


def _svg(nom: str) -> str:
    return ('<svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.6" '
            'stroke-linecap="round" stroke-linejoin="round">' + PICTO[nom] + "</svg>")


CSS = """
.tete{max-width:62rem;margin:0 auto;padding:2.4rem 1.4rem 1.6rem;text-align:left}
.tete .marque{margin:0 0 .6rem;font-size:.78rem;font-weight:800;letter-spacing:.16em;text-transform:uppercase;color:#e23a3e}
.tete h1{display:block;font-size:clamp(1.7rem,5.6vw,2.9rem);line-height:1.08;letter-spacing:-.02em;text-transform:none;
  font-weight:800;max-width:40rem;text-wrap:balance}
.tete .sous{margin:.8rem 0 0;color:#9db2c6;font-size:.95rem}
.cases{max-width:62rem;margin:0 auto;padding:0 1.4rem;display:grid;gap:.9rem;grid-template-columns:repeat(3,1fr)}
.cases-2{margin-top:.9rem}
.case{display:flex;flex-direction:column;gap:.35rem;padding:1.1rem 1.2rem;background:rgba(10,26,43,.82);
  border:1px solid rgba(126,214,214,.2);border-radius:4px;color:#eef3f7;min-width:0}
.case:hover,.case:focus-visible{border-color:#e23a3e;background:rgba(15,36,56,.95)}
.case:focus-visible{outline:2px solid #a8ecec;outline-offset:3px}
.case svg{width:1.7rem;height:1.7rem;color:#e23a3e;flex:0 0 auto}
.case b{font-size:1.02rem;letter-spacing:.01em}
.case span.l{font-size:.86rem;line-height:1.35;color:#9db2c6}
.case-grande{min-height:11.5rem;border-top:3px solid #e23a3e;padding:1.4rem}
.case-grande svg{width:2.8rem;height:2.8rem}
.case-grande b{font-size:1.5rem;letter-spacing:-.01em}
.case-grande span.l{font-size:.95rem;color:#c9d6e2}
.case-grande .v{margin-top:auto;font-size:.8rem;font-weight:700;letter-spacing:.1em;text-transform:uppercase;color:#eef3f7}
.chiffres-2026{max-width:62rem;margin:2.4rem auto 0;padding:0 1.4rem;display:grid;gap:1.4rem;grid-template-columns:3fr 2fr}
.blocn{border-top:1px solid rgba(226,58,62,.55);padding-top:.8rem;background:rgba(6,18,33,.6)}
.blocn h2{margin:0;font-size:.82rem;letter-spacing:.14em;text-transform:uppercase;color:#eef3f7}
.blocn .date{margin:.15rem 0 .9rem;font-size:.78rem;color:#9db2c6}
.nombres{display:grid;gap:1rem;grid-template-columns:repeat(3,1fr)}
.blocn-site .nombres{grid-template-columns:repeat(3,1fr)}
.nombre b{display:block;font-size:clamp(1.5rem,3.4vw,2.2rem);font-weight:300;letter-spacing:-.02em;color:#fff;line-height:1.05}
.nombre span{display:block;margin-top:.3rem;font-size:.82rem;color:#eef3f7}
.nombre small{display:block;margin-top:.2rem;font-size:.7rem;line-height:1.3;color:#9db2c6}
.liens-sobres{max-width:62rem;margin:1.8rem auto 0;padding:0 1.4rem;display:flex;flex-wrap:wrap;gap:.5rem 1.4rem;font-size:.88rem;color:#9db2c6}
.liens-sobres a{border-bottom:1px dotted rgba(159,179,200,.5)}
.liens-sobres a:hover{color:#fff}
@media (max-width:760px){
  .cases{grid-template-columns:1fr;gap:.6rem}
  .cases-2{margin-top:.6rem}
  .case-grande{min-height:0;flex-direction:row;flex-wrap:wrap;align-items:center;column-gap:.9rem;row-gap:.1rem;padding:1rem 1.1rem}
  .case-grande svg{width:2.2rem;height:2.2rem}
  .case-grande b{flex:1 1 0}
  .case-grande span.l{flex:1 0 100%}
  .case-grande .v{display:none}
  .case{padding:.8rem 1rem}
  .tete{padding:1.4rem 1.4rem 1rem}
  .chiffres-2026{grid-template-columns:1fr}
  .nombres{grid-template-columns:1fr 1fr 1fr;gap:.7rem}
}
@media (max-width:420px){.nombres{grid-template-columns:1fr 1fr}}
"""


def _case(grande: bool, nom: str, href: str, plus: str = "") -> str:
    cls = "case case-grande" if grande else "case"
    v = f'<span class="v" data-t="v_{nom}"></span>' if grande else ""
    return (f'<a class="{cls}" href="{href}" target="_blank" rel="noopener">{_svg(nom)}'
            f'<b data-t="c_{nom}"></b><span class="l" data-t="l_{nom}"></span>{v}</a>')


def corps(x: dict, T: dict) -> str:
    """Le HTML français ; la page se traduit ensuite par data-t à partir de T (même table, six langues)."""
    f = T["fr"]
    # on pose le texte français dans le HTML : lisible sans JavaScript, et par les moteurs de recherche
    def cas(grande, nom, href):
        h = _case(grande, nom, href)
        return re.sub(r'data-t="([^"]+)"></(b|span)>', lambda m: f'data-t="{m.group(1)}">{f[m.group(1)]}</{m.group(2)}>', h)

    grandes = "".join(cas(True, n, h) for n, h in [("stages", "stages.html"), ("regates", "regates.html"), ("cours", "cours.html")])
    petites = "".join(cas(False, n, h) for n, h in [("leman", "carte.html"), ("regles", "regles-de-course.html"), ("lexique", "lexique.html"),
                                                      ("ports", "ports.html"), ("bateaux", "bateaux.html"), ("chants", "chants-de-marin.html")])

    def nb(cle_n, cle_l, cle_d=None, exact=""):
        d = f'<small data-t="{cle_d}">{f[cle_d]}</small>' if cle_d else ""
        t = f' title="{exact}"' if exact else ""
        return f'<div class="nombre"><b data-t="{cle_n}"{t}>{f[cle_n]}</b><span data-t="{cle_l}">{f[cle_l]}</span>{d}</div>'

    fr_n = lambda v: _n(v, "fr")
    reseaux = (
        '<div class="blocn blocn-reseaux"><h2><span data-t="r_titre">%s</span></h2>'
        '<p class="date"><span data-t="r_date">%s</span> <span data-t="rdate">%s</span></p><div class="nombres">%s%s%s</div></div>'
    ) % (f["r_titre"], f["r_date"], f["rdate"],
         nb("n_abo", "r_abo", "abo_d", fr_n(x["abonnes"])),
         nb("n_vues", "r_vues", "r_vues_d", fr_n(x["vues_mesurees"])),
         nb("n_cont", "r_cont", "r_cont_d"))
    site = (
        '<div class="blocn blocn-site"><h2><span data-t="s_titre">%s</span></h2>'
        '<p class="date"><span data-t="s_date">%s</span> <span data-t="sdate">%s</span></p><div class="nombres">%s%s%s</div></div>'
    ) % (f["s_titre"], f["s_date"], f["sdate"],
         nb("n_off", "s_off"), nb("n_eco", "s_eco"), nb("n_reg", "s_reg"))
    liens = "".join(f'<a href="{h}" target="_blank" rel="noopener" data-t="{k}">{f[k]}</a>' for k, h in
                    [("k_jeux", "jeux.html"), ("k_fav", "mes-favoris.html"), ("k_compte", "mon-compte.html"), ("k_ann", "annonceurs.html")])
    # les mêmes adresses de réseaux que l'ancien accueil, en liens sobres (noms propres, pas de traduction)
    reso = "".join(f'<a href="{h}" target="_blank" rel="noopener">{n}</a>' for n, h in
                   [("Facebook", "https://www.facebook.com/SailingMore"), ("Instagram", "https://www.instagram.com/sailingmorehere/"),
                    ("YouTube", "https://www.youtube.com/@SailingMore"), ("Telegram", "https://t.me/sailingmorehere"),
                    ("X", "https://x.com/SailingMore")])
    liens += reso
    return f"""<!--accueil-2026-->
<style id="accueil-2026">{CSS}</style>
<section class="tete"><p class="marque">Sailing More</p><h1 data-t="h1">{f['h1']}</h1><p class="sous" data-t="sous">{f['sous']}</p></section>

<section class="cases cases-1" aria-label="Stages, régates, cours">{grandes}</section>
<section class="cases cases-2" aria-label="Carte du Léman, règles, lexique, ports, bateaux, chants">{petites}</section>

<section class="chiffres-2026" aria-label="Chiffres">{reseaux}{site}</section>
<nav class="liens-sobres" aria-label="Jeux, favoris, compte, annonceurs">{liens}</nav>

<div class="cookies" id="cookies" hidden>
  <p><span data-t="cook_t">{f['cook_t']}</span> <a href="confidentialite.html" data-t="cook_l" target="_blank" rel="noopener">{f['cook_l']}</a></p>
  <button id="cookies-ok" data-t="cook_b">{f['cook_b']}</button>
</div>

<footer>
  <a href="stages.html" target="_blank" rel="noopener">Stages · Courses</a>
  <a href="regates.html" target="_blank" rel="noopener">Régates · Regattas</a>
  <a href="cours.html" target="_blank" rel="noopener">Cours · Lessons</a>
  <a href="regles-de-course.html" target="_blank" rel="noopener">Règles · Rules</a>
  <a href="lexique.html" target="_blank" rel="noopener">Lexique · Glossary</a>
  <a href="mentions-legales.html" target="_blank" rel="noopener">Mentions légales · Legal notice</a>
  <a href="confidentialite.html" target="_blank" rel="noopener">Confidentialité · Privacy</a>
  <a href="delete.html" target="_blank" rel="noopener">Suppression de données · Data deletion</a>
  <span>© 2026 Sailing More</span>
</footer>
</div>

<script>
const T = {json.dumps(T, ensure_ascii=False, separators=(",", ":"))};
function choisir() {{
  const l = (typeof window.smLangue === "function") ? window.smLangue() : "en";
  if (l === "bzh") return "fr";
  return T[l] ? l : "en";
}}
function appliquer(l) {{
  const d = T[l] || T.en;
  document.documentElement.lang = l;
  document.title = d.titre;
  document.querySelectorAll("[data-t]").forEach(el => {{ const v = d[el.dataset.t]; if (v !== undefined) el.textContent = v; }});
  let c = null; try {{ c = localStorage.getItem("sm-langue"); }} catch (e) {{}}
  document.querySelectorAll("#langues button").forEach(b => b.setAttribute("aria-pressed", String(b.dataset.lang === (c || "auto"))));
}}
document.querySelectorAll("#langues button").forEach(b => b.addEventListener("click", () => {{
  try {{ localStorage.setItem("sm-langue", b.dataset.lang); }} catch (e) {{}}
  appliquer(b.dataset.lang === "auto" ? choisir() : b.dataset.lang);
}}));
(function () {{
  const b = document.getElementById("cookies");
  if (!b) return;
  let vu = null; try {{ vu = localStorage.getItem("sm-cookies"); }} catch (e) {{}}
  if (!vu) b.hidden = false;
  document.getElementById("cookies-ok").addEventListener("click", () => {{
    try {{ localStorage.setItem("sm-cookies", "1"); }} catch (e) {{}}
    b.setAttribute("hidden", ""); b.style.display = "none";
  }});
}})();
appliquer(choisir());
</script>
</body>
</html>
"""


# --------------------------------------------------------------------------- assemblage
PRIORITE = ["index.html", "stages.html", "regates.html", "cours.html"]


def _ordonner_menu(mid: str) -> str:
    """Le menu suit l'ordre des priorités : accueil, stages, régates, cours, puis le reste, dans son ordre."""
    m = re.search(r'(<nav aria-label="Toutes les pages du site">)(.*?)(</nav>)', mid, re.S)
    if not m:
        return mid
    liens = re.findall(r"<a .*?</a>", m.group(2), re.S)
    cle = lambda a: re.search(r'href="([^"]+)"', a).group(1)
    tete = [a for p in PRIORITE for a in liens if cle(a) == p]
    reste = [a for a in liens if cle(a) not in PRIORITE]
    return mid[:m.start(2)] + "".join(tete + reste) + mid[m.end(2):]


def refondre(html: str, racine: Path) -> str:
    """Prend une page d'accueil (ancienne ou déjà refondue), garde son gabarit, remplace tout le corps."""
    x = mesures(racine)
    T = textes(x)
    i_body = html.index("<body>") + len("<body>")
    i_contenu = html.index('<div class="contenu">')
    i_fin = min(i for i in (html.find("<!--accueil-2026-->"), html.find('<section class="hero')) if i >= 0)
    mid = _ordonner_menu(html[i_contenu:i_fin])
    # les titres et la description du gabarit suivent la nouvelle promesse
    tete = html[:i_body]
    tete = re.sub(r"<title>.*?</title>", f"<title>{T['fr']['titre']}</title>", tete, flags=re.S)
    desc = "Stages, régates et cours de voile : les offres de stage, le calendrier des régates, les règles de course, le lexique."
    tete = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{desc}">', tete)
    tete = re.sub(r'<meta property="og:title" content="[^"]*">', '<meta property="og:title" content="Sailing More — stages, régates et cours de voile">', tete)
    tete = re.sub(r'<meta property="og:description" content="[^"]*">', f'<meta property="og:description" content="{desc}">', tete)
    return tete + "\n\n" + mid + corps(x, T)


def main() -> int:
    racine = Path(__file__).resolve().parents[1]
    cible = racine / "projets/sailingmore/site/index.html"
    neuf = refondre(cible.read_text(encoding="utf-8"), racine)
    cible.write_text(neuf, encoding="utf-8")
    x = mesures(racine)
    print(f"écrit {cible} · {len(neuf.encode('utf-8'))} octets")
    for k, v in x.items():
        print(f"  {k} = {v}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
