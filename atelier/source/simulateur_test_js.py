#!/usr/bin/env python3
# Test de fumée du JS du simulateur sous node, avec un faux DOM : parcourt les 50 scénarios
# dans les six langues, répond, et vérifie qu'aucun rendu ne contient NaN / undefined.
import os, re, shutil, subprocess, sys
RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
page = open(os.path.join(RACINE, "projets/sailingmore/site/simulateur.html"), encoding="utf8").read()
js = re.search(r"<script>(.*?)</script>", page, re.S).group(1)
harnais = """
var els={},handler=null,bad=[];
function el(id){return els[id]||(els[id]={id:id,_h:'',textContent:'',hidden:false,className:'',
  set innerHTML(v){this._h=v;if(/NaN|undefined|\\[object/.test(String(v)))bad.push(id+':'+String(v).slice(0,80));},get innerHTML(){return this._h;},
  getElementsByTagName:function(){var m=this._h.match(/<button[^>]*>/g)||[];return m.map(function(x){var r=/data-r="(\\w+)"/.exec(x);return {_v:r&&r[1],disabled:false,className:'',getAttribute:function(){return this._v;}};});},
  querySelector:function(){return null;}});}
var document={documentElement:{},title:'',getElementById:el,addEventListener:function(e,f){handler=f;}};
var location={hash:'',origin:'x',pathname:'/s'};var history={replaceState:function(){}};
var navigator={language:'fr'};var window={prompt:function(){}};
function click(attrs,id){var b={id:id||'',hasAttribute:function(k){return k in attrs;},getAttribute:function(k){return attrs[k];},set textContent(v){}};
  handler({target:{closest:function(){return b;}}});}
"""
fin = """
var n=0;
['fr','en','de','it','es','pt'].forEach(function(l){
  click({'data-l':l});
  click({'data-f':'all'});
  for(var i=0;i<50;i++){click({'data-r':'A'});click({},'suiv');n++;}
  if(el('corr').innerHTML.indexOf('<b>')<0)bad.push('pas de correction '+l);
});
['rrs','col','luc'].forEach(function(f){click({'data-f':f});});
console.log(JSON.stringify({rendus:n,problemes:bad.slice(0,5)}));
"""
nd = shutil.which("node")
if not nd:
    print("node absent : test JS non lancé"); sys.exit(0)
tmp = os.path.join(RACINE, "_simu_fumee.js")
open(tmp, "w", encoding="utf8").write(harnais + js + fin)
p = subprocess.run([nd, tmp], capture_output=True, text=True, timeout=60)
os.remove(tmp)
print(p.stdout.strip() or p.stderr.strip()[:800])
sys.exit(0 if '"problemes":[]' in p.stdout else 1)
