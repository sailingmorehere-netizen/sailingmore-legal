#!/usr/bin/env python3
"""Tâche 25 : si site/cours.html est redevenu le monolithe (reconstruction), le prendre comme matière première
puis relancer decoupe_cours.py. Même effet que cours_page.ecrire_page, sans pavillons_cours (absent de la copie)."""
import re
import shutil
import subprocess
import sys

S = 'projets/sailingmore/site/cours.html'
BAK = 'projets/sailingmore/preparation/cours-monolithe-avant-56.html'
t = open(S, encoding='utf-8').read()
if len(re.findall(r'<h1', t)) > 1:
    shutil.copyfile(S, BAK)
    print('monolithe actuel copié en matière première')
sys.exit(subprocess.run([sys.executable, 'scripts/decoupe_cours.py']).returncode)
