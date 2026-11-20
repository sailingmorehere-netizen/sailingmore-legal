# L'atelier du site sailingmore.fr

Tu travailles sur `sailingmore.fr` (site statique, GitHub Pages). La branche `claude` est
**l'atelier** : on y écrit la source, jamais le site publié.

## La règle en une phrase

**Tu pousses sur `claude`, jamais sur `main`.** Le serveur reconstruit le site avec la même commande
que le travail à la main, le contrôle, puis publie sur `main`. Rien de ce que tu pousses ne va en
ligne tel quel.

## Travailler

```bash
git clone https://github.com/sailingmorehere-netizen/sailingmore-legal
cd sailingmore-legal && git checkout claude
# éditer atelier/source/accueil_site.py, site_blocks.py, mer_louvoyage.py, carte_site.py
```

Tester le rendu, sans rien publier :

```bash
cd atelier
SITE_ROOT="$PWD/donnees" PYTHONPATH="$PWD/source" python3 source/mer_louvoyage.py
SITE_ROOT="$PWD/donnees" PYTHONPATH="$PWD/source" python3 source/accueil_site.py --site
# résultat : donnees/projets/sailingmore/site/index.html
```

Puis :

```bash
git add -A atelier && git commit -m "ce que tu as changé, en clair" && git push origin claude
```

Dans les quinze minutes, la reconstruction tourne, contrôle la charte et la taille de page, et
publie. Tu reçois le résultat dans le fil Telegram de Nicolas (« ATELIER PUBLIÉ · sha · message »
ou « ATELIER NON PUBLIÉ » avec la raison). Si c'est refusé, corrige et repousse sur `claude`.

## Ce qui est interdit

- **Pousser sur `main`** : c'est le site en production, un commit y va en ligne en deux minutes,
  sans contrôle.
- **Modifier les `.html` à la racine du dépôt** : ils sont régénérés à chaque publication, tes
  retouches seraient écrasées. La forme se change dans `atelier/source/`, jamais dans le HTML produit.
- **Ajouter un second chemin de publication** (un script qui écrit le site ailleurs). C'est ce qui a
  causé le bug du 20/11/2026 : un cron publiait un vieux gabarit et effaçait les correctifs du jour.

## Ce qui ne se touche pas sans Nicolas

- Charte : marine `#0a1a2b`, panneaux `#0f2438`, rouge `#e23a3e` (il souligne, il n'écrit pas).
- Les vagues, la houle et le cordage ont été retirés le 19/11/2026 : ne pas les remettre.
- Six langues (FR, EN, IT, ES, PT, DE) : toute chaîne visible passe par une clé de traduction dans
  les six.
- Aucun chiffre inventé : les bourses viennent de `atelier/donnees/projets/sailingmore/bourses.json`.
- Un seul écart vertical entre sections : 6,5 rem.
- Les pages de la racine ne portent pas de données de travail : `donnees/` est la seule source.

## Si la reconstruction échoue

Le message dit pourquoi (trace Python, charte absente, page trop petite de 10 %). Corrige dans
`atelier/source/`, repousse sur `claude`. Ne touche pas à `main` pour « réparer » : la version en
ligne est la dernière qui a passé le contrôle.
