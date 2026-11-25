"""Tâche 68 — l'accueil ne bouge pas : l'ensemble des règles CSS de <style id="accueil-2026"> (index.html
actuel) est comparé à celui de accueil_2026.CSS reconstruit (ordre ignoré)."""
import re
import sys
from pathlib import Path

ICI = Path(__file__).resolve().parent
sys.path.insert(0, str(ICI))
import accueil_2026  # noqa: E402

html = (ICI.parent / "projets" / "sailingmore" / "site" / "index.html").read_text(encoding="utf-8")
m = re.search(r'<style id="accueil-2026">(.*?)</style>', html, re.S)


def regles(css: str) -> list:
    css = re.sub(r"\s+", " ", css)
    sortie, media = [], ""
    for morceau in re.split(r"(?<=\})", css):
        morceau = morceau.strip()
        if not morceau or morceau == "}":
            media = "" if morceau == "}" else media
            continue
        if morceau.startswith("@media"):
            media, morceau = morceau.split("{", 1)
            morceau = morceau.strip()
            sortie.append((media.strip(), morceau))
        else:
            sortie.append((media, morceau))
    return sorted(sortie)


ancien = regles(m.group(1))
nouveau = regles(accueil_2026.CSS)
print("règles : ancien", len(ancien), "nouveau", len(nouveau))
print("seulement avant :", [r for r in ancien if r not in nouveau])
print("seulement après :", [r for r in nouveau if r not in ancien])
