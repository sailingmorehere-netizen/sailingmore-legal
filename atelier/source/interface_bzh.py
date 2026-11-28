# © 2026 Sailing More — tous droits réservés. All rights reserved.
"""Interface en breton — BROUILLON NON BRANCHÉ (tâche 39, nuit du 25/11/2026).

Une seule source pour les textes d'interface bretons. Aucun générateur ne l'importe encore :
tant qu'un brittophone ne l'a pas relu, le site reste en français avec l'encart (règle déjà posée
dans site_blocks.py). Chaque entrée porte son statut :
  "attesté"  = mot ou terme présent dans TermOfis/Devri (breton-source.md) ;
  "courant"  = mot de base du breton (degemer, klask, ger…), pas de la voile, à faire confirmer ;
  None       = pas de breton sûr : on garde le français (clé absente de INTERFACE_BZH).
Les clés sont celles de `UI` dans lexique_page.py. Pour brancher : `interface_de(ui, "bzh", cle)`
retombe déjà sur le français clé par clé, il suffit d'ajouter `"bzh": INTERFACE_BZH_LEXIQUE` à UI.
"""

# Interface de la page Lexique (clés de lexique_page.UI).
INTERFACE_BZH_LEXIQUE = {
    "titre": "Geriadur merdeiñ",   # geriadur = dictionnaire ; Merdeiñ = domaine voile de TermOfis
    "chapo": "Gerioù ar merdeiñ, pep hini displeget en ur frazenn ha troet e c'hwec'h yezh.",
    "retour": "← Sailing More",
    "placeholder": "Ur ger, ur pezh eus ar bag, un displegadur…",   # bag : attesté Devri
    "aria": "Klask er geriadur",
    "tous": "An holl",
    "theme": "Danvez",
    "un": "ger",
    "n": "gerioù",
    "aucun": "Ger ebet ne glot gant ar c'hlask-mañ.",
}

# Noms de rubriques. None = on laisse le français (pas de breton sûr).
RUBRIQUES_BZH = {
    "Accueil": "Degemer",          # courant
    "Cours": "Kentelioù",          # courant (kentel = leçon)
    "Lexique": "Geriadur",         # courant
    "Contact": "Darempred",        # courant
    "Régates": None,
    "Mentions légales": None,
    "Stages": None,
}

# Termes de voile attestés (extraits de breton-source.md, fiches TermOfis « Merdeiñ »), pour les chapôs.
TERMES_ATTESTES = {
    "grand-voile": "gouel vras", "génois": "fok bras", "bôme": "bomm", "drisse": "driñs",
    "point d'écoute": "poent skout", "tribord": "stribourzh", "bâbord": "babourzh",
    "catamaran": "katamaran", "bouée": "boue", "équipier": "bageer", "cockpit": "kibell",
    "gréement": "greiamant", "gouvernail": "stur", "mât": "gwern", "voile": "gouel",
    "vent": "avel", "mer": "mor", "bateau": "bag", "quai": "kae",
    # Jamais traduits : écoute (seul), ris, vent arrière, près, travers, bon plein, pétole.
}
