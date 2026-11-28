# © 2026 Sailing More — tous droits réservés. Source unique du copyright (pied de page + en-têtes de code).
"""Copyright sur tout le site (tâche n°1, demande du 28/11/2026).

- `poser_pied(site)` : pose, sur chaque page HTML, un pied « © ANNEE Sailing More » visible, et un
  commentaire d'en-tête © juste après le doctype. Idempotent : le bloc entre `<!--cr-debut-->` et
  `<!--cr-fin-->` est remplacé, jamais empilé. Les pages qui portent déjà un © dans leur propre
  pied (accueil, régates…) ne reçoivent pas de second pied visible, seulement l'en-tête.
- `poser_entetes_code(racine)` : une ligne © en tête des scripts Python durables (hors `_*.py`) et
  des JS/CSS du site.

Texte neutre quant à la langue : aucun mot de français sous une étiquette étrangère.
Lancement : python3 scripts/copyright_site.py
"""
from __future__ import annotations

import datetime
import re
import sys
from pathlib import Path

ANNEE = datetime.date.today().year
NOM = "Sailing More"
LIGNE = f"© {ANNEE} {NOM} — sailingmore.fr"
ENTETE_CODE = f"© {ANNEE} {NOM} — tous droits réservés. All rights reserved."
MARQUE_HTML = re.compile(r"<!--cr-debut-->.*?<!--cr-fin-->\n?", re.S)
COMMENTAIRE_HTML = re.compile(r"<!--\s*©[^>]*?-->\n?")


def _pied() -> str:
    return ('<!--cr-debut--><p class="copyright-site" style="position:relative;z-index:2;margin:0;'
            'padding:1.2rem 1rem 1.6rem;text-align:center;font-size:.78rem;letter-spacing:.04em;'
            f'color:#9fb3c4">{LIGNE}</p><!--cr-fin-->\n')


def _page(html: str) -> str:
    # Le pied visible : sauf si la page porte déjà son propre © (hors de notre bloc).
    sans = MARQUE_HTML.sub("", html)
    html = sans
    deja = "©" in re.sub(r"<!--.*?-->", "", html, flags=re.S)
    if not deja:
        pied = _pied()
        if "<!--mer-debut-->" in html:
            html = html.replace("<!--mer-debut-->", pied + "<!--mer-debut-->", 1)
        elif "</body>" in html:
            html = html.replace("</body>", pied + "</body>", 1)
        else:
            html += "\n" + pied
    # L'en-tête : commentaire © après le doctype (ou en tête si absent).
    html = COMMENTAIRE_HTML.sub("", html, count=1) if html.lstrip().startswith(("<!--", "<!doctype", "<!DOCTYPE")) else html
    com = f"<!-- {ENTETE_CODE} -->\n"
    m = re.match(r"\s*<!doctype[^>]*>\s*", html, re.I)
    if m:
        html = html[:m.end()] + com + html[m.end():]
    else:
        html = com + html
    return html


def poser_pied(site: Path) -> int:
    n = 0
    for p in sorted(site.rglob("*.html")):
        if "api" in p.relative_to(site).parts[:1]:
            continue
        ancien = p.read_text()
        nouveau = _page(ancien)
        if nouveau != ancien:
            p.write_text(nouveau)
        n += 1
    return n


def _entete_fichier(p: Path, ouvre: str, ferme: str = "") -> bool:
    texte = p.read_text()
    if "©" in "\n".join(texte.splitlines()[:4]):
        return False
    ligne = f"{ouvre} {ENTETE_CODE}{(' ' + ferme) if ferme else ''}\n"
    lignes = texte.splitlines(keepends=True)
    i = 0
    while i < len(lignes) and (lignes[i].startswith("#!") or re.match(r"#.*coding[:=]", lignes[i])):
        i += 1
    p.write_text("".join(lignes[:i]) + ligne + "".join(lignes[i:]))
    return True


def poser_entetes_code(racine: Path) -> int:
    n = 0
    for p in sorted((racine / "scripts").glob("*.py")):
        if not p.name.startswith("_"):
            n += _entete_fichier(p, "#")
    site = racine / "projets/sailingmore/site"
    for p in sorted(site.glob("*.js")):
        if p.name != "auto-trad.js":      # fichier généré, réécrit à chaque construction
            n += _entete_fichier(p, "/*", "*/")
    for p in sorted(site.glob("*.css")):
        n += _entete_fichier(p, "/*", "*/")
    return n


if __name__ == "__main__":
    racine = Path(__file__).resolve().parent.parent
    site = racine / "projets/sailingmore/site"
    print(f"pied © posé sur {poser_pied(site)} page(s)")
    print(f"en-tête © posé sur {poser_entetes_code(racine)} fichier(s) de code")
