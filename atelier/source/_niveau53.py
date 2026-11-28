"""Passe 53 : relit le corps des pages (cache _niveau58_corps.json, lu en curl GET) pour les offres sans niveau ;
pose niveau seulement sur phrase explicite (motifs elargis NL/DE/IT/FR/EN). Sinon vide.
Usage: python3 scripts/_niveau53.py [--ecrit]"""
import json, re, sys, shutil, os, collections
P = 'projets/sailingmore/stages.json'
d = json.load(open(P, encoding='utf-8'))
L = d['offres']
corps = json.load(open('scripts/_niveau58_corps.json', encoding='utf-8'))
DEB = re.compile(
    r'(zeil)?ervaring is (niet |absoluut niet )?nodig|geen (zeil|voor)?(kennis|ervaring) (nodig|vereist)|zonder (zeil)?ervaring|'
    r'no (previous |prior |sailing |boating )?experience|beginners? (are )?welcome|suitable for (all )?beginners|for (absolute |complete )?beginners|'
    r'keine (segel|boots)?(erfahrung|vorkenntnisse)|ohne (segel)?(erfahrung|vorkenntnisse)|f[üu]r (absolute )?(segel)?anf[äa]nger|anf[äa]ngerkurs|'
    r'senza (alcuna )?esperienza|nessuna (precedente )?esperienza|per (chi )?(principianti|non ha mai)|'
    r'sans (aucune )?exp[ée]rience|aucune (connaissance|exp[ée]rience)|pour (les )?d[ée]butants|niveau d[ée]butant|'
    r'sin experiencia|para principiantes|voor (absolute )?beginners|beginnerscursus|beginner course', re.I)
CON = re.compile(
    r'(prior|previous|sufficient|solid|good|considerable) (sailing |boating )?experience (is )?(required|needed|necessary|essential)|'
    r'experience (is )?(required|essential)|for (more )?(experienced|advanced) (sailors|skippers|crew|students|sailing)|'
    r'(zeil)?ervaring (is )?(vereist|noodzakelijk)|voor (ervaren|gevorderde) (zeilers|schippers)|voor gevorderden|'
    r'vorkenntnisse (sind )?(erforderlich|n[öo]tig|vorausgesetzt)|f[üu]r (erfahrene|fortgeschrittene)|segelerfahrung (ist )?(erforderlich|vorausgesetzt)|'
    r'per (velisti )?(esperti|chi ha gi[àa] esperienza)|esperienza (pregressa )?(richiesta|necessaria)|'
    r'pour (les )?(marins |navigateurs )?(confirm[ée]s|exp[ée]riment[ée]s)|exp[ée]rience (pr[ée]alable )?(requise|exig[ée]e)', re.I)
nn = collections.Counter()
for e in L:
    if e.get('niveau'):
        continue
    t = corps.get(e.get('lien') or '') or ''
    # le pied de page « cookies / experience while you navigate » n'est pas une phrase d'offre
    a, b = DEB.search(t), CON.search(t)
    # offres qui couvrent tous les niveaux ou les deux a la fois : on laisse vide
    if e['titre'].startswith(('Meezeilen op de Noordzee', 'Sailing holidays', 'The RYA Scheme Progression')):
        continue
    if bool(a) != bool(b):
        niv = 'debutant' if a else 'confirme'
        if '--ecrit' not in sys.argv:
            print(e['ecole'][:22], '|', e['titre'][:40], '|', niv, '|', (a or b).group(0))
        else:
            e['niveau'] = niv
        nn[niv] += 1
print(dict(nn), 'total', sum(nn.values()))
if '--ecrit' in sys.argv:
    if not os.path.exists(P + '.bak-avant-53'):
        shutil.copy(P, P + '.bak-avant-53')
    json.dump(d, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('reste vide', sum(1 for e in L if not e.get('niveau')))
