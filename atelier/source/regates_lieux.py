# © 2026 Sailing More — tous droits réservés. All rights reserved.
"""Le pays d'une épreuve quand aucune source ne le donne.

Trois sources le donnent (Manage2Sail, FFVoile, ACVL) ; World Sailing, spencer.club et notre
fonds propre ne le donnent pas. Sans pays, `regates_collecte.region()` ne peut pas savoir qu'une
épreuve à Lorient est française : elle tombe dans « Monde » et s'affiche sans drapeau
(constaté le 22/11/2026 sur 144 épreuves).

Ce module comble le trou, dans cet ordre — du plus sûr au plus deviné :

1. la source elle-même, quand elle est fédérale : FFVoile = France, ACVL = Suisse ;
2. un nom de pays écrit dans la ville, le club ou le nom (« Amami, Japan ») ;
3. le cache `cache/rhum/villes-pays.json`, rempli par OpenStreetMap (Nominatim) une fois par
   ville inconnue, 1,1 s entre deux appels comme le demande leur politique d'usage ;
4. la même ville ou le même club vus ailleurs avec un pays (Manage2Sail, FFVoile, ACVL, majeures).

Rien trouvé : la fonction rend "", l'épreuve reste dans « Monde » et sans drapeau. On ne devine
jamais un pays par ressemblance de nom de ville — « Newport » existe des deux côtés de l'Atlantique.

`python3 scripts/regates_lieux.py --villes` liste les villes encore inconnues du cache.
"""
from __future__ import annotations

import json
import re
import sys
import time
import unicodedata
import urllib.parse
import urllib.request
from collections import Counter
from pathlib import Path

ICI = Path("/opt/data")
BRUT = ICI / "cache/rhum/regates-brut"
CACHE = ICI / "cache/rhum/villes-pays.json"

# Codes pays du site : ISO 3166 alpha-3, sauf là où World Sailing et la FFVoile écrivent autre
# chose (GER, SUI, NED, DEN, POR, RSA, MAS, INA, PHI, TPE…). C'est cette table qui décide, donc
# le drapeau de `regates_drapeaux.py` et le pays affiché tombent toujours juste.
ISO2 = {
    "AD": "AND", "AE": "UAE", "AF": "AFG", "AG": "ANT", "AL": "ALB", "AM": "ARM", "AO": "ANG",
    "AR": "ARG", "AT": "AUT", "AU": "AUS", "AW": "ARU", "AZ": "AZE", "BA": "BIH", "BB": "BAR",
    "BD": "BAN", "BE": "BEL", "BG": "BUL", "BH": "BRN", "BJ": "BEN", "BM": "BER", "BN": "BRU",
    "BO": "BOL", "BR": "BRA", "BS": "BAH", "BW": "BOT", "BY": "BLR", "BZ": "BIZ", "CA": "CAN",
    "CD": "COD", "CH": "SUI", "CI": "CIV", "CK": "COK", "CL": "CHI", "CM": "CMR", "CN": "CHN",
    "CO": "COL", "CR": "CRC", "CU": "CUB", "CV": "CPV", "CW": "CUW", "CY": "CYP", "CZ": "CZE",
    "DE": "GER", "DJ": "DJI", "DK": "DEN", "DM": "DMA", "DO": "DOM", "DZ": "ALG", "EC": "ECU",
    "EE": "EST", "EG": "EGY", "ES": "ESP", "ET": "ETH", "FI": "FIN", "FJ": "FIJ", "FO": "FRO",
    "FR": "FRA", "GB": "GBR", "GD": "GRN", "GE": "GEO", "GG": "GBR", "GH": "GHA", "GI": "GIB",
    "GL": "GRL", "GM": "GAM", "GN": "GUI", "GP": "FRA", "GQ": "GEQ", "GR": "GRE", "GT": "GUA",
    "GU": "GUM", "GY": "GUY", "HK": "HKG", "HN": "HON", "HR": "CRO", "HT": "HAI", "HU": "HUN",
    "ID": "INA", "IE": "IRL", "IL": "ISR", "IM": "GBR", "IN": "IND", "IQ": "IRQ", "IR": "IRI",
    "IS": "ISL", "IT": "ITA", "JM": "JAM", "JO": "JOR", "JP": "JPN", "KE": "KEN", "KG": "KGZ",
    "KH": "CAM", "KM": "COM", "KN": "SKN", "KR": "KOR", "KW": "KUW", "KY": "CAY", "KZ": "KAZ",
    "LB": "LIB", "LC": "LCA", "LI": "LIE", "LK": "SRI", "LR": "LBR", "LT": "LTU", "LU": "LUX",
    "LV": "LAT", "LY": "LBA", "MA": "MAR", "MC": "MON", "MD": "MDA", "ME": "MNE", "MG": "MAD",
    "MH": "MHL", "MK": "MKD", "ML": "MLI", "MM": "MYA", "MN": "MGL", "MO": "MAC", "MQ": "FRA",
    "MR": "MTN", "MT": "MLT", "MU": "MRI", "MV": "MDV", "MW": "MAW", "MX": "MEX", "MY": "MAS",
    "MZ": "MOZ", "NA": "NAM", "NC": "FRA", "NG": "NGR", "NI": "NCA", "NL": "NED", "NO": "NOR",
    "NP": "NEP", "NZ": "NZL", "OM": "OMA", "PA": "PAN", "PE": "PER", "PF": "FRA", "PG": "PNG",
    "PH": "PHI", "PK": "PAK", "PL": "POL", "PR": "PUR", "PT": "POR", "PY": "PAR", "QA": "QAT",
    "RE": "FRA", "RO": "ROU", "RS": "SRB", "RU": "RUS", "RW": "RWA", "SA": "KSA", "SC": "SEY",
    "SD": "SUD", "SE": "SWE", "SG": "SGP", "SI": "SLO", "SK": "SVK", "SL": "SLE", "SM": "SMR",
    "SN": "SEN", "SO": "SOM", "SR": "SUR", "ST": "STP", "SV": "ESA", "SX": "SXM", "SY": "SYR",
    "SZ": "SWZ", "TC": "TCA", "TD": "CHA", "TG": "TOG", "TH": "THA", "TJ": "TJK", "TN": "TUN",
    "TO": "TGA", "TR": "TUR", "TT": "TTO", "TW": "TPE", "TZ": "TAN", "UA": "UKR", "UG": "UGA",
    "US": "USA", "UY": "URU", "UZ": "UZB", "VA": "VAT", "VC": "VIN", "VE": "VEN", "VG": "IVB",
    "VI": "ISV", "VN": "VIE", "VU": "VAN", "WS": "SAM", "ZA": "RSA", "ZM": "ZAM", "ZW": "ZIM",
}

# Noms de pays écrits dans le texte des épreuves (« Amami, Japan », « Kiel, Germany »).
# Complète `regates_drapeaux.NOMS_PAYS`, qui ne connaît que les treize pays à drapeau.
NOMS = {
    "france": "FRA", "francia": "FRA", "frankreich": "FRA",
    "suisse": "SUI", "switzerland": "SUI", "schweiz": "SUI", "svizzera": "SUI", "suiza": "SUI",
    "italia": "ITA", "italy": "ITA", "italie": "ITA", "italien": "ITA",
    "espana": "ESP", "spain": "ESP", "espagne": "ESP", "spanien": "ESP", "españa": "ESP",
    "germany": "GER", "deutschland": "GER", "allemagne": "GER", "germania": "GER",
    "netherlands": "NED", "nederland": "NED", "holland": "NED", "pays-bas": "NED",
    "belgium": "BEL", "belgique": "BEL", "belgien": "BEL", "belgio": "BEL",
    "portugal": "POR", "portogallo": "POR", "portugal.": "POR",
    "united kingdom": "GBR", "great britain": "GBR", "grande-bretagne": "GBR",
    "england": "GBR", "scotland": "GBR",
    "wales": "GBR", "northern ireland": "GBR", "angleterre": "GBR", "royaume-uni": "GBR",
    "grossbritannien": "GBR", "großbritannien": "GBR", "inghilterra": "GBR",
    "ireland": "IRL", "irlande": "IRL", "irland": "IRL", "irlanda": "IRL",
    "denmark": "DEN", "danemark": "DEN", "danemark": "DEN", "dänemark": "DEN", "danimarca": "DEN",
    "sweden": "SWE", "suede": "SWE", "suède": "SWE", "schweden": "SWE", "svezia": "SWE",
    "norway": "NOR", "norvege": "NOR", "norvège": "NOR", "norwegen": "NOR", "norvegia": "NOR",
    "finland": "FIN", "finlande": "FIN", "finnland": "FIN", "finlandia": "FIN",
    "estonia": "EST", "estonie": "EST", "estland": "EST",
    "lithuania": "LTU", "lituanie": "LTU", "litauen": "LTU",
    "poland": "POL", "pologne": "POL", "polen": "POL", "polonia": "POL",
    "czech": "CZE", "tschechien": "CZE", "republique tcheque": "CZE",
    "austria": "AUT", "autriche": "AUT", "osterreich": "AUT", "österreich": "AUT",
    "hungary": "HUN", "hongrie": "HUN", "ungarn": "HUN",
    "slovenia": "SLO", "slovenie": "SLO", "slowenien": "SLO",
    "croatia": "CRO", "croatie": "CRO", "kroatien": "CRO",
    "greece": "GRE", "grece": "GRE", "grèce": "GRE", "griechenland": "GRE", "grecia": "GRE",
    "turkey": "TUR", "turquie": "TUR", "türkei": "TUR", "turkiye": "TUR",
    "malta": "MLT", "malte": "MLT", "monaco": "MON", "monaco.": "MON",
    "cyprus": "CYP", "chypre": "CYP", "israel": "ISR", "israele": "ISR",
    "russia": "RUS", "russie": "RUS", "russland": "RUS",
    "ukraine": "UKR", "latvia": "LAT", "lettonie": "LAT",
    "usa": "USA", "u.s.a.": "USA", "united states": "USA", "etats-unis": "USA",
    "états-unis": "USA", "america": "USA", "california": "USA", "florida": "USA",
    "canada": "CAN", "quebec": "CAN", "british columbia": "CAN",
    "mexico": "MEX", "mexique": "MEX", "brasil": "BRA", "brazil": "BRA", "bresil": "BRA",
    "argentina": "ARG", "argentine": "ARG", "chile": "CHI", "chili": "CHI", "uruguay": "URU",
    "peru": "PER", "pérou": "PER", "colombia": "COL", "colombie": "COL",
    "venezuela": "VEN", "ecuador": "ECU", "equateur": "ECU",
    "south africa": "RSA", "afrique du sud": "RSA", "sudafrica": "RSA",
    "japan": "JPN", "japon": "JPN", "giappone": "JPN", "korea": "KOR", "coree": "KOR",
    "corée": "KOR", "south korea": "KOR", "china": "CHN", "chine": "CHN", "cina": "CHN",
    "taiwan": "TPE", "hong kong": "HKG", "hongkong": "HKG", "montenegro": "MNE", "finland": "FIN", "helsinki": "FIN", "macao": "MAC", "macau": "MAC",
    "singapore": "SGP", "singapour": "SGP",
    "thailand": "THA", "thailande": "THA", "thaïlande": "THA", "malaysia": "MAS",
    "malaisie": "MAS", "indonesia": "INA", "indonesie": "INA", "philippines": "PHI",
    "india": "IND", "inde": "IND", "sri lanka": "SRI", "vietnam": "VIE", "viet nam": "VIE",
    "australia": "AUS", "australie": "AUS", "new zealand": "NZL", "nouvelle-zelande": "NZL",
    "fiji": "FIJ", "tahiti": "FRA", "nouvelle-caledonie": "FRA", "new caledonia": "FRA",
    "reunion": "FRA", "réunion": "FRA", "martinique": "FRA", "guadeloupe": "FRA",
    "uae": "UAE", "united arab emirates": "UAE", "emis": "UAE", "emirats": "UAE",
    "émirats": "UAE", "oman": "OMA", "qatar": "QAT", "bahrain": "BRN", "kuwait": "KUW",
    "saudi": "KSA", "arabie saoudite": "KSA", "morocco": "MAR", "maroc": "MAR",
    "tunisia": "TUN", "tunisie": "TUN", "algeria": "ALG", "algerie": "ALG",
    "egypt": "EGY", "egypte": "EGY", "senegal": "SEN", "sénégal": "SEN", "kenya": "KEN",
    "mauritius": "MRI", "maurice": "MRI", "seychelles": "SEY",
    "bermuda": "BER", "bermudes": "BER", "antigua": "ANT", "barbados": "BAR",
    "grenada": "GRN", "trinidad": "TTO", "jamaica": "JAM", "cuba": "CUB",
    "st maarten": "SXM", "sint maarten": "SXM", "st. maarten": "SXM",
    "puerto rico": "PUR", "aruba": "ARU", "curacao": "CUW", "curaçao": "CUW",
    "british virgin islands": "IVB", "us virgin islands": "ISV",
    "st lucia": "LCA", "saint lucia": "LCA", "st. lucia": "LCA", "st kitts": "SKN",
    "panama": "PAN", "costa rica": "CRC", "guatemala": "GUA", "honduras": "HON",
    "iceland": "ISL", "islande": "ISL", "faroe": "FRO", "groenland": "GRL",
    "greenland": "GRL", "malta.": "MLT", "gibraltar": "GIB", "andorra": "AND",
    "luxembourg": "LUX", "liechtenstein": "LIE", "bulgaria": "BUL", "bulgarie": "BUL",
    "romania": "ROU", "roumanie": "ROU", "serbia": "SRB", "serbie": "SRB",
    "montenegro": "MNE", "bosnia": "BIH", "albania": "ALB", "albanie": "ALB",
    "slovakia": "SVK", "slovaquie": "SVK", "azerbaijan": "AZE", "georgia": "GEO",
    "saint-marin": "SMR", "trinite": "TTO", "republique dominicaine": "DOM",
    "porto rico": "PUR", "iles vierges britanniques": "IVB",
}

# Une source fédérale ne laisse aucun doute sur le pays de l'épreuve qu'elle publie.
SOURCES_FIXES = {"ffvoile": "FRA", "acvl": "SUI"}

# Les codes pays que la table ci-dessus sait nommer : un code lu ailleurs (le code club de la
# FFVoile, qui vaut « USA » ou « POR » pour un club étranger) n'est retenu que s'il en est.
CODES = set(NOMS.values())

# Mots de la table qui désignent aussi autre chose : « America's Cup » se court à Barcelone,
# « Georgia » est un État américain. Ils ne servent pas à contrôler le pays d'une épreuve.
AMBIGUS = {"america", "american", "georgia", "california", "florida", "quebec",
           "british columbia"}

# Villes dont le pays est connu sans réseau : le Léman, la Suisse, les ports français. Ce sont
# celles que les sources sans pays citent le plus, et une carte du Léman en « Monde » choque.
VILLES = {
    "FRA": """ajaccio arcachon arles arzon bandol bastia benodet biarritz la-trinite-sur-mer
        bordeaux boulogne-sur-mer brest cannes carcassonne carnon cherbourg cherbourg-en-cotentin
        concarneau dieppe dinard douarnenez dunkerque fécamp fecamp fontainebleau fouesnant
        granville gujan-mestras hendaye hyeres hyères la baule la rochelle la rochelle-port des
        sables-d-olonne les-sables-d-olonne lorient marseille martigues maubuisson menton
        mille-pattes noirmoutier nantes nice nimes nîmes ouistreham palavas
        perros-guirec port-camargue port-la-foret porto-vecchio quiberon rochefort royan
        saint-malo saint-nazaire saint-tropez sainte-maxime sete sète six-fours
        toulon trouville sur-mer valenciennes vannes villefranche-sur-mer
        """.split(),
    "SUI": """aigle allaman anieres anières arbon bale basel bellevue berne bern bienne bier
        brienz brissago buchillon caux celigny cèligny chancy chavannes clarens coppet corsier
        crans cully dardagny estavayer fribourg geneve genève genthod hermance kreuzlingen
        lausanne lonay lucerne luzern lugano montreux morges neuchatel neuchâtel nyon
        preverenges pully rapperswil rolle sarnen sierre soral spiez stansstad st-prex
        st-sulpice thoune versoix versoye vevey villeneuve yverdon zurich zürich
        """.split(),
    "ITA": "capri genova genoa imperia livorno milano napoli palermo roma sorrente sorrento trieste venezia venice scarlino".split(),
    "ESP": "barcelona barcelone cartagena mallorca palma palma-de-mallorca santander vigo".split(),
    "GER": "hamburg kiel kiel-schilksee rostock travemunde travemünde warnemunde warnemünde bremen".split(),
    "NED": "almere amsterdam medemblik rotterdam scheveningen".split(),
    "GBR": "cowes portsmouth plymouth southampton falmouth".split(),
    "USA": "annapolis chicago miami newport san-francisco charleston new-orleans key-west".split(),
}

# Ce que le géocodage s'est trompé à trouver : une ville de nom commun prend le pays du premier
# résultat OpenStreetMap (« Burnham » → États-Unis, « Sandringham » → Canada alors que le yacht
# club est à Melbourne). Relu à la main le 22/11/2026 ; ces valeurs passent avant le cache.
CORRECTIONS = {
    "burnham": "GBR",                       # Burnham-on-Crouch, le club de dérive
    "sandringham": "AUS",                   # Sandringham Yacht Club, Melbourne
    "hebe haven yacht club": "HKG",         # Port Shelter, Hong Kong
    "club de vela ballena alegre": "ESP",   # Sant Pere Pescador, Costa Brava
    "portoroz / izola": "SLO",              # Portorož, Slovénie
    "skovshoved harbor": "DEN",             # Skovshoved, Copenhague
    "the royal yacht club of tasmania": "AUS",
    "vilamoura sailing": "POR",
    "tbc": "",                              # un champ « à confirmer » n'est pas une ville
}

_cache: dict | None = None
_geo: tuple[dict, dict] | None = None


def sans_accent(t: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFKD", t or "") if not unicodedata.combining(c))


def cle(t: str) -> str:
    return re.sub(r"\s+", " ", sans_accent(t).lower()).strip(" ,.")


def _villes_connues() -> dict[str, str]:
    return {cle(v): k for k, vs in VILLES.items() for v in vs if not v.endswith("?")}


VILLES_CONNUES = _villes_connues()


def _lire_cache() -> dict:
    global _cache
    if _cache is None:
        try:
            d = json.loads(CACHE.read_text())
            _cache = d if isinstance(d, dict) else {}
        except (OSError, ValueError):
            _cache = {}
    return _cache


def ecrire_cache(d: dict) -> None:
    global _cache
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    tmp = CACHE.with_suffix(".tmp")
    tmp.write_text(json.dumps(d, ensure_ascii=False, indent=0, sort_keys=True))
    tmp.replace(CACHE)
    _cache = d


def _gazetteer() -> tuple[dict, dict]:
    """Villes et clubs déjà vus avec un pays, dans les relevés bruts des sources qui le donnent."""
    global _geo
    if _geo is not None:
        return _geo
    villes: dict[str, Counter] = {}
    clubs: dict[str, Counter] = {}
    for f in sorted(BRUT.glob("*.json")):
        try:
            lignes = json.loads(f.read_text())
        except (OSError, ValueError):
            continue
        if not isinstance(lignes, list):
            continue
        for e in lignes:
            if not isinstance(e, dict):
                continue
            pays = (e.get("pays") or "").strip().upper()
            if len(pays) != 3 or not pays.isalpha():
                continue
            if e.get("ville"):
                villes.setdefault(cle(e["ville"]), Counter())[pays] += 1
            if e.get("club"):
                clubs.setdefault(cle(e["club"]), Counter())[pays] += 1
    _geo = (villes, clubs)
    return _geo


def _par_nom(texte: str) -> str:
    t = " " + cle(texte) + " "
    for nom, code in sorted(NOMS.items(), key=lambda kv: -len(kv[0])):
        if re.search(r"(^|[\s,/(\-])" + re.escape(nom) + r"($|[\s,.)/\-])", t):
            return code
    return ""


def _motif_pays():
    """Une seule expression pour tous les noms de pays : six millions de recherches ligne à
    ligne coûteraient une demi-minute à la page."""
    global _MOTIF
    try:
        return _MOTIF
    except NameError:
        pass
    mots = sorted((m for m in NOMS if m not in AMBIGUS), key=len, reverse=True)
    _MOTIF = re.compile(r"(?<![a-z0-9])(" + "|".join(re.escape(m) for m in mots) + r")(?![a-z0-9])")
    return _MOTIF


def pays_du_texte(texte: str) -> set[str]:
    """Tous les pays que nomme un texte, sans doublon (« Championnat à HONG KONG » → {HKG}).

    Sert au contrôle de la page : ce que l'épreuve dit d'elle-même ne doit pas contredire son
    drapeau. Les mots ambigus (« America's Cup », « Georgia ») sont écartés pour ne pas
    accuser une épreuve à tort.
    """
    t = cle(texte)
    if not t:
        return set()
    motif = _motif_pays()
    vus: set[str] = set()
    for variante in (t, t.replace("-", " "), t.replace(" ", "-")):
        for mot in motif.findall(variante):
            vus.add(NOMS[mot])
    return vus


def pays_par_nom(texte: str) -> str:
    """Le pays nommé dans un texte (« HONG KONG », « Kiel, Germany »), ou "".

    Les traits d'union varient d'une source à l'autre (« PAYS BAS », « Pays-Bas ») : on essaie
    les trois écritures plutôt que de doubler la table.
    """
    t = texte or ""
    if not t.strip():
        return ""
    for essai in (t, t.replace("-", " "), t.replace(" ", "-")):
        code = _par_nom(essai)
        if code:
            return code
    return ""


def pays(ville: str = "", club: str = "", nom: str = "", sources=(), departement: str = "",
         etranger: bool = False) -> str:
    """Le code pays d'une épreuve, ou "" quand rien ne le dit avec assez de sûreté.

    `etranger` : le club est hors de France. La source fédérale ne fait alors plus pays par
    défaut — une fédération publie aussi les épreuves de ses clubs ailleurs dans le monde, et
    « ffvoile → FRA » a mis un drapeau français sur un championnat du monde à Hong Kong
    (24/11/2026).
    """
    if not etranger:
        for s in sources or ():
            if s in SOURCES_FIXES:
                return SOURCES_FIXES[s]
    if cle(ville) in CORRECTIONS:
        return CORRECTIONS[cle(ville)]
    for texte in (ville, club):
        code = _par_nom(texte or "")
        if code:
            return code
    v = cle(ville)
    if v:
        # Cache OpenStreetMap d'abord : il est précis et couvre les villes hors d'Europe.
        pays_cache = (_lire_cache().get("villes") or {}).get(v)
        if pays_cache:
            return pays_cache
        if v in VILLES_CONNUES:
            return VILLES_CONNUES[v]
        geo_villes, _ = _gazetteer()
        if v in geo_villes:
            return geo_villes[v].most_common(1)[0][0]
        # Ville inconnue mais sans ambiguïté (même sans pays) : on ne devine pas.
    c = cle(club)
    if c:
        _, geo_clubs = _gazetteer()
        if c in geo_clubs:
            return geo_clubs[c].most_common(1)[0][0]
        code = (_lire_cache().get("clubs") or {}).get(c)
        if code:
            return code
    return ""


def villes_inconnues(villes) -> list[str]:
    """Villes ni dans le cache ni dans les tables locales, à géocoder."""
    cache = _lire_cache().get("villes") or {}
    geo_villes, _ = _gazetteer()
    out = []
    for v in sorted({cle(x) for x in villes if cle(x)}):
        if v in cache or v in VILLES_CONNUES or v in geo_villes:
            continue
        if _par_nom(v):
            continue
        out.append(v)
    return out


def geocoder(villes, limite: int = 60, pause: float = 1.1) -> int:
    """Remplit le cache pour les villes demandées, `limite` au plus par passage.

    Nominatim demande un appel par seconde et un agent identifiable : les deux sont ici. Un échec
    réseau laisse la ville hors du cache, elle sera retentée au passage suivant — on n'écrit
    jamais un pays au hasard pour se débarrasser d'une ville.
    """
    cache = dict(_lire_cache())
    table = dict(cache.get("villes") or {})
    villes = [v for v in villes if v not in table][:limite]
    faits = 0
    for v in villes:
        url = "https://nominatim.openstreetmap.org/search?" + urllib.parse.urlencode(
            {"q": v, "format": "jsonv2", "limit": 1, "addressdetails": 1, "accept-language": "fr"})
        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": "SailingMore/1.0 (+https://sailingmore.fr; [secret-masqué])"})
            with urllib.request.urlopen(req, timeout=20) as r:
                d = json.loads(r.read().decode())
        except Exception:  # noqa: BLE001 — réseau : on retentera
            time.sleep(pause)
            continue
        time.sleep(pause)
        if not d:
            table[v] = ""
            continue
        adresse = d[0].get("address") or {}
        code2 = (adresse.get("country_code") or "").upper()
        code = CORRECTIONS.get(v, ISO2.get(code2, ""))
        if not code:
            table[v] = ""
            continue
        table[v] = code
        faits += 1
    cache["villes"] = table
    cache.setdefault("maj", time.strftime("%Y-%m-%dT%H:%M:%S"))
    ecrire_cache(cache)
    return faits


def coords_cache() -> dict:
    """Coordonnées déjà trouvées : clé de ville → [lat, lon] (liste vide = Nominatim n'a rien trouvé)."""
    return _lire_cache().get("coords") or {}


def geocoder_coords(villes, limite: int = 40, pause: float = 1.1) -> int:
    """Une requête Nominatim par ville, une seule fois : le résultat va dans le cache du projet
    (clé « coords ») et la page ne rappelle jamais Nominatim à l'affichage. Un échec réseau
    laisse la ville hors du cache, retentée au passage suivant. Données © contributeurs OpenStreetMap."""
    cache = dict(_lire_cache())
    table = dict(cache.get("coords") or {})
    faits = 0
    for v in [v for v in villes if v not in table][:limite]:
        url = "https://nominatim.openstreetmap.org/search?" + urllib.parse.urlencode(
            {"q": v, "format": "jsonv2", "limit": 1, "accept-language": "fr"})
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "SailingMore/1.0 (+https://sailingmore.fr)"})
            with urllib.request.urlopen(req, timeout=20) as r:
                d = json.loads(r.read().decode())
        except Exception:  # noqa: BLE001 — réseau : on retentera
            time.sleep(pause)
            continue
        time.sleep(pause)
        if d:
            table[v] = [round(float(d[0]["lat"]), 3), round(float(d[0]["lon"]), 3)]
            faits += 1
        else:
            table[v] = []
    cache["coords"] = table
    ecrire_cache(cache)
    return faits


def completer(listes: list[tuple[str, list[dict]]], limite: int = 60, reseau: bool = True) -> None:
    """Géocode les villes des relevés qui n'ont pas encore de pays. À appeler avant la fusion.
    Puis, pour la carte et « près de moi », leurs coordonnées (villes absentes de la table de la page)."""
    try:
        import regates_page
        vues = {cle(e["ville"]) for _, lignes in listes for e in lignes if e.get("ville")}
        sans = sorted(v for v in vues if v and v not in coords_cache()
                      and not regates_page._LIEUX_RE.search(regates_page._sans_accent(v)))
        if sans and reseau:
            print(f"  lieux : {len(sans)} ville(s) sans coordonnées, {min(40, len(sans))} géocodée(s)")
            print(f"  lieux : {geocoder_coords(sans)} coordonnées trouvées en ligne")
    except Exception as ex:  # noqa: BLE001 — la collecte ne doit jamais tomber pour des coordonnées
        print(f"  lieux : coordonnées sautées ({ex})")
    villes = []
    for _, lignes in listes:
        for e in lignes:
            if len(((e.get("pays") or "").strip())) == 3:
                continue
            if e.get("ville"):
                villes.append(e["ville"])
    a_faire = villes_inconnues(villes)
    if not a_faire:
        return
    print(f"  lieux : {len(a_faire)} ville(s) sans pays connu"
          + (f", {min(limite, len(a_faire))} géocodée(s)" if reseau else ", géocodage sauté"))
    if reseau:
        n = geocoder(a_faire, limite=limite)
        print(f"  lieux : {n} pays trouvé(s) en ligne")


def main() -> int:
    if "--villes" not in sys.argv:
        print(__doc__)
        return 0
    villes = []
    for f in sorted(BRUT.glob("*.json")):
        try:
            lignes = json.loads(f.read_text())
        except (OSError, ValueError):
            continue
        if isinstance(lignes, list):
            villes += [e.get("ville") or "" for e in lignes if isinstance(e, dict)]
    a_faire = villes_inconnues(villes)
    print(f"{len(a_faire)} ville(s) sans pays :")
    for v in a_faire:
        print("  " + v)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
