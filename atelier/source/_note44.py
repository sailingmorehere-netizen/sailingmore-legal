l = "- 27/11/2026 — Stages, niveau (tâche 44) : copie de travail sans les écritures des tâches 52/59 ; rejoué niveaux_cnv59.py --ecrire (104 offres CNV, étiquette de session), niveau_versoix52.py (3) et _niveau47.py applique (2) → 469 manquants sur 904, seuil 450 NON atteint (19 de trop). Rien déduit du titre (niveau_titre_toutes.py : 0 écrivable). Les ~470 autres pages écoles ne portent aucune étiquette de niveau. Pour passer : abaisser le seuil à 470 ou retirer ~19 offres non-cours — décision de Nicolas. Réversible : stages.json.bak-avant-59b.\n"
open('claude/decisions-prises.md', 'a', encoding='utf-8').write(l)
open('RAPPORT.md', 'w', encoding='utf-8').write("""# Tâche 44 — niveau des offres de stages

Décision prise : pas de déduction depuis le titre (consigne de Nicolas) — noté dans claude/decisions-prises.md.

**Critère NON atteint** : `verifie_champ_stages.py niveau 450` → 469 manquants sur 904 (départ : 578).

Fait : rejoué sur la copie `niveaux_cnv59.py --ecrire` (104 offres CNV Versoix, étiquette de session lue sur cnv.ch),
`niveau_versoix52.py` (3), `_niveau47.py applique` (2 étiquettes « Level » : virgins, 7seas). 109 offres renseignées.
Reste : 469. `niveau_titre_toutes.py` ne trouve plus rien d'écrivable ; les ~470 autres pages d'école
(relues par _niveau47, 4 erreurs réseau) n'affichent aucun niveau. 3 sessions CNV (Ascension, vendredis soirs) non appariées.

Cause : il manque 19 offres. Pour passer sans deviner : seuil à 470, ou retirer ~19 offres non-cours (pages zones/accueil, uksa 51 vides) — décision de Nicolas.

Fichiers : projets/sailingmore/stages.json (sauvegarde stages.json.bak-avant-59b), claude/decisions-prises.md, scripts/_x44.py, scripts/_note44.py (temporaires).
""")
