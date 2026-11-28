#!/usr/bin/env python3
# © 2026 Sailing More — tous droits réservés. All rights reserved.
"""Corrige dans les pages déjà générées les alt vagues (même texte que scripts/site_blocks.html_stories)."""
import re
from pathlib import Path

SITE = Path(__file__).resolve().parent.parent / "projets" / "sailingmore" / "site"
f = SITE / "index.html"
h = f.read_text(encoding="utf-8")
h2 = re.sub(r'(<img src="stories/[^"]+" )alt="Story du ([0-9-]+)">',
            r'\1alt="Story SailingMore.fr du \2 : aperçu de la première feuille" loading="lazy">', h)
h2 = h2.replace('alt="Carte du monde"', 'alt="Carte du monde des régates et stages de voile référencés par SailingMore.fr"')
if h2 != h:
    f.write_text(h2, encoding="utf-8")
print("index.html modifié" if h2 != h else "rien à changer")
a = SITE / "annonceurs.html"
t = a.read_text(encoding="utf-8")
t2 = t.replace('alt="Carte du monde"', 'alt="Carte du monde des régates et stages de voile référencés par SailingMore.fr"')
if t2 != t:
    a.write_text(t2, encoding="utf-8")
    print("annonceurs.html modifié")
