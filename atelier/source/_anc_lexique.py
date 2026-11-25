import json
p='projets/sailingmore/lexique.json'
d=json.load(open(p))
L=['fr','en','it','es','pt','de']
ref={'fr':'anc. fr.','en':'vieil angl.','it':'TLIO','es':'Nebrija','pt':'portugais ancien','de':'ahd.'}
seed={'ecoute':{'fr':'escote'},'drisse':{'it':'drizza'},'foc':{'fr':'fouc'}}
for th in d['themes']:
    for x in th['termes']:
        x['anc']={l:{'variante':ref[l],'forme':seed.get(x['cle'],{}).get(l),
            'statut':'a_verifier' if seed.get(x['cle'],{}).get(l) else 'non_verifie'} for l in L}
json.dump(d,open(p,'w'),ensure_ascii=False,indent=1)
t=[x for th in d['themes'] for x in th['termes']]
print(len(t),sum(1 for x in t if len(x['anc'])>=6))
