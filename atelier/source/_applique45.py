"""Tâche 45 : comparatif persistant (localStorage sm-comparatif) + bouton « Ajouter au comparatif » avec rang."""
import sys
p = sys.argv[1] if len(sys.argv) > 1 else 'scripts/stages_page.py'
s = open(p, encoding='utf-8').read()


def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (a, s.count(a))
    s = s.replace(a, b)


L = {
    '"Tout retirer", "fermer": "Fermer", "ajouter": "Comparer"': ('Ajouter au comparatif', 'Dans le comparatif'),
    '"Clear all", "fermer": "Close", "ajouter": "Compare"': ('Add to comparison', 'In comparison'),
    '"Alles entfernen", "fermer": "Schließen", "ajouter": "Vergleichen"': ('Zum Vergleich hinzufügen', 'Im Vergleich'),
    '"Togli tutto", "fermer": "Chiudi", "ajouter": "Confronta"': ('Aggiungi al confronto', 'Nel confronto'),
    '"Quitar todo", "fermer": "Cerrar", "ajouter": "Comparar"': ('Añadir a la comparación', 'En la comparación'),
    '"Retirar tudo", "fermer": "Fechar", "ajouter": "Comparar"': ('Adicionar à comparação', 'Na comparação'),
}
for a, (x, y) in L.items():
    pre = a.rsplit('"ajouter": ', 1)[0]
    rep(a, pre + '"ajouter": "%s", "dans": "%s"' % (x, y))

rep("""aria-pressed="'+(cmpPos(o.__i)>=0?'true':'false')+'">'+esc(c('ajouter'))+'</button>'""",
    """aria-pressed="'+(cmpPos(o.__i)>=0?'true':'false')+'">'+esc(cmpLibelle(o.__i))+'</button>'""")
rep("""    bs[k].setAttribute('aria-pressed',cmpPos(i)>=0?'true':'false')}""",
    """    bs[k].setAttribute('aria-pressed',cmpPos(i)>=0?'true':'false');bs[k].textContent=cmpLibelle(i)}""")
rep("""function cmpPos(i){""", """/* Stockage (sans compte) : localStorage « sm-comparatif » = {v:1, ids:[lien de l'offre,…], maj:ms}.
   On range le lien de l'offre, pas son rang dans la page (le rang change à chaque régénération) ;
   c'est le format qu'une synchronisation par l'API des favoris (rangs 500→507) pourra lire et
   écrire tel quel. L'adresse (?cmp=) l'emporte sur le stockage quand elle est présente. */
var CLE_CMP='sm-comparatif';
function cmpId(o){return o.lien||o.titre}
function cmpLire(){try{var s=JSON.parse(localStorage.getItem(CLE_CMP)||'null');return s&&s.v===1&&Array.isArray(s.ids)?s.ids:[]}catch(e){return[]}}
function cmpSauve(){try{localStorage.setItem(CLE_CMP,JSON.stringify({v:1,ids:CMP.map(function(i){return cmpId(D.offres[i])}),maj:Date.now()}))}catch(e){}}
function cmpDepuisIds(ids){var r=[];ids.forEach(function(id){for(var i=0;i<D.offres.length;i++)if(cmpId(D.offres[i])===id){if(r.indexOf(i)<0)r.push(i);break}});return r.slice(0,4)}
function cmpLibelle(i){var p=cmpPos(i);return p>=0?'✓ '+(p+1)+' · '+c('dans'):c('ajouter')}
function cmpPos(i){""")
rep("""  if(cp){CMP=cp.split(',').map(Number).filter(function(i){return i>=0&&i<D.offres.length}).slice(0,4)}""",
    """  if(cp){CMP=cp.split(',').map(Number).filter(function(i){return i>=0&&i<D.offres.length}).slice(0,4)}
  else CMP=cmpDepuisIds(cmpLire());""")
rep("""  if(!cmpBascule(i)){var a=document.getElementById('cmp-aide');if(a)a.textContent=c('max');return}
  majBoutonsCmp();dessinerCmp();ecrireUrl();""",
    """  if(!cmpBascule(i)){ouvrirCmp(true,true);var a=document.getElementById('cmp-aide');if(a)a.textContent=c('max');return}
  cmpSauve();majBoutonsCmp();dessinerCmp();ecrireUrl();""")
rep("""function(){CMP=[];majBoutonsCmp();dessinerCmp();ecrireUrl()}""",
    """function(){CMP=[];cmpSauve();majBoutonsCmp();dessinerCmp();ecrireUrl()}""")
open(p, 'w', encoding='utf-8').write(s)
print('ok')
