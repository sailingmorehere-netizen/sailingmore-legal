import ast
from pathlib import Path
S = Path(__file__).parent
for n in ["accueil_2026", "accueil_site", "site_blocks", "bateaux_page", "bateaux_controle", "regates_page", "comptes_page", "favoris_page"]:
    ast.parse((S / f"{n}.py").read_text(encoding="utf-8"))
    print(n, "ok")
