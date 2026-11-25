#!/usr/bin/env python3
"""Une page par mot du lexique : `site/lexique/<cle>.html`.

Entrée  : `projets/sailingmore/lexique.json` (les mots) + `site/cours.html` (les phrases du cours).
Sortie  : `projets/sailingmore/site/lexique/<cle>.html`, une page par mot.

La page dit, en six langues : le mot, sa définition, la phrase du cours qui le traite, deux questions
pour s'entraîner et le stage à réserver. Le contenu n'est **pas** écrit à la main : il est tiré des deux
sources ci-dessus à chaque construction. Un mot qui entre dans le cours reçoit sa question tout seul,
c'est le « mode auto » voulu par Nicolas le 25/11/2026 (« Oui en mode auto ensuite compris ? »).

Appelé par `lexique_page.py --site`, qui est le seul chemin de construction du lexique.
"""
from __future__ import annotations

import hashlib
import html as _html
import json
import re
import unicodedata
from pathlib import Path
from urllib.parse import quote

import jsonld
import site_blocks as _sb

LGS = ["fr", "en", "de", "it", "es", "pt"]
NOMS_LANGUES = {"fr": "français", "en": "English", "de": "Deutsch",
                "it": "italiano", "es": "español", "pt": "português"}

# Le texte de la page elle-même, dans les six langues.
UI = {
    "fr": {"ou": "Où l'apprendre", "questions": "Deux questions pour l'apprendre",
           "stage": "Réserver un stage", "voisins": "Les mots de la même famille",
           "prec": "Mot précédent", "suiv": "Mot suivant", "cours": "Le cours",
           "traductions": "Le mot dans six langues", "juste": "Bonne réponse.",
           "faux": "Non — la bonne réponse était :", "lexique": "Lexique",
           "retour": "← Sailing More", "detail": "Le mot en détail"},
    "en": {"ou": "Where to learn it", "questions": "Two questions to learn it",
           "stage": "Book a course", "voisins": "Words of the same family",
           "prec": "Previous word", "suiv": "Next word", "cours": "The lesson",
           "traductions": "The word in six languages", "juste": "Correct.",
           "faux": "No — the right answer was:", "lexique": "Glossary",
           "retour": "← Sailing More", "detail": "The word in detail"},
    "de": {"ou": "Wo man es lernt", "questions": "Zwei Fragen zum Lernen",
           "stage": "Kurs buchen", "voisins": "Wörter derselben Familie",
           "prec": "Voriges Wort", "suiv": "Nächstes Wort", "cours": "Die Lektion",
           "traductions": "Das Wort in sechs Sprachen", "juste": "Richtig.",
           "faux": "Nein — richtig war:", "lexique": "Lexikon",
           "retour": "← Sailing More", "detail": "Das Wort im Detail"},
    "it": {"ou": "Dove impararlo", "questions": "Due domande per impararlo",
           "stage": "Prenota un corso", "voisins": "Le parole della stessa famiglia",
           "prec": "Parola precedente", "suiv": "Parola successiva", "cours": "La lezione",
           "traductions": "La parola in sei lingue", "juste": "Risposta giusta.",
           "faux": "No — la risposta giusta era:", "lexique": "Lessico",
           "retour": "← Sailing More", "detail": "La parola in dettaglio"},
    "es": {"ou": "Dónde aprenderlo", "questions": "Dos preguntas para aprenderlo",
           "stage": "Reservar un curso", "voisins": "Las palabras de la misma familia",
           "prec": "Palabra anterior", "suiv": "Palabra siguiente", "cours": "La lección",
           "traductions": "La palabra en seis idiomas", "juste": "Respuesta correcta.",
           "faux": "No — la respuesta correcta era:", "lexique": "Léxico",
           "retour": "← Sailing More", "detail": "La palabra en detalle"},
    "pt": {"ou": "Onde o aprender", "questions": "Duas perguntas para o aprender",
           "stage": "Reservar um curso", "voisins": "As palavras da mesma família",
           "prec": "Palavra anterior", "suiv": "Palavra seguinte", "cours": "A lição",
           "traductions": "A palavra em seis línguas", "juste": "Resposta certa.",
           "faux": "Não — a resposta certa era:", "lexique": "Léxico",
           "retour": "← Sailing More", "detail": "A palavra em detalhe"},
}

# La deuxième question : « comment dit-on … ? », vers le français, ou vers l'anglais pour un lecteur
# francophone. Elle marche pour les 505 mots, même ceux que le cours ne traite pas encore.
Q_TRAD = {
    "fr": [("en", "Comment dit-on « {m} » en anglais ?"),
           ("de", "Et en allemand ?")],
    "en": [("fr", "How do you say « {m} » in French?"),
           ("de", "And in German?")],
    "de": [("fr", "Wie sagt man « {m} » auf Französisch?"),
           ("en", "Und auf Englisch?")],
    "it": [("fr", "Come si dice « {m} » in francese?"),
           ("en", "E in inglese?")],
    "es": [("fr", "¿Cómo se dice « {m} » en francés?"),
           ("en", "¿Y en inglés?")],
    "pt": [("fr", "Como se diz « {m} » em francês?"),
           ("en", "E em inglês?")],
}

# L'entrée de la première question, dans la langue du lecteur.
Q_TROU = {"fr": "Quel mot manque ?", "en": "Which word is missing?", "de": "Welches Wort fehlt?",
          "it": "Quale parola manca?", "es": "¿Qué palabra falta?", "pt": "Que palavra falta?"}

CSS_PLUS = """
.mot-tete{margin:0 0 .4rem}
.fil{font-size:.66rem;letter-spacing:.14em;text-transform:uppercase;color:#6f8598;margin:1.4rem 0 0}
.fil a{color:#9db2c6}
.fil a:hover{color:#fff}
.def{font-size:1.02rem;color:#dbe6f0;max-width:38rem;margin:.2rem 0 1.6rem}
.bloc{border-top:1px solid rgba(255,255,255,.09);padding:1.3rem 0 .3rem;margin-top:1.2rem}
.bloc h2{font-size:.68rem;letter-spacing:.16em;text-transform:uppercase;color:#9db2c6;
  font-weight:500;margin:0 0 .8rem}
.citation{margin:0 0 .8rem;padding-left:.9rem;border-left:2px solid var(--rouge);
  color:#cfe0ee;font-size:.95rem;max-width:40rem}
.chap-lien{display:inline-block;color:#fff;border-bottom:1px solid rgba(226,58,62,.6);
  font-size:.9rem;padding-bottom:1px}
.chap-lien:hover{color:var(--rouge)}
table.trad{width:100%;border-collapse:collapse;font-size:.92rem;max-width:34rem}
table.trad th,table.trad td{text-align:left;padding:.32rem 0;border-bottom:1px solid rgba(255,255,255,.06);
  font-weight:400}
table.trad th{width:9rem;color:#9db2c6;font-size:.72rem;letter-spacing:.1em;text-transform:uppercase}
.q{margin:0 0 1.2rem}
.q p{margin:0 0 .5rem;font-size:.95rem}
.q .choix{display:flex;gap:.4rem;flex-wrap:wrap}
.q button{background:none;border:1px solid rgba(157,178,198,.32);color:#cfe0ee;border-radius:999px;
  padding:.34rem .8rem;font:inherit;font-size:.86rem;cursor:pointer}
.q button:hover{border-color:#9db2c6;color:#fff}
.q button.juste{border-color:#3fbf7f;color:#8ff0c0}
.q button.faux{border-color:var(--rouge);color:#ffb3b5}
.q .dit{font-size:.78rem;color:#9db2c6;margin-top:.4rem;min-height:1em}
.voisins ul{list-style:none;padding:0;margin:0;display:flex;gap:.4rem .9rem;flex-wrap:wrap}
.voisins a{font-size:.88rem;color:#cfe0ee;border-bottom:1px solid rgba(226,58,62,.35)}
.voisins a:hover{color:#fff}
.pas{display:flex;justify-content:space-between;gap:1rem;margin-top:2.4rem;font-size:.82rem;
  border-top:1px solid rgba(255,255,255,.09);padding-top:1rem}
.pas a{color:#9db2c6}
.pas a:hover{color:#fff}
.stage-lien{display:inline-block;margin-top:.2rem;border:1px solid rgba(226,58,62,.7);color:#fff;
  border-radius:2px;padding:.55rem 1rem;font-size:.82rem;letter-spacing:.06em;text-transform:uppercase}
.stage-lien:hover{background:rgba(226,58,62,.16)}
"""

JS = r"""
(function(){
  var D = null;
  try{ D = JSON.parse(document.getElementById('mot-donnees').textContent); }catch(e){ return; }
  var L = (typeof window.smLangue === 'function') ? window.smLangue() : 'fr';
  if(L === 'bzh' || L.indexOf) {}
  if(D.langues.indexOf(L) < 0) L = 'fr';
  var u = D.ui[L] || D.ui.fr;
  function txt(id, v){ var e = document.getElementById(id); if(e && v != null) e.textContent = v; }
  function esc(s){ return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); }

  function questions(){
    var z = document.getElementById('zone-q'); if(!z) return;
    var qs = D.questions[L] || [], out = '';
    qs.forEach(function(q, i){
      out += '<div class="q" data-i="' + i + '"><p>' + esc(q.q) + '</p><div class="choix">';
      q.a.forEach(function(c, j){ out += '<button type="button" data-bon="' + (j === q.bon ? 1 : 0) + '">' + esc(c) + '</button>'; });
      out += '</div><div class="dit"></div></div>';
    });
    z.innerHTML = out;
  }

  function cours(){
    var z = document.getElementById('zone-cours'); if(!z) return;
    var c = D.cours[L] || D.cours.fr;
    if(!c){ z.innerHTML = ''; return; }
    z.innerHTML = (c.phrase ? '<p class="citation">« ' + esc(c.phrase) + ' »</p>' : '')
      + '<a class="chap-lien"></a>';
    var a = z.querySelector('.chap-lien');
    if(a){ a.textContent = c.titre; a.href = '../cours.html#ch' + c.n + '-' + L; }
  }

  function apply(){
    txt('titre', D.mot[L]); txt('def', D.def[L]);
    txt('t-ou', u.ou); txt('t-questions', u.questions); txt('t-stage', u.stage);
    txt('t-voisins', u.voisins); txt('t-trad', u.traductions);
    txt('l-lexique', u.lexique); txt('l-retour', u.retour);
    var stage = document.getElementById('lien-stage'); if(stage) stage.textContent = u.stage;
    var th = document.getElementById('lien-theme'); if(th) th.textContent = D.theme.nom[L];
    questions(); cours();
    document.querySelectorAll('.voisins a').forEach(function(a, i){
      var v = D.voisins[i]; if(v) a.textContent = v.mot[L];
    });
    document.querySelectorAll('td[data-lg]').forEach(function(c){ c.textContent = D.mot[c.dataset.lg]; });
  }

  document.addEventListener('click', function(ev){
    var b = ev.target.closest ? ev.target.closest('.q button') : null;
    if(!b) return;
    var box = b.closest('.q'), dit = box.querySelector('.dit');
    box.querySelectorAll('button').forEach(function(x){ x.classList.remove('juste','faux'); });
    var bon = b.dataset.bon === '1';
    b.classList.add(bon ? 'juste' : 'faux');
    var i = +box.dataset.i, q = (D.questions[L] || [])[i];
    if(bon){ dit.textContent = u.juste; }
    else{
      box.querySelectorAll('button').forEach(function(x){ if(x.dataset.bon === '1') x.classList.add('juste'); });
      dit.textContent = u.faux + ' ' + (q ? q.a[q.bon] : '');
    }
  });

  apply();
})();
"""


# ── les sources ────────────────────────────────────────────────────────────────────────────────
def _plat(t: str) -> str:
    t = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", t, flags=re.S)
    t = re.sub(r"<[^>]+>", " ", t)
    t = _html.unescape(t)
    t = re.sub(r"\s+", " ", t)
    t = re.sub(r"\s+([,.;:!?»’])", r"\1", t)   # pas d'espace avant la ponctuation
    t = re.sub(r"([«‘])\s+", r"\1", t)
    t = re.sub(r"([’'])\s+", r"\1", t)         # l' étrave -> l'étrave
    return t.strip()


def _nu(s: str) -> str:
    s = unicodedata.normalize("NFD", s.lower())
    return re.sub(r"[\u0300-\u036f]", "", s)


def _a_trou(texte: str, mot: str) -> str:
    """Remplace le mot par « … » dans un texte, accents compris, en gardant le reste intact."""
    if len(mot) < 3:
        return texte
    nfd = unicodedata.normalize("NFD", texte)
    base = "".join(c for c in unicodedata.normalize("NFD", mot)
                   if not unicodedata.combining(c)).lower()
    frag = "".join(r"\s+" if c.isspace() else re.escape(c) + "[\u0300-\u036f]*" for c in base)
    remplace, n = re.subn(r"\b" + frag + r"\b", "…", nfd, count=1, flags=re.I)
    return unicodedata.normalize("NFC", remplace) if n else texte


def sections(site: Path) -> dict[str, dict]:
    """Les chapitres du cours publié, découpés par langue : {(n, langue): {titre, texte}}."""
    f = site / "cours.html"
    if not f.exists():
        return {}
    h = f.read_text(encoding="utf-8")
    out = {}
    for m in re.finditer(r'<section[^>]*id="ch(\d+)-([a-z]{2})"[^>]*>(.*?)</section>', h, flags=re.S):
        n, lg, corps = int(m.group(1)), m.group(2), m.group(3)
        t = re.search(r"<h2>(.*?)</h2>", corps, flags=re.S)
        titre = _plat(t.group(1)) if t else ""
        titre = re.sub(r"^\d+\s*", "", titre)
        out[(n, lg)] = {"titre": titre, "texte": _plat(corps)}
    return out


def _phrase(texte: str, motif: str) -> str:
    for p in re.split(r"(?<=[.!?])\s+", texte):
        if re.search(motif, _nu(p)):
            p = p.strip()
            if 12 <= len(p.split()) <= 40:
                return p
    return ""


def ou_est(mot: dict, secs: dict, prefere: int | None = None) -> dict:
    """Pour chaque langue : le chapitre du cours qui parle le plus du mot, et la phrase qui le porte."""
    res = {}
    for lg in LGS:
        res[lg] = None
        m = _nu(mot.get(lg, "")).strip()
        if len(m) < 3:
            continue
        motif = r"\b" + re.escape(m) + r"\b"
        best = None
        for (n, l), s in secs.items():
            if l != lg:
                continue
            c = len(re.findall(motif, _nu(s["texte"])))
            if not c:
                continue
            if best is None or c > best[0] or (c == best[0] and n < best[1]):
                best = (c, n, s)
        # Le chapitre du thème d'abord : c'est celui que le lexique annonce déjà au lecteur.
        p = secs.get((prefere, lg)) if prefere else None
        if p and re.search(motif, _nu(p["texte"])):
            best = (1, prefere, p)
        if best:
            res[lg] = {"n": best[1], "titre": best[2]["titre"],
                       "phrase": _phrase(best[2]["texte"], motif)}
    return res


def _melange(cle: str, items: list) -> list:
    """Ordre stable (même page à chaque construction) mais pas alphabétique."""
    return sorted(items, key=lambda s: hashlib.sha256((cle + "·" + s).encode()).hexdigest())


def questions(cle: str, mot: dict, defs: dict, cours: dict, voisins: list) -> dict:
    """Deux questions par langue, tirées des sources : la phrase du cours à trous, la définition à trous.

    Rien n'est écrit à la main : les questions suivent le cours et le lexique quand ils changent. Les
    deux mauvaises réponses sont deux mots de la même famille, donc plausibles.
    """
    res = {}
    for lg in LGS:
        m = mot.get(lg, "")
        if len(m) < 3:
            continue
        dispo = [v["mot"][lg] for v in voisins if v["mot"].get(lg) and v["mot"][lg].lower() != m.lower()]
        autres = _melange(cle + lg, dispo)[:2]
        if len(autres) < 2:
            continue
        qs = []
        c = cours.get(lg)
        if c and c.get("phrase"):
            trou = _a_trou(c["phrase"], m)
            if "…" in trou:
                choix = _melange(cle + lg + "c", [m] + autres)
                qs.append({"q": Q_TROU[lg] + " « " + trou + " »",
                           "a": choix, "bon": choix.index(m)})
        # 2 et 3. les traductions : le mot dans une autre langue, deux mots voisins pour brouiller.
        for k, (cible, gabarit) in enumerate(Q_TRAD[lg]):
            bon_mot = mot.get(cible, "")
            faux = [v["mot"][cible] for v in voisins
                    if v["mot"].get(cible) and v["mot"][cible] != bon_mot]
            faux = _melange(cle + lg + "t" + str(k), faux)[:2]
            if len(bon_mot) >= 2 and len(faux) == 2:
                choix = _melange(cle + lg + "td" + str(k), [bon_mot] + faux)
                qs.append({"q": gabarit.format(m=m), "a": choix, "bon": choix.index(bon_mot)})
        if qs:
            res[lg] = qs
    return res


# ── la page ───────────────────────────────────────────────────────────────────────────────────
def page_mot(entree: dict, voisins: list, prec: dict | None, suiv: dict | None,
             ou: dict, css: str, url_theme: str) -> str:
    e = _html.escape
    x, theme = entree["x"], entree["theme"]
    cle = x["cle"]
    fr = "fr"
    qs = questions(cle, x["mot"], x["def"], ou, voisins)
    vi = [{"cle": v["cle"], "mot": v["mot"]} for v in voisins]
    donnees = {"langues": LGS, "cle": cle, "ui": UI,
               "theme": {"cle": theme["cle"], "nom": theme["nom"]},
               "mot": {lg: x["mot"][lg] for lg in LGS},
               "def": {lg: x["def"][lg] for lg in LGS},
               "cours": ou, "questions": qs, "voisins": vi}
    brut = json.dumps(donnees, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")

    # Le chapitre français, écrit en dur pour les moteurs de recherche.
    c = ou.get(fr)
    bloc_cours = (f'<p class="citation">« {e(c["phrase"])} »</p>' if c and c["phrase"] else "") + (
        f'<a class="chap-lien" href="cours.html#ch{c["n"]}-fr">{e(c["titre"])}</a>' if c else "")

    # Les questions françaises, écrites en dur (le script les reconstruit pour les autres langues).
    qhtml = []
    for i, q in enumerate(qs.get(fr, [])):
        boutons = "".join(f'<button type="button" data-bon="{1 if j == q["bon"] else 0}">{e(a)}</button>'
                          for j, a in enumerate(q["a"]))
        qhtml.append(f'<div class="q" data-i="{i}"><p>{e(q["q"])}</p>'
                     f'<div class="choix">{boutons}</div><div class="dit"></div></div>')

    voisins_html = "".join(
        f'<li><a href="{e(v["cle"])}.html">{e(v["mot"][fr])}</a></li>' for v in voisins)
    prec_html = (f'<a href="{e(prec["cle"])}.html">← {e(prec["mot"][fr])}</a>' if prec else "<span></span>")
    suiv_html = (f'<a href="{e(suiv["cle"])}.html">{e(suiv["mot"][fr])} →</a>' if suiv else "<span></span>")

    titre_seo = f"{x['mot'][fr]} : définition, traduction et questions | Lexique de voile"
    desc = re.sub(r"\s+", " ", x["def"][fr])[:155]
    url = f"{jsonld.SITE}/lexique/{cle}.html"
    ld = jsonld.bloc(
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Sailing More", "item": jsonld.SITE + "/"},
            {"@type": "ListItem", "position": 2, "name": "Lexique de voile",
             "item": jsonld.SITE + "/lexique.html"},
            {"@type": "ListItem", "position": 3, "name": x["mot"][fr], "item": url}]},
        {"@type": "DefinedTerm", "@id": url, "name": x["mot"][fr], "description": x["def"][fr],
         "url": url, "inDefinedTermSet": {"@id": f"{jsonld.SITE}/lexique.html#lexique"},
         "inLanguage": "fr"})

    return (
        '<!doctype html>\n<html lang="fr"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        f"<title>{e(titre_seo)}</title>"
        f'<link rel="canonical" href="{url}">'
        + _sb.script_langue() + ld +
        f'<meta name="description" content="{e(desc)}">'
        + jsonld.social(f"lexique/{cle}.html", titre_seo, desc) +
        "<style>" + css + CSS_PLUS + "</style></head><body>"
        + _sb.barre_autonome("lexique.html", LGS) +
        '<main class="page">'
        f'<p class="fil"><a id="l-retour" href="../index.html">← Sailing More</a> · '
        f'<a id="l-lexique" href="../lexique.html">Lexique</a> · '
        f'<a id="lien-theme" href="{e(url_theme)}">{e(theme["nom"][fr])}</a></p>'
        f'<h1 class="mot-tete" id="titre">{e(x["mot"][fr])}</h1>'
        f'<p class="def" id="def">{e(x["def"][fr])}</p>'
        '<section class="bloc"><h2 id="t-trad">Le mot dans six langues</h2>'
        '<table class="trad">'
        + "".join(f'<tr><th>{e(NOMS_LANGUES[lg])}</th><td data-lg="{lg}">{e(x["mot"][lg])}</td></tr>'
                  for lg in LGS)
        + '</table></section>'
        '<section class="bloc"><h2 id="t-ou">Où l\'apprendre</h2>'
        f'<div id="zone-cours">{bloc_cours}</div></section>'
        '<section class="bloc"><h2 id="t-questions">Deux questions pour l\'apprendre</h2>'
        f'<div id="zone-q">{"".join(qhtml)}</div></section>'
        '<section class="bloc"><h2 id="t-stage">Un stage à réserver</h2>'
        f'<a class="stage-lien" id="lien-stage" href="../stages.html?q={quote(x["mot"][fr])}">Réserver un stage</a>'
        '</section>'
        '<section class="bloc voisins"><h2 id="t-voisins">Les mots de la même famille</h2>'
        f'<ul>{voisins_html}</ul></section>'
        f'<nav class="pas">{prec_html}{suiv_html}</nav>'
        '</main>'
        f'<script type="application/json" id="mot-donnees">{brut}</script>'
        "<script>" + JS + "</script></body></html>\n"
    )


def _liens_du_dossier(html: str) -> str:
    """Les pages vivent dans `lexique/` : tout lien du site écrit en relatif remonte d'un cran.

    La barre du site, le chapitre du cours et le stage écrivent `cours.html`, `stages.html` : depuis
    `lexique/`, ces adresses tombent dans le vide. On les préfixe ici, une fois, plutôt que de faire
    deux barres ou deux listes de liens.
    """
    def remplace(m):
        url = m.group(1)
        if url.startswith(("/", "#", "http", "mailto:", "..")):
            return m.group(0)
        return 'href="../' + url + '"'
    return re.sub(r'href="([^"]*)"', remplace, html)


def ecrire_tout(site: Path, themes: list[dict], css: str) -> tuple[int, int]:
    """Écrit une page par mot. Rend (nombre de pages, nombre de pages avec une phrase du cours)."""
    from lexique_page import ancre_cours, numero_chapitre  # noqa: PLC0415 (import circulaire)
    secs = sections(site)
    dossier = site / "lexique"
    dossier.mkdir(parents=True, exist_ok=True)
    # Tous les mots, dans l'ordre alphabétique français, pour les liens précédent/suivant.
    tous = [{"x": x, "theme": t} for t in themes for x in t["termes"]]
    tous.sort(key=lambda o: _nu(o["x"]["mot"]["fr"]))
    n_cours = 0
    for i, o in enumerate(tous):
        x, t = o["x"], o["theme"]
        voisins = [{"cle": v["x"]["cle"], "mot": v["x"]["mot"]}
                   for v in tous if v["theme"]["cle"] == t["cle"] and v["x"]["cle"] != x["cle"]][:5]
        prefere = numero_chapitre().get(ancre_cours(t["cle"]), 1)
        url_theme = "../lexique.html#" + t["cle"]
        ou = ou_est(x["mot"], secs, prefere)
        av = {"cle": tous[i - 1]["x"]["cle"], "mot": tous[i - 1]["x"]["mot"]} if i else None
        ap = ({"cle": tous[i + 1]["x"]["cle"], "mot": tous[i + 1]["x"]["mot"]}
              if i + 1 < len(tous) else None)
        html = page_mot(o, voisins, av, ap, ou, css, url_theme)
        (dossier / f"{x['cle']}.html").write_text(_liens_du_dossier(html), encoding="utf-8")
        if ou.get("fr"):
            n_cours += 1
    return len(tous), n_cours


def ecrire_page(site: Path) -> str:
    """Le point d'entrée appelé par `accueil_site.py --site`, comme les autres pages du site."""
    from lexique_page import CSS, charger, themes_affichables  # noqa: PLC0415 (import circulaire)
    d = charger()
    n, avec = ecrire_tout(site, themes_affichables(d), CSS)
    return f"{n} page(s) de mot, {avec} avec une phrase du cours"
