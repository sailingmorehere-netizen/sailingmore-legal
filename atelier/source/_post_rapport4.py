"""Rejoue, DANS la copie, les étapes d'habillage de accueil_site.py (bloc stages, mer, barre, équilibre) sur le site
déjà écrit. Même chemin que le build complet, sans la page d'accueil (citations-marins.json absent de la copie)."""
import os, sys
from pathlib import Path
racine = Path(__file__).resolve().parent.parent
os.environ["SITE_ROOT"] = str(racine)
os.environ["SAILINGMORE_RACINE"] = str(racine)
sys.path.insert(0, str(racine / "scripts"))
import accueil_site as A
import stages_page
print("site :", A.SITE)
print("bloc stages :", stages_page.injecter_bloc(A.SITE))
print("mer :", A.poser_mer_partout())
print("barre :", A.poser_entete_partout())
print("équilibre :", A.poser_equilibre(A.SITE))
