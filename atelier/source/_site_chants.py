"""Lance `accueil_site.py --site` contre la copie de travail (SITE_ROOT et SAILINGMORE_RACINE = racine de la copie). N'envoie rien."""
import os, sys, runpy
from pathlib import Path
racine = Path(__file__).resolve().parent.parent
os.environ["SITE_ROOT"] = str(racine)
os.environ["SAILINGMORE_RACINE"] = str(racine)
sys.argv = ["accueil_site.py", "--site"]
runpy.run_path(str(racine / "scripts" / "accueil_site.py"), run_name="__main__")
