#!/usr/bin/env python3
"""Tuteur du cours (tâche 63) : la réponse ne sort jamais sans sa phrase-source cliquable.

PRINCIPE
  1. LE CODE CHOISIT : l'index (tuteur-index.json) est tiré des pages de chapitre déjà publiées
     (cours-<slug>.html, français). Une question est comparée aux phrases du cours (recouvrement de mots
     pondéré par la rareté) ; le code retient UN chapitre et UNE phrase. Aucun modèle ne choisit.
  2. LE MODÈLE FORMULE (ou pas) : `formuler()` ne reçoit que la phrase-source ; sa sortie est refusée si elle
     introduit un nombre absent de la phrase. Aucun modèle n'est branché ici : la réponse est la phrase du cours.
  3. SANS PHRASE-SOURCE, ON S'ABSTIENT : seuils de score et de couverture ; en dessous, aucune réponse.
  4. Chaque réponse porte le chapitre, la phrase, et un lien vers l'ancre du chapitre (cours-<slug>.html#chN-fr).

Le même algorithme est repris dans tuteur-cours.js (le navigateur) ; les paramètres (mots vides, seuils, règle
de radical) viennent de l'index, pas du JS.

    python3 scripts/tuteur_cours.py --ecrire     # écrit site/tuteur-index.json, tuteur-cours.js, tuteur-cours.html
    python3 scripts/tuteur_cours.py --controle   # les 20 questions + les questions hors cours + citations vérifiées
    python3 scripts/tuteur_cours.py "ma question"
Bibliothèque standard seulement.
"""
from __future__ import annotations

import json
import math
import os
import re
import sys
import unicodedata
from html.parser import HTMLParser
from pathlib import Path

RACINE = Path(os.environ.get("SITE_ROOT", str(Path(__file__).resolve().parent.parent)))
SITE = RACINE / "projets" / "sailingmore" / "site"
QUESTIONS = Path(__file__).resolve().parent / "tuteur_questions.json"

MOTS_VIDES = ("le la les un une des du de d l au aux et ou en a à y est sont se sa son ses ce cet cette ces que qui "
              "quoi quel quelle quels quelles quand comment pourquoi combien dans sur par pour avec sans "
              "ne pas plus il elle ils elles on nous vous je tu mon ma mes ton ta tes leur leurs ca cela "
              "faut faire fait dit dire peut peu être etre avoir ont as si mais donc car ni "
              "doit doivent signifie veut quelle quelles appelle appelle-t-on s t qu c n m j "
              "entre cours chapitre voile").split()
RADICAL = 7          # un mot est ramené à ses 7 premières lettres, après retrait d'un s/x final
MIN_MOTS = 3         # une phrase du cours compte au moins 3 mots
SEUIL_COUVERTURE = 0.6   # part (pondérée) des mots utiles de la question retrouvés dans la phrase
SEUIL_SCORE = 2.5        # somme des raretés des mots retrouvés
POIDS_INCONNU = 3.0      # poids d'un mot de la question absent de tout le cours (dans l'index : poids_inconnu)


def _plat(t: str) -> str:
    """Minuscules, sans accents."""
    t = t.lower().replace("œ", "oe").replace("æ", "ae")
    return "".join(c for c in unicodedata.normalize("NFD", t) if unicodedata.category(c) != "Mn")


def mots(texte: str, vides: set[str] | None = None) -> list[str]:
    """Radical : s/x final, puis « er » (si > 5 lettres), puis « e » final (si > 3), puis 7 lettres au plus."""
    vides = {_plat(v) for v in (MOTS_VIDES if vides is None else vides)}
    out = []
    for m in re.findall(r"[a-z0-9]+", _plat(texte)):
        if m in vides or (len(m) < 3 and not m.isdigit()):
            continue
        if len(m) > 3 and m[-1] in "sx":
            m = m[:-1]
        if len(m) > 5 and m.endswith("er"):
            m = m[:-2]
        elif len(m) > 3 and m.endswith("e"):
            m = m[:-1]
        out.append(m[:RADICAL])
    return out


# ── 1. L'INDEX, tiré des pages publiées ─────────────────────────────────────────────────────────────────
class _Chapitre(HTMLParser):
    SUIVIS = {"div", "aside", "svg", "details", "section", "nav", "figure", "script", "style"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.chap_id = ""
        self.titre = ""
        self.blocs: list[str] = []
        self._pile: list[tuple[str, bool]] = []   # (balise, ignorée ?)
        self._tampon: list[str] | None = None
        self._h1 = False

    def _ignore(self) -> bool:
        return any(s for _, s in self._pile)

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        cls = (a.get("class") or "").split()
        if tag == "section" and "chap" in cls and not self.chap_id:
            self.chap_id = a.get("id") or ""
            self._pile.append((tag, False))
            return
        if tag in self.SUIVIS:
            saut = tag in {"aside", "svg", "details", "script", "style", "nav"} or "exo" in cls or "encart-stage" in cls
            self._pile.append((tag, saut))
            return
        if not self.chap_id:
            return
        if tag == "h1" and not self.titre:
            self._h1 = True
            self._tampon = []
        elif tag in ("p", "li") and not self._ignore() and "note" not in cls and "haut-lien" not in cls:
            self._tampon = []

    def handle_endtag(self, tag):
        if tag in self.SUIVIS:
            for i in range(len(self._pile) - 1, -1, -1):
                if self._pile[i][0] == tag:
                    del self._pile[i:]
                    break
            return
        if tag == "h1" and self._h1:
            self.titre = re.sub(r"^\d+\s*", "", "".join(self._tampon or []).strip())
            self._h1, self._tampon = False, None
        elif tag in ("p", "li") and self._tampon is not None:
            t = re.sub(r"\s+", " ", "".join(self._tampon)).strip()
            self._tampon = None
            if t:
                self.blocs.append(t)

    def handle_data(self, data):
        if self._tampon is not None:
            self._tampon.append(data)


def phrases_de(bloc: str) -> list[str]:
    morceaux = re.split(r"(?<=[.!?])\s+(?=[A-ZÀ-ÝÉÈÊ«\d])", bloc)
    return [p.strip() for p in morceaux if len(p.split()) >= MIN_MOTS]


def pages_chapitres() -> list[Path]:
    out = []
    for f in sorted(SITE.glob("cours-*.html")):
        if re.search(r"-(en|de|it|es|pt)\.html$", f.name) or f.name == "cours-revision.html":
            continue
        if 'class="chap"' in f.read_text(encoding="utf-8"):
            out.append(f)
    return out


def construire_index() -> dict:
    chapitres, phrases = [], []
    for f in pages_chapitres():
        p = _Chapitre()
        p.feed(f.read_text(encoding="utf-8"))
        if not (p.chap_id and p.titre and p.blocs):
            continue
        ci = len(chapitres)
        chapitres.append({"titre": p.titre, "page": f.name, "ancre": p.chap_id})
        vus = set()
        for b in p.blocs:
            for s in phrases_de(b):
                if s not in vus:
                    vus.add(s)
                    phrases.append({"c": ci, "s": s, "m": sorted(set(mots(s)))})
    df: dict[str, int] = {}
    for ph in phrases:
        for m in ph["m"]:
            df[m] = df.get(m, 0) + 1
    n = len(phrases)
    idf = {m: round(math.log(1 + n / d), 3) for m, d in df.items()}
    return {"version": 1, "langue": "fr", "radical": RADICAL, "seuil_score": SEUIL_SCORE,
            "seuil_couverture": SEUIL_COUVERTURE, "poids_inconnu": POIDS_INCONNU, "mots_vides": MOTS_VIDES, "idf": idf,
            "chapitres": chapitres, "phrases": phrases}


# ── 2. LE CHOIX, par le code ────────────────────────────────────────────────────────────────────────────
def repondre(question: str, idx: dict) -> dict:
    """{"statut": "reponse", chapitre, phrase, lien} ou {"statut": "abstention", raison}. Rien d'autre."""
    q = sorted(set(mots(question, set(idx["mots_vides"]))))
    idf = idx["idf"]
    connus = [m for m in q if m in idf]
    if not connus:
        return {"statut": "abstention", "raison": "aucun mot de la question n'apparaît dans le cours"}
    total = sum(idf[m] for m in connus) + POIDS_INCONNU * sum(1 for m in q if m not in idf)   # un mot inconnu pèse : il baisse la couverture
    meilleur = None
    par_chap: dict[int, float] = {}
    for ph in idx["phrases"]:
        trouves = [m for m in connus if m in ph["m"]]
        if not trouves:
            continue
        score = sum(idf[m] for m in trouves)
        cov = score / total
        if cov >= idx["seuil_couverture"] and score >= idx["seuil_score"]:
            par_chap[ph["c"]] = max(par_chap.get(ph["c"], 0), score)
            # à score égal, la phrase la plus courte (la plus ciblée) l'emporte
            if meilleur is None or (score, cov, -len(ph["m"])) > (meilleur[0], meilleur[1], -len(meilleur[2]["m"])):
                meilleur = (score, cov, ph)
    if meilleur is None:
        return {"statut": "abstention", "raison": "aucune phrase du cours ne couvre la question"}
    ph = meilleur[2]
    ch = idx["chapitres"][ph["c"]]
    return {"statut": "reponse", "chapitre": ch["titre"], "phrase": ph["s"],
            "lien": f'{ch["page"]}#{ch["ancre"]}', "score": round(meilleur[0], 2), "couverture": round(meilleur[1], 2)}


def formuler(reponse: dict, modele=None) -> str:
    """Le modèle reformule la PHRASE-SOURCE, jamais le choix. Refusé s'il ajoute un nombre ; sinon la phrase telle quelle."""
    src = reponse["phrase"]
    if modele is None:
        return src
    try:
        sortie = modele(src).strip()
    except Exception:  # noqa: BLE001
        return src
    nb = lambda t: set(re.findall(r"\d+", t))  # noqa: E731
    return sortie if sortie and nb(sortie) <= nb(src) else src


# ── 3. LA PAGE ET LE JS ─────────────────────────────────────────────────────────────────────────────────
JS = r"""/* Tuteur du cours : même algorithme que scripts/tuteur_cours.py, paramètres lus dans tuteur-index.json. */
(function () {
  var f = document.getElementById('tuteur-form'), q = document.getElementById('tuteur-q'), out = document.getElementById('tuteur-rep');
  if (!f) return;
  var idx = null;
  function charger() { return idx ? Promise.resolve(idx) : fetch('/tuteur-index.json').then(function (r) { return r.json(); }).then(function (j) { idx = j; return j; }); }
  function mots(t, vides) {
    var s = t.toLowerCase().replace(/œ/g, 'oe').replace(/æ/g, 'ae').normalize('NFD').replace(/[̀-ͯ]/g, ''), out = [], m = s.match(/[a-z0-9]+/g) || [];
    for (var i = 0; i < m.length; i++) {
      var w = m[i];
      if (vides[w] || (w.length < 3 && !/^\d+$/.test(w))) continue;
      if (w.length > 3 && /[sx]$/.test(w)) w = w.slice(0, -1);
      if (w.length > 5 && /er$/.test(w)) w = w.slice(0, -2); else if (w.length > 3 && /e$/.test(w)) w = w.slice(0, -1);
      out.push(w.slice(0, idx.radical));
    }
    return out.filter(function (x, k) { return out.indexOf(x) === k; }).sort();
  }
  function repondre(question) {
    var vides = {}; idx.mots_vides.forEach(function (v) { vides[v.normalize('NFD').replace(/[̀-ͯ]/g, '')] = 1; });
    var qm = mots(question, vides), connus = qm.filter(function (m) { return idx.idf[m] !== undefined; });
    if (!connus.length) return null;
    var total = 0; connus.forEach(function (m) { total += idx.idf[m]; }); total += idx.poids_inconnu * (qm.length - connus.length);
    var best = null;
    idx.phrases.forEach(function (ph) {
      var sc = 0; connus.forEach(function (m) { if (ph.m.indexOf(m) >= 0) sc += idx.idf[m]; });
      if (!sc) return;
      var cov = sc / total;
      if (cov >= idx.seuil_couverture && sc >= idx.seuil_score && (!best || sc > best.sc || (sc === best.sc && (cov > best.cov || (cov === best.cov && ph.m.length < best.ph.m.length))))) best = { sc: sc, cov: cov, ph: ph };
    });
    return best && best.ph;
  }
  f.addEventListener('submit', function (e) {
    e.preventDefault();
    var question = q.value.trim(); if (!question) return;
    charger().then(function () {
      var ph = repondre(question); out.textContent = '';
      var box = document.createElement('div');
      if (!ph) {
        box.className = 'abst';
        box.textContent = "Je ne trouve pas la réponse dans le cours, donc je ne réponds pas. Reformule avec les mots du cours, ou parcours le sommaire.";
        var a0 = document.createElement('a'); a0.href = '/cours.html'; a0.textContent = ' Ouvrir le cours'; box.appendChild(a0);
      } else {
        var ch = idx.chapitres[ph.c];
        var bq = document.createElement('blockquote'); bq.textContent = ph.s;
        var src = document.createElement('p'); src.className = 'src'; src.appendChild(document.createTextNode('Source : chapitre « '));
        var a = document.createElement('a'); a.href = '/' + ch.page + '#' + ch.ancre; a.textContent = ch.titre;
        src.appendChild(a); src.appendChild(document.createTextNode(' » — phrase du cours ci-dessus.'));
        box.appendChild(bq); box.appendChild(src);
      }
      out.appendChild(box);
    });
  });
})();
"""

PAGE = """<!doctype html>
<html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Tuteur du cours | Sailing More</title><meta name="robots" content="noindex">
<link rel="canonical" href="https://sailingmore.fr/tuteur-cours.html">
<style>body{font:1.05rem/1.55 system-ui,sans-serif;max-width:42rem;margin:2rem auto;padding:0 1.2rem;color:#0a1f33}
input{width:100%;padding:.7rem;font:inherit;border:1px solid #9ab;border-radius:.4rem;box-sizing:border-box}
button{margin-top:.6rem;padding:.6rem 1.2rem;font:inherit;border:0;border-radius:.4rem;background:#0a4f7a;color:#fff;cursor:pointer}
blockquote{margin:1.2rem 0 .4rem;padding:.6rem 1rem;border-left:4px solid #0a4f7a;background:#eef5fa}
.src{font-size:.95rem}.abst{margin-top:1.2rem;padding:.8rem 1rem;background:#fff6e5;border-radius:.4rem}</style></head>
<body><h1>Tuteur du cours</h1>
<p>Pose une question sur le cours. La réponse est toujours une phrase du cours, avec le chapitre d'où elle vient ; si le cours ne la contient pas, le tuteur ne répond pas.</p>
<form id="tuteur-form"><label for="tuteur-q">Ta question</label><input id="tuteur-q" autocomplete="off" placeholder="Qu'est-ce que le vent apparent ?"><button type="submit">Demander</button></form>
<div id="tuteur-rep" aria-live="polite"></div><p><a href="/cours.html">← Retour au cours</a></p>
<script src="/tuteur-cours.js" defer></script></body></html>
"""


def ecrire() -> dict:
    idx = construire_index()
    (SITE / "tuteur-index.json").write_text(json.dumps(idx, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    (SITE / "tuteur-cours.js").write_text(JS, encoding="utf-8")
    (SITE / "tuteur-cours.html").write_text(PAGE, encoding="utf-8")
    return idx


# ── 4. LE CONTRÔLE : citations vérifiées dans la page publiée ───────────────────────────────────────────
def citation_valide(rep: dict) -> str:
    """Vide si la phrase se retrouve mot pour mot dans la page citée, sous l'ancre citée ; sinon la cause."""
    page, _, ancre = rep["lien"].partition("#")
    f = SITE / page
    if not f.exists():
        return f"page absente : {page}"
    h = f.read_text(encoding="utf-8")
    if f'id="{ancre}"' not in h:
        return f"ancre absente : {ancre}"
    p = _Chapitre()
    p.feed(h)
    if not any(rep["phrase"] in b for b in p.blocs):
        return "phrase absente de la page"
    return ""


def controle() -> int:
    idx = construire_index()
    jeu = json.loads(QUESTIONS.read_text(encoding="utf-8"))
    ko = 0
    for q in jeu["questions"]:
        r = repondre(q["q"], idx)
        cause = ""
        if r["statut"] != "reponse":
            cause = "abstention à tort : " + r["raison"]
        elif r["lien"].split("#")[0] not in ([q["page"]] if isinstance(q["page"], str) else q["page"]):
            cause = f'mauvais chapitre : {r["lien"]} « {r["phrase"][:110]} »'
        elif q["contient"].lower() not in r["phrase"].lower():
            cause = f'mauvaise phrase : {r["phrase"][:90]}'
        else:
            cause = citation_valide(r)
        ko += bool(cause)
        print(("KO " if cause else "OK ") + q["q"] + (f"  → {cause}" if cause else f'  → {r["lien"]}'))
    for q in jeu["hors_cours"]:
        r = repondre(q, idx)
        mal = r["statut"] != "abstention"
        ko += mal
        print(("KO " if mal else "OK ") + q + ("  → a répondu : " + r["phrase"][:80] if mal else "  → abstention"))
    n = len(jeu["questions"]) + len(jeu["hors_cours"])
    print(f"{n - ko}/{n} · {len(idx['phrases'])} phrases · {len(idx['chapitres'])} chapitres")
    return 1 if ko else 0


def main() -> int:
    a = sys.argv[1:]
    if "--ecrire" in a:
        idx = ecrire()
        print(f"{len(idx['phrases'])} phrases, {len(idx['chapitres'])} chapitres → tuteur-index.json, tuteur-cours.js, tuteur-cours.html")
        return 0
    if "--controle" in a:
        return controle()
    if a:
        r = repondre(" ".join(a), construire_index())
        print(json.dumps(r, ensure_ascii=False, indent=1))
        return 0
    print(__doc__)
    return 0


if __name__ == "__main__":
    sys.exit(main())
