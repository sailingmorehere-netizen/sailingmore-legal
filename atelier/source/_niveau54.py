"""Passe 54 : relit les corps de pages en cache (lus par curl en passe 58) et pose niveau
seulement sur phrase explicite debutant OU confirme (jamais les deux). Sinon vide."""
import json, re, sys, shutil, os
P = 'projets/sailingmore/stages.json'
if not os.path.exists(P + '.bak-avant-54'):
    shutil.copy(P, P + '.bak-avant-54')
d = json.load(open(P, encoding='utf-8'))
L = d['offres']
cb = json.load(open('scripts/_niveau58_corps.json'))
DEB = re.compile(r'(for|geared to|aimed at|suitable for|ideal for|perfect for) (complete |absolute |total |true )?(beginners|novices|first[- ]time sailors)|'
                 r'(complete|absolute|total) beginners?|no (previous |prior |sailing )?experience|never (sailed|been sailing)|'
                 r'beginner[s]? (course|level|sailing)|level\s*:?\s*beginner|'
                 r'(voor|f[üu]r) (absolute )?(beginners|anf[äa]nger|einsteiger)|ohne (segel)?vorkenntnisse|keine (segel)?vorkenntnisse|geen (zeil)?ervaring|'
                 r'(pour|aux) (les )?d[ée]butants|niveau\s*:?\s*d[ée]butant|sin experiencia|para principiantes|'
                 r'per (i )?principianti|nessuna esperienza|senza esperienza|iniciantes', re.I)
CON = re.compile(r'(for|geared to|aimed at|suitable for) (more )?(experienced|advanced|competent|qualified) (sailors|skippers|crew|students|sailing)|'
                 r'(prior|previous|solid|good|some|sailing) experience (is )?(required|needed|necessary|essential)|'
                 r'(you|candidates|students) (must|should) (have|hold) (a |an )?(day skipper|competent crew|rya)|'
                 r'level\s*:?\s*(advanced|experienced)|voor gevorderden|f[üu]r (erfahrene|fortgeschrittene)|'
                 r'(pour|aux) (les )?(marins )?(confirm[ée]s|exp[ée]riment[ée]s)|niveau\s*:?\s*confirm[ée]|'
                 r'para (navegantes )?(avanzados|experimentados)|per (velisti )?esperti|esperienza (precedente )?(richiesta|necessaria)', re.I)
n = 0
for e in L:
    if e.get('niveau'):
        continue
    t = cb.get(e.get('lien') or '') or ''
    a, b = DEB.search(t), CON.search(t)
    if bool(a) != bool(b):
        m = a or b
        if len(sys.argv) > 1:
            print('D' if a else 'C', e['ecole_slug'], '|', t[max(0, m.start() - 60):m.end() + 60])
        e['niveau'] = 'debutant' if a else 'confirme'
        n += 1
json.dump(d, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('poses', n, '; vides', sum(1 for e in L if not e.get('niveau')))
