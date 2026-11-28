#!/usr/bin/env python3
# © 2026 Sailing More — tous droits réservés. All rights reserved.
"""verifie_langue.py — compte le TEXTE manquant d'une langue, famille par famille (règle du 27/11/2026).

Usage :
  python3 scripts/verifie_langue.py <code> [--complet]   détail par famille ; --complet : sortie 0 si aucun texte manquant, 1 sinon
  python3 scripts/verifie_langue.py --table              une ligne par code (texte brut, nombres seuls) et écrit
                                                          cache/rhum/langues-manquantes.json
Colonnes de --table : code textes lexique_mots interface pages schemas jsonld hreflang
  textes = total de tous les textes manquants (mots + définitions du lexique compris).

Ce qui est compté (jamais un simple marqueur) :
  interface      clés des dictionnaires UI de chaque générateur (+ libellés fr/en/... de site_blocks) absentes dans <code>
  lexique_mots   termes de lexique.json sans mot <code> ; lexique_defs : sans définition <code> (+ phrase de cours si le champ existe)
  pages          pages multilingues du site sans la langue ; pages à copies monolingues « *-xx.html » sans copie <code>
  schemas        légendes / textes de schémas (dicts par langue des données de bateaux, simulateur) + equivalences.json
  jsonld         copies monolingues dont og:locale / JSON-LD inLanguage ne portent pas leur propre langue
  hreflang       pages à alternates sans hreflang <code> + sitemap sans hreflang <code>
Une page servie dans une seule langue (ports, bateaux, stories…) n'est comparée qu'à elle-même : jamais un trou.
"""
import ast
import json
import re
import sys
from pathlib import Path

ICI = Path(__file__).resolve().parent
RACINE_DEPOT = ICI.parent
SITE = RACINE_DEPOT / "projets" / "sailingmore" / "site"
SERVIES = ["fr", "en", "de", "it", "es", "pt"]
CIBLES = ["nl", "el", "hr", "sv", "da", "no", "pl", "tr"]
TOUS = SERVIES + CIBLES
OG = {"fr": "fr_FR", "en": "en_GB", "de": "de_DE", "it": "it_IT", "es": "es_ES", "pt": "pt_PT", "pl": "pl_PL",
      "nl": "nl_NL", "el": "el_GR", "hr": "hr_HR", "sv": "sv_SE", "da": "da_DK", "no": "nb_NO", "tr": "tr_TR"}
GENERATEURS_UI = ["bateaux_page", "comparatif_stages_page", "equivalences_page", "lexique_page", "regles_page",
                  "securite_page", "simulateur_donnees", "stages_page"]
FICHIERS_SCHEMAS = ["bateaux_dessins", "bateaux_dessins2", "bateaux_rendu", "bateaux_mots", "simulateur_donnees"]
COPIE = re.compile(r"-(%s)\.html$" % "|".join(TOUS))


# ---------- dictionnaires par langue (AST, sans exécuter les générateurs) ----------
def _cles(n):
    if isinstance(n, ast.Dict) and all(isinstance(k, ast.Constant) and isinstance(k.value, str) for k in n.keys if k):
        return {k.value: v for k, v in zip(n.keys, n.values) if k}
    return None


def _manque_dict(noeud, code, interface):
    """Compte les textes manquants dans les dicts par langue d'un arbre AST. Renvoie (manquants, total_unites)."""
    man = 0
    pile = [noeud]
    while pile:
        n = pile.pop()
        d = _cles(n) if isinstance(n, ast.Dict) else None
        if d and "fr" in d and "en" in d and set(d) <= set(TOUS) | {"bzh"}:
            # référence = clés de « en » : une clé propre au français (ex. « desole ») n'est pas due aux autres langues
            ref = _cles(d["en"]) if isinstance(d["en"], ast.Dict) else None
            if ref is not None:  # dict d'interface : {lang: {cle: texte}}
                cur = _cles(d[code]) if code in d and isinstance(d[code], ast.Dict) else {}
                man += len([c for c in ref if c not in (cur or {})])
            else:  # feuille : {lang: texte}
                if code not in d:
                    man += 1
            continue
        pile.extend(ast.iter_child_nodes(n))
    return man


def _arbre(nom):
    p = ICI / (nom + ".py")
    return ast.parse(p.read_text(encoding="utf-8")) if p.exists() else None


def interface(code):
    total, detail = 0, {}
    for nom in GENERATEURS_UI:
        arbre = _arbre(nom)
        if arbre is None:
            continue
        n = 0
        for st in arbre.body:
            if isinstance(st, ast.Assign) and any(isinstance(t, ast.Name) and t.id in ("UI", "ui") for t in st.targets):
                n += _manque_dict(st.value, code, True)
        if n:
            detail[nom] = n
        total += n
    sb = _arbre("site_blocks")
    if sb is not None:
        n = 0
        for st in sb.body:
            if isinstance(st, ast.Assign):
                n += _manque_dict(st.value, code, True)
            elif isinstance(st, ast.FunctionDef):
                n += sum(_manque_dict(x, code, True) for x in ast.walk(st) if isinstance(x, ast.Assign))
        if n:
            detail["site_blocks"] = n
        total += n
    return total, detail


def schemas(code):
    total, detail = 0, {}
    for nom in FICHIERS_SCHEMAS:
        arbre = _arbre(nom)
        if arbre is None:
            continue
        n = 0
        for st in arbre.body:
            if isinstance(st, ast.Assign) and not any(isinstance(t, ast.Name) and t.id in ("UI", "ui") for t in st.targets):
                n += _manque_dict(st.value, code, False)
        if n:
            detail[nom] = n
        total += n
    # equivalences.json : chaque texte porté par une correspondance, par langue
    eq = RACINE_DEPOT / "projets" / "sailingmore" / "equivalences.json"
    n = 0
    if eq.exists():
        for c in json.loads(eq.read_text(encoding="utf-8")).get("correspondances", []):
            for champ, v in c.items():
                if isinstance(v, dict) and "fr" in v and not v.get(code):
                    n += 1
    if n:
        detail["equivalences.json"] = n
    return total + n, detail


def lexique(code):
    d = json.loads((RACINE_DEPOT / "projets" / "sailingmore" / "lexique.json").read_text(encoding="utf-8"))
    mots = defs = phr = 0
    for th in d["themes"]:
        for t in th["termes"]:
            if not (t.get("mot") or {}).get(code):
                mots += 1
            if not (t.get("def") or {}).get(code):
                defs += 1
            for champ in ("phrase_cours", "cours"):
                if isinstance(t.get(champ), dict) and not t[champ].get(code):
                    phr += 1
    return mots, defs, phr


# ---------- pages ----------
def pages_et_balises(code):
    """pages, jsonld, hreflang, détail. Une page monolingue n'est comparée qu'à elle-même."""
    bases, copies = {}, {}
    for p in SITE.glob("*.html"):
        m = COPIE.search(p.name)
        if m:
            copies.setdefault(p.name[: m.start()] + ".html", {})[m.group(1)] = p
        else:
            bases[p.name] = p
    pages = jsonld = hreflang = 0
    detail = {}
    for nom, p in sorted(bases.items()):
        t = p.read_text(encoding="utf-8", errors="replace")
        fam = re.split(r"[-.]", nom)[0]
        # multilingue = au moins deux langues au sélecteur ; « auto + fr » seul = page servie en une langue
        multi = 'data-lang="fr"' in t and 'data-lang="en"' in t
        if nom in copies:  # famille à copies monolingues
            if code != "fr" and code not in copies[nom]:
                pages += 1
                detail[fam] = detail.get(fam, 0) + 1
            # alternates : comparés seulement si la page en porte (cours.html n'en porte aucun : signalé au rapport)
            if code != "fr" and 'rel="alternate" hreflang=' in t and 'hreflang="%s"' % code not in t:
                hreflang += 1
        elif multi and code != "fr" and 'data-lang="%s"' % code not in t:
            pages += 1
            detail[fam] = detail.get(fam, 0) + 1
    for nom, cp in copies.items():
        p = cp.get(code)
        if p is None:
            continue
        t = p.read_text(encoding="utf-8", errors="replace")
        if not re.search(r'og:locale"[^>]*content="%s' % OG[code], t) or '"inLanguage"' in t and not re.search(r'"inLanguage"\s*:\s*"%s' % code, t):
            jsonld += 1
        if 'hreflang="%s"' % code not in t and code != "fr":
            hreflang += 1
    sm = SITE / "sitemap.xml"
    if sm.exists():
        t = sm.read_text(encoding="utf-8", errors="replace")
        if code != "fr" and not re.search(r'hreflang="%s"' % code, t) and re.search(r'hreflang="(%s)"' % "|".join(SERVIES), t):
            hreflang += 1
        elif code != "fr" and code not in OG:
            hreflang += 1
    return pages, jsonld, hreflang, detail


def mesure(code):
    ui, d_ui = interface(code)
    sc, d_sc = schemas(code)
    mots, defs, phr = lexique(code)
    pg, ld, hl, d_pg = pages_et_balises(code)
    textes = ui + sc + mots + defs + phr + pg + ld + hl
    return {"code": code, "textes": textes, "lexique_mots": mots, "interface": ui, "pages": pg, "schemas": sc,
            "jsonld": ld, "hreflang": hl, "lexique_defs": defs, "lexique_phrases": phr,
            "detail": {"interface": d_ui, "schemas": d_sc, "pages": d_pg}}


COLS = ["textes", "lexique_mots", "interface", "pages", "schemas", "jsonld", "hreflang"]


def main() -> int:
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help"):
        print(__doc__)
        return 2
    if "--table" in args:
        res = [mesure(c) for c in TOUS]
        for r in res:
            print(r["code"], *[r[c] for c in COLS])
        out = RACINE_DEPOT / "cache" / "rhum" / "langues-manquantes.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps({r["code"]: {k: v for k, v in r.items() if k != "code"} for r in res},
                                  ensure_ascii=False, indent=1), encoding="utf-8")
        return 0
    code = args[0]
    if code not in TOUS:
        print(f"code inconnu : {code}")
        return 2
    r = mesure(code)
    try:
        sys.path.insert(0, str(ICI))
        import site_blocks
        print(f"{code} dans LANGUES_PRETES : {code in site_blocks.LANGUES_PRETES}")
    except Exception as e:
        print(f"(site_blocks non importable : {e})")
    for k in COLS[1:] + ["lexique_defs", "lexique_phrases"]:
        print(f"{k:16} {r[k]}")
    for fam, det in r["detail"].items():
        for cle, n in sorted(det.items()):
            print(f"  {fam}: {cle} = {n}")
    print(f"{r['textes']} texte(s) manquant(s) en {code}")
    return 0 if r["textes"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
