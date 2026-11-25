"""Lance chants_page.py contre la copie de travail (SAILINGMORE_RACINE = racine de la copie). Usage : --verifier | --ecrire"""
import os, sys, runpy
from pathlib import Path
racine = Path(__file__).resolve().parent.parent
os.environ["SAILINGMORE_RACINE"] = str(racine)
sys.argv = ["chants_page.py"] + sys.argv[1:]
runpy.run_path(str(racine / "scripts" / "chants_page.py"), run_name="__main__")
