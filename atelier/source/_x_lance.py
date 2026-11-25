"""Lance un script de scripts/ avec SAILINGMORE_RACINE = la copie de travail (le garde-fou refuse le préfixe d'environnement)."""
import os
import runpy
import sys

RACINE = "/opt/data/cache/claude-nuit/travail"
os.environ["SAILINGMORE_RACINE"] = RACINE
os.environ["SITE_ROOT"] = RACINE
script = sys.argv[1]
sys.argv = [script] + sys.argv[2:]
sys.path.insert(0, RACINE + "/scripts")
runpy.run_path(RACINE + "/scripts/" + script, run_name="__main__")
