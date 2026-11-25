import os, runpy
os.environ["SITE_ROOT"] = "/opt/data/cache/claude-nuit/travail"
runpy.run_path("/opt/data/cache/claude-nuit/travail/scripts/accueil_site.py", run_name="__main__")
