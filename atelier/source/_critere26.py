"""Tâche 26 : copie la page à la racine de la copie de travail (là où le critère la lit) et le compte."""
import re
import shutil
from pathlib import Path

R = Path(__file__).resolve().parent.parent
shutil.copyfile(R / "projets/sailingmore/site/regates.html", R / "regates.html")
t = (R / "regates.html").read_text(encoding="utf-8")
v = re.sub(r'<script.*?</script>', '', t, flags=re.S)
n = len(re.findall(r'class=.epreuve', v))
print('epreuves HTML', n)
assert n >= 200
