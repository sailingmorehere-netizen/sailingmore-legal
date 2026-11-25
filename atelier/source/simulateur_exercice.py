#!/usr/bin/env python3
"""Le simulateur de priorités, en exercice interactif posé dans le cours théorique.

Nicolas, 24/11/2026 : « pour simulateur ça tu ranges ça dans la section cours ». La page autonome
`simulateur.html` reste en ligne ; ce module en tire une version **sans sa barre et sans son CSS de
page**, posée dans le chapitre « Régate : les priorités », pour qu'on s'exerce là où on vient de lire
la règle.

Rien n'est réécrit : le masque HTML et le `<script>` viennent de
`projets/sailingmore/pages/simulateur.html`. On retire la barre (retour, langues), la langue lue dans
l'adresse, le titre et l'introduction (le chapitre les porte déjà), le bouton « Copier le lien » (il
renvoie à la page autonome) et les filtres (dans un chapitre, on ne filtre pas). Tous les
identifiants sont préfixés : une page de cours n'a pas le droit d'avoir deux `#scene`.

    python3 scripts/simulateur_exercice.py     # construit l'exercice et vérifie qu'il tient debout
"""
from __future__ import annotations

import re
from pathlib import Path

RACINE = Path("/opt/data")
PAGE = RACINE / "projets/sailingmore/pages/simulateur.html"

# Le masque du simulateur, réduit à ce qui sert dans un chapitre. `%(p)s` est le préfixe des ids.
MASQUE = """<section class="exo-sim" id="%(p)s-exercice">
<div class="entete-sc"><span id="%(p)s-num"></span><span class="badge" id="%(p)s-badge"></span></div>
<div id="%(p)s-scene"></div>
<div id="%(p)s-panneau"></div>
<p class="q" id="%(p)s-question"></p>
<div class="rep" id="%(p)s-rep"></div>
<div class="corr" id="%(p)s-corr" hidden></div>
<div class="nav"><button type="button" id="%(p)s-prec"></button><button type="button" id="%(p)s-suiv"></button><button type="button" id="%(p)s-alea"></button><span class="score" id="%(p)s-score"></span></div>
<p class="pied" id="%(p)s-avert"></p>
</section>"""

# Les identifiants que le script manipule via `$('x')`, avec le préfixe.
GARDES = ("num", "badge", "scene", "panneau", "question", "rep", "corr", "prec", "suiv", "alea", "score", "avert")


def _script(brut: str, prefixe: str, langue: str = "fr") -> str:
    """Le script du simulateur, débarrassé de la page autonome, ids préfixés."""
    m = re.search(r"<script>\s*(\(function\(\)\{.*?\}\)\(\);)\s*</script>", brut, re.S)
    if not m:
        return ""
    js = m.group(1)
    # `function $(i){return document.getElementById(i);}` reçoit un id préfixé : un seul point à changer.
    js = js.replace("return document.getElementById(i);",
                    "return document.getElementById('%s-' + i);".replace("%s", "{{P}}"))
    # Les boutons sont comparés par leur id (`b.id==='suiv'`) : dans le cours ils s'appellent
    # `sim-fr-suiv`. Sans ce retrait, « Suivant », « Précédent » et « Au hasard » ne répondaient
    # plus (24/11/2026 : le numéro restait bloqué sur « Scénario 1 / 50 », sans erreur au journal).
    js = js.replace("function $(i){return document.getElementById('{{P}}-' + i);}",
                    "function $(i){return document.getElementById('{{P}}-' + i);}\n"
                    "function _id(b){return b.id.replace('{{P}}-','');}")
    # Seulement les quatre boutons du bandeau : `b.id==='B'` désigne ailleurs un bateau du schéma,
    # et le remplacer partout aurait cassé le clic sur un bateau (24/11/2026).
    for bouton in ("prec", "suiv", "alea", "lien"):
        js = js.replace("b.id==='%s'" % bouton, "_id(b)==='%s'" % bouton)
    # Les lignes de la page autonome qui n'ont plus d'objet dans un chapitre : barre, langues,
    # filtres, titre, intro, partage. On coupe par lignes, jamais par expression régulière ancrée en
    # fin de ligne — le `$` de `$('retour')` s'y confond avec la fin de ligne, et le motif dévorait
    # tout le script (24/11/2026 : plus aucun gestionnaire de clic ne survivait).
    #
    # Le partage est le seul cas délicat : sa branche `else if(b.id==='lien')` s'étale sur quatre
    # lignes, et la quatrième (`}}`) ferme le partage **et** la fonction de clic. Le `});` de la
    # ligne suivante ferme l'écouteur. On garde ce `});`, et la ligne du partage devient une branche
    # vide suivie de `}` qui referme la fonction. Vérifié par `node --check` à chaque construction.
    ABSENTS = ("$('retour')", "$('langues')", "$('lien')", "$('filtres')",
               "$('titre')", "$('intro')")
    lignes = []
    saute = 0          # lignes du corps du partage à sauter
    apres_partage = False
    for ligne in js.split("\n"):
        if saute > 0:
            saute -= 1
            apres_partage = saute == 0
            continue
        if "_id(b)==='lien'" in ligne and "var u=location.origin" in ligne:
            saute = 3                      # `u`, les deux branches, la ligne `else{…;}}`
            # La branche est refermée ici : `{}`. Le `}` qui suit sur la ligne sautée refermait la
            # branche, et c'est le `}` du `});` suivant qui ferme la fonction de clic — les deux
            # ensemble donnaient une accolade de trop (`script invalide : missing )`, 24/11/2026).
            lignes.append(" else if(_id(b)==='lien'){}")
            continue
        if "navigator.share" in ligne or "window.prompt" in ligne or "navigator.clipboard" in ligne:
            continue
        if "$('lien').textContent" in ligne:
            # Cette ligne porte les libellés des trois boutons et celui du partage : on garde les
            # trois premiers, on retire le partage (24/11/2026 : boutons du bandeau sortis vides).
            ligne = ligne.replace("$('lien').textContent=t('lien');", "")
        if "$('langues').innerHTML=g;}" in ligne:
            # Cette ligne porte deux choses : le menu des langues, qui n'existe plus ici, et le `}`
            # qui referme `maj()`. On garde l'accolade (24/11/2026 : sans elle, `Unexpected token`).
            lignes.append("}")
            continue
        if any(a in ligne for a in ABSENTS):
            continue
        lignes.append(ligne)
        if apres_partage and ligne.strip() == "});":
            apres_partage = False
    js = "\n".join(lignes)
    # La langue vient du cours, pas de l'adresse.
    js = re.sub(r"\(location\.search[^)]*\)[^;]*;", ";", js)
    js = re.sub(r"new URLSearchParams\([^)]*\)[^;]*;", ";", js)
    # La langue est celle du chapitre qui porte l'exercice, pas celle du navigateur : les six
    # instances vivent dans la même page, et `document.documentElement.lang` leur donnerait à toutes
    # la même langue (24/11/2026 : le simulateur allemand parlait français).
    js = js.replace("var L='fr'", "var L='%s'" % langue)
    # La langue du document appartient au cours : six instances écriraient chacune la leur.
    js = js.replace("document.documentElement.lang=L;", "")
    # Le clic est écouté sur le document : le simulateur vit dans un chapitre, à côté de sept copies
    # pour les six langues. Sans cette garde il répond pour toutes, et le « Suivant » de l'une fait
    # avancer les autres — le 24/11/2026, « Suivant » ne changeait donc jamais de situation.
    js = re.sub(r"var b=e\.target\.closest\?e\.target\.closest\('button'\):null;if\(!b\)return;",
                "var b=e.target.closest?e.target.closest('button'):null;if(!b)return;"
                "var _m=document.getElementById('{{P}}-exercice');"
                "if(_m&&!(_m.contains(b)&&b.closest('.exo-sim')===_m))return;", js)
    # Le fil des adresses : chaque situation s'écrit dans l'adresse sur la page autonome ; dans le
    # cours, cela remplacerait le lien de la page ouverte par `#s=…&l=…`.
    js = re.sub(r"function histo\(\)\{[^\n]*\n", "function histo(){}\n", js)
    # Borné à la fonction elle-même : `.*?` avec `re.S` partait du premier `function depuisHash`
    # jusqu'au dernier `}` du script, et supprimait le gestionnaire de clic au passage (24/11/2026).
    # Les bornes : la fonction telle que la page l'écrit, à l'identique, jusqu'à la fin de son bloc.
    ancien = re.search(r"function depuisHash\(\)\{.*?\}\ndocument\.addEventListener", js, re.S)
    if ancien:
        js = js.replace(ancien.group(0),
                        "function depuisHash(){liste();}\ndocument.addEventListener")
    # Ce que le masque n'a pas : titre, intro, filtres, partage, menu des langues.
    for retrait in ("$('titre').textContent=t('titre');document.title=t('titre')+' — Sailing More';",
                    "$('intro').textContent=t('intro');",
                    "var f=[['all','tous'],['rrs','f_rrs'],['col','f_col'],['luc','f_luc']],h='';",
                    "f.forEach(function(x){h+='<button data-f=\"'+x[0]+'\" aria-pressed=\"'+(filtre===x[0])+'\">'+esc(t(x[1]))+'</button>';});",
                    "$('filtres').innerHTML=h;",
                    "var g='';LANGS.forEach(function(l){g+='<button data-l=\"'+l+'\" aria-pressed=\"'+(L===l)+'\">'+l+'</button>';});",
                    "$('langues').innerHTML=g;"):
        js = js.replace(retrait, "")
    return js


def exercice(prefixe: str = "sim") -> str:
    """L'exercice prêt à poser dans le chapitre, ou une chaîne vide si la page a disparu."""
    if not PAGE.exists():
        return ""
    brut = PAGE.read_text(encoding="utf-8")
    langue = prefixe.rsplit("-", 1)[-1] if "-" in prefixe else "fr"
    js = _script(brut, prefixe, langue)
    if not js:
        return ""
    js = js.replace("{{P}}", prefixe)
    masque = MASQUE % {"p": prefixe}
    return f"{masque}\n<script>{js}</script>"


def verifier(html: str = "") -> list[str]:
    """Ce qui empêcherait l'exercice de tourner. Liste vide = il tient debout."""
    html = html or exercice()
    pbs = []
    if not html:
        return ["exercice vide : page simulateur.html introuvable ou script illisible"]
    declares = set(re.findall(r'id="(sim-[a-z]+)"', html))
    attendus = {f"sim-{g}" for g in GARDES}
    manquants = sorted(attendus - declares)
    if manquants:
        pbs.append(f"blocs absents du masque : {', '.join(manquants)}")
    if "getElementById(i);" in html:
        pbs.append("le préfixe n'a pas été posé sur $() : les ids du cours ne seraient jamais trouvés")
    if re.search(r"\bb\.id==='(?:prec|suiv|alea|lien)'", html):
        pbs.append("les boutons sont comparés à leur id d'origine : Précédent, Suivant et Au hasard"
                   " ne répondraient pas (les ids du cours sont préfixés)")
    for reste in ("retour", "langues", "filtres"):
        if re.search(r"""\$\('""" + reste + r"""'\)""", html):
            pbs.append(f"le script cherche encore « {reste} », absent du chapitre")
    # Le seul contrôle qui aurait attrapé mes six essais à l'aveugle : le script doit être du JS
    # valide. Node est là, il coûte dix millisecondes, et sans lui une page part avec un script mort.
    js = re.search(r"<script>(.*)</script>", html, re.S)
    if js:
        import subprocess  # noqa: PLC0415
        import tempfile  # noqa: PLC0415
        with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False, encoding="utf-8") as f:
            f.write(js.group(1).replace("{{P}}", "sim"))
            chemin = f.name
        try:
            n = subprocess.run(["node", "--check", chemin], capture_output=True, text=True, timeout=30)
            if n.returncode != 0:
                pbs.append("script invalide : " + (n.stderr or "").strip().splitlines()[0][:120])
        except (OSError, subprocess.TimeoutExpired) as e:
            pbs.append(f"contrôle du script impossible : {e}")
        finally:
            Path(chemin).unlink(missing_ok=True)
    for m in re.finditer(r"var D=(\{.*?\});\n", html, re.S):
        if '"sc"' not in m.group(1):
            pbs.append("les scénarios ne sont pas embarqués")
        break
    else:
        pbs.append("aucune donnée D trouvée : l'exercice n'aurait aucune situation")
    return pbs


def main() -> int:
    html = exercice()
    pbs = verifier(html)
    for p in pbs:
        print("  ✗", p)
    if not pbs:
        print(f"exercice construit : {len(html)} octets · 12 blocs · scénarios embarqués")
    return 1 if pbs else 0


if __name__ == "__main__":
    raise SystemExit(main())
