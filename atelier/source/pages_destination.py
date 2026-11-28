#!/usr/bin/env python3
# © 2026 Sailing More — tous droits réservés. All rights reserved.
"""Pages par destination (audit SEO 24/11/2026, correction 12) : PAGE MODÈLE, rien n'est publié.

Source unique : le bloc de données `<script id="donnees">` de site/stages.html (les offres déjà présentes).
Aucun chiffre n'est écrit à la main : nombre d'offres, d'écoles, prix mini et maxi, certifications
viennent de ce bloc. Le texte propre à la page est composé de phrases courtes à partir de ces comptes.

Sortie : projets/sailingmore/preparation/stage-voile-<pays>.html
(dossier volontairement HORS de `site/` et de `pages/`, que le générateur recopie en ligne :
Nicolas valide la page modèle avant toute publication).

    python3 scripts/pages_destination.py GRC          # écrit la page modèle
"""
from __future__ import annotations

import html
import json
import re
import sys
from collections import Counter
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
SITE = RACINE / "projets" / "sailingmore" / "site"
SORTIE = RACINE / "projets" / "sailingmore" / "preparation"
URL = "https://sailingmore.fr"

# Un pays = un mot-clé principal et ses variantes. Rien d'autre n'est écrit à la main.
PAYS = {
    "GRC": {"slug": "grece", "nom": "Grèce", "en": "en Grèce",
            "variantes": ["stage voile Grèce", "stage croisière Grèce", "formation RYA en Grèce",
                          "école de voile en Grèce", "stage catamaran Grèce"]},
}
CERTIF = {"RYA": "RYA"}


def offres() -> list[dict]:
    s = (SITE / "stages.html").read_text(encoding="utf-8")
    m = re.search(r'<script id="donnees" type="application/json">', s)
    return json.loads(s[m.end():s.find("</script>", m.end())])["offres"]


def e(x) -> str:
    return html.escape(str(x), quote=True)


def eur(n: float) -> str:
    return f"{int(round(n)):,}".replace(",", " ") + " €"


def jour(iso: str) -> str:
    a, m, j = iso.split("-")
    return f"{j}/{m}/{a}"


def construire(code: str) -> tuple[str, dict]:
    P = PAYS[code]
    o = [x for x in offres() if x.get("pays") == code]
    if not o:
        raise SystemExit(f"aucune offre pour {code}")
    n = len(o)
    ecoles = Counter(x["ecole"] for x in o)
    prix = sorted(x["prix_eur"] for x in o if x.get("prix_publie") and x.get("prix_eur"))
    certifs = Counter(x["certif"] for x in o if x.get("certif"))
    theorie = sum(1 for x in o if x.get("type") == "theorie")
    mis_a_jour = max(x["verifie"] for x in o if x.get("verifie"))
    nom, pour = P["nom"], P["en"]

    titre = f"Stage de voile {pour} : {n} offres et prix | Sailing More"
    # Phrases : courtes, chaque nombre vient des comptes ci-dessus.
    liste_ecoles = ", ".join(f"{k} ({v})" for k, v in ecoles.most_common())
    intro = (f"Vous cherchez un stage de voile {pour} ? Sailing More réunit {n} offres, "
             f"relevées chez {len(ecoles)} écoles. Chaque offre renvoie vers la fiche de l'école, qui fait foi. "
             f"Dernière vérification des liens : {jour(mis_a_jour)}.")
    p_offre = [f"Ce sont des stages de voile {pour} proposés par {len(ecoles)} écoles : {liste_ecoles}."]
    if certifs:
        c = ", ".join(f"{v} offre{'s' if v > 1 else ''} {k}" for k, v in certifs.most_common())
        p_offre.append(f"Côté certification, l'école l'indique pour {sum(certifs.values())} offres : {c}.")
    if theorie:
        p_offre.append(f"{theorie} de ces offres sont des cours théoriques, pas des stages en mer.")
    if prix:
        p_prix = (f"{len(prix)} offres sur {n} affichent un prix. La moins chère est à {eur(prix[0])}, "
                  f"la plus chère à {eur(prix[-1])}. Les autres n'ont pas de prix publié : "
                  f"on ne l'invente pas, demandez-le à l'école.")
    else:
        p_prix = (f"Aucune des {n} offres n'affiche de prix pour l'instant. On ne l'invente pas : "
                  f"demandez-le à l'école.")
    p_choix = ("Pour comparer avec les autres pays, filtrez par niveau, par durée ou par langue "
               "sur la page des stages de voile en Europe.")

    lis = []
    for x in sorted(o, key=lambda x: (x.get("debut") or "9999", x["ecole"], x["titre"])):
        bits = [x["ecole"]]
        if x.get("certif"):
            bits.append(x["certif"])
        if x.get("duree_jours"):
            bits.append(f"{x['duree_jours']} jour{'s' if x['duree_jours'] > 1 else ''}")
        if x.get("debut"):
            bits.append("du " + jour(x["debut"]) + (" au " + jour(x["fin"]) if x.get("fin") and x["fin"] != x["debut"] else ""))
        bits.append(eur(x["prix_eur"]) if x.get("prix_publie") and x.get("prix_eur") else "prix à demander")
        lis.append(f'<li><a href="{e(x["lien"])}" rel="noopener nofollow" target="_blank">{e(x["titre"])}</a>'
                   f'<span> · {e(" · ".join(bits))}</span></li>')

    mots = len(re.findall(r"\w+", " ".join([intro] + p_offre + [p_prix, p_choix])))
    desc = (f"{n} stages de voile {pour} de {len(ecoles)} écoles"
            + (f", de {eur(prix[0])} à {eur(prix[-1])}" if prix else "")
            + f". Écoles, certifications et liens directs vers chaque offre.")
    page_url = f"{URL}/stage-voile-{P['slug']}.html"
    ld = {"@context": "https://schema.org", "@graph": [
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Accueil", "item": f"{URL}/"},
            {"@type": "ListItem", "position": 2, "name": "Stages de voile", "item": f"{URL}/stages.html"},
            {"@type": "ListItem", "position": 3, "name": f"Stage de voile {pour}", "item": page_url}]},
        {"@type": "ItemList", "name": f"Stages de voile {pour}", "numberOfItems": n,
         "itemListElement": [{"@type": "ListItem", "position": i + 1, "url": x["lien"], "name": x["titre"]}
                             for i, x in enumerate(o)]}]}
    corps = f"""<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(titre)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{page_url}">
<meta property="og:title" content="{e(titre)}"><meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{page_url}"><meta property="og:type" content="website">
<meta property="og:site_name" content="Sailing More"><meta property="og:image" content="{URL}/og-image.jpg">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:image" content="{URL}/og-image.jpg">
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False, separators=(",", ":"))}</script>
<style>
body{{margin:0;background:#071c31;color:#f4efe4;font:16px/1.6 "Inter SM",system-ui,sans-serif}}
main{{max-width:46rem;margin:0 auto;padding:2rem 1rem 4rem}}
h1{{font-weight:300;text-transform:uppercase;letter-spacing:.02em;line-height:1.2}}
h2{{margin-top:2rem}} a{{color:#9fd3e6}} ul{{padding-left:1.1rem}} li{{margin:.5rem 0}} li span{{opacity:.8}}
</style>
</head>
<body>
<main>
<p><a href="stages.html">← Tous les stages de voile</a></p>
<h1>Stage de voile {e(pour)} : {n} offres, écoles et prix</h1>
<p>{e(intro)}</p>
<h2>Stage voile {e(nom)} : ce que proposent les écoles</h2>
<p>{e(" ".join(p_offre))}</p>
<h2>Prix d'un stage de voile {e(pour)}</h2>
<p>{e(p_prix)}</p>
<h2>Les {n} offres de stage de voile {e(pour)}</h2>
<ul>
{chr(10).join(lis)}
</ul>
<h2>Comparer avec d'autres destinations</h2>
<p>{e(p_choix)} <a href="stages.html">Voir tous les stages</a>.</p>
</main>
</body>
</html>
"""
    return corps, {"offres": n, "ecoles": len(ecoles), "prix": len(prix), "mots_propres": mots, "titre": titre,
                   "titre_car": len(titre), "desc_car": len(desc), "slug": P["slug"]}


def main() -> None:
    code = (sys.argv[1] if len(sys.argv) > 1 else "GRC").upper()
    corps, info = construire(code)
    SORTIE.mkdir(parents=True, exist_ok=True)
    chemin = SORTIE / f"stage-voile-{info['slug']}.html"
    chemin.write_text(corps, encoding="utf-8")
    print(chemin, info)


if __name__ == "__main__":
    main()
