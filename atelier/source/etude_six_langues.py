#!/usr/bin/env python3
# © 2026 Sailing More — tous droits réservés. All rights reserved.
"""Étude six langues : mesure data-t, tables T, head, sans-JS, en ligne. Lecture seule.
Usage : python3 scripts/etude_six_langues.py [--ligne]   -> écrit sortie-test/etude-six-langues.json et imprime un tableau."""
import json, re, sys, glob, os, datetime, urllib.request, html as H

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(RACINE, "projets", "sailingmore", "site")
LANGS = ["fr", "de", "en", "it", "es", "pt"]
# mots français fréquents : sert à repérer du texte resté en français dans une table non-fr
FR = set("le la les des une un du de et pour avec sur dans votre vos nous vous est sont ce cette qui que au aux par plus ou où".split())

def lire(p):
    with open(p, encoding="utf-8") as f:
        return f.read()

def table_T(src):
    """Retourne les dicts de traduction trouvés : toute affectation `X = {"fr": {...}` (T, TXT…)."""
    out = {}
    for m in re.finditer(r'(?:const|let|var)\s+(\w+)\s*=\s*(?=\{\s*"fr"\s*:\s*\{)', src):
        try:
            obj, _ = json.JSONDecoder().raw_decode(src[m.end():])
            out[m.group(1)] = obj
        except Exception:
            pass
    return out

def blobs(src):
    """Tous les objets JSON/JS embarqués : <script type=application/json>, et `X = {...}` / `X = [...]` en JS."""
    out = []
    for m in re.finditer(r'<script[^>]*type="application/json"[^>]*>(.*?)</script>', src, re.S):
        try:
            out.append(("json#" + (re.search(r'id="([^"]+)"', m.group(0)) or [0, "?"])[1], json.loads(m.group(1))))
        except Exception:
            out.append(("json-illisible", None))
    for m in re.finditer(r'(?:const|let|var)\s+(\w+)\s*=\s*(?=[\[{])', src):
        try:
            obj, _ = json.JSONDecoder().raw_decode(src[m.end():])
            out.append((m.group(1), obj))
        except Exception:
            pass
    return out

def cherche(node, chemin, tables, entrees):
    """tables : dicts {lang:{cle:val}} ; entrees : dicts {lang:'texte'} (une citation, un mot de lexique…)."""
    if isinstance(node, dict):
        ks = set(node)
        if {"fr", "en"} <= ks and ks <= set(LANGS) | {"auto"}:
            if all(isinstance(v, dict) for v in node.values()):
                tables.append((chemin, node)); return
            if all(isinstance(v, str) for v in node.values()):
                entrees.append((chemin, node)); return
        for k, v in node.items():
            cherche(v, chemin + "/" + str(k), tables, entrees)
    elif isinstance(node, list):
        for i, v in enumerate(node):
            cherche(v, chemin + "[]", tables, entrees)

def analyser_table(t):
    fr = t.get("fr", {})
    langs = {}
    for l in LANGS:
        d = t.get(l, {})
        manq = sorted(k for k in fr if k not in d or not str(d[k]).strip())
        idem = sorted(k for k in fr if l != "fr" and k in d and d[k] == fr[k]
                      and len(re.findall(r"[a-zA-ZÀ-ÿ]{3,}", str(d[k]))) >= 3)
        frmots = sorted(k for k in fr if l != "fr" and k in d and d[k] != fr[k]
                        and len(set(re.findall(r"[a-zà-ÿ']+", str(d[k]).lower())) & FR) >= 4)
        langs[l] = {"cles": len(d), "manquantes": manq, "identiques_fr": idem, "mots_fr_suspects": frmots}
    return {"cles_fr": len(fr), "langues": langs}

def tete(src):
    g = lambda r: (re.search(r, src, re.S) or [None, None])[1]
    return {
        "lang": g(r'<html[^>]*\blang="([^"]*)"'),
        "title": g(r'<title>(.*?)</title>'),
        "description": g(r'<meta\s+name="description"\s+content="([^"]*)"'),
        "og_title": g(r'<meta\s+property="og:title"\s+content="([^"]*)"'),
        "og_description": g(r'<meta\s+property="og:description"\s+content="([^"]*)"'),
        "canonical": g(r'<link\s+rel="canonical"\s+href="([^"]*)"'),
        "hreflang": len(re.findall(r'hreflang=', src)),
        "script_titre_langue": bool(re.search(r'document\.title\s*=', src)),
    }

def sans_js(src):
    s = re.sub(r'<(script|style)\b.*?</\1>', ' ', src, flags=re.S)
    s = re.sub(r'<[^>]+>', ' ', s)
    return re.sub(r'\s+', ' ', H.unescape(s)).strip()

def etat_page(nom):
    src = lire(os.path.join(SITE, nom))
    r = {"page": nom, "octets": len(src.encode()), "tete": tete(src)}
    cles_html = re.findall(r'data-t="([^"]+)"', src)
    r["data_t_elements"] = len(cles_html)
    r["data_t_cles_uniques"] = len(set(cles_html))
    tables, entrees = [], []
    for nomb, b in blobs(src):
        if b is not None:
            cherche(b, nomb, tables, entrees)
    r["tables"] = {}
    toutes_cles_fr = set()
    for chemin, t in tables:
        a = analyser_table(t)
        r["tables"][chemin] = a
        toutes_cles_fr |= set(t.get("fr", {}))
    r["data_t_sans_table"] = sorted(set(cles_html) - toutes_cles_fr) if tables else sorted(set(cles_html))
    # entrées plurilingues (citations, lexique…) : langues absentes ou texte identique au français
    ag = {}
    for chemin, e in entrees:
        a = ag.setdefault(chemin, {"entrees": 0, "langue_absente": {l: 0 for l in LANGS}, "identique_fr": {l: 0 for l in LANGS if l != "fr"}})
        a["entrees"] += 1
        for l in LANGS:
            if not str(e.get(l, "")).strip(): a["langue_absente"][l] += 1
            elif l != "fr" and e.get(l) == e.get("fr") and len(e["fr"]) > 25: a["identique_fr"][l] += 1
    r["entrees_plurilingues"] = ag
    r["data_l"] = {l: len(re.findall(r'data-l="%s"' % l, src)) for l in LANGS}   # blocs HTML par langue (cours.html)
    r["selecteur_langue"] = bool(re.search(r'id="langues"|data-lang=', src))
    r["detecte_langue"] = bool(re.search(r'navigator\.language|sm-langue', src))
    txt = sans_js(src)
    r["sans_js"] = {"mots_visibles": len(txt.split()), "mots_fr_courants": sum(1 for w in re.findall(r"[a-zà-ÿ']+", txt.lower()) if w in FR)}
    return r

def ligne(nom):
    u = "https://sailingmore.fr/" + ("" if nom == "index.html" else nom)
    try:
        req = urllib.request.Request(u, headers={"User-Agent": "mesure-site"})
        with urllib.request.urlopen(req, timeout=20) as f:
            b = f.read()
            return {"url": u, "statut": f.status, "octets": len(b), "hreflang": len(re.findall(rb'hreflang=', b)),
                    "identique_copie": b == open(os.path.join(SITE, nom), "rb").read()}
    except Exception as e:
        return {"url": u, "erreur": str(e)[:100]}

if __name__ == "__main__":
    pages = sorted(os.path.basename(p) for p in glob.glob(SITE + "/*.html"))
    res = {"date": datetime.datetime.now().isoformat(timespec="minutes"), "pages": [etat_page(p) for p in pages]}
    if "--ligne" in sys.argv:
        for p in res["pages"]:
            p["en_ligne"] = ligne(p["page"])
    os.makedirs(os.path.join(RACINE, "sortie-test"), exist_ok=True)
    with open(os.path.join(RACINE, "sortie-test", "etude-six-langues.json"), "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=1)
    print("page | octets | data-t | tables(clés fr) | manquantes/identiques/suspects par langue | hreflang | JS titre | en ligne")
    for p in res["pages"]:
        tabs = "; ".join(f"{n}:{t['cles_fr']}" for n, t in p["tables"].items()) or "-"
        det = ""
        for n, t in p["tables"].items():
            det += f"[{n}] " + " ".join(f"{l}={len(v['cles'] and v['manquantes'])}/{len(v['identiques_fr'])}/{len(v['mots_fr_suspects'])}" for l, v in t["langues"].items() if l != "fr")
        if p["data_t_sans_table"]: det += f" data-t SANS TABLE ({len(p['data_t_sans_table'])}): {p['data_t_sans_table'][:12]}"
        for n, a in p["entrees_plurilingues"].items():
            if "voix" in n or a["entrees"] < 2: continue
            det += f" <{n} entrées={a['entrees']} absentes={a['langue_absente']} idem_fr={a['identique_fr']}>"
        e = p.get("en_ligne", {})
        det += f" | data-l={list(p['data_l'].values())} sélecteur={p['selecteur_langue']} détecte={p['detecte_langue']} mots_sans_js={p['sans_js']['mots_visibles']} (courants fr={p['sans_js']['mots_fr_courants']})"
        print(p["page"], p["octets"], p["data_t_elements"], tabs, det, p["tete"]["hreflang"], p["tete"]["script_titre_langue"],
              (e.get("statut"), e.get("octets"), e.get("identique_copie"), e.get("erreur")) if e else "")
