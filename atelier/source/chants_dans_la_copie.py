#!/usr/bin/env python3
"""Écrit la page chants dans la copie de travail, puis la contrôle (rien n'est envoyé nulle part).

    python3 scripts/chants_dans_la_copie.py

Contrôles : données conformes, six fiches, quatre lecteurs, un emplacement vidéo par chant (vide),
hreflang complet + x-default (et pas de `br` tant que le breton n'existe pas), JSON-LD valide, aucune
page blanche (le français est dans le HTML), le JS compile et bascule dans les sept langues (si `node`
est là), le menu et le sitemap portent la page.
"""
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
os.environ["SAILINGMORE_RACINE"] = str(RACINE)
sys.path.insert(0, str(RACINE / "scripts"))
import chants_page  # noqa: E402
import site_blocks  # noqa: E402

ok = True


def verif(nom: str, cond: bool, detail: str = "") -> None:
    global ok
    ok &= bool(cond)
    print(("OK   " if cond else "ÉCHEC"), nom, detail)


d = chants_page.charger()
pb = chants_page.verifier(d)
verif("données conformes", not pb, "; ".join(pb))
print(chants_page.ecrire_page(chants_page.SITE))
h = (chants_page.SITE / chants_page.PAGE).read_text(encoding="utf-8")
statique = h.split('<script type="application/json" id="chants-donnees">')[0]   # le HTML sans les gabarits du script
verif("six fiches dans le HTML", len(re.findall(r'<article class="fiche"', statique)) == 6)
verif("quatre lecteurs dans le HTML", statique.count('<div class="lecteur"') == 4)
verif("six emplacements vidéo, vides", len(re.findall(r'<div class="emplacement-video" data-chant="\w+"></div>', h)) == 6)
verif("h1 français non vide", "<h1 id=\"h1\">Chants de marins</h1>" in h)
hl = re.findall(r'hreflang="([^"]+)"', h)
verif("hreflang fr en it es pt de + x-default, sans br", hl == ["fr", "en", "it", "es", "pt", "de", "x-default"], str(hl))
verif("canonical", '<link rel="canonical" href="https://sailingmore.fr/chants-de-marin.html">' in h)
ld = re.findall(r'<script type="application/ld\+json">(.*?)</script>', h, re.S)
verif("un seul bloc JSON-LD valide", len(ld) == 1 and json.loads(ld[0])["@graph"])
verif("pas de VideoObject (aucune vidéo publiée)", "VideoObject" not in h)
verif("pas de second sélecteur de langue ni d'en-tête propre", 'id="langues"' not in h and 'id="langue"' not in h)
verif("paroles de Santiano absentes", 'data-id="santiano"' in h and "Plante" not in h.split('data-id="santiano"')[1].split("</article>")[0].replace("Jacques Plante : protégées", ""))
verif("menu du site porte la page", any(f == chants_page.PAGE for f, _, _ in site_blocks.MENU_PAGES))
verif("barre pas encore posée ici (le fera poser_entete_partout)", 'class="entete"' not in h)
sm = chants_page.SITE / "sitemap.xml"
verif("sitemap", sm.exists() and chants_page.PAGE in sm.read_text(encoding="utf-8"))

# La barre du site posée comme le fait la construction, pour tester la bascule de langue de bout en bout.
barre = site_blocks.barre_autonome(chants_page.PAGE, site_blocks.LANGUES, True)
test = re.sub(r"(<body[^>]*>)", lambda m: m.group(1) + barre, h, count=1)
verif("barre posable (7 options + auto)", test.count("<option") == 8, str(test.count("<option")))

node = shutil.which("node")
if not node:
    print("INFO node absent : la bascule de langue n'a pas été exécutée, seulement vérifiée sur les données")
    for l in chants_page.LANGUES:
        verif(f"interface {l} complète", all(k in d["ui"][l] for k in chants_page.CLES_UI))
else:
    # Mini DOM : assez pour exécuter le script de la page, changer de langue 7 fois et compter les fiches.
    script = re.search(r"<script>(\n\(function\(\)\{\nvar D=.*?)</script>", h, re.S).group(1)
    donnees = re.search(r'id="chants-donnees">(.*?)</script>', h, re.S).group(1)
    harnais = r"""
const els={};
function E(id){return els[id]||(els[id]={id,textContent:'',innerHTML:'',value:'',placeholder:'',dataset:{},style:{},
 classList:{_s:new Set(),toggle(c){return this._s.has(c)?(this._s.delete(c),false):(this._s.add(c),true)},contains(c){return this._s.has(c)}},
 addEventListener(t,f){(this._l=this._l||{})[t]=f},setAttribute(){},querySelectorAll(){return[]},querySelector(){return null}})}
const fiches=()=>{const m=(E('liste').innerHTML.match(/<article class="fiche"/g)||[]).length;return m};
global.document={getElementById:E,documentElement:{lang:''},body:E('body'),querySelectorAll(){return[]},querySelector(){return null},
 addEventListener(t,f){(global._doc=global._doc||{})[t]=f}};
global.location={search:''};Object.defineProperty(global,'navigator',{value:{languages:['fr']},configurable:true});
global.Audio=function(){this.pause=()=>{};this.load=()=>{};this.removeAttribute=()=>{}};
let store={};global.localStorage={getItem:k=>store[k]??null,setItem:(k,v)=>{store[k]=v}};
E('chants-donnees').textContent=process.env.DONNEES;
const res=[];
eval(process.env.SCRIPT);
const fr=E('h1').textContent;res.push(['fr',document.documentElement.lang,fr,fiches()]);
for(const l of ['en','it','es','pt','de','bzh']){
  store['sm-langue']=l==='bzh'?'fr':l; store['sm-bzh']=l==='bzh'?'1':null;
  global._doc.click({target:{closest:()=>({getAttribute:()=>store['sm-langue']})}});
  res.push([l,document.documentElement.lang,E('h1').textContent,fiches(),/Paroles|Lyrics|Testo|Letra|Text/.test(E('liste').innerHTML)]);
}
console.log(JSON.stringify(res));
"""
    r = subprocess.run([node, "-e", harnais], capture_output=True, text=True,
                       env={**os.environ, "SCRIPT": script, "DONNEES": donnees})
    if r.returncode:
        verif("script exécutable", False, r.stderr[-400:])
    else:
        res = json.loads(r.stdout.strip().splitlines()[-1])
        print(res)
        verif("bascule : 7 langues, six fiches chacune", len(res) == 7 and all(x[3] == 6 for x in res))
        verif("le breton retombe sur le français", res[-1][2] == "Chants de marins" and res[-1][1] == "fr")
        verif("titres distincts dans les six langues", len({x[2] for x in res[:6]}) == 6)

print("\nTOUT TIENT" if ok else "\nÀ CORRIGER")
sys.exit(0 if ok else 1)
