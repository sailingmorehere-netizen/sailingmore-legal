"""Tâche 68 : déplace le CSS des carrés de accueil_2026.py vers site_blocks.CASES_CSS (une fois)."""
from pathlib import Path

p = Path(__file__).resolve().parent / "accueil_2026.py"
s = p.read_text(encoding="utf-8")
if "site_blocks.CASES_CSS" in s:
    print("déjà fait")
    raise SystemExit(0)
a = s.index(".cases{max-width:62rem")
b = s.index(".chiffres-2026{max-width")
s = s[:a] + ".cases-2{margin-top:.9rem}\n" + s[b:]
for l in ["  .cases{grid-template-columns:1fr;gap:.6rem}\n",
          "  .case-grande{min-height:0;flex-direction:row;flex-wrap:wrap;align-items:center;column-gap:.9rem;row-gap:.1rem;padding:1rem 1.1rem}\n",
          "  .case-grande svg{width:2.2rem;height:2.2rem}\n", "  .case-grande b{flex:1 1 0}\n",
          "  .case-grande span.l{flex:1 0 100%}\n", "  .case-grande .v{display:none}\n", "  .case{padding:.8rem 1rem}\n"]:
    assert l in s, l
    s = s.replace(l, "", 1)
fin = '@media (max-width:420px){.nombres{grid-template-columns:1fr 1fr}}\n"""'
j = s.index(fin) + len(fin)
s = (s[:j] + "\n\nimport site_blocks  # noqa: E402  (le composant des carrés : une seule feuille, accueil et cours)\n\n"
     "CSS = site_blocks.CASES_CSS + CSS\n" + s[j:])
p.write_text(s, encoding="utf-8")
print("ok")
