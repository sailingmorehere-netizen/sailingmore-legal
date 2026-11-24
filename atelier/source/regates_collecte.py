#!/usr/bin/env python3
"""Calendrier des régates de Sailing More : collecte les sources, écrit un JSON unique.

Une seule sortie : `projets/sailingmore/regates.json`, lue par `regates_page.py`.
Chaque source est collectée séparément, mise en cache dans `cache/rhum/regates-brut/`,
puis toutes sont normalisées et fusionnées ici — un seul endroit décide du format.

    python3 scripts/regates_collecte.py                 # collecte + fusion
    python3 scripts/regates_collecte.py --sans-reseau   # refusionne le cache existant
    python3 scripts/regates_collecte.py --forcer        # écrit malgré une baisse contrôlée

Le fichier n'est remplacé que si les comptes par relevé et le total tiennent face à
`cache/rhum/regates-veille.json` ; sinon l'ancien `regates.json` reste en place et le code
de sortie est 1.

Les sources, du plus large au plus précis :

1. **Manage2Sail** (`manage2sail.com/en-US/search?filterYear=…&page=…`) — le plus gros
   bloc : des milliers d'épreuves tous pays, y compris le calendrier ACVL du Léman et
   l'essentiel de la saison suisse 2027. Table HTML : année | début | fin | nom | état |
   pays | ville | club.
2. **FFVoile** (`regates.ffvoile.fr/api/competitions`) — le calendrier fédéral français,
   avec club, comité départemental, ligue et classes. API JSON ouverte, calendrier publié
   jusqu'à fin décembre seulement.
3. **ACVL** (`acvl.ch/association/calendrier-des-regates/`) — les régates lémaniques, avec
   leurs liens Manage2Sail (informations, inscription, résultats).
4. **World Sailing** (`datafeed.sailing.org/stats/api/regatta`) — les épreuves classées
   internationales, dont la saison 2027.
5. **spencer.club** (`/en-US/calendar`) — la course au large 2026-2028, seule source
   structurée qui donne 2027 côté océan (Spi Ouest, Paprec 600, CIC, 52 Super Series…).
6. **Notre fonds propre** : `cache/rhum/calendrier-connu.json` et `CALENDRIER` de
   `courses_du_jour.py` — les épreuves déjà décrites par le blog, avec leur notoriété.
"""
from __future__ import annotations

import json
import os
import re
import sys
import time
import unicodedata
import urllib.parse
import urllib.request
import html as H
from datetime import date, datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
# Les puces de filtre de la page : une seule liste, tenue par la page. Une région que la
# collecte produirait sans puce serait inatteignable par les filtres (cas de l'Isère, 21/11).
from regates_page import REGIONS as PUCES  # noqa: E402
# Le pays quand aucune source ne le donne (22/11/2026) : sans lui, une épreuve à Lorient reste
# dans « Monde » et sans drapeau. Table locale + cache OpenStreetMap, voir le module.
import regates_lieux  # noqa: E402

ICI = Path("/opt/data")
BRUT = ICI / "cache/rhum/regates-brut"
SORTIE = ICI / "projets/sailingmore/regates.json"
UA = {"User-Agent": "Mozilla/5.0 (compatible; SailingMore/1.0; +https://sailingmore.fr)"}
MOIS = {
    "janvier": 1, "février": 2, "fevrier": 2, "mars": 3, "avril": 4, "mai": 5, "juin": 6,
    "juillet": 7, "août": 8, "aout": 8, "septembre": 9, "octobre": 10, "novembre": 11,
    "décembre": 12, "decembre": 12,
}


def lit(url: str, essais: int = 3, attente: int = 3) -> str:
    dernier = None
    for n in range(essais):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=90) as r:
                return r.read().decode("utf-8", "ignore")
        except Exception as e:  # noqa: BLE001
            dernier = e
            time.sleep(attente * (n + 1))
    raise RuntimeError(f"{url} : {dernier}")


def sans_accent(t: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFKD", t or "") if not unicodedata.combining(c))


def cle(t: str) -> str:
    return re.sub(r"[\W_]+", "", sans_accent(t).lower())


# ─────────────────────────────────────────────────────────────── Manage2Sail


def manage2sail(annee: int) -> list[dict]:
    """Relève toutes les pages d'une année. ~15 événements par page."""
    sortie = []
    premiere = lit(f"https://www.manage2sail.com/en-US/search?filterYear={annee}&page=1")
    m = re.search(r"filterYear=\d+&amp;page=(\d+)\">Last", premiere)
    dernieres = int(m.group(1)) if m else 1
    for pg in range(1, dernieres + 1):
        h = premiere if pg == 1 else lit(
            f"https://www.manage2sail.com/en-US/search?filterYear={annee}&page={pg}")
        for tr in re.findall(r"(?s)<tr>(.*?)</tr>", h):
            tds = re.findall(r"(?s)<td[^>]*>(.*?)</td>", tr)
            if len(tds) < 7:
                continue

            def txt(s):
                return H.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", s))).strip()

            lien = re.search(r'href="(/[a-z]{2}-[A-Z]{2}/event/[0-9a-f-]{36})"', tds[3])
            d, f = txt(tds[1]), txt(tds[2])
            if not re.match(r"\d{2}\.\d{2}\.", d):
                continue
            j1, m1 = d[:5].split(".")
            j2, m2 = f[:5].split(".")
            sortie.append(
                {
                    "nom": txt(tds[3]),
                    "debut": f"{annee}-{m1}-{j1}",
                    "fin": f"{annee}-{m2}-{j2}",
                    "etat": txt(tds[4]),
                    "pays": txt(tds[5]),
                    "ville": txt(tds[6]) if len(tds) > 6 else "",
                    "club": txt(tds[7]) if len(tds) > 7 else "",
                    "lien": "https://www.manage2sail.com" + lien.group(1) if lien else "",
                }
            )
        print(f"  manage2sail {annee} : page {pg}/{dernieres}", flush=True)
    return sortie


# ────────────────────────────────────────────────────────────────────── FFVoile


def ffvoile(annee: int) -> list[dict]:
    sortie, page = [], 1
    while page <= 80:
        url = ("https://regates.ffvoile.fr/api/competitions?"
               f"dateDebutMin={annee}-01-01&dateDebutMax={annee}-12-31"
               f"&limit=100&page={page}&sortOrder=ASC")
        d = json.loads(lit(url))
        for c in d.get("data", []):
            club = c.get("club") or {}
            cdv = c.get("cdv") or {}
            # Le code du club commence par le département (`76010` → 76) : c'est la seule
            # géographie fiable de cette API, `cdv` étant vide ou « 99 » pour les épreuves
            # fédérales.
            dep = (cdv.get("nomCourt") or "").strip()
            if not dep or dep == "99":
                dep = (club.get("code") or "")[:2]
            sortie.append(
                {
                    "nom": (c.get("competitionNom") or "").strip(),
                    "debut": (c.get("dateDebut") or "")[:10],
                    "fin": (c.get("dateFin") or c.get("dateDebut") or "")[:10],
                    "pays": "FRA",
                    "ville": "",
                    "club": (club.get("nom") or "").strip(),
                    "cdv": (cdv.get("nom") or "").strip(),
                    "departement": dep,
                    "ligue": ((c.get("ligue") or {}).get("nom") or "").strip(),
                    "classes": [b.get("code") for b in c.get("bateaux") or [] if b.get("code")],
                    "annulee": bool(c.get("competitionAnnulee")),
                    "lien": f"https://regates.ffvoile.fr/competitions/{c.get('competitionId')}/",
                }
            )
        meta = d.get("meta") or {}
        if page >= int(meta.get("lastPage") or 1):
            break
        page += 1
    return sortie


# ───────────────────────────────────────────────────────────────────────── ACVL


def acvl() -> list[dict]:
    h = lit("https://www.acvl.ch/association/calendrier-des-regates/")
    sortie = []
    for date_txt, nom, lieu_club, bloc in re.findall(
        r"(?s)event-date'>([^<]+)</span><h4>(.*?)</h4><h5>(.*?)</h5>(.*?)</div>", h
    ):
        nom = H.unescape(re.sub(r"<[^>]+>", "", nom)).strip()
        lieu_club = H.unescape(re.sub(r"<[^>]+>", "", lieu_club)).strip()
        mm = re.match(r"(\d{1,2})\s+(\w+)\s+(\d{4})", date_txt.strip())
        if not mm or not nom:
            continue
        jour, mois, annee = int(mm.group(1)), MOIS.get(sans_accent(mm.group(2)).lower()), int(mm.group(3))
        if not mois:
            continue
        liens = dict(
            (t, u) for u, t in re.findall(r"href='([^']+)'[^>]*>([^<]+)<", bloc)
        )
        lieu, _, club = lieu_club.partition(" - ")
        sortie.append(
            {
                "nom": nom,
                "debut": date(annee, mois, jour).isoformat(),
                "fin": date(annee, mois, jour).isoformat(),
                "pays": "SUI",
                "ville": lieu.strip(),
                "club": club.strip(),
                "lien": liens.get("information") or liens.get("inscription") or "",
                "resultats": liens.get("résultats") or "",
            }
        )
    return sortie


# ──────────────────────────────────────────────────────────────── World Sailing


def worldsailing() -> list[dict]:
    base = "https://datafeed.sailing.org/stats/api/regatta"
    params = {
        "filter[endDate]": date.today().isoformat() + " 00:00:00",
        "filterOptions[endDate]": "greaterThanEqualTo",
        "include": "venue.country,level",
        "sort[startDate]": "asc",
        "paginate": 100,
    }
    sortie = []
    for page in range(1, 21):  # limite dure : 20 pages
        params["page"] = page
        d = json.loads(lit(base + "?" + urllib.parse.urlencode(params)))
        data = d.get("data", [])
        if not data:
            break
        for r in data:
            v = r.get("venue") or {}
            pays = v.get("country") or {}
            sortie.append(
                {
                    "nom": r.get("name") or r.get("_admin_name") or "",
                    "debut": (r.get("startDate") or "")[:10],
                    "fin": (r.get("endDate") or r.get("startDate") or "")[:10],
                    "pays": pays.get("code") or "",
                    "ville": v.get("name") or "",
                    "niveau": (r.get("level") or {}).get("name") or "",
                    "lien": f"https://www.sailing.org/events/{r.get('slug') or ''}",
                }
            )
        if len(data) < 100:
            break
    return sortie


# ─────────────────────────────────────────────────────────────────── spencer


def spencer() -> list[dict]:
    h = lit("https://www.spencer.club/en-US/calendar")
    morceaux = re.findall(r'self\.__next_f\.push\(\[1,(".*?")\]\)', h, re.S)
    blob = ""
    for c in morceaux:
        try:
            blob += json.loads(c)
        except Exception:  # noqa: BLE001
            pass
    i = blob.find('"allRaces":[')
    if i < 0:
        return []
    j = blob.index("[", i + len('"allRaces":'))
    prof, k, dans = 0, j, False
    while k < len(blob):
        ch = blob[k]
        if ch == '"' and blob[k - 1] != "\\":
            dans = not dans
        if not dans:
            if ch == "[":
                prof += 1
            elif ch == "]":
                prof -= 1
                if prof == 0:
                    break
        k += 1
    try:
        races = json.loads(blob[j:k + 1].replace("$D", "").replace("$undefined", "null"))
    except Exception:  # noqa: BLE001
        return []
    return [
        {
            "nom": r.get("raceName") or "",
            "debut": (r.get("startDate") or "")[:10],
            "fin": (r.get("endDate") or r.get("startDate") or "")[:10],
            "pays": "",
            "ville": r.get("departure") or "",
            "classes": [c.get("name") for c in r.get("classes") or [] if c.get("name")],
            "lien": f"https://www.spencer.club/en-US/calendar/{r.get('raceSlug')}/{r.get('year')}",
            "ocean": True,
        }
        for r in races
    ]


# ─────────────────────────────────────────────────────── notre fonds de courses


def majeures() -> list[dict]:
    """Les épreuves vérifiées à la main, qu'aucune API ne donne (21/11/2026).

    Bol d'Or, 5 Jours du Léman, Voiles de Saint-Tropez : leurs dates sont publiées sur le
    site de l'organisateur un an à l'avance, jamais dans un flux. Chaque entrée porte sa
    date de vérification et la phrase qui la justifie — une date sans source ici est une
    invention, et on n'en veut pas dans un calendrier.
    """
    f = ICI / "projets/sailingmore/regates-majeures.json"
    if not f.exists():
        return []
    return json.loads(f.read_text())


def fonds_propre() -> list[dict]:
    sortie = []
    connu = ICI / "cache/rhum/calendrier-connu.json"
    if connu.exists():
        for c in json.loads(connu.read_text()):
            sortie.append(
                {
                    "nom": c.get("nom") or "",
                    "debut": c.get("debut") or "",
                    "fin": c.get("fin") or c.get("debut") or "",
                    "pays": "",
                    "ville": c.get("sous_en") or "",
                    "lien": c.get("source") or "",
                    "connue": c.get("connue") or "",
                }
            )
    return sortie


# ─────────────────────────────────────────────────────────────── normalisation

# Stages, formations, entraînements, assemblées : présents dans Manage2Sail, ce ne sont
# pas des régates. On les garde mais marqués, pour que la page puisse les écarter.
MOTS_HORS_REGATE = (
    "formation", "fortbildung", "training", "stage", "theorie", "wochenende", "lehrgang",
    "assemblee", "ag", "reunion", "generalversammlung", "workshop", "seminar",
    "test de connaissances", "entrainement", "schulung", "kontrolle", "abnahme",
    "pruefung",
)
# L'allemand colle ses mots : « Wintertraining », « Regattatraining » ne sont pas des régates et
# l'ancien `\b…\b` les laissait passer (constaté le 22/11/2026 sur « Wind und Natur
# (Wintertraining) »). Ces mots-là se cherchent donc en fin de mot composé, sans barrière à gauche.
MOTS_EN_COMPOSE = ("training", "lehrgang", "schulung", "seminar", "fortbildung", "entrainement")
LEMAN = [
    "versoix", "pully", "morges", "estavayer", "hermance", "nernier", "sciez", "rolle",
    "nyon", "vevey", "la tour-de-peilz", "cully", "lausanne", "vidy", "villeneuve",
    "thonon", "evian", "yvoire", "st-prex", "preverenges", "clarens", "montreux",
    "chavannes", "crans", "buchillon", "allaman", "lonay", "st-sulpice", "sierre",
    "le bouveret", "villeneuve", "vevey-montreux", "mies", "celigny", "coppet", "founex",
    "anieres", "corsier", "meillerie", "lugrin", "maxilly", "amplepuis", "sechex",
    "geneve", "genève", "bellevue", "genthod", "versoye", "chancy", "dardagny", "soral",
]
SUISSE_HORS_LEMAN = [
    "zurich", "zürich", "berne", "bern", "lucerne", "luzern", "bale", "basel", "lugano",
    "lucerne", "bienne", "bier", "neuchatel", "neuchâtel", "fribourg", "stansstad",
    "arbon", "kreuzlingen", "rapperswil", "brienz", "thoune", "spiez", "sarnen",
]
REGIONS_FR = {
    "74": "Haute-Savoie", "73": "Savoie", "01": "Ain", "38": "Isère", "39": "Jura",
}


def region_departement(dep: str) -> tuple[str, str]:
    """Rend (région affichée, région repliée) pour une épreuve française.

    Décision de Nicolas (21/11/2026) : pas de puce par département ; un département connu
    mais sans puce (Isère, Jura) tombe dans « France », et le repli est noté pour que le
    contrôle le compte. La table reste complète : une puce ajoutée à `REGIONS` côté page
    sera alimentée sans retoucher la collecte.
    """
    nom = REGIONS_FR.get(dep or "", "")
    if not nom:
        return "France", ""
    if nom in PUCES:
        return nom, ""
    return "France", nom


def region(p: dict) -> str:
    """Région affichée. Écrit aussi `p["region_repliee"]` (vide s'il n'y a pas eu de repli)."""
    p["region_repliee"] = ""
    v = sans_accent((p.get("ville") or "").lower())
    pays = (p.get("pays") or "").upper()
    if any(k in v for k in LEMAN):
        return "Léman"
    # Une course au large n'est pas une régate française parce qu'elle part de France : la
    # Transat Paprec quitte Concarneau et reste dans « Océan » (sinon le pays trouvé par
    # `regates_lieux` la ferait basculer dans « France », 22/11/2026).
    if p.get("ocean"):
        return "Océan"
    if pays in ("SUI", "CH", "SWITZERLAND") or any(k in v for k in SUISSE_HORS_LEMAN):
        return "Suisse"
    if pays in ("FRA", "FR", "FRANCE"):
        r, p["region_repliee"] = region_departement(p.get("departement") or "")
        return r
    return "Monde"


def type_de(p: dict) -> str:
    t = sans_accent((p.get("nom") or "").lower())
    if p.get("ocean"):
        return "course au large"
    if any(re.search(r"\b" + re.escape(k) + r"s?\b", t) for k in MOTS_HORS_REGATE):
        return "hors-regate"
    if any(re.search(re.escape(k) + r"s?\b", t) for k in MOTS_EN_COMPOSE):
        return "hors-regate"
    nom = (p.get("nom") or "").lower()
    if "championnat" in nom or "world" in nom or "cup" in nom or "troph" in nom:
        return "championnat"
    if "regate de club" in nom or "régate de club" in nom or "interne" in nom:
        return "club"
    return "régate"


def fusionner(listes: list[tuple[str, list[dict]]]) -> list[dict]:
    """Fusionne par (nom normalisé, date de début complète) : deux sources qui décrivent la même
    épreuve ne font qu'une entrée, et les sources s'accumulent dans `sources`."""
    index: dict[tuple, dict] = {}
    limite = date.today().toordinal() + 1100  # au-delà de trois ans, c'est une faute de saisie
    for source, lignes in listes:
        for p in lignes:
            d = (p.get("debut") or "")[:10]
            if len(d) != 10:
                continue
            try:
                if date.fromisoformat(d).toordinal() > limite:
                    continue
            except ValueError:
                continue
            k = (cle(p.get("nom")), d)
            e = {
                "nom": (p.get("nom") or "").strip(),
                "debut": d,
                "fin": max(p.get("fin") or d, d) if (p.get("fin") or d) >= d else d,
                "ville": (p.get("ville") or "").strip(),
                "pays": (p.get("pays") or "").strip().upper(),
                "club": (p.get("club") or "").strip(),
                "classes": p.get("classes") or [],
                "lien": p.get("lien") or "",
                "resultats": p.get("resultats") or "",
                "niveau": p.get("niveau") or "",
                "connue": p.get("connue") or "",
                "annulee": bool(p.get("annulee")),
                "ocean": bool(p.get("ocean")),
                "departement": p.get("departement") or "",
                "ligue": p.get("ligue") or "",
                "sources": [source],
            }
            if len(e["pays"]) != 3 or not e["pays"].isalpha():
                e["pays"] = regates_lieux.pays(e["ville"], e["club"], e["nom"],
                                               [source], e["departement"])
            e["region"] = region(e)
            e["type"] = type_de(e)
            if k in index:
                g = index[k]
                g["sources"] = sorted(set(g["sources"]) | {source})
                for champ in ("ville", "club", "lien", "resultats", "niveau", "connue", "ligue",
                              "pays"):
                    if not g.get(champ) and e.get(champ):
                        g[champ] = e[champ]
                if len(e["classes"]) > len(g["classes"]):
                    g["classes"] = e["classes"]
                if e["fin"] > g["fin"]:
                    g["fin"] = e["fin"]
                if e["ocean"] and not g["ocean"]:
                    g["ocean"] = True
                # une entrée « hors-regate » ne doit pas absorber une vraie régate
                if g["type"] == "hors-regate" and e["type"] != "hors-regate":
                    g["type"] = e["type"]
                # le pays et le large peuvent venir de la seconde source : on reclasse
                if g.get("pays") or g.get("ocean"):
                    g["region"] = region(g)
                    g["type"] = type_de(g)
            else:
                index[k] = e
    out = sorted(index.values(), key=lambda x: (x["debut"], cle(x["nom"])))
    return out


def _flou(e: dict) -> bool:
    """Vrai quand la source ne connaît que le mois ou la saison (« Transat Paprec », 1er janvier)."""
    debut = e["debut"]
    if debut.endswith("-01-01"):
        return True
    try:
        return (date.fromisoformat(e["fin"]) - date.fromisoformat(debut)).days > 45
    except ValueError:
        return False


def _fusionner_deux(g: dict, e: dict) -> dict:
    """Garde les dates de `g`, y prend tout ce que `e` sait de plus. `g` survit."""
    for champ in ("ville", "club", "lien", "resultats", "niveau", "connue", "ligue", "pays",
                  "departement"):
        if not g.get(champ) and e.get(champ):
            g[champ] = e[champ]
    g["classes"] = g["classes"] + [c for c in e["classes"] if c not in g["classes"]]
    g["sources"] = sorted(set(g["sources"]) | set(e["sources"]))
    g["ocean"] = bool(g["ocean"] or e["ocean"])
    g["annulee"] = bool(g["annulee"])
    if e["fin"] > g["fin"]:
        g["fin"] = e["fin"]
    g["region"] = region(g)
    g["type"] = type_de(g)
    return g


def dedoublonner(entrees: list[dict]) -> tuple[list[dict], list[tuple]]:
    """La même course rangée deux fois — deux sources, deux dates, deux régions.

    Constaté le 22/11/2026 : « Transat Paprec » figurait le 1er janvier dans Océan/course au
    large et le 18 avril dans Monde/régate. La fusion de `fusionner` ne peut pas le voir : elle
    apparie sur la date de début exacte, or l'une des deux sources ne connaît que l'année.

    On apparie donc sur (nom, lieu, année d'arrivée) et on ne réunit que deux cas :
      * les sources sont différentes — deux relevés qui décrivent la même épreuve ;
      * l'une des deux est approximative (`_flou`) — « année 2028 » contre une vraie date.
    Deux épreuves du même nom, même lieu, même année, de même source et à dates précises
    restent séparées : ce sont deux manches, pas un doublon.

    L'entrée qui survit est la plus précise, puis celle qui a le plus de sources ; l'autre lui
    donne ses classes, son drapeau et son caractère océanique. Renvoie les fusions faites.
    """
    groupes: dict[tuple, list[dict]] = {}
    seuls: dict[int, dict] = {}
    for e in entrees:
        k = (cle(e["nom"]), cle(e.get("ville") or "") or cle(e.get("club") or ""),
             (e.get("fin") or e["debut"])[:4])
        if not k[0]:
            seuls[id(e)] = e
            continue
        groupes.setdefault(k, []).append(e)

    out: list[dict] = list(seuls.values())
    journal: list[tuple] = []
    for k, lot in groupes.items():
        if len(lot) == 1:
            out.append(lot[0])
            continue
        lot.sort(key=lambda x: (not _flou(x), len(x["sources"]), x["debut"]), reverse=True)
        garde = lot[0]
        for autre in lot[1:]:
            memes_sources = bool(set(garde["sources"]) & set(autre["sources"]))
            if memes_sources and not (_flou(garde) or _flou(autre)):
                out.append(autre)       # deux manches distinctes : on n'y touche pas
                continue
            journal.append((garde["nom"], garde["debut"], autre["debut"],
                            ", ".join(autre["sources"]), garde["region"], autre["region"]))
            garde = _fusionner_deux(garde, autre)
        out.append(garde)
    out.sort(key=lambda x: (x["debut"], cle(x["nom"])))
    return out, journal


# ──────────────────────────────────────────────────────────────── contrôle d'écriture

# Comptes de la veille : « n » (total fusionné, format historique de `maj_regates`) et
# « sources » (entrées brutes par relevé, avant fusion).
VEILLE = ICI / "cache/rhum/regates-veille.json"
PLANCHER_TOTAL = 0.40
# Choisi à la main, non calibré : je n'ai aucune série de comptes quotidiens pour mesurer la
# variation normale d'une source. Un relevé qui tombe sous la moitié de la veille est
# suspect ; à ajuster dès qu'on aura l'historique.
PLANCHER_SOURCE = 0.50


def lire_veille() -> dict:
    """Les comptes de la dernière collecte acceptée ; vide s'il n'y en a pas (premier passage)."""
    try:
        d = json.loads(VEILLE.read_text())
    except (OSError, ValueError):
        return {}
    return d if isinstance(d, dict) else {}


def controler(comptes: dict[str, int], total: int, veille: dict) -> list[str]:
    """Liste des raisons de refuser l'écriture (vide = on peut écrire).

    Le contrôle est par relevé, pas seulement sur le total : Manage2Sail pèse tant que si FFVoile
    ou l'ACVL tombent à zéro, le total reste au-dessus du plancher et la page perd quand même
    une source entière sans que rien ne le dise.
    """
    problemes = []
    n_veille = veille.get("n")
    if isinstance(n_veille, int) and n_veille > 0 and total < n_veille * PLANCHER_TOTAL:
        problemes.append(f"total : {total} épreuves contre {n_veille} à la collecte précédente "
                         f"(plancher {PLANCHER_TOTAL:.0%})")
    precedents = veille.get("sources")
    if not isinstance(precedents, dict):
        # Veille à l'ancien format (total seul) : pas de base par source, on ne devine pas.
        return problemes
    for nom, avant in sorted(precedents.items()):
        # Un relevé absent d'aujourd'hui (l'année qui change) n'est pas une panne ; un relevé
        # nouveau n'a rien à qui se comparer. Seuls ceux présents des deux côtés comptent.
        if nom not in comptes or not isinstance(avant, int) or avant <= 0:
            continue
        if comptes[nom] < avant * PLANCHER_SOURCE:
            problemes.append(f"{nom} : {comptes[nom]} entrées contre {avant} à la collecte précédente "
                             f"(plancher {PLANCHER_SOURCE:.0%})")
    return problemes


def ecrire_atomique(cible: Path, texte: str, relire=None) -> None:
    """Écrit dans un fichier voisin puis renomme : un lecteur voit l'ancien fichier ou le
    nouveau en entier, jamais un fichier à moitié écrit. Même dossier, car `os.replace` n'est
    atomique qu'au sein d'un même système de fichiers.

    `relire`, si fourni, reçoit le texte relu depuis le disque et lève une exception s'il est
    incohérent : le renommage n'a alors pas lieu et l'ancien fichier reste en place."""
    cible.parent.mkdir(parents=True, exist_ok=True)
    tmp = cible.with_name(f"{cible.name}.{os.getpid()}.tmp")
    try:
        with open(tmp, "w", encoding="utf-8") as f:
            f.write(texte)
            f.flush()
            os.fsync(f.fileno())
        if relire:
            relire(tmp.read_text(encoding="utf-8"))
        os.replace(tmp, cible)
    finally:
        tmp.unlink(missing_ok=True)


def ecrire_apres_controle(charge: str, total: int) -> None:
    """Dépose `regates.json` seulement si le fichier temporaire se relit et contient tout."""
    def relire(texte: str) -> None:
        # Un disque plein ou une écriture coupée donnerait un JSON tronqué, qu'il vaut mieux
        # découvrir ici que dans `regates_page.py`.
        n = len(json.loads(texte).get("regates", []))
        if n != total:
            raise RuntimeError(f"fichier temporaire incohérent : {n} épreuves relues pour {total}")
    ecrire_atomique(SORTIE, charge, relire)


def ecrire_veille(comptes: dict[str, int], total: int) -> None:
    """Rangée seulement après l'écriture de `regates.json` : la veille décrit ce qui a été accepté."""
    ecrire_atomique(VEILLE, json.dumps(
        {"date": date.today().isoformat(), "n": total, "sources": comptes},
        ensure_ascii=False))


def main() -> int:
    sans_reseau = "--sans-reseau" in sys.argv
    BRUT.mkdir(parents=True, exist_ok=True)
    annee = date.today().year
    annees = [annee, annee + 1]

    def cache(nom: str, fonction):
        f = BRUT / f"{nom}.json"
        if sans_reseau and f.exists():
            return json.loads(f.read_text())
        try:
            d = fonction()
        except Exception as e:  # noqa: BLE001
            if f.exists():
                print(f"  {nom} : échec ({e}) — on garde le cache de {f.stat().st_mtime:.0f}")
                return json.loads(f.read_text())
            print(f"  {nom} : ÉCHEC {e}")
            return []
        f.write_text(json.dumps(d, ensure_ascii=False))
        print(f"  {nom} : {len(d)} entrées")
        return d

    listes = []
    comptes: dict[str, int] = {}

    def releve(source: str, nom: str, donnees: list[dict]) -> None:
        listes.append((source, donnees))
        comptes[nom] = len(donnees)

    for a in annees:
        releve("manage2sail", f"manage2sail-{a}", cache(f"manage2sail-{a}", lambda a=a: manage2sail(a)))
    for a in annees:
        releve("ffvoile", f"ffvoile-{a}", cache(f"ffvoile-{a}", lambda a=a: ffvoile(a)))
    releve("acvl", "acvl", cache("acvl", acvl))
    releve("worldsailing", "worldsailing", cache("worldsailing", worldsailing))
    releve("spencer", "spencer", cache("spencer", spencer))
    releve("majeures", "majeures", cache("majeures", majeures))
    releve("fonds-propre", "fonds-propre", fonds_propre())
    # Épreuves lues sur des sites de clubs (tâche 62) : {URL source: [épreuves]}, écrit par
    # scripts/regates_clubs.py. Les sources sont l'URL elle-même.
    fc = ICI / "projets/sailingmore/regates-clubs.json"
    if fc.exists():
        for url, lignes in json.loads(fc.read_text()).items():
            releve(url, "club:" + url.split("/")[2], lignes)

    # Le pays des épreuves que leurs sources ne situent pas : quelques villes nouvelles par
    # passage, une fois pour toutes (cache). Sans réseau, on se sert du cache et des tables.
    regates_lieux.completer(listes, limite=40, reseau=not sans_reseau)

    tout = fusionner(listes)
    tout, doublons = dedoublonner(tout)
    if doublons:
        print(f"  doublons réunis : {len(doublons)}")
        for nom, garde, autre, src, r1, r2 in doublons:
            print(f"    {nom} : {garde} gardée ({r1}), {autre} retirée ({src}, {r2})")
    a_venir = [p for p in tout if p["debut"] >= date.today().isoformat()]
    charge = json.dumps(
        {"maj": datetime.now().isoformat(timespec="seconds"), "total": len(tout),
         "a_venir": len(a_venir), "regates": tout},
        ensure_ascii=False, indent=1)

    veille = lire_veille()
    problemes = controler(comptes, len(tout), veille)
    if problemes and "--forcer" in sys.argv:
        print("CONTRÔLE IGNORÉ (--forcer) :")
        for p in problemes:
            print("  - " + p)
        problemes = []
    if problemes:
        # Sur stderr et en dernière ligne : `maj_regates` en cite la dernière ligne dans son
        # message d'échec. Ni `regates.json` ni la veille ne sont touchés.
        print("COLLECTE REFUSÉE · le fichier précédent est conservé, rien n'a été écrit", file=sys.stderr)
        for p in problemes:
            print("  - " + p, file=sys.stderr)
        print(f"{len(problemes)} contrôle(s) en échec (relancer avec --forcer si la baisse est réelle)",
              file=sys.stderr)
        return 1
    ecrire_apres_controle(charge, len(tout))
    ecrire_veille(comptes, len(tout))

    from collections import Counter
    print(f"\n{len(tout)} épreuves, {len(a_venir)} à venir -> {SORTIE}")
    print("par source :", dict(Counter(s for p in tout for s in p["sources"])))
    print("par région :", dict(Counter(p["region"] for p in a_venir)))
    print("par type   :", dict(Counter(p["type"] for p in a_venir)))
    print("années     :", dict(Counter(p["debut"][:4] for p in a_venir)))
    print("replis     :", dict(Counter(p["region_repliee"] for p in a_venir if p["region_repliee"])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
