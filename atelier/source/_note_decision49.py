ligne = ("\n- 27/11/2026 — En-têtes de sécurité (tâche 49) : .htaccess posé à la racine de projets/sailingmore/site/ "
         "(HSTS max-age=31536000 sans includeSubDomains/preload ; nosniff ; strict-origin-when-cross-origin ; CSP avec 'unsafe-inline' "
         "faute de nonces, 21 910 pages ont du script en ligne). Origines autorisées : maps.googleapis/gstatic, unpkg, ipwho.is, "
         "openstreetmap/youtube-nocookie en iframe, accounts.google.com (tâche 28). Pas de test navigateur ici : relevé statique "
         "(scripts/_origines_csp.py). Réversible : supprimer .htaccess en ligne.\n")
with open("claude/decisions-prises.md", "a", encoding="utf-8") as f:
    f.write(ligne)
print("ok")
