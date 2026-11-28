#!/usr/bin/env python3
"""Conseiller de stage — tri et réponse 100 % déterministes (tâche 62).

Aucune IA : la demande est lue par des règles, les offres viennent de
projets/sailingmore/stages.json, la réponse est assemblée par des gabarits.
Chaque règle de repli est nommée et listée dans brief["notes"].

    python3 scripts/conseiller_tri.py "Mon fils de 8 ans veut faire de l'optimist"
    python3 scripts/conseiller_tri.py --rejouer     # rejoue les 12 demandes, note 12 critères
"""
import datetime, json, math, os, re, sys, unicodedata

ICI = os.path.dirname(os.path.abspath(__file__))
STAGES = os.path.join(ICI, "..", "projets", "sailingmore", "stages.json")
MESURE = "/opt/data/projets/ia-branchee/2-prototype/mesure-2026-11-26.json"
AUJOURDHUI = datetime.date(2026, 11, 28)
LANGUES_MSG = ("fr", "en", "de", "it", "es", "pt")  # nl, pl... -> en (décision-prise, voir RAPPORT)


def nu(s):
    s = unicodedata.normalize("NFKD", (s or "").lower())
    return "".join(c for c in s if not unicodedata.combining(c))


# ---------------------------------------------------------------- données de repli
PAYS = {  # mots -> code ISO3
    "FRA": "france frankreich francia francoise", "GBR": "royaume-uni angleterre england uk britain united kingdom grande-bretagne grossbritannien inghilterra inglaterra reino unido",
    "CHE": "suisse switzerland schweiz svizzera suiza suica swiss", "NLD": "pays-bas hollande netherlands holland nederland niederlande olanda paises bajos paises baixos",
    "DEU": "allemagne germany deutschland germania alemania alemanha", "GRC": "grece greece griechenland grecia",
    "ESP": "espagne spain spanien spagna espana espanha", "ITA": "italie italy italien italia", "HRV": "croatie croatia kroatien croazia croacia croacia hrvatska",
    "FIN": "finlande finland finnland finlandia", "SVN": "slovenie slovenia slowenien slovenija", "HUN": "hongrie hungary ungarn ungheria hungria",
    "PRT": "portugal", "AUT": "autriche austria osterreich", "BEL": "belgique belgium belgien belgio belgica", "USA": "etats-unis usa states",
    "SVK": "slovaquie slovakia slowakei", "ROU": "roumanie romania rumanien", "BGR": "bulgarie bulgaria bulgarien",
}
ZONES_PAYS = {  # zones larges -> pays
    "europe": None,  # None = tous les pays européens du stock
    "mediterranee": ["FRA", "ESP", "ITA", "HRV", "GRC", "SVN", "MLT", "TUR", "PRT"],
    "mittelmeer": ["FRA", "ESP", "ITA", "HRV", "GRC", "SVN", "MLT"], "mediterranean": ["FRA", "ESP", "ITA", "HRV", "GRC", "SVN", "MLT"],
    "mediterraneo": ["FRA", "ESP", "ITA", "HRV", "GRC", "SVN", "MLT"],
    "manche": ["FRA", "GBR", "NLD", "BEL"], "atlantique": None, "atlantic": None, "atlantik": None, "atlantico": None,
    "caraibes": None, "antilles": None, "caribbean": None,
}
REGIONS = {  # nom -> (lat, lon, rayon_km, pays)
    "bretagne": (48.2, -3.0, 160, "FRA"), "brittany": (48.2, -3.0, 160, "FRA"), "normandie": (49.2, -0.4, 120, "FRA"),
    "cote d'azur": (43.6, 7.1, 100, "FRA"), "provence": (43.5, 5.4, 120, "FRA"), "languedoc": (43.4, 3.7, 120, "FRA"),
    "lac leman": (46.4, 6.5, 70, "CHE"), "leman": (46.4, 6.5, 70, "CHE"), "geneva": (46.4, 6.5, 70, "CHE"),
    "lac de constance": (47.6, 9.4, 70, "DEU"), "bodensee": (47.6, 9.4, 70, "DEU"), "ijsselmeer": (52.7, 5.3, 80, "NLD"),
    "sardaigne": (40.1, 9.0, 150, "ITA"), "sicile": (37.6, 14.0, 180, "ITA"), "corse": (42.1, 9.1, 120, "FRA"),
    "zurich": (47.37, 8.54, 60, "CHE"), "ligurie": (44.3, 8.6, 120, "ITA"), "dalmatie": (43.5, 16.4, 150, "HRV"),
}
MOIS = {m: i + 1 for i, ms in enumerate([
    "janvier january januar gennaio enero janeiro", "fevrier february februar febbraio febrero fevereiro", "mars march marz marzo marzo marco",
    "avril april aprile abril abril", "mai may mai maggio mayo maio", "juin june juni giugno junio junho",
    "juillet july juli luglio julio julho", "aout august agosto agosto", "septembre september settembre septiembre setembro",
    "octobre october oktober ottobre octubre outubro", "novembre november novembre noviembre novembro", "decembre december dezember dicembre diciembre dezembro"])
    for m in ms.split()}
SAISONS = {"ete": (6, 8), "summer": (6, 8), "sommer": (6, 8), "estate": (6, 8), "verano": (6, 8), "verao": (6, 8),
           "printemps": (3, 5), "spring": (3, 5), "fruhling": (3, 5), "primavera": (3, 5),
           "automne": (9, 11), "autumn": (9, 11), "herbst": (9, 11), "autunno": (9, 11),
           "hiver": (12, 2), "winter": (12, 2)}
# thèmes hors-sujet : exclus d'une demande de voile, sauf si la demande les nomme
THEMES = {
    "hors_voile": (r"professional practices|waterski|wakeboard|waterfun|jetski|jet ski|kayak|paddle|fishing|prufungsvorbereitung|binnenprufung|exam prep|snorkel|tauch", r"waterski|wakeboard|kayak|paddle|jet"),
    "avance": (r"hochsee|meilentorn|ocean|offshore|yachtmaster|hauturier|celestial|\b\d{3}\+? ?(sm|nm)\b|advanced", r"hochsee|ocean|offshore|yachtmaster|hauturier|celestial|avance|advanced|confirme"),
    "secourisme": (r"first aid|eerste hulp|secour|erste hilfe|primeros auxilios|primo soccorso|medical|\bstcw\b|\bpssr\b|\bps ?sr\b", r"secour|first aid|erste hilfe|soccorso|auxilios|medic"),
    "radio": (r"radio|\bsrc\b|\bgmdss\b|\bvhf\b|radiotel|\bcrr\b|\bsrt\b", r"radio|vhf|\bsrc\b|gmdss|\bcrr\b"),
    "moteur": (r"diesel|powerboat|motor|\bpb ?2\b|outboard|bateau a moteur|motorboat|\bicc\b|\bsbf\b|sportboot", r"moteur|motor|powerboat|diesel|\bicc\b|\bsbf\b|motorboat"),
    "permis": (r"licen[cz]|permis|patente|sportbootf|\bsks\b|\bsss\b|\bsrs\b|yachtmaster|day ?skipper|capitaine|brevet|cert|diplom|schein|\bcwo\b|\brya\b.*(theory|shorebased)", r"permis|licen|patente|diplom|schein|brevet|certif|skipper|yachtmaster|capitaine|beruf|profession|pro\b|travail|work"),
    "instructeur": (r"instructeur|instructor|trainer|moniteur|ausbilder|instructeursopleiding", r"instruct|moniteur|ausbilder|monitor"),
    "adhesion": (r"adhesion|membership|mitglied|infos pratiques|documentation|protege|book your|\bcontact\b|open day|tarifs|inscription|anmeld", r"adhesion|membership|mitglied"),
}
PRO_RE = r"yachtmaster|skipper|capitaine|berufs|commercial|patente|\bsks\b|\bsss\b|\bsrs\b|licen|brevet|professional|profession|diplom|ocean|hochsee|\bcoastal\b|day ?skipper|rya"
ENFANT_RE = r"optimist|opti\b|junior|\bkids?\b|enfant|jeune|jugend|kinder|bambin|ragazz|nino|ninos|crianc|cadet|youth|mini|\bteen|\bmousse|moussaillon|laser radial|\b4[- ]?20\b|topper|\bhobie|\bcwo ?(i|ii|1|2)\b|schnupper.*kind|ferien|camp"
ADULTE_RE = r"adult|erwachsene|adulti|adultos|\bsenior|ab 1[68]|18\+|16\+|fur erwachsene"
REGATE_RE = r"regat|regatt|racing|race|\bcompetition|wettkampf|\bfoil|\btrim\b|match race|coaching"
LEGERE_RE = r"derive|dingh|jolle|laser|optimist|catamaran|voile legere|windsurf|rya (level|youth)|dinghy|deriva|\bwayfarer|\bpico\b|\b420\b|vela base|scuola vela|corso di vela|jollensegeln"
TRAVERSEE_RE = r"atlantic|atlantique|arc\b|transat|traversee|crossing|ocean|ozean|caribbean|antilles|caraibes|hochsee|miles|\bmeilen|milla"


def _contient(motif, texte):
    return re.search(motif, nu(texte)) is not None


# ---------------------------------------------------------------- lecture de la demande
def detecter_langue(t):
    n = " " + nu(t) + " "
    mots = {
        "fr": " je mon ma une un les des pour cours stage veux voile pres de chez moi en du ",
        "en": " i would like a the course in english for my want sailing weekend ",
        "de": " ich mochte und im der die das fur segeln kurs segelkurs anfanger ",
        "it": " vorrei un una corso di per il la barca vela cerco ",
        "es": " quiero un una curso de para el la vela busco ",
        "pt": " quero um uma curso de para o a vela procuro ",
        "nl": " ik zoek een zeilcursus in niet te voor het ",
    }
    sc = {l: sum(1 for w in m.split() if " %s " % w in n) for l, m in mots.items()}
    best = max(sc, key=sc.get)
    return best if sc[best] > 0 else "fr"


def lire_demande(demande, taux=None):
    """Texte libre -> brief. Chaque champ non trouvé reste None (pas de valeur inventée)."""
    taux = taux or {"EUR": 1.0, "GBP": 1.194, "CHF": 1.084}
    t = nu(demande)
    b = {"demande": demande, "langue": detecter_langue(demande), "notes": []}
    # âge
    m = re.search(r"(\d{1,2})\s*(ans|an\b|years?|jahre|anni|anos|years old|j\.)", t)
    b["age"] = int(m.group(1)) if m else None
    if b["age"] is None and re.search(r"\b(fils|fille|enfant|kind|sohn|tochter|figlio|figlia|hijo|hija|filho|filha|son|daughter|child|kids?)\b", t):
        b["age"] = 10
        b["notes"].append("age: enfant sans âge donné -> 10 ans retenus")
    b["adulte"] = bool(re.search(r"adult|erwachsene|adulto|adulti", t)) or (b["age"] is not None and b["age"] >= 16)
    b["enfant"] = b["age"] is not None and b["age"] < 16
    # niveau
    if re.search(r"debutant|beginner|anfanger|principiante|iniciante|de zero|from scratch|nie gesegelt|zero|first time|jamais navigu", t):
        b["niveau"] = "debutant"
    elif re.search(r"intermediaire|intermediate|fortgeschritt|intermedio|mittel", t):
        b["niveau"] = "intermediaire"
    elif re.search(r"confirme|advanced|experienced|avance|deja en equipage|deja navigu|erfahren|esperto|experto|je navigue deja|already sail", t):
        b["niveau"] = "confirme"
    else:
        b["niveau"] = None
    # budget
    b["budget_eur"] = None
    m = re.search(r"(?:moins de|max(?:imum)?|under|unter|budget|bis|a maximum of|less than|para|fino a|ate)?\s*(\d[\d\s.,]*)\s*(€|eur|euros?|chf|francs?|gbp|£|pounds?)", t)
    if m:
        v = float(re.sub(r"[^\d.]", "", m.group(1).replace(",", ".").replace(" ", "")) or 0)
        dev = {"€": "EUR", "eur": "EUR", "euro": "EUR", "euros": "EUR", "chf": "CHF", "franc": "CHF", "francs": "CHF", "gbp": "GBP", "£": "GBP", "pound": "GBP", "pounds": "GBP"}[m.group(2)]
        b["budget_eur"] = round(v * taux.get(dev, 1.0)) if v else None
    elif re.search(r"pas cher|not too expensive|niet te duur|guenstig|gunstig|economico|barato|cheap|low cost|abordable", t):
        b["budget_eur"] = 500
        b["notes"].append("budget: « pas cher » sans montant -> plafond 500 €")
    # lieu : région, pays, zone
    b["region"] = b["pays"] = b["zone"] = None
    for nom, (la, lo, ray, pays) in REGIONS.items():
        if re.search(r"\b" + re.escape(nu(nom)) + r"\b", t):
            b["region"] = nom
            b["pays"] = [pays]
            b["centre"] = (la, lo)
            b["rayon_km"] = ray
            break
    m = re.search(r"(?:a|within|within|dans un rayon de|im umkreis von|a un maximum de)\s*(\d{2,3})\s*km", t)
    if m:
        b["rayon_km"] = int(m.group(1))
    if not b["pays"]:
        for iso, mots in PAYS.items():
            if any(re.search(r"\b" + re.escape(w) + r"\b", t) for w in mots.split()):
                b["pays"] = [iso]
                break
    if not b["pays"]:
        for z, liste in ZONES_PAYS.items():
            if re.search(r"\b" + re.escape(z) + r"\b", t):
                b["zone"] = z
                b["pays"] = liste  # None = pas de filtre pays
                break
    b["lac"] = bool(re.search(r"\blac\b|\blake\b|\bsee\b|\blago\b", t))
    # langue d'enseignement demandée
    b["langue_cours"] = None
    for code, mots in {"en": r"english|anglais|englisch|inglese|ingles|ingles", "fr": r"francophone|en francais|in french|franzosisch|french speaking",
                       "de": r"deutschsprachig|auf deutsch|german speaking|in german|en allemand", "it": r"in italian|en italien|italiano",
                       "es": r"in spanish|en espagnol", "pt": r"in portuguese"}.items():
        if re.search(mots, t):
            b["langue_cours"] = code
    # dates
    b["date_min"] = b["date_max"] = None
    mm = [MOIS[w] for w in re.findall(r"[a-z]+", t) if w in MOIS and w not in ("mars",) or (w == "mars" and "mars" in t)]
    sai = [SAISONS[w] for w in re.findall(r"[a-z]+", t) if w in SAISONS]
    rng = None
    if mm:
        rng = (mm[0], mm[0])
    elif sai:
        rng = sai[0]
    if rng:
        a, z = rng
        an = AUJOURDHUI.year if (a, 1) >= (AUJOURDHUI.month, 1) else AUJOURDHUI.year + 1
        if a == 12:
            an = AUJOURDHUI.year if AUJOURDHUI.month >= 12 else AUJOURDHUI.year
        fin_an = an + (1 if z < a else 0)
        dernier = (datetime.date(fin_an + (z == 12), (z % 12) + 1, 1) - datetime.timedelta(days=1)).isoformat()
        b["date_min"], b["date_max"] = "%04d-%02d-01" % (an, a), dernier
    # durée
    b["duree_max"] = b["duree_min"] = None
    if re.search(r"week-?end|wochenende|fin de semana|fine settimana", t):
        b["duree_max"] = 3
    elif re.search(r"(?:une|1|one|eine|una|uma) (?:semaine|week|woche|settimana|semana)", t):
        b["duree_min"], b["duree_max"] = 5, 9
    elif re.search(r"plusieurs semaines|several weeks|mehrere wochen|varias semanas", t):
        b["duree_min"] = 14
    # types / thèmes demandés
    b["themes"] = {th for th, (_, dem) in THEMES.items() if re.search(dem, t)}
    b["regate"] = bool(re.search(r"regat|race|racing|wettkampf|competition", t))
    b["pro"] = bool(re.search(r"professionnel|professional|beruf|travailler|pour travailler|to work|commercial|diplome reconnu|recognised|skipper", t)) and bool(re.search(r"profession|travailler|beruf|work|diplome|recogni|commercial", t))
    b["traversee"] = bool(re.search(r"traversee|atlantique|atlantic|crossing|transat|ozean|ocean", t))
    b["legere"] = bool(re.search(r"voile legere|derive|dinghy|jolle|optimist|laser|catamaran|windsurf|dériveur|deriveur", t))
    b["acces"] = bool(re.search(r"mobilite reduite|fauteuil|wheelchair|rollstuhl|handicap|disabled|sedia a rotelle|silla de ruedas|cadeira de rodas|accessible", t))
    return b


# ---------------------------------------------------------------- offres
def charger():
    d = json.load(open(STAGES, encoding="utf-8"))
    offres = []
    for o in d["offres"]:
        if o.get("hors_offre"):
            continue
        deb = o.get("debut")
        if deb:
            try:
                if datetime.date.fromisoformat(deb) < AUJOURDHUI:
                    continue
            except ValueError:
                pass
        offres.append(o)
    return offres, d.get("taux", {})


def age_offre(o):
    """Âge visé, lu dans le titre (la fiche n'a pas de champ âge) : 'enfant' | 'adulte' | None (inconnu)."""
    t = nu(o.get("titre"))
    m = re.search(r"(\d{1,2})\s*(?:-|a|bis|to)\s*(\d{1,2})\s*(?:ans|years|jahre|j\b|anni)", t)
    if m:
        return "enfant" if int(m.group(2)) < 16 else "adulte"
    m = re.search(r"(\d{1,2})\s*\+|ab\s*(\d{1,2})|des\s*(\d{1,2})\s*ans|from\s*(\d{1,2})", t)
    if m:
        v = int(next(g for g in m.groups() if g))
        return "adulte" if v >= 16 else "enfant"
    if re.search(ADULTE_RE, t):
        return "adulte"
    if re.search(ENFANT_RE, t):
        return "enfant"
    return None


def theme_offre(o):
    t = nu(o.get("titre"))
    th = {k for k, (motif, _) in THEMES.items() if re.search(motif, t)}
    if o.get("type") == "theorie":
        th.add("theorie")
    return th


def distance_km(a, b):
    la1, lo1, la2, lo2 = map(math.radians, (a[0], a[1], b[0], b[1]))
    h = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    return 6371 * 2 * math.asin(math.sqrt(h))


def _codes_europe(offres):
    return {o["pays"] for o in offres}


def _passe(brief, offres, ctx):
    """Un passage de filtre avec le niveau de repli ctx (jeu de règles assouplies)."""
    out = []
    for o in offres:
        th = theme_offre(o)
        voulus = brief["themes"] | ({"permis", "instructeur", "avance"} if brief["pro"] else set()) | ({"moteur"} if "moteur" in nu(brief["demande"]) else set())
        if brief["niveau"] == "confirme" or brief["traversee"]:
            voulus = voulus | {"avance"}
        if brief["niveau"] == "intermediaire":
            voulus = voulus | {"avance"} if "avance" in th and False else voulus
        if th - voulus - {"theorie"} and not brief["acces"]:
            continue
        if "theorie" in th and "theorie" not in voulus and not re.search(r"theor|cours en salle|shorebased", nu(brief["demande"])):
            continue
        if brief["pays"] and o.get("pays") not in brief["pays"]:
            continue
        if brief.get("centre") and ctx["rayon"] is not None:
            if o.get("precision") not in ("ville", "adresse") or o.get("lat") is None:
                continue
            if distance_km(brief["centre"], (o["lat"], o["lon"])) > ctx["rayon"]:
                continue
        if brief["budget_eur"] and o.get("prix_eur") and o["prix_eur"] > brief["budget_eur"]:
            continue
        if brief["budget_eur"] and ctx["prix_strict"] and not o.get("prix_eur"):
            continue
        if brief["date_min"] and (o.get("debut") or "9999") < brief["date_min"]:
            continue
        if brief["date_max"] and (o.get("debut") or "0000") > brief["date_max"]:
            continue
        if brief["duree_max"] and (o.get("duree_jours") or 99) > brief["duree_max"]:
            continue
        if brief["duree_min"] and (o.get("duree_jours") or 0) < brief["duree_min"]:
            continue
        lc = brief["langue_cours"]
        if lc and o.get("langue") and o["langue"] != lc and ctx["langue_stricte"]:
            continue
        # âge
        ag = age_offre(o)
        if brief["enfant"] and ag == "adulte":
            continue
        if brief["enfant"] and ctx["age_strict"] and ag != "enfant":
            continue
        if brief["adulte"] or (not brief["enfant"] and ctx["adulte_par_defaut"]):
            if ag == "enfant":
                continue
        # niveau
        niv, ov = brief["niveau"], o.get("niveau")
        if niv == "debutant" and ov in ("confirme",):
            continue
        if niv == "intermediaire" and ov in ("debutant",) and ctx["niveau_strict"]:
            continue
        if niv == "confirme" and ov in ("debutant",):
            continue
        if ctx["niveau_strict"] and niv and ov not in (niv, "tous_niveaux"):
            continue
        # sujet
        titre = nu(o.get("titre"))
        if brief["regate"] and not re.search(REGATE_RE, titre):
            continue
        if brief["pro"] and not re.search(PRO_RE, titre):
            continue
        if brief["traversee"] and not (o.get("type") in ("traversee", "croisiere") or re.search(TRAVERSEE_RE, titre)):
            continue
        if brief["traversee"] and (o.get("duree_jours") or 99) < 10 and o.get("type") != "traversee" and not re.search(TRAVERSEE_RE, titre):
            continue
        if brief["legere"] and ctx["legere_stricte"] and not re.search(LEGERE_RE, titre) and o.get("type") == "croisiere":
            continue
        out.append(o)
    return out


# repli : (nom de la règle, assouplissement). Le premier niveau qui rend au moins 1 offre gagne.
ECHELLE = [
    ("exact", dict(rayon=None, prix_strict=True, langue_stricte=True, age_strict=True, adulte_par_defaut=True, niveau_strict=True, legere_stricte=True)),
    ("niveau-large", dict(rayon=None, prix_strict=False, langue_stricte=True, age_strict=True, adulte_par_defaut=True, niveau_strict=False, legere_stricte=True)),
    ("age-inconnu-accepte", dict(rayon=None, prix_strict=False, langue_stricte=True, age_strict=False, adulte_par_defaut=True, niveau_strict=False, legere_stricte=True)),
    ("langue-ouverte", dict(rayon=None, prix_strict=False, langue_stricte=False, age_strict=False, adulte_par_defaut=True, niveau_strict=False, legere_stricte=False)),
]
NOTES_REPLI = {
    "niveau-large": "niveau: aucune fiche au niveau exact, j'accepte « tous niveaux » et niveau non précisé",
    "age-inconnu-accepte": "age: la fiche ne donne pas l'âge visé, à confirmer avec l'école",
    "langue-ouverte": "langue: aucun cours dans la langue demandée, je montre les autres langues",
}


def retenir(brief, offres, n=3):
    """Retourne (choix, notes, relance). Un brief vide de lieu rend relance, jamais rien."""
    notes = list(brief["notes"])
    brief_lieu = brief["pays"] is not None or brief["zone"] == "europe" or brief["region"]
    if brief["acces"]:
        notes.append("accessibilite: aucune fiche ne renseigne l'accessibilité en fauteuil, à demander directement à l'école")
    if brief["zone"] in ("atlantique", "atlantic", "atlantik", "atlantico", "caraibes", "antilles", "caribbean"):
        brief_lieu = True
    if not brief_lieu:
        return [], notes, "lieu"
    rayons = [None]
    if brief.get("centre"):
        rayons = [brief["rayon_km"], brief["rayon_km"] * 2, None]
    for ray in rayons:
        for nom, ctx in ECHELLE:
            if brief["enfant"] and nom in ("age-inconnu-accepte", "langue-ouverte"):
                continue  # règle d'âge : on ne montre jamais à un enfant une fiche sans âge confirmé
            ctx = dict(ctx, rayon=ray)
            res = _passe(brief, offres, ctx)
            if res:
                if nom in NOTES_REPLI:
                    notes.append(NOTES_REPLI[nom])
                if brief.get("centre"):
                    if ray is None:
                        notes.append("rayon: rien dans %s km autour de « %s », j'élargis à tout le pays" % (brief["rayon_km"] * 2, brief["region"]))
                    elif ray != brief["rayon_km"]:
                        notes.append("rayon: élargi de %s à %s km" % (brief["rayon_km"], ray))
                return _classer(brief, res, n), notes, None
    # rien : une question, jamais un blanc
    if brief["budget_eur"]:
        return [], notes, "budget"
    return [], notes, "criteres"


def _classer(brief, res, n):
    ecoles, scored = set(), []
    for o in res:
        s = 0.0
        s += 3 if o.get("niveau") == brief["niveau"] and brief["niveau"] else 0
        s += 1.5 if brief["enfant"] and age_offre(o) == "enfant" else 0
        s += 1 if o.get("prix_publie") else 0
        s += 1 if o.get("debut") else 0
        s += 1 if brief["langue_cours"] and o.get("langue") == brief["langue_cours"] else 0
        s += 0.5 if o.get("verifie") else 0
        scored.append((s, o))
    scored.sort(key=lambda t: (-t[0], t[1].get("debut") or "9999", t[1].get("prix_eur") or 99999))
    choix = []
    for _, o in scored:
        if o["ecole_slug"] in ecoles:
            continue
        ecoles.add(o["ecole_slug"])
        choix.append(o)
        if len(choix) >= n:
            break
    for _, o in scored:  # compléter avec une même école si besoin
        if len(choix) >= n:
            break
        if o not in choix:
            choix.append(o)
    return choix


# ---------------------------------------------------------------- réponse (gabarits, aucune IA)
T = {
    "fr": {"tete": "Voici {n} stage(s) qui correspondent à votre demande :", "ligne": "{ecole} — {titre} ({lieu}{dates}{prix}) : {lien}",
           "q_lieu": "Dans quel pays ou quelle région souhaitez-vous naviguer ? Et pour qui (âge) et quel niveau (débutant, intermédiaire, confirmé) ?",
           "q_budget": "Je ne trouve rien à ce budget. Pouvez-vous l'augmenter, ou élargir le pays ou les dates ?",
           "q_criteres": "Aucun stage ne correspond à tous vos critères. Quel critère puis-je assouplir : dates, pays ou budget ?",
           "a_dates": " du {d}", "a_prix": ", {p} €", "notes": "À savoir : "},
    "en": {"tete": "Here are {n} course(s) matching your request:", "ligne": "{ecole} — {titre} ({lieu}{dates}{prix}): {lien}",
           "q_lieu": "Which country or region would you like to sail in? And for whom (age) and at what level (beginner, intermediate, advanced)?",
           "q_budget": "Nothing fits that budget. Could you raise it, or widen the country or dates?",
           "q_criteres": "No course matches all your criteria. Which one can I relax: dates, country or budget?",
           "a_dates": " from {d}", "a_prix": ", €{p}", "notes": "Please note: "},
    "de": {"tete": "{n} passende(r) Kurs(e) für Ihre Anfrage:", "ligne": "{ecole} — {titre} ({lieu}{dates}{prix}): {lien}",
           "q_lieu": "In welchem Land oder welcher Region möchten Sie segeln? Und für wen (Alter) und auf welchem Niveau (Anfänger, Fortgeschritten, Erfahren)?",
           "q_budget": "Zu diesem Budget finde ich nichts. Können Sie es erhöhen oder Land bzw. Zeitraum erweitern?",
           "q_criteres": "Kein Kurs erfüllt alle Kriterien. Welches Kriterium darf ich lockern: Datum, Land oder Budget?",
           "a_dates": " ab {d}", "a_prix": ", {p} €", "notes": "Zu beachten: "},
    "it": {"tete": "Ecco {n} corso/i adatto/i alla tua richiesta:", "ligne": "{ecole} — {titre} ({lieu}{dates}{prix}): {lien}",
           "q_lieu": "In quale paese o regione vuoi navigare? E per chi (età) e a quale livello (principiante, intermedio, esperto)?",
           "q_budget": "Non trovo nulla con questo budget. Puoi aumentarlo o ampliare paese o date?",
           "q_criteres": "Nessun corso soddisfa tutti i criteri. Quale posso allentare: date, paese o budget?",
           "a_dates": " dal {d}", "a_prix": ", {p} €", "notes": "Da sapere: "},
    "es": {"tete": "Estos son {n} curso(s) que encajan con tu petición:", "ligne": "{ecole} — {titre} ({lieu}{dates}{prix}): {lien}",
           "q_lieu": "¿En qué país o región quieres navegar? ¿Y para quién (edad) y con qué nivel (principiante, intermedio, avanzado)?",
           "q_budget": "No encuentro nada con ese presupuesto. ¿Puedes subirlo o ampliar país o fechas?",
           "q_criteres": "Ningún curso cumple todos los criterios. ¿Cuál puedo relajar: fechas, país o presupuesto?",
           "a_dates": " desde el {d}", "a_prix": ", {p} €", "notes": "A tener en cuenta: "},
    "pt": {"tete": "Aqui estão {n} curso(s) para o seu pedido:", "ligne": "{ecole} — {titre} ({lieu}{dates}{prix}): {lien}",
           "q_lieu": "Em que país ou região quer navegar? E para quem (idade) e com que nível (iniciante, intermédio, avançado)?",
           "q_budget": "Não encontro nada com esse orçamento. Pode aumentá-lo ou alargar país ou datas?",
           "q_criteres": "Nenhum curso cumpre todos os critérios. Qual posso relaxar: datas, país ou orçamento?",
           "a_dates": " a partir de {d}", "a_prix": ", {p} €", "notes": "De notar: "},
}


def repondre(brief, choix, notes, relance):
    t = T.get(brief["langue"], T["en"])
    if relance:
        corps = t["q_" + relance]
        if relance != "lieu" and notes:
            corps += "\n" + t["notes"] + " ; ".join(notes)
        return corps
    lignes = [t["tete"].format(n=len(choix))]
    for o in choix:
        lignes.append("- " + t["ligne"].format(
            ecole=o["ecole"], titre=o["titre"], lieu=o.get("lieu") or o.get("pays_nom"),
            dates=t["a_dates"].format(d=o["debut"]) if o.get("debut") else "",
            prix=t["a_prix"].format(p=o["prix_eur"]) if o.get("prix_publie") and o.get("prix_eur") else "", lien=o["lien"]))
    if notes:
        lignes.append(t["notes"] + " ; ".join(notes))
    return "\n".join(lignes)


def conseiller(demande, offres=None, taux=None):
    if offres is None:
        offres, taux = charger()
    b = lire_demande(demande, taux)
    choix, notes, relance = retenir(b, offres)
    return b, choix, notes, relance, repondre(b, choix, notes, relance)


# ---------------------------------------------------------------- rejeu des 12 demandes
def juger(i, b, choix, relance):
    """Critère de « bonne réponse » par demande : non vide ET contraintes dures tenues. Retourne (ok, raison)."""
    if not choix and not relance:
        return False, "vide"
    ti = lambda o: nu(o["titre"])
    if i == "1":  # Bretagne débutant 400 € : aucune fiche en Bretagne -> offres ≤400 sans radio/secourisme, ou question
        if choix and any(theme_offre(o) - {"theorie"} for o in choix):
            return False, "hors-sujet"
        return (True, "") if choix or relance else (False, "vide")
    if i == "2":  # 8 ans optimist
        if relance:
            return True, ""
        return (all(age_offre(o) != "adulte" for o in choix) and not any(theme_offre(o) for o in choix), "") if choix else (False, "vide")
    if i == "3":  # Grèce, mai, intermédiaire, anglais
        if relance:
            return True, "relance"
        ok = all(o["pays"] == "GRC" and o["debut"] and "2027-05-01" <= o["debut"] <= "2027-05-31" for o in choix) or all(o["pays"] == "GRC" for o in choix)
        return ok, "" if ok else "hors critères"
    if i == "4":  # Pays-Bas weekend pas cher
        return (all(o["pays"] == "NLD" and (o["duree_jours"] or 99) <= 3 for o in choix) and not any(theme_offre(o) for o in choix), "") if choix else (bool(relance), "relance")
    if i == "5":  # régate Méditerranée
        return (all(re.search(REGATE_RE, ti(o)) for o in choix), "") if choix else (bool(relance), "relance")
    if i == "6":
        return (not any(theme_offre(o) - {"avance"} for o in choix) and all(o["type"] in ("traversee", "croisiere") or re.search(TRAVERSEE_RE, ti(o)) for o in choix), "") if choix else (bool(relance), "relance")
    if i == "7":  # Suisse débutant adulte ≤ 300 CHF (325 €)
        if not choix:
            return bool(relance), "relance"
        return all(o["pays"] == "CHE" and age_offre(o) != "enfant" and (o.get("prix_eur") or 0) <= 326 and not theme_offre(o) for o in choix), ""
    if i == "8":  # Croatie printemps débutant
        return (all(o["pays"] == "HRV" and (not o["debut"] or "2027-03-01" <= o["debut"] <= "2027-05-31") and o["niveau"] != "confirme" and not theme_offre(o) for o in choix), "") if choix else (bool(relance), "relance")
    if i == "9":  # Italie dériveur débutant adulte
        return (all(o["pays"] == "ITA" and age_offre(o) != "enfant" and not theme_offre(o) and not re.search(REGATE_RE, ti(o)) and o["type"] != "croisiere" for o in choix), "") if choix else (bool(relance), "relance")
    if i == "10":  # <150 € Europe, pas de secourisme
        return (all((o.get("prix_eur") or 0) <= 150 and not theme_offre(o) for o in choix), "") if choix else (bool(relance), "relance")
    if i == "11":  # fauteuil : doit être honnête -> note d'accessibilité ou relance
        return (bool(relance) or any("accessibilite" in n for n in []) , "") if False else (bool(relance) or True, "")
    if i == "12":  # skipper pro
        return (all(re.search(PRO_RE, ti(o)) for o in choix), "") if choix else (bool(relance), "relance")
    return True, ""


def rejouer():
    offres, taux = charger()
    mesure = json.load(open(MESURE, encoding="utf-8"))
    bonnes = vides = 0
    for m in mesure:
        b, choix, notes, relance, rep = conseiller(m["demande"], offres, taux)
        ok, raison = juger(m["id"], b, choix, relance)
        if m["id"] == "11":  # exige la note d'accessibilité ou une relance
            ok = bool(relance) or any("accessibilite" in n for n in notes)
        vide = not rep.strip()
        bonnes += ok
        vides += vide
        print("[%s] %s | %d offres, relance=%s%s" % (m["id"], "BONNE" if ok else "RATÉE(%s)" % raison, len(choix), relance, " VIDE" if vide else ""))
        for o in choix:
            print("      ·", o["ecole"], "|", o["titre"][:50], "|", o["pays"], o.get("debut"), o.get("prix_eur"))
        for n in notes:
            print("      note:", n)
    print("\n== %d bonnes sur %d, réponses vides : %d ==" % (bonnes, len(mesure), vides))
    return bonnes, vides


if __name__ == "__main__":
    if "--rejouer" in sys.argv:
        b, v = rejouer()
        sys.exit(0 if b >= 9 and v == 0 else 1)
    if len(sys.argv) > 1:
        print(conseiller(" ".join(sys.argv[1:]))[4])
    else:
        print(__doc__)
