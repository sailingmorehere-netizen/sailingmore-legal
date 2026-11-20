# sailingmore.fr — dossier de travail pour Claude Code

Fait le 20/11/2026 pour Nicolas. Ce dossier est **autonome** : le site se régénère avec la commande
plus bas, sans rien d'autre que Python 3 et Pillow. Il a été testé ici : il produit un `index.html`
identique **au caractère près** à celui qui est en ligne.

## 1. Ce qu'est ce site

Site **statique** (HTML + un fichier JS + des images), publié sur GitHub Pages, dépôt public
`https://github.com/sailingmorehere-netizen/sailingmore-legal`, branche `main`, servi sur
`sailingmore.fr`. Une publication = un commit unique ; GitHub Pages reconstruit en une à deux minutes.
Pas de CMS, pas de base de données, pas de PHP.

**La source n'est pas dans le dépôt** : le HTML publié est un produit, généré par les scripts de
`source/`. C'est le piège numéro un.

## 2. Le piège : modifier le HTML publié ne tient pas

`index.html`, `jeux.html`, `annonceurs.html` sont **régénérés** à chaque publication. Une retouche
faite directement dans le HTML du dépôt est **écrasée** au passage suivant. Il faut modifier la
source Python, régénérer, puis publier.

## 3. Régénérer

```bash
cd site-claude
SITE_ROOT="$PWD/donnees" PYTHONPATH="$PWD/source" python3 source/accueil_site.py --site
```

Résultat dans `donnees/cache/rhum/site/` : `index.html`, `jeux.html`, `concours.html`, les pages
légales, `robots.txt`, `sitemap.xml`, `404.html`, et les images déjà en place. Ouvrir
`donnees/cache/rhum/site/index.html` dans un navigateur pour voir le rendu.

Référence de comparaison : `reference/index.html` est exactement ce que sert le site au 20/11/2026.
Un écart de 25 Ko n'est pas une retouche, c'est un retour en arrière (le 19/11, un envoi portait
encore l'ancien design à 113 Ko).

## 4. Ce qui ne se touche pas sans Nicolas

- **Charte** : marine `#0a1a2b`, panneaux `#0f2438`, rouge `#e23a3e` — le rouge souligne, il n'écrit pas.
  Filets droits, rien de franchement arrondi.
- **Les vagues, la houle et le cordage** ont été retirés le 19/11/2026 : ne pas les remettre.
- **Six langues** : FR, EN, IT, ES, PT, DE. Toute chaîne visible passe par une clé de traduction dans
  les six, sinon les pages étrangères affichent du français.
- **Aucun chiffre inventé.** Les bourses viennent de `donnees/projets/sailingmore/bourses.json` ; le
  nombre de participants est précédé de « ≈ » et n'apparaît que si Nicolas l'a fourni.
- **Un seul écart vertical entre sections : 6,5 rem.** Corrigé le 20/11, ne doit pas revenir.
- **La publication reste une décision de Nicolas.** Claude livre un patch ou les fichiers modifiés,
  avec la commande de régénération et une capture du rendu — pas un commit direct sur `main`.

## 5. Contenu du dossier

- `source/` : `accueil_site.py` (le générateur), `site_blocks.py` (les blocs), `mer_louvoyage.py`
  (la scène WebGL en fond), `carte_site.py` (la carte du monde).
- `donnees/cache/rhum/` : les chiffres, les citations, la file de vidéos, la géographie des villes,
  l'audience par pays, et le site déjà généré.
- `donnees/cache/documents/demo-v3-detaillee.html` : le moteur WebGL d'origine.
- `donnees/projets/sailingmore/bourses.json` : les bourses aux équipiers (groupes Facebook, zones).
- `reference/index.html` : la copie de ce qui est en ligne.
