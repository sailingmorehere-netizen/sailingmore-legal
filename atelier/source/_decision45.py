l = ("- 26/11/2026 — tâche 45 (comparatif persistant) : cinquième offre = refusée avec le mot « Quatre offres au maximum… » "
     "(le panneau s'ouvre pour le montrer), pas de remplacement de la plus ancienne. Clé `sm-comparatif` = "
     "`{v:1, ids:[\"école|lien|titre|début\",…], maj:ms}` : le lien seul n'est pas unique (725 offres, 531 liens) et le rang "
     "dans la page change à chaque génération. `?cmp=` (rangs) l'emporte sur le stockage quand il est présent. "
     "Le générateur `stages_page.py` ne tourne pas dans la copie (module `clics_sortants` absent) : le patch est posé aussi dans `stages.html`.\n")
with open('claude/decisions-prises.md', 'a', encoding='utf-8') as f:
    f.write(l)
print('ok')
