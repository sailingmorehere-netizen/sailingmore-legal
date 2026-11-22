"""Lance un générateur de page DANS la copie de travail (sans ça, ICI = /opt/data : hors copie).
Usage : _construire_ici.py regates_page|stages_page|... [--verifier|--ecrire]"""
import os, sys, runpy
from pathlib import Path
racine = Path(__file__).resolve().parent.parent
os.environ["SAILINGMORE_RACINE"] = str(racine)
nom = sys.argv[1]
sys.argv = [nom] + sys.argv[2:]
sys.path.insert(0, str(racine / "scripts"))
runpy.run_path(str(racine / "scripts" / (nom + ".py")), run_name="__main__")
