#!/usr/bin/env python3
"""Vérifie cours.html : chapitres/sommaire, ancres, liens lexique et règles, six langues."""
import re
import sys
from pathlib import Path

S = Path(__file__).resolve().parent.parent / "projets" / "sailingmore" / "site"
c = (S / "cours.html").read_text(encoding="utf-8")
lex = (S / "lexique.html").read_text(encoding="utf-8")
reg = (S / "regles-de-course.html").read_text(encoding="utf-8")
ok = True
print("octets", len(c.encode()))
for l in ["fr", "en", "it", "es", "pt", "de"]:
    bloc = re.search(r'<div data-l="%s".*?\n</div>' % l, c, re.S).group(0)
    chap = re.findall(r'<section class="chap" id="ch(\d+)-%s"' % l, bloc)
    somm = re.findall(r'href="#ch(\d+)-%s"' % l, bloc)
    exo = bloc.count('class="exo"')
    rev = bloc.count("<b>") and len(re.findall(r'<p><b>\d\.</b>', bloc))
    print(l, "chapitres", len(chap), "sommaire", len(somm), "exos", exo, "revision", rev)
    if not (len(chap) == len(somm) == exo == 12 and rev == 4):
        ok = False
ids = set(re.findall(r'id="([^"]+)"', c))
for h in set(re.findall(r'href="#([^"]+)"', c)):
    if h not in ids:
        print("ancre cassée", h); ok = False
lex_ids = set(re.findall(r'id="([^"]+)"', lex))
for h in sorted(set(re.findall(r'href="lexique\.html#([^"]+)"', c))):
    if h not in lex_ids:
        print("lexique absent", h); ok = False
reg_ids = set(re.findall(r'id="([^"]+)"', reg))
for h in sorted(set(re.findall(r'href="regles-de-course\.html#([^"]+)"', c))):
    if h not in reg_ids:
        print("règle absente", h); ok = False
print("OK" if ok else "PROBLEMES")
sys.exit(0 if ok else 1)
