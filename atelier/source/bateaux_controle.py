#!/usr/bin/env python3
"""Contrôle de la page des bateaux, en lecture seule : poids, ancres, correspondance, XML, polices, équilibre du JS.

    python3 scripts/bateaux_controle.py
"""
from __future__ import annotations

import json
import os
import re
import sys
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path

RACINE = Path(os.environ.get("SITE_ROOT") or Path(__file__).resolve().parent.parent)
SITE = RACINE / "projets" / "sailingmore" / "site"
SRC = RACINE / "projets" / "sailingmore" / "images-src" / "bateaux"


class Balises(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids, self.liens, self.mots = set(), [], []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if "id" in a:
            self.ids.add(a["id"])
        if tag == "a" and a.get("href", "").startswith("lexique.html#"):
            self.liens.append((a["href"].split("#")[1], a.get("target"), a.get("rel")))
        if a.get("class", "").split()[:1] == ["lb"] and "data-mot" in a:
            self.mots.append((a["id"], a["data-mot"]))


def equilibre(js: str) -> list[str]:
    """Parenthèses, accolades, crochets et guillemets équilibrés, hors chaînes et commentaires."""
    pb, pile, i = [], [], 0
    paires = {")": "(", "]": "[", "}": "{"}
    while i < len(js):
        c = js[i]
        if js.startswith("/*", i):
            i = js.index("*/", i) + 2
            continue
        if js.startswith("//", i) and js[i - 1] != ":":
            i = js.index("\n", i)
            continue
        if c in "'\"":
            j = i + 1
            while js[j] != c:
                j += 2 if js[j] == "\\" else 1
                if j >= len(js) or js[j] == "\n" and c != "`":
                    if j >= len(js) or js[j] == "\n":
                        break
            i = j + 1
            continue
        if c == "/" and re.match(r"/[^/*\s][^\n]*?/[gimuy]*[,;)\.]", js[i:i + 120]) and js[i - 1] in "(,=:[!&|?{};\n ":
            m = re.match(r"/(?:\\.|[^/\\\n])+/[gimuy]*", js[i:])
            if m:
                i += m.end()
                continue
        if c in "([{":
            pile.append(c)
        elif c in ")]}":
            if not pile or pile.pop() != paires[c]:
                pb.append(f"fermeture {c} inattendue à {i}")
        i += 1
    if pile:
        pb.append(f"{len(pile)} ouvrante(s) non fermée(s) : {''.join(pile[-5:])}")
    return pb


def main() -> int:
    import ast
    pb: list[str] = []
    for nom in ("accueil_site.py", "site_blocks.py", "bateaux_page.py", "bateaux_dessins.py", "bateaux_dessins2.py",
                "bateaux_mots.py", "bateaux_controle.py"):
        try:
            ast.parse((Path(__file__).resolve().parent / nom).read_text(encoding="utf-8"), nom)
        except SyntaxError as e:
            pb.append(f"{nom} : {e}")
    print("syntaxe Python : " + ("OK" if not pb else str(pb)))
    page = (SITE / "bateaux.html").read_text(encoding="utf-8")
    taille = len(page.encode("utf-8"))
    print(f"bateaux.html : {taille / 1024:.1f} Ko ({'OK' if taille < 150 * 1024 else 'TROP LOURD'})")
    if taille >= 150 * 1024:
        pb.append("page ≥ 150 Ko")
    lex = Balises()
    lex.feed((SITE / "lexique.html").read_text(encoding="utf-8"))
    bat = Balises()
    bat.feed(page)
    # 1. chaque étiquette mène à une ancre du lexique, en nouvel onglet
    manque = sorted({a for a, _, _ in bat.liens if a not in lex.ids})
    print(f"étiquettes : {len(bat.liens)} liens, {len({a for a, _, _ in bat.liens})} ancres distinctes, ancres absentes du lexique : {manque or 'aucune'}")
    pb += [f"ancre absente du lexique : {a}" for a in manque]
    if any(t != "_blank" or r != "noopener" for _, t, r in bat.liens):
        pb.append("un lien sans target=_blank rel=noopener")
    print(f"lexique : {len(lex.ids)} ancres")
    # 2. bateaux.json : aucune ancre absente de la page
    js = json.loads((SITE / "bateaux.json").read_text(encoding="utf-8"))
    anc = [x["ancre"] for v in js["mots"].values() for x in v]
    # une pièce numérotée n'a pas d'étiquette dans le HTML statique : son numéro (id = l'ancre) est créé par le script
    donnees_page = json.loads(re.search(r'id="donnees-bateaux">(.*?)</script>', page, flags=re.S).group(1).replace("<\\/", "</"))
    numerotees = {p[0] for b in donnees_page["bateaux"].values() for p in b["p"] if p[4]}
    statiques = {i for i, _ in bat.mots}
    sans_etiquette = [a for a in anc if a not in statiques]
    absentes = [a for a in anc if a not in statiques and a not in numerotees]
    pb += [f"bateaux.json cite une ancre absente de la page : {a}" for a in absentes]
    print(f"ancres de bateaux.json absentes de la page : {absentes or 'aucune'}")
    print(f"bateaux.json : {len(js['mots'])} mots, {len(anc)} ancres ; sans étiquette statique (numérotées) : {len(sans_etiquette)}")
    for mot in ("bome", "quille", "spinnaker", "foil", "wishbone", "pataras"):
        print(f"  {mot:10} → {[x['bateau'] for x in js['mots'].get(mot, [])]}")
    for mot, v in js["mots"].items():
        if mot not in lex.ids:
            pb.append(f"bateaux.json : {mot} sans ancre au lexique")
        for x in v:
            if not x["ancre"].startswith(x["bateau"] + "-"):
                pb.append(f"ancre mal préfixée : {x['ancre']}")
    # 3. chaque étiquette porte id + data-mot, le même mot que l'ancre
    for ident, mot in bat.mots:
        if not ident.endswith("-" + mot):
            pb.append(f"id/mot incohérents : {ident} / {mot}")
    # 4. XML bien formé : sources d'images et sitemap
    for f in sorted(SRC.glob("*.svg")):
        try:
            ET.parse(f)
        except ET.ParseError as e:
            pb.append(f"{f.name} : {e}")
    sm = (SITE / "sitemap.xml").read_text(encoding="utf-8")
    try:
        ET.fromstring(sm)
    except ET.ParseError as e:
        pb.append(f"sitemap : {e}")
    print(f"sitemap : {sm.count('<image:loc>')} images, bateaux.html {'présent' if 'bateaux.html' in sm else 'ABSENT'}")
    # 5. polices : aucune taille CSS ou attribut sous 12 px dans la page
    petites = [int(x) for x in re.findall(r"font-size:(\d+)px", page) if int(x) < 12]
    print(f"polices < 12 px déclarées : {petites or 'aucune'}")
    if petites:
        pb.append("police < 12 px")
    # 6. JavaScript : équilibre (pas de moteur JS ici)
    for k, bloc in enumerate(re.findall(r"<script>(.*?)</script>", page, flags=re.S)):
        e = equilibre(bloc)
        print(f"script {k} : {len(bloc)} car., équilibre {'OK' if not e else e}")
        pb += e
    donnees = re.search(r'id="donnees-bateaux">(.*?)</script>', page, flags=re.S).group(1)
    json.loads(donnees.replace("<\\/", "</"))
    print("données JSON de la page : valides")
    for p in pb:
        print("ÉCHEC ·", p)
    print("OK" if not pb else f"{len(pb)} problème(s)")
    return 1 if pb else 0


if __name__ == "__main__":
    sys.exit(main())
