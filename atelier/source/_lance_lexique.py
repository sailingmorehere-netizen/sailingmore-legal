import os, sys, runpy, pathlib
racine = pathlib.Path(__file__).resolve().parent.parent
os.environ["SAILINGMORE_RACINE"] = str(racine)
sys.path.insert(0, str(racine / "scripts"))
sys.argv = ["lexique_page.py", "--site"]
runpy.run_path(str(racine / "scripts/lexique_page.py"), run_name="__main__")
