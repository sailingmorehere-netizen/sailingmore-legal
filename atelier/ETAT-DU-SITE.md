# État réel du site au 20/11/2026, 17 h 50

Deux versions existent, et elles ne sont pas identiques :

| Fichier | Taille | Design |
|---|---|---|
| `reference/index.html` — ce que la source produit | 143 676 octets | le design courant (marine `#0a1a2b`, écart de titre en colonne) |
| `https://sailingmore.fr` — ce qui est en ligne | 120 883 octets | l'ancien design (marine `#08162a`, pas de `row-gap:.72rem`) |

Vérifié par `curl https://sailingmore.fr/?x=2` le 20/11 à 17 h 50 : le fichier en ligne est identique
octet pour octet à `donnees/cache/rhum/site/index.html`, la copie de préparation à la publication, qui
n'a pas été régénérée par le générateur courant.

Cause : le cron `13e6caeaf574` (« Page d'accueil — stories du jour », 17 h 20) lance
`site_du_jour.py`, qui appelle `accueil_site.main()` avec `--publier` mais **sans `--site`**. Sans
`--site`, le générateur écrit le gabarit `page()` — l'ancien — dans `cache/rhum/site`, puis le publie.
Le design courant n'est produit que par `sortir_le_site()` (`--site`), qui écrit dans
`projets/sailingmore/site` et n'est jamais publié par ce cron.

Conséquence : les correctifs du 20/11 (écart unique de 6,5 rem, boutons à filet, titre en colonne,
carte sans légende) ont été publiés dans la journée, puis écrasés à 17 h 20 par la republication
automatique.

Rien n'a été republié : une mise en ligne demande l'accord de Nicolas.
