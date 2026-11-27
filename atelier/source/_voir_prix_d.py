import os
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
open(os.path.join(R, 'claude/decisions-prises.md'), 'a', encoding='utf-8').write(
    "- 27/11/2026 — Stages, prix lot D (tâche 14) : refusée en une ligne, aucune modification. "
    "86/128 (67 %), seuil 90 % = 116. Parmi les 42 vides, 22 seulement sont de vraies offres "
    "(dernière colonne 0), 20 sont des pages nav/vitrine/actu : même tous posés, 108 < 116. "
    "Atteindre le seuil exige d'inventer des prix ou de changer le seuil / retirer les lignes "
    "non-stage de LOTS. Ne plus mettre ce lot en file avant que le seuil ou la liste change. "
    "Réversible : rien à défaire.\n")
