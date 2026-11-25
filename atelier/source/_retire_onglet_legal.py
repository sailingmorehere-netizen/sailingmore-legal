"""Applique aux deux pages légales déjà écrites la même passe que habillage_pages_legales."""
import re
from pathlib import Path

SITE = Path(__file__).resolve().parent.parent / "projets" / "sailingmore" / "site"


def sans_onglet_interne(html: str) -> str:
    def rempl(m):
        tag = m.group(0)
        h = re.search(r'href="([^"]*)"', tag)
        if "_blank" not in tag or (h and h.group(1).startswith(("http://", "https://", "//"))
                                   and "sailingmore.fr" not in h.group(1)):
            return tag
        return re.sub(r'\s+(?:target="_blank"|rel="noopener")', "", tag)
    return re.sub(r"<a\b[^>]*>", rempl, html)


for nom in ("mentions-legales.html", "confidentialite.html"):
    p = SITE / nom
    brut = p.read_text(encoding="utf-8")
    neuf = sans_onglet_interne(brut)
    p.write_text(neuf, encoding="utf-8")
    print(nom, len(brut) - len(neuf), "caractères retirés")
