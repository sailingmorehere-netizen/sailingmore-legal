#!/usr/bin/env python3
"""verifie_langue.py <code> — liste les trous d'une langue, page par page (règle du 27/11/2026).

Contrôles mécaniques, sans réseau :
  1. LANGUES_PRETES contient-elle le code ?  (information, pas un trou)
  2. Pour chaque page HTML du site : le code apparaît-il comme hreflang, comme og:locale,
     et comme bouton/bloc `data-lang="<code>"` ? Référence = la même page pour une langue servie (pt).
  3. sitemap.xml : nombre d'URL portant hreflang=<code>.
Sortie : trous par page, total, code de sortie 0 seulement si zéro trou.
Usage : python3 scripts/verifie_langue.py pl [--ref pt]
"""
import re
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent / "projets" / "sailingmore" / "site"
OG = {"fr": "fr_FR", "en": "en_GB", "de": "de_DE", "it": "it_IT", "es": "es_ES", "pt": "pt_PT", "pl": "pl_PL"}


def marques(texte: str, code: str) -> dict:
    return {
        "hreflang": len(re.findall(r'hreflang="%s"' % code, texte)),
        "og:locale": len(re.findall(r'og:locale[^>]*content="%s' % OG.get(code, code), texte)),
        "data-lang": len(re.findall(r'data-lang="%s"' % code, texte)),
    }


def main() -> int:
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        return 2
    code = args[0]
    ref = args[args.index("--ref") + 1] if "--ref" in args else "pt"
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    try:
        import site_blocks
        print(f"{code} dans LANGUES_PRETES : {code in site_blocks.LANGUES_PRETES}")
    except Exception as e:  # le contrôle de pages reste utile sans l'import
        print(f"(site_blocks non importable : {e})")
    trous = 0
    pages = sorted(RACINE.rglob("*.html"))
    for p in pages:
        t = p.read_text(encoding="utf-8", errors="replace")
        mr, mc = marques(t, ref), marques(t, code)
        for cle in mr:
            if mr[cle] and mc[cle] < mr[cle]:
                trous += 1
                print(f"TROU {p.relative_to(RACINE)} : {cle} {code}={mc[cle]} < {ref}={mr[cle]}")
    sm = RACINE / "sitemap.xml"
    if sm.exists():
        t = sm.read_text(encoding="utf-8", errors="replace")
        a, b = len(re.findall(r'hreflang="%s"' % ref, t)), len(re.findall(r'hreflang="%s"' % code, t))
        if b < a:
            trous += 1
            print(f"TROU sitemap.xml : hreflang {code}={b} < {ref}={a}")
    print(f"{len(pages)} pages lues, {trous} trou(s)")
    return 0 if trous == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
