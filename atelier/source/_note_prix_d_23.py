import os
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
d = ("- 27/11/2026 — Stages, prix lot D (tâche 23, 4e passe) : scripts/applique_prix_d.py rejoué "
     "(93/132, 70 %). Aucune nouvelle recherche : les passes 24, 26, 29, 31 ont épuisé les pages ; "
     "les 25 lignes o[16]=1 ne sont pas des stages et les pages restantes n'affichent aucun montant. "
     "Seuil 90 % inatteignable sans inventer un prix ou retirer des lignes (suppression = décision de Nicolas). "
     "Ne plus mettre ce lot dans la file tant que la règle du seuil ou la liste n'a pas changé. "
     "Réversible : remettre prix à null.\n")
with open(os.path.join(R, 'claude/decisions-prises.md'), 'a') as f:
    f.write(d)
r = ("# Rapport — tâche 23, prix lot D\n\n"
     "Décision prise : pas de 5e tour de recherche, rejeu de scripts/applique_prix_d.py seulement "
     "(échec identique aux tâches 24/26/29/31 ; noté dans claude/decisions-prises.md).\n\n"
     "- Résultat : `verifie_stages_champ.py prix_d` = 93/132 (70 %), seuil 90 % → sort en 1. **Tâche non réussie.**\n"
     "- Fait : copie revenue à 86/132, rejeu du script → 7 prix reposés (indices 76, 100, 101, 106, 209, 211, 291).\n"
     "- Pourquoi bloqué : 25 lignes (o[16]=1) sont des pages d'histoire/quiz/adhésion, pas des stages ; "
     "les autres pages (Reichenau, Rehbach, Schluchsee, Slowlife, Windzone…) n'affichent aucun montant. "
     "Atteindre 119/132 demande d'inventer des prix ou de retirer des lignes.\n"
     "- Pour Nicolas : retirer les 25 lignes non-stage du lot, ou baisser le seuil, ou sortir cette tâche de la file.\n"
     "- Fichiers : projets/sailingmore/site/stages-proches.json (via script), claude/decisions-prises.md, scripts/etat_prix_d.py et _note_prix_d_23.py (outils).\n"
     "- Questions posées : 0.\n")
with open(os.path.join(R, 'RAPPORT.md'), 'w') as f:
    f.write(r)
