"""Passe 59 : remplit niveau (d'apres le titre seul, regles prudentes) et duree_jours (fin - debut + 1).
Ne touche jamais un champ deja rempli. Une regle qui ne reconnait rien laisse le champ vide."""
import json, re, shutil, datetime, collections
P = 'projets/sailingmore/stages.json'
import os
if not os.path.exists(P + '.bak-avant-59'):
    shutil.copy(P, P + '.bak-avant-59')
d = json.load(open(P + '.bak-avant-59', encoding='utf-8'))  # repart toujours de l'etat d'avant la passe
EXCL = r'stcw|fire ?fighting|paddle|business and law|professional|rasys|\bsup\b|kayak|canoe|hour glass|first aid|vhf|radar'
R = [
 ('confirme', r'yachtmaster|coastal skipper|offshore|\bocean\b|\bmaster\b|advanced|instructor|hauturi|asa 10[678]\b|\borals?\b|rya professional'),
 ('intermediaire', r'day ?skipper|asa 10[345]\b'),
 ('debutant', r'start yachting|intro to sailing|intro(?:duction)? to|\bdiscover|d[ée]couverte|d[ée]butant|beginner|anf[äa]nger|level 1\b|\bbasic|grundkurs|asa 10[12]\b|initiation|optimist|competent crew|learn to sail|voor beginners|sportbootf[üu]hrerschein|\bsbf\b|principiant|iniciaci[óo]n'),
]
nn = nd = 0
par = collections.Counter()
for e in d['offres']:
    if not e.get('niveau'):
        t = (e.get('titre') or '').lower()
        for niv, rx in ([] if re.search(EXCL, t) else R):
            if re.search(rx, t):
                e['niveau'] = niv; nn += 1; par[niv] += 1
                break
    if e.get('duree_jours') in (None, '') and e.get('debut') and e.get('fin'):
        try:
            n = (datetime.date.fromisoformat(e['fin']) - datetime.date.fromisoformat(e['debut'])).days + 1
            if 1 <= n <= 60:
                e['duree_jours'] = n; nd += 1
        except ValueError:
            pass
json.dump(d, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
L = d['offres']
print('niveau remplis', nn, dict(par), 'duree remplis', nd)
print('reste niveau vide', sum(1 for e in L if not e.get('niveau')), 'duree vide', sum(1 for e in L if e.get('duree_jours') in (None, '')))
