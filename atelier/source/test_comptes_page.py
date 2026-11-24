"""Garde-fous des écrans de compte : python3 scripts/test_comptes_page.py (code de sortie 1 si un interdit apparaît)."""
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import comptes_page  # noqa: E402
import site_blocks  # noqa: E402

echecs = []


def ok(cond, msg):
    if not cond:
        echecs.append(msg)


tmp = Path(tempfile.mkdtemp())
comptes_page.ecrire_page(tmp)
comptes = (tmp / "js/comptes.js").read_text(encoding="utf-8")
ui = (tmp / "js/comptes-ui.js").read_text(encoding="utf-8")

# 1. les trois pages existent, noindex, sans aucun champ ni formulaire dans le HTML
for nom in comptes_page.PAGES:
    h = (tmp / nom).read_text(encoding="utf-8")
    ok('name="robots" content="noindex' in h, f"{nom}: pas de noindex")
    ok("<input" not in h and "<form" not in h, f"{nom}: un champ ou un formulaire dans le HTML")
    ok("1er décembre" in h, f"{nom}: phrase honnête absente")

# 2. aucun enregistrement de mot de passe, nulle part
for nom, src in (("comptes.js", comptes), ("comptes-ui.js", ui)):
    for interdit in ("localStorage.setItem", "sessionStorage", "document.cookie", "indexedDB", "setItem("):
        ok(interdit not in src, f"{nom}: « {interdit} » présent")
ok("localStorage.getItem" in ui and ui.count("localStorage") == 1, "comptes-ui.js: localStorage ne sert qu'à lire sm-langue")

# 3. l'interrupteur : le mode local refuse avant tout fetch ; un seul fetch dans la couche d'appel
ok(comptes.count("fetch(") == 1, "comptes.js: plus d'un fetch")
ok(comptes.index('cfg().comptes === "api"') < comptes.index("fetch("), "comptes.js: l'interrupteur doit précéder le fetch")
ok("fetch(" not in ui and "XMLHttpRequest" not in ui, "comptes-ui.js: appel réseau direct")
ok(re.search(r'function appel\(.*?\n\s*if\(!ouvert\(\)\) return echec', comptes, re.S), "appel(): pas de garde 'local'")
# les formulaires ne se construisent que si le mode est api
ok(ui.index("if(!C || !C.ouvert())") < ui.index("ecranInscription(racine)"), "comptes-ui.js: formulaire avant l'interrupteur")

# 4. les quatre adresses du contrat
for adr in ('"/comptes/inscription"', '"/comptes/connexion"', '"/comptes/mot-de-passe"', 'appel("DELETE", "/comptes")'):
    ok(adr in comptes, f"comptes.js: {adr} absent")

# 5. aucun lien dans le menu, aucune page dans le sitemap des sources
liens = {f for f, _, _ in site_blocks.MENU_PAGES}
ok(not liens & set(comptes_page.PAGES), "une page de compte est dans MENU_PAGES")
ok(all(site_blocks.balises_comptes(p) for p in comptes_page.PAGES) and not site_blocks.balises_comptes("index.html"), "balises_comptes")

# 6. sept langues : six blocs complets, mêmes clés
zone = ui[ui.index("var T = {"):ui.index("function lg()")]
morceaux = re.split(r"\n    (fr|en|it|es|pt|de): \{", zone)
cles = {morceaux[i]: set(re.findall(r"\b([a-zA-Z_]+): \"", morceaux[i + 1])) for i in range(1, len(morceaux), 2)}
ok(len(cles) == 6, f"langues trouvées: {sorted(cles)}")
if cles:
    ref = cles.get("fr", set())
    for l, c in cles.items():
        ok(c == ref, f"{l}: clés différentes de fr ({sorted(ref ^ c)})")
    for k in ("e_prise", "e_court", "e_expire", "ferme"):
        ok(k in ref, f"clé {k} absente")

# 7. syntaxe JS si node est là (sinon dit non vérifié)
node = shutil.which("node")
if node:
    for nom in ("comptes.js", "comptes-ui.js"):
        r = subprocess.run([node, "--check", str(tmp / "js" / nom)], capture_output=True, text=True)
        ok(r.returncode == 0, f"{nom}: syntaxe — {r.stderr[:200]}")
else:
    print("node absent : syntaxe JS NON vérifiée")

shutil.rmtree(tmp, ignore_errors=True)
print("ÉCHECS :" if echecs else "OK : tous les garde-fous passent")
for e in echecs:
    print(" -", e)
sys.exit(1 if echecs else 0)
