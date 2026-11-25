import os, sys, pathlib
COPIE = pathlib.Path(__file__).resolve().parent.parent
os.environ["SITE_ROOT"] = str(COPIE)
sys.path.insert(0, str(COPIE / "scripts"))
import accueil_site
assert str(accueil_site.SITE).startswith(str(COPIE)), accueil_site.SITE
print(accueil_site.SITE, accueil_site.poser_langue_partout())
