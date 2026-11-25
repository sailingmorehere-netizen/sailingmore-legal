"""Construit projets/sailingmore/chants-de-marin.json à partir des livres téléchargés (cache/chants/src).

    python3 scripts/chants_construire.py      # réécrit le JSON (les six chants d'origine sont conservés tels quels)

Aucune parole n'est écrite ici : elles sont lues dans l'OCR des livres, ligne par ligne (plages dans _chants_specs.py),
nettoyées (apostrophes, guillemets, numéros de couplet, astérisques de notes) et jamais réécrites.
"""
import json
import re
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _chants_specs import SPECS, LIVRES, NUMERO, BILLY_BOY, BILLY_NOTE, PAGES_SMITH, W, T1, T2, S  # noqa: E402
from _chants_specs import JOINS, MANUEL, RAISON, COMPLETS_AJOUTS  # noqa: E402

ECARTS = {"home-dearie-home": 5}   # écart de lignes OCR qui sépare deux couplets (3 par défaut)
# Rio Grande (Smith) : lignes de l'OCR où s'ouvre un couplet (solo, solo, chœur, « &c. ») ; l'écart de lignes ne les sépare pas
DEBUTS = {"rio-grande-smith": {1548, 1551, 1556, 1569, 1575, 1581, 1587, 1593, 1599, 1605, 1610, 1621, 1627},
          "whisky-for-my-johnny": {2798, 2806, 2819, 2827, 2836}, "sally-brown-smith": {4063, 4072, 4081}}

COUPURES = {"pen-", "thou-"}   # mots coupés en fin de ligne dans le livre (pen-non, thou-sand), recollés
ENTETE = re.compile(r"OF THE W\s?[A-Z]\s?[A-Z]")   # titre courant de Smith, en capitales dans l'OCR ; sensible à la casse : « think of the wife » est un vers

SRC = RACINE / "cache/chants/src"
JSON_F = RACINE / "projets/sailingmore/chants-de-marin.json"
ORDRE_CLES = ["maj", "note", "ui", "langueNoms"]

OCR_T2 = [(r"\bDont\b", "Don't"), (r"\bCant\b", "Can't"), (r"\bIts\b", "It's"), (r"\bPm\b", "I'm"), (r"\bIll\b", "I'll"),
          (r"\bId\b", "I'd"), (r"Tommy”", "Tommy's"), (r"Tammy’s", "Tommy's"), (r"\bÎ\b", "I")]
COMPLETS = {"dreadnought", "reuben-ranzo", "cheerly-man", "saucy-arethusa", "handy-jim", "ved-balasthjoning"}


NUM = re.compile(r"^\s*(\d{1,2}|[&B])[\.,]\s+|^\s*[\.,]\s+|^\s*\d\s\d[\.,]\s+")   # le dernier : « 1 8. » (numéro à deux chiffres coupé par l'OCR, Bonny)
BRUIT = [(r"\}", ""), (r"\bQO\b", "O"), (r"\bOQ\b", "O"), (r"\b0'", "o'"), (r"\(tw[a-z0-9¢]{1,3}ce\)", "(twice)"),
         (r"\(tatce\)", "(twice)"), (r"\(thrtce\)", "(thrice)"), (r"\(tw7ce\)", "(twice)"), (r"\(¢wice\)", "(twice)"),
         (r"^\[n ", "In "), (r"^\[had ", "I had "), (r"^OI ", "O I "), (r"Tommy[\"?](?= gone)", "Tommy's"),
         (r"\bboire 4\b", "boire à"), (r"donne a boire", "donne à boire"), (r"\b4 ses\b", "à ses"), (r"^A grands", "À grands"),
         (r"pàid", "paid"), (r"Tammy's", "Tommy's"), (r"\" Mexico,\"", '"Mexico,"'),
         (r"oh\*\.", "oh."), (r"^1 For it blows", "For it blows"), (r"\bpen-non\b", "pennon"), (r"(?<=Scott,) 1$", ""),
         (r"(?<=mail\.\") 2$", ""), (r"(?<=meal\.) 3$", ""), (r", luna\)$", ","), (r"\s*\|\s*\(twice$", ""),
         (r"^%\s+", ""), (r"hundied", "hundred"), (r"thefosey", "the Josey"), (r"^Chorus\s+(?=\w)", ""),
         (r"^Solo & Chorus\.\s*", ""), (r"^So[/lI1]o\.\s*", ""), (r"^Solo\.\s+(?=South Australia is)", ""), (r"^,\s*\d{1,2}\.\s+", ""), (r"\bete\.$", "etc."), (r"^I\.\s+", ""), (r"^\d{1,2}\.\s+(?=King Louis)", ""),
         (r"^S\.olo\.\s*-?\s*", ""), (r"(?<=o'foyre\.) 1$", ""), (r"(?<=Elbow,) 2$", ""), (r"\bW T hisky\b", "Whisky"), (r"\bmy johnny\b", "my Johnny")]


def nettoyer(t: str, livre: str):
    """Renvoie (texte propre, vrai si la ligne ouvrait un couplet numéroté)."""
    t = t.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"').replace("’", "'")
    t = t.replace("''", '"')
    num = bool(NUM.match(t))
    t = NUM.sub("", t)
    if livre == S:
        t2 = re.sub(r"^(Solo|Chorus)\.\s*", "", t)
        if t2 != t:   # le guillemet ouvrant qui suit « Solo. » n'est pas un vers ; ailleurs il fait partie du texte
            t2 = re.sub(r"^[\"u]\s+", "", t2)
        t = re.sub(r"\s*\"\s*$", "", t2)
    t = re.sub(r"^[\*\+†]+\s*", "", t)                     # appel de note en tête
    t = re.sub(r"[\*\+†]+$", "", t.rstrip()).strip()        # appel de note en queue
    t = t.replace('"*', '"').replace("* ", " ")
    t = re.sub(r"^'\"\s*", '"', t).replace("'\"'", '"').replace("'\"", '"')
    if livre == T2:
        for a, b in OCR_T2:
            t = re.sub(a, b, t)
    for a, b in BRUIT:
        t = re.sub(a, b, t)
    t = re.sub(r"^\"\s+", '"', t)
    return t.strip(), num


def lire(livre: str):
    return (SRC / LIVRES[livre][0]).read_text(encoding="utf-8").splitlines()


def pages_whall(lignes):
    return [(n, int(s)) for n, s in ((i, l.strip()) for i, l in enumerate(lignes, 1)) if n >= 1706 and re.fullmatch(r"\d{1,3}", s)]


def extraire(lignes, plages, excl, livre, joins=frozenset(), ecart=3, debuts=frozenset()):
    gardes = []
    for a, b in plages:
        for n in range(a, b + 1):
            if n in excl:
                continue
            t = lignes[n - 1].strip()
            if t and not ENTETE.search(t):
                c, num = nettoyer(t, livre)
                if n in joins and gardes and c:   # suite de la ligne précédente (retour à la ligne de la colonne du livre)
                    pn, pc, pnum = gardes[-1]
                    if pc.endswith("-"):
                        pc = pc[:-1] if pc.split()[-1] in COUPURES else pc   # « pen- / non » : un seul mot coupé en fin de ligne
                        gardes[-1] = (n, pc + c, pnum)
                    else:
                        gardes[-1] = (n, pc + " " + c, pnum)
                # ligne de bruit : aucun mot de trois lettres
                elif c and re.search(r"[A-Za-zÀ-ÿ]{3,}", c):
                    gardes.append((n, c, num))
    numerote = livre != W and sum(1 for g in gardes if g[2]) >= 2
    couplets, cur, prec = [], [], None
    for n, c, num in gardes:
        coupure = (n in debuts) if debuts else (num if numerote else (prec is not None and n - prec >= ecart))
        if coupure and cur:
            couplets.append("\n".join(cur))
            cur = []
        cur.append(c)
        prec = n
    if cur:
        couplets.append("\n".join(cur))
    return "\n\n".join(couplets), (gardes[0][0] if gardes else None)


def source(cle, titre, livre, debut, marqueurs):
    nom, _, _, url = LIVRES[livre][1], 0, 0, LIVRES[livre][3]
    if livre == W:   # les numéros de page de l'OCR sont trop lacunaires : seule la p. 1 (Shenandoah) est certaine
        return f"{nom}, « {titre} »" + (", p. 1" if cle == "shenandoah" else "") + f" — {url}"
    if livre == S:
        return f"{nom}, {PAGES_SMITH[cle]} — {url}"
    num, page = NUMERO.get(cle, (None, None))
    return f"{nom}, n° {num}" + (f", p. {page}" if page else "") + f" — {url}"


def ecrire_json(d):
    out = ["{"]
    for i, k in enumerate(ORDRE_CLES):
        v = d[k]
        virg = ","
        if k == "ui":
            out.append('"ui": {')
            out.append(",\n".join(f'{json.dumps(l)}: ' + json.dumps(x, ensure_ascii=False, separators=(",", ":")) for l, x in v.items()))
            out.append("},")
        else:
            out.append(f'{json.dumps(k)}: {json.dumps(v, ensure_ascii=False, separators=(",", ":"))}{virg}')
    out.append('"chants": [')
    out.append(",\n".join(json.dumps(c, ensure_ascii=False, separators=(",", ":")) for c in d["chants"]))
    out.append("]\n}")
    JSON_F.write_text("\n".join(out) + "\n", encoding="utf-8")


def main():
    d = json.loads(JSON_F.read_text(encoding="utf-8"))
    anciens = [c for c in d["chants"] if not c.get("livre")]   # les six d'origine
    d["chants"] = anciens
    src_anciens = {
        "haul": "Paroles non retrouvées dans Terry I-II ni Whall (leur « Haul Away, Joe » est différent) — à vérifier ; audio : Wikimedia Commons, Haul_Away_Joe.ogg",
        "wellerman": "Paroles non retrouvées dans les livres de référence — à vérifier ; audio : Wikimedia Commons, Wellerman.wav",
        "merck": "Audio : Wikimedia Commons, Merck-toch-hoe-sterck-_fragment.ogg (domaine public) ; pas de paroles publiées",
        "lurrighan": "Audio : Wikimedia Commons, Leis_a_Lurrighan.ogg ; pas de paroles publiées",
        "trimartolod": "Chant traditionnel breton ; liens d'écoute seulement, pas de paroles publiées",
        "santiano": "Texte français de 1961 protégé jusqu'en 2057 : jamais publié ; liens d'écoute seulement",
    }
    for c in anciens:
        c["source"] = src_anciens.get(c["id"], c.get("source", ""))
    cache = {k: lire(k) for k in LIVRES}
    marq = pages_whall(cache[W])
    rejets = []
    for cle, titre, typ, livre, plages, excl, nfr, nen in SPECS:
        txt, debut = extraire(cache[livre], plages, set(excl), livre, JOINS.get(cle, frozenset()), ECARTS.get(cle, 3), DEBUTS.get(cle, frozenset()))
        if cle in MANUEL:
            txt = MANUEL[cle]
        if len(txt.splitlines()) < 4:
            rejets.append((titre, "moins de 4 vers lisibles"))
            continue
        lg = {"capitaine-du-mexico": "fr", "ved-balasthjoning": "no", "ali-alo": "fr"}.get(cle, "en")
        c = {"id": cle, "type": typ, "lg": lg, "titre": titre,
             "annees": "≤" + LIVRES[livre][2], "livre": livre,
             "resume": {"fr": nfr, "en": nen}, "paroles": txt, "accords": "", "audio": None, "video": None,
             "source": source(cle, titre, livre, debut, marq) + ("" if cle in COMPLETS or cle in COMPLETS_AJOUTS else " — " + RAISON.get(cle, "paroles partielles : le premier couplet et le refrain, notés sous la portée, ne sont pas toujours lisibles"))}
        if cle not in COMPLETS and cle not in COMPLETS_AJOUTS:
            c["partiel"] = True
        d["chants"].append(c)
    # Billy Boy (Terry I) : recopié à la main, deux colonnes entrelacées dans le scan
    d["chants"].append({"id": "billy-boy", "type": "virer", "lg": "en", "titre": "Billy Boy", "annees": "≤1921", "livre": T1,
                        "resume": {"fr": BILLY_NOTE[0], "en": BILLY_NOTE[1]}, "paroles": BILLY_BOY, "accords": "", "audio": None,
                        "video": None, "partiel": True,
                        "source": source("billy-boy", "Billy Boy", T1, 0, marq) + " — paroles partielles : couplets 2 à 4 ; le premier est noté sous la portée"})
    d["maj"] = "2026-11-25"
    d["note"] = ("Source unique de la page chants-de-marin.html (générateur : scripts/chants_page.py ; construit par scripts/chants_construire.py "
                 "depuis les livres Terry I-II et Whall, cache/chants/src). Les chants ne se traduisent JAMAIS : titre et paroles restent dans la langue d'origine (lg). "
                 "`resume` : fr et en obligatoires, les autres langues retombent sur le français. `source` : livre et page ou n° du chant. `partiel` : couplets manquants "
                 "(jamais inventés). `livre` : clé du livre d'où viennent les paroles. `video` : vide tant que la chaîne YouTube @SailingMore n'a pas publié le chant. "
                 "Santiano : texte français de 1961 protégé jusqu'en 2057, `paroles` reste vide.")
    pompe = {"fr": "À la pompe", "en": "Pump", "it": "Alla pompa", "es": "A la bomba", "pt": "À bomba", "de": "Pumplied"}
    grp = {"fr": "Chants par famille", "en": "Songs by family", "it": "Canti per famiglia", "es": "Cantos por familia", "pt": "Cantos por família", "de": "Lieder nach Gattung"}
    chapo = {
        "fr": "Les chants qui ont vraiment servi à bord : ce qu'ils faisaient à la manœuvre, les paroles du domaine public dans leur langue d'origine, chacune adossée à un livre cité (Terry, Whall, Smith). Quand un couplet est illisible dans le livre, il manque : il n'est jamais inventé. Ce qui est protégé est dit, jamais recopié.",
        "en": "The songs that actually worked a ship: what each one did at the ropes, public-domain lyrics in their original language, each tied to a cited book (Terry, Whall, Smith). When a verse is unreadable in the book it is missing, never invented. Anything still under copyright is named, never copied.",
        "it": "I canti che hanno davvero fatto lavorare una nave: cosa facevano a bordo, testi di pubblico dominio nella lingua originale, ciascuno legato a un libro citato (Terry, Whall, Smith). Un verso illeggibile nel libro manca, non viene mai inventato.",
        "es": "Los cantos que de verdad hacían trabajar un barco: qué hacían a bordo, letras de dominio público en su lengua original, cada una apoyada en un libro citado (Terry, Whall, Smith). Un verso ilegible en el libro falta; nunca se inventa.",
        "pt": "Os cantos que realmente faziam trabalhar um navio: o que faziam a bordo, letras de domínio público na língua original, cada uma apoiada num livro citado (Terry, Whall, Smith). Um verso ilegível no livro falta; nunca é inventado.",
        "de": "Die Lieder, mit denen wirklich gearbeitet wurde: was sie an Bord taten, Texte aus der Public Domain in der Originalsprache, jeder mit einem zitierten Buch belegt (Terry, Whall, Smith). Eine im Buch unlesbare Strophe fehlt, sie wird nie erfunden.",
    }
    for l in d["ui"]:
        d["ui"][l]["chapo"] = chapo[l]
    no = {"fr": "Norvégien", "en": "Norwegian", "it": "Norvegese", "es": "Noruego", "pt": "Norueguês", "de": "Norwegisch"}
    for l in d["langueNoms"]:
        d["langueNoms"][l]["no"] = no[l]
    for l in d["ui"]:
        d["ui"][l]["pompe"] = pompe[l]
        d["ui"][l]["sommaire"] = grp[l]
        d["ui"][l]["srcLib"] = {"fr": "Source", "en": "Source", "it": "Fonte", "es": "Fuente", "pt": "Fonte", "de": "Quelle"}[l]
    ecrire_json(d)
    n = len(d["chants"])
    print(f"{n} chants ; {sum(1 for c in d['chants'] if c.get('paroles') and not c.get('partiel'))} à paroles complètes (dont anciens) ; rejets : {rejets}")


if __name__ == "__main__":
    main()
