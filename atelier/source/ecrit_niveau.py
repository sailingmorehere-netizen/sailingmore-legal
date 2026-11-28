# © 2026 Sailing More — tous droits réservés. All rights reserved.
"""Ecrit `niveau` dans stages.json quand le TITRE de l'offre le dit (echelle RYA / ASA / ISPA, mots explicites).
Ne touche jamais un niveau deja present. Rien d'ecrit quand le titre ne dit rien."""
import json, re
P = 'projets/sailingmore/stages.json'
raw = json.load(open(P, encoding='utf-8'))
L = raw if isinstance(raw, list) else max([v for v in raw.values() if isinstance(v, list)], key=len)

EXCLU = re.compile(r'essentials|next step|preparation for|pre course|instructor|requirements|payment|'
                   r'policies|cancellation|checklist|first time|schedule|regatta schedule|girls only|luxury|flotilla|'
                   r'charter|marinas|tips|winds|itinerary|destinations|holiday|vacation', re.I)
REGLES = [
    ('confirme', r'yachtmaster|coastal skipper|dinghy advanced|advanced powerboat|asa 10[56]\b|advanced week|'
                 r'performance sailing|professional skipper|advanced regatta|ocean|ISPA Coastal Skipper|'
                 r'powerboat advanced|vela avanzato'),
    ('intermediaire', r'day skipper|dinghy improver|asa 10[34]\b|asa 114|powerboat (course )?level 2|'
                      r'coastal navigator|essential navigation|gennaker|advanced 3-day|fortgeschrittenen|'
                      r'helmsman|catamaran training|basic ii|spi-segelkurs|trapez-segelkurs|spinnakertraining|corso spinnaker'),
    ('debutant', r'start yachting|competent crew|dinghy level 1|dinghy start|dinghy minis|intro to sailing|'
                 r'beginner|asa 101\b|basic sailing course|anf[aä]nger|reinschnuppern|powerboat level 1|'
                 r'discover sailing|proefles|zeilen voor de vakantie|basic i\\b|schnupper|^grundkurs|vela base|'
                 r'bautismo de vela|segeln lernen|d[ée]butants'),
]
n = 0
for e in L:
    if e.get('niveau') or EXCLU.search(e.get('titre') or ''):
        continue
    for niv, rx in REGLES:
        if re.search(rx, e.get('titre') or '', re.I):
            e['niveau'] = niv
            n += 1
            break
json.dump(raw, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('ecrits', n, '; sans niveau', sum(1 for e in L if not e.get('niveau')), '/', len(L))
