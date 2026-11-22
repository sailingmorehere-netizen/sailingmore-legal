"""Régénère stages.html DANS la copie de travail (stages_page.py écrit sinon sous /opt/data)."""
import sys
from pathlib import Path

ICI = Path(__file__).resolve().parent
sys.path.insert(0, str(ICI))
import stages_page  # noqa: E402

cible = ICI.parent / "projets/sailingmore/site"
print(f"{cible / 'stages.html'} : {stages_page.ecrire_page(cible)} offre(s) publiable(s)")
