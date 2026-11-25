"""Lance un script de la copie avec SAILINGMORE_RACINE pointé sur la copie : python3 scripts/_n4_lance.py chants_page.py --verifier"""
import os
import runpy
import sys

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.environ["SAILINGMORE_RACINE"] = RACINE
os.environ["SITE_ROOT"] = RACINE   # accueil_site.py lit SITE_ROOT (défaut /opt/data = arbre réel, hors copie)
script = os.path.join(RACINE, "scripts", sys.argv[1])
sys.argv = [script] + sys.argv[2:]
sys.path.insert(0, os.path.dirname(script))
os.chdir(RACINE)
runpy.run_path(script, run_name="__main__")
